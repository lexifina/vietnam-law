"""Plain text from a Word 97-2003 .doc (piece table), split into main text and footnotes.

    main, notes = read(path)   # main: list of paragraphs, footnote references as "\x02"; notes: list of footnote texts
"""
import struct
import olefile


def _pieces(clx):
    i = 0
    while clx[i] == 0x01:                       # Prc entries
        cb = struct.unpack_from('<H', clx, i + 1)[0]
        i += 3 + cb
    if clx[i] != 0x02:
        raise ValueError('no Pcdt in Clx')
    lcb = struct.unpack_from('<I', clx, i + 1)[0]
    plc = clx[i + 5:i + 5 + lcb]
    n = (lcb - 4) // 12
    cps = struct.unpack_from(f'<{n + 1}I', plc, 0)
    out = []
    for k in range(n):
        fc = struct.unpack_from('<I', plc, 4 * (n + 1) + 8 * k + 2)[0]
        out.append((cps[k], cps[k + 1], fc))
    return out


def _text(path):
    ole = olefile.OleFileIO(path)
    wd = ole.openstream('WordDocument').read()
    flags = struct.unpack_from('<H', wd, 0x0A)[0]
    table = ole.openstream('1Table' if flags & 0x0200 else '0Table').read()
    ccp_text, ccp_ftn = struct.unpack_from('<II', wd, 76)
    fc_clx, lcb_clx = struct.unpack_from('<II', wd, 418)
    chars = []
    for cp0, cp1, fc in _pieces(table[fc_clx:fc_clx + lcb_clx]):
        n = cp1 - cp0
        if fc & 0x40000000:
            off = (fc & ~0x40000000) // 2
            chars.append(wd[off:off + n].decode('cp1252', errors='replace'))
        else:
            chars.append(wd[fc:fc + 2 * n].decode('utf-16-le', errors='replace'))
    s = ''.join(chars)
    return s[:ccp_text], s[ccp_text:ccp_text + ccp_ftn]


def _clean(s):
    out, depth, show = [], 0, []
    for ch in s:
        o = ord(ch)
        if o == 0x13:
            depth += 1; show.append(False); continue
        if o == 0x14 and depth:
            show[-1] = True; continue
        if o == 0x15 and depth:
            depth -= 1; show.pop(); continue
        if depth and not show[-1]:
            continue
        if o in (0x01, 0x08):
            continue
        if o in (0x07, 0x0B, 0x0C, 0x0E):
            out.append('\r' if o in (0x07, 0x0C) else ' '); continue
        out.append(ch)
    return ''.join(out)


def read(path):
    main, ftn = _text(path)
    paras = [p for p in _clean(main).split('\r')]
    notes = [n for n in _clean(ftn).split('\x02') if n is not None]
    # footnote text: each note starts with its reference mark \x02; split leaves a leading fragment
    notes = [n.replace('\r', ' ').strip() for n in notes[1:]]
    return paras, notes


if __name__ == '__main__':
    import sys
    p, n = read(sys.argv[1])
    print(len(p), 'paragraphs', len(n), 'notes', sum(x.count('\x02') for x in p), 'refs')
    for x in p[:40]:
        print(repr(x[:150]))
    print(n[:3])


# ---------------------------------------------------------------- .docx (Office Open XML), same result shape

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def _docx_paras(root, refs=None):
    out = []
    for p in root.iter(W + 'p'):
        buf = []
        for el in p.iter():
            if el.tag == W + 't' and el.text:
                buf.append(el.text)
            elif el.tag in (W + 'tab',):
                buf.append(' ')
            elif el.tag in (W + 'br', W + 'cr'):
                buf.append(' ')
            elif el.tag == W + 'footnoteReference' and refs is not None:
                refs.append(el.get(W + 'id'))
                buf.append('\x02')
        out.append(''.join(buf))
    return out


def read_docx(path):
    import zipfile
    import xml.etree.ElementTree as ET
    z = zipfile.ZipFile(path)
    refs = []
    paras = _docx_paras(ET.fromstring(z.read('word/document.xml')), refs)
    notes_by_id = {}
    if 'word/footnotes.xml' in z.namelist():
        for fn in ET.fromstring(z.read('word/footnotes.xml')).iter(W + 'footnote'):
            notes_by_id[fn.get(W + 'id')] = ' '.join(x for x in _docx_paras(fn) if x).strip()
    return paras, [notes_by_id.get(i, '') for i in refs]


def read_any(path):
    with open(path, 'rb') as f:
        head = f.read(4)
    return read_docx(path) if head[:2] == b'PK' else read(path)
