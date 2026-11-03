"""Read an official consolidated text (văn bản hợp nhất, VBHN) from its gazette .doc parts.

    arts, notes, header, struct_notes = read(paths)
    arts:   {unit key: {'heading': 'Điều N. ...', 'lines': [text lines, footnote marks removed], 'notes': [note numbers]}}
    notes:  {note number: footnote text}   (numbered across the parts in order)
    header: paragraphs before the first article (the list of consolidated laws, recitals)
"""
import re
import unicodedata

import doc97
from parse import norm, art_key

ART = re.compile(r'^Điều (\d+)([a-zđ]?)(?:\. ?(.*)|)$')
JUNK = re.compile(r'^\((?:Tiếp theo|Xem tiếp) Công báo số [\d +]+\)$')
STRUCT = re.compile(r'^(Phần thứ|Chương [IVXLC]+|Mục \d+|PHẦN THỨ|CHƯƠNG)')


def read(paths):
    arts, notes, header = {}, {}, []
    struct_notes = []
    n = 0
    cur = None
    ended = False
    for pi, path in enumerate(paths):
        paras, fn = doc97.read(path)
        paras = [unicodedata.normalize('NFC', x).replace('Ð', 'Đ') for x in paras]
        fn = [unicodedata.normalize('NFC', x).replace('Ð', 'Đ') for x in fn]
        refs = sum(p.count('\x02') for p in paras)
        if refs != len(fn):
            raise ValueError(f'{path}: {refs} footnote marks, {len(fn)} notes')
        start = 0
        if pi > 0:   # skip the issue's cover and table of contents
            k = [i for i, p in enumerate(paras) if re.match(r'^\(Tiếp theo Công báo số', p.strip())]
            if len(k) != 1:
                raise ValueError(f'{path}: continuation marker found {len(k)} times')
            # notes on the cover/TOC pages are counted too
            start = k[0] + 1
        base = n
        seen = 0
        for i, p in enumerate(paras):
            cnt = p.count('\x02')
            marks = list(range(base + seen + 1, base + seen + cnt + 1))
            seen += cnt
            if i < start or ended:
                continue
            t = p
            for m in marks:
                t = t.replace('\x02', f'\x00{m}\x00', 1)
            t = norm(t.replace('\x00', '\x00'))  # norm collapses whitespace; marks survive
            if not t or JUNK.match(t):
                continue
            if t.startswith('VĂN PHÒNG QUỐC HỘI') or 'XÁC THỰC VĂN BẢN HỢP NHẤT' in t:
                ended = True
                continue
            plain = re.sub(r'\x00\d+\x00', '', t).strip()
            mk = [int(x) for x in re.findall(r'\x00(\d+)\x00', t)]
            m = ART.match(plain)
            if m:
                key = art_key(m.group(1), m.group(2))
                if key in arts:
                    raise ValueError(f'duplicate {key} in {path}')
                cur = arts[key] = {'heading': plain, 'lines': [], 'notes': mk}
                continue
            if cur is None:
                header.append(plain)
                continue
            if STRUCT.match(plain) or (plain.isupper() and len(plain) > 3):
                cur.setdefault('struct_after', []).append(plain)
                if mk:
                    struct_notes.append((plain, mk))
                continue
            cur['lines'].append(plain)
            cur['notes'] += mk
        for j, txt in enumerate(fn):
            notes[base + j + 1] = norm(txt)
        n = base + len(fn)
    return arts, notes, header, struct_notes


LAW_NUM = re.compile(r'(\d+/\d{4}/ ?QH\d+)')
AMEND = re.compile(r'được (?:sửa đổi|bổ sung|thay thế|bãi bỏ|bỏ)|bị bãi bỏ|(?:sửa đổi|bổ sung|thay thế|bãi bỏ|bỏ) theo quy định tại')
DATE = re.compile(r'có hiệu lực (?:thi hành )?(?:kể )?từ ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})')


def note_laws(text, own=None):
    """The amending law(s) an amendment footnote credits: the first law number after each "theo quy định tại"
    ("... được sửa đổi, bổ sung theo quy định tại khoản 22 Điều 1 của Luật số 12/2017/QH14 ..."), never the act's own
    number. [] for notes that only quote or explain (an amending law's in-force clause, "... quy định như sau: ...")."""
    if not AMEND.search(text):
        return []
    out = set()
    for m in re.finditer(r'theo quy định tại', text):
        k = LAW_NUM.search(text, m.end(), m.end() + 300)
        if k and k.group(1).replace(' ', '') != own:
            out.add(k.group(1).replace(' ', ''))
    return sorted(out)


def header_laws(header):
    """[(law number, in-force day)] from the consolidated text's list of amending laws: the lines after
    "... được sửa đổi, bổ sung bởi:" (the first line, the act itself, is included too) up to the recitals."""
    out = []
    on = False
    for h in header:
        if h.startswith('Căn cứ'):
            break
        if 'được sửa đổi, bổ sung bởi' in h:
            on = True
        if not on:
            continue
        m = DATE.search(h)
        nums = LAW_NUM.findall(h)
        if m and nums:
            out.append((nums[0].replace(' ', ''), f'{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'))
    return out
