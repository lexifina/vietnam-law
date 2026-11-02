"""Dated versions of an act from its text as enacted and the official consolidated texts (VBHN) that follow it.

An amended article takes the consolidated text's wording, on the in-force day of the law its footnotes credit; an
article no footnote credits keeps the earlier text. See build_versions().
"""
import re

import vbhn


def unit_text(a):
    return '\n'.join(['# ' + a['heading']] + a['lines']) + '\n'


def article_laws(a, notes, own):
    out = set()
    for i in a['notes']:
        out |= set(vbhn.note_laws(notes[i], own))
    return out


REPEALED = re.compile(r'\((?:được|bị) bãi bỏ\)\s*$')


def build_versions(base_units, base_from, own, consolidated, law_keys, label_of=None):
    """base_units: units of the text as enacted (in force from base_from).
    consolidated: [(name, arts, notes, header, struct_notes)] in issue order.
    law_keys: {law number: corpus law key}.
    Returns (versions after the first, decisions, problems)."""
    dates = {}
    for name, arts, notes, header, sn in consolidated:
        for num, d in vbhn.header_laws(header):
            if num != own:
                dates.setdefault(num, d)
    laws = sorted(dates, key=lambda n: (dates[n], n))
    info = []   # per VBHN: {key: (laws, text)}
    for name, arts, notes, header, sn in consolidated:
        inc = {n for n, _ in vbhn.header_laws(header)}
        per = {k: (article_laws(a, notes, own), a) for k, a in arts.items()}
        rem = []
        for line, mk in sn:
            ls = set()
            for i in mk:
                ls |= set(vbhn.note_laws(notes[i], own))
            m = re.match(r'^Chương ([IVXLC]+)\b', line)
            if m and REPEALED.search(line):
                rem.append((m.group(1), ls))
        info.append({'name': name, 'inc': inc, 'per': per, 'rem_chapters': rem})
    state = dict(base_units)
    versions, problems, decisions = [], [], []
    prev_from = base_from
    deferred = {}   # key -> laws whose change could not be dated alone
    for L in laws:
        d = dates[L]
        changes, credits = {}, {}
        holders = [v for v in info if L in v['inc']]
        if not holders:
            problems.append(f'{L}: no consolidated text includes it'); continue
        first = holders[0]
        keys = set()
        for v in holders:
            keys |= {k for k, (ls, _) in v['per'].items() if L in ls}
        for k in sorted(keys):
            cand = None
            touch = set()
            for v in info:
                if k in v['per']:
                    touch |= v['per'][k][0]
            need = {x for x in touch if dates.get(x, '0000') <= d}
            for v in holders:
                if k in v['per']:
                    ls, a = v['per'][k]
                    if L in ls and all(dates.get(x, '0000') <= d for x in ls) and need <= v['inc'] | {own}:
                        cand = (v, ls, a); break
            if cand is None:
                deferred.setdefault(k, set()).add(L)
                continue
            v, ls, a = cand
            new = None if REPEALED.search(a['heading']) and not a['lines'] else unit_text(a)
            if new is not None and state.get(k, {}).get('text') == new:
                continue
            if new is None:
                if k in state:
                    changes[k] = None
            else:
                old = state.get(k)
                changes[k] = {'label': (old or {}).get('label') or label_of(k), 'kind': 'art', 'text': new}
            credits[k] = sorted({law_keys[L]} | {law_keys[x] for x in deferred.pop(k, set()) if x in law_keys})
        # whole chapters repealed: their articles are absent from the consolidated text
        for chap, ls in first['rem_chapters']:
            if L in ls:
                prev = [v for v in info if L not in v['inc']]
                base_keys = set(state)
                present = set()
                for v in holders:
                    present |= set(v['per'])
                gone = sorted(k for k in base_keys if k.startswith('art-') and k not in present
                              and changes.get(k, 0) is not None)
                for k in gone:
                    changes[k] = None
                    credits[k] = [law_keys[L]]
                if 'cau-truc' in state:
                    lines = state['cau-truc']['text'].rstrip('\n').split('\n')
                    i = [j for j, x in enumerate(lines) if x == f'Chương {chap}' or x.startswith(f'Chương {chap} ')]
                    if len(i) == 1:
                        j = i[0] + 1
                        while j < len(lines) and not re.match(r'^(Chương|Phần) ', lines[j]):
                            j += 1
                        del lines[i[0]:j]
                        changes['cau-truc'] = dict(state['cau-truc'], text='\n'.join(lines) + '\n')
                        credits['cau-truc'] = [law_keys[L]]
                    else:
                        problems.append(f'{L}: Chương {chap} found {len(i)} times in cau-truc')
                decisions.append(f'Chương {chap} repealed by {L} from {d}: its articles {gone[0]}..{gone[-1]} ({len(gone)}) are removed.')
        if not changes:
            problems.append(f'{L}: no change found'); continue
        for k, u in changes.items():
            if u is None:
                state.pop(k, None)
            else:
                state[k] = u
        ver = {'from': d, 'changes': changes, 'credits': credits, '_law': L, '_src': first['name']}
        if d == prev_from:
            ver['same_day'] = True
        versions.append(ver)
        prev_from = d
    for k, ls in deferred.items():
        problems.append(f'{k}: change by {sorted(ls)} could not be dated (only a later consolidated text shows it)')
    return versions, decisions, problems
