"""Build corpus.json for Vietnam from the cached vbpl.vn pages (no network).

Run: python -X utf8 parse.py
"""
import hashlib
import html as htmlmod
import json
import os
import re
import sys

import vbpl

HERE = os.path.dirname(os.path.abspath(__file__))
RETRIEVED = '2026-10-28'

# ---------------------------------------------------------------- text

_QUOTES = {'“': '"', '”': '"', '„': '"', '‘': "'", '’': "'"}


def norm(s):
    s = htmlmod.unescape(s)
    s = s.replace(' ', ' ').replace('​', '').replace('﻿', '')
    for a, b in _QUOTES.items():
        s = s.replace(a, b)
    s = s.replace('–', '-').replace('—', '-').replace('…', '...')
    s = re.sub(r'\s*-{5,}\s*$', '', s)          # stray rule lines appended by the publisher
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def paragraphs(html):
    """[(cls, id, merged, text)] for every <p> outside tables, in order."""
    html = re.sub(r'<table.*?</table>', '', html, flags=re.S)
    out = []
    for m in re.finditer(r'<p\b([^>]*)>(.*?)</p>', html, flags=re.S):
        attrs, inner = m.group(1), m.group(2)
        inner = re.sub(r'<br\s*/?>', ' ', inner)
        text = norm(re.sub(r'<[^>]+>', '', inner))
        cls = re.search(r'class="([^"]+)"', attrs)
        pid = re.search(r'id="([^"]+)"', attrs)
        out.append((cls.group(1) if cls else '', pid.group(1) if pid else '',
                    'data-merged' in attrs, text))
    # join data-merged continuations onto the element with the same id
    joined = []
    for p in out:
        if p[2] and joined and joined[-1][1] == p[1]:
            c, i, _, t = joined[-1]
            joined[-1] = (c, i, False, (t + ' ' + p[3]).strip())
        else:
            joined.append(p)
    return [p for p in joined if p[3]]


ART_RE = re.compile(r'^Điều (\d+)([a-zđ]?)\b\.?\s*(.*)$')


def art_key(num, suf):
    return f'art-{int(num):03d}' + (f'-{suf}' if suf else '')


def units_from_html(html, preamble_start):
    """Split an act's text into units: preamble, one per Điều, structure headings, closing."""
    ps = paragraphs(html)
    units = {}
    order = []
    heads = []
    pre = []
    closing = []
    cur = None
    started_pre = False
    seen_struct = False
    for cls, _pid, _m, t in ps:
        kind = cls.split()[0] if cls else ''
        if kind in ('prov-part', 'prov-chapter', 'prov-section', 'prov-subsection'):
            seen_struct = True
            cur = None
            heads.append(t)
            continue
        if kind == 'prov-article':
            m = ART_RE.match(t)
            if not m:
                raise ValueError(f'article heading not parsed: {t!r}')
            seen_struct = True
            key = art_key(m.group(1), m.group(2))
            if key in units:
                raise ValueError(f'duplicate article {key}')
            label = f'Điều {int(m.group(1))}{m.group(2)}'
            units[key] = {'label': label, 'kind': 'art', 'lines': ['# ' + t]}
            order.append(key)
            cur = key
            continue
        if not seen_struct:
            if not started_pre and re.match(preamble_start, t):
                started_pre = True
            if started_pre:
                pre.append(t)
            continue
        if cur is not None and kind in ('prov-clause', 'prov-item', 'prov-point', 'prov-content', ''):
            if kind == '' and re.search(r'thông qua ngày \d+ tháng \d+ năm \d{4}', t):
                cur = None
                closing.append(t)
                continue
            units[cur]['lines'].append(t)
            continue
        if cur is None:
            closing.append(t)
            continue
        raise ValueError(f'unhandled paragraph {cls!r}: {t[:80]!r}')
    out = {}
    if pre:
        out['loi-mo-dau'] = {'label': 'Lời mở đầu', 'kind': 'preamble', 'text': '\n'.join(pre) + '\n'}
    for k in order:
        u = units[k]
        out[k] = {'label': u['label'], 'kind': u['kind'], 'text': '\n'.join(u['lines']) + '\n'}
    if heads:
        out['cau-truc'] = {'label': 'Cấu trúc (phần, chương, mục)', 'kind': 'headings', 'text': '\n'.join(heads) + '\n'}
    if closing:
        out['ket-thuc'] = {'label': 'Kết thúc', 'kind': 'closing', 'text': '\n'.join(closing) + '\n'}
    return out


# ---------------------------------------------------------------- amendments (replay)

def _strip_quotes(lines):
    lines = list(lines)
    lines[0] = re.sub(r'^"', '', lines[0])
    lines[-1] = re.sub(r'"\s*[;.,]?\s*$', '', lines[-1])
    return lines


def amendment_ops(html):
    """Parse 'N. Sửa đổi, bổ sung [khoản K] Điều X như sau:' + quoted text from an amending act."""
    ps = paragraphs(html)
    ops = []
    cur = None
    in_art1 = False
    for cls, _pid, _m, t in ps:
        kind = cls.split()[0] if cls else ''
        if kind == 'prov-article':
            in_art1 = t.startswith('Điều 1')
            cur = None
            continue
        if not in_art1:
            continue
        m = re.match(r'^(\d+)\. Sửa đổi, bổ sung (?:khoản (\d+) )?Điều (\d+) như sau:$', t)
        if kind == 'prov-clause' and m:
            cur = {'item': int(m.group(1)), 'clause': int(m.group(2)) if m.group(2) else None,
                   'art': int(m.group(3)), 'lines': []}
            ops.append(cur)
            continue
        if cur is not None and kind == 'prov-content':
            cur['lines'].append(t)
            continue
        if kind == 'prov-content' and cur is None:
            continue
        raise ValueError(f'unhandled amendment paragraph: {t[:80]!r}')
    return ops


def apply_ops(units, ops, law_key):
    units = {k: dict(v) for k, v in units.items()}
    credits = {}
    for op in ops:
        key = art_key(op['art'], '')
        lines = _strip_quotes(op['lines'])
        if op['clause'] is None:
            head = f'Điều {op["art"]}'
            if not lines[0].startswith(head):
                raise ValueError(f'replacement for {head} starts {lines[0][:40]!r}')
            rest = lines[0][len(head):]
            # vbpl joins the article heading and a footnote marker ("Điều 9" + "1") onto the first line
            body = []
            if rest.strip():
                mm = re.match(r'^\s*\d*\s*(\d+\. .*)$', rest) if not re.match(r'^\s*\d+\. ', rest) else re.match(r'^\s*(.*)$', rest)
                body.append(mm.group(1).strip())
            body += lines[1:]
            old_head = units[key]['text'].split('\n', 1)[0]
            units[key]['text'] = '\n'.join([old_head] + body) + '\n'
        else:
            old = units[key]['text'].rstrip('\n').split('\n')
            idx = [i for i, l in enumerate(old) if re.match(rf'^{op["clause"]}\. ', l)]
            if len(idx) != 1:
                raise ValueError(f'clause {op["clause"]} of {key}: {len(idx)} matches')
            i = idx[0]
            j = i + 1
            while j < len(old) and not re.match(r'^\d+\. ', old[j]):
                j += 1
            old[i:j] = lines
            units[key]['text'] = '\n'.join(old) + '\n'
        credits[key] = [law_key]
    return units, credits


# ---------------------------------------------------------------- corpus

SLUG = {
    'hp2013': 'hien-phap-nam-2013--32801',
    'nq203': 'nghi-quyet-so-203-2025-qh15-sua-doi-bo-sung-mot-so-dieu-cua-hien-phap-nuoc-cong-hoa-xa-hoi-chu-nghia-viet-nam--178314',
    'blds': 'bo-luat-dan-su-so-91-2015-qh13--95942',
    'blhs': 'bo-luat-hinh-su-so-100-2015-qh13--96122',
}


def page(name):
    r = vbpl.load(SLUG[name], fetch_missing=False)
    r['sha256'] = hashlib.sha256(r['raw']).hexdigest()
    return r


def day(s):
    return s[:10] if s else None


def main():
    laws = {}
    acts = []
    decisions = []

    # ---- Constitution 2013 + Resolution 203/2025/QH15
    hp = page('hp2013')
    nq = page('nq203')
    laws['hien-phap-2013'] = {
        'label': 'Hiến pháp 2013', 'title': 'Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam', 'kind': 'law',
        'enacted': day(hp['doc']['issueDate']), 'published': None, 'url': hp['url'],
        'temporary_until': None, 'restores': None, 'note': None}
    laws['nq-203-2025-qh15'] = {
        'label': 'Nghị quyết 203/2025/QH15',
        'title': 'Nghị quyết sửa đổi, bổ sung một số điều của Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam',
        'kind': 'law', 'enacted': day(nq['doc']['issueDate']), 'published': None, 'url': nq['url'],
        'temporary_until': None, 'restores': None, 'note': None}
    u1 = units_from_html(hp['html'], r'^LỜI NÓI ĐẦU$')
    ops = amendment_ops(nq['html'])
    u2, cr2 = apply_ops(u1, ops, 'nq-203-2025-qh15')
    if not re.search(r'Nghị quyết này có hiệu lực thi hành từ ngày được thông qua', ''.join(t for *_, t in paragraphs(nq['html']))):
        raise SystemExit('NQ 203/2025 in-force clause changed')
    acts.append({
        'slug': 'hien-phap', 'short': 'HP', 'title': 'Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (2013)',
        'url': hp['url'], 'first_law': 'hien-phap-2013', 'earlier_laws': [],
        'versions': [
            {'from': day(hp['doc']['effFrom']), 'source_url': hp['url'], 'sha256': hp['sha256'], 'units': u1, 'credits': {}},
            {'from': day(nq['doc']['issueDate']), 'source_url': nq['url'], 'sha256': nq['sha256'], 'units': u2, 'credits': cr2,
             'note': 'Replayed from Nghị quyết 203/2025/QH15, Điều 1 (whole-article replacements of Điều 9, 10, 110, 111 and of khoản 1 Điều 84) on the 2013 text.'},
        ]})
    decisions.append('Hiến pháp 2013: the text as adopted (vbpl.vn "văn bản gốc", ItemID 32801) is in force from 2014-01-01 (its own Điều 120 and Nghị quyết 64/2013/QH13); vbpl gives effFrom 2014-01-01.')
    decisions.append('Hiến pháp: the 2025 version is a replay of Nghị quyết 203/2025/QH15 Điều 1 (5 instructions, each replacing a whole article or one clause) on the 2013 text; it takes effect on the day it was adopted, 2025-06-16, per its own Điều 2 khoản 1. Điều 2 khoản 2 (end of district-level units from 2025-07-01) changes no words of the Constitution.')
    decisions.append('vbpl.vn prints a footnote number after the article heading inside the quoted replacement text ("Điều 91. Mặt trận..." for Điều 9 + note 1); the replay drops that marker.')

    # ---- Civil Code 2015
    ds = page('blds')
    laws['blds-91-2015-qh13'] = {
        'label': 'Bộ luật Dân sự 91/2015/QH13', 'title': 'Bộ luật Dân sự', 'kind': 'law',
        'enacted': day(ds['doc']['issueDate']), 'published': None, 'url': ds['url'],
        'temporary_until': None, 'restores': None, 'note': None}
    acts.append({
        'slug': 'bo-luat-dan-su', 'short': 'BLDS', 'title': 'Bộ luật Dân sự (Luật số 91/2015/QH13)',
        'url': ds['url'], 'first_law': 'blds-91-2015-qh13', 'earlier_laws': [],
        'versions': [{'from': day(ds['doc']['effFrom']), 'source_url': ds['url'], 'sha256': ds['sha256'],
                      'units': units_from_html(ds['html'], r'^Căn cứ'), 'credits': {}}]})
    decisions.append('Bộ luật Dân sự 2015: one version, as enacted, in force 2017-01-01 (its Điều 688). vbpl.vn lists it as "Còn hiệu lực" with no amending act and no consolidated text, so no later version is built.')

    # ---- Criminal Code 2015 (as enacted only, for now)
    hs = page('blhs')
    laws['blhs-100-2015-qh13'] = {
        'label': 'Bộ luật Hình sự 100/2015/QH13', 'title': 'Bộ luật Hình sự', 'kind': 'law',
        'enacted': day(hs['doc']['issueDate']), 'published': None, 'url': hs['url'],
        'temporary_until': None, 'restores': None, 'note': None}
    acts.append({
        'slug': 'bo-luat-hinh-su', 'short': 'BLHS', 'title': 'Bộ luật Hình sự (Luật số 100/2015/QH13)',
        'url': hs['url'], 'first_law': 'blhs-100-2015-qh13', 'earlier_laws': [],
        'versions': [{'from': day(hs['doc']['effFrom']), 'source_url': hs['url'], 'sha256': hs['sha256'],
                      'units': units_from_html(hs['html'], r'^Căn cứ'), 'credits': {}}]})

    corpus = {
        'country': {
            'code': 'VN', 'name': 'Vietnam', 'slug': 'vietnam', 'lang': 'vi', 'tz': 'Asia/Ho_Chi_Minh',
            'future_branch': 'tuong-lai',
            'publisher': {'name': 'Cơ sở dữ liệu quốc gia về pháp luật (vbpl.vn, Bộ Tư pháp)', 'email': 'vbpl@vbpl.invalid'},
            'default_in_force_rule': {
                'text': 'Luật Ban hành văn bản quy phạm pháp luật 2015, Điều 151: the date of entry into force is stated in the document itself, not earlier than 45 days after adoption or signing (urgent cases excepted). Every act built here states its own date.',
                'source': 'https://vbpl.vn/van-ban/chi-tiet/luat-ban-hanh-van-ban-quy-pham-phap-luat-so-80-2015-qh13--70800'},
            'licence_note': 'Nguồn: Cơ sở dữ liệu quốc gia về pháp luật (vbpl.vn), Bộ Tư pháp. Legal normative documents are not protected by copyright in Vietnam (Luật Sở hữu trí tuệ, Điều 15).',
        },
        'sources': [
            {'name': 'Cơ sở dữ liệu quốc gia về pháp luật (vbpl.vn), Bộ Tư pháp', 'url': 'https://vbpl.vn', 'retrieved': RETRIEVED,
             'requests': count_requests(),
             'licence': 'Official text; Luật Sở hữu trí tuệ 2005 Điều 15 khoản 2: legal normative documents are not objects of copyright protection.',
             'notes': 'Detail pages https://vbpl.vn/van-ban/chi-tiet/<slug>--<id> (Next.js); metadata from the embedded "initialDoc" (issueDate, effFrom, effStatus) and the full text from its documentContent HTML. Document list from the public sitemaps https://vbpl.vn/sitemap/1-12.xml. robots.txt disallows /api/ and /Pages/, which were not used.'},
        ],
        'laws': laws,
        'acts': acts,
        'applies': [],
        'decisions': decisions + [
            'Units: one file per Điều (article), with the heading line "# Điều N. Title" and one line per khoản/điểm/paragraph; the preamble ("Lời nói đầu" or the "Căn cứ" recitals) is loi-mo-dau, the part/chapter/section headings are kept in order in cau-truc, and the adoption line is ket-thuc. Signature blocks are dropped.',
            'Normalisation: NBSP to space, runs of spaces collapsed, curly quotes to straight, en and em dashes to "-", publisher rule lines ("———") removed; vbpl splits some headings over two <p> elements marked data-merged, which are joined with a space.',
        ],
        'ai_use': ['Claude Code with Claude Opus 5.5 (claude-opus-5-5) wrote fetch.py, vbpl.py and parse.py. No model wrote or edited any legal text; every unit is parsed by code from vbpl.vn.'],
    }
    tmp = os.path.join(HERE, 'corpus.json.tmp')
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write('\n')
    os.replace(tmp, os.path.join(HERE, 'corpus.json'))
    for a in acts:
        print(a['slug'], [(v['from'], len(v['units'])) for v in a['versions']])


def count_requests():
    p = os.path.join(HERE, '.cache', 'requests.jsonl')
    if not os.path.exists(p):
        return 0
    with open(p, encoding='utf-8') as f:
        return sum(1 for line in f if 'vbpl.vn/van-ban/' in line)


if __name__ == '__main__':
    main()
