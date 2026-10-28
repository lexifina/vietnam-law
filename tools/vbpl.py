"""Read vbpl.vn detail pages from the cache: metadata (initialDoc) and full-text HTML."""
import json
import re

import fetch

BASE = 'https://vbpl.vn/van-ban/chi-tiet/'


def page_url(slug):
    return BASE + slug


def load(slug, fetch_missing=True):
    url = page_url(slug)
    raw = fetch.get(url) if fetch_missing else fetch.cached(url)
    b = raw.decode('utf-8')
    rows = {}
    for c in re.findall(r'self\.__next_f\.push\((\[.*?\])\)</script>', b, flags=re.S):
        v = json.loads(c)
        if len(v) > 1 and v[1]:
            rows.setdefault('_all', []).append(v[1])
    allj = ''.join(rows.get('_all', []))
    i = allj.find('"initialDoc":')
    doc, _ = json.JSONDecoder().raw_decode(allj[i + 13:])
    content = (doc.get('documentContent') or {}).get('content') or ''
    m = re.fullmatch(r'\$(\w+)', content)
    if m:
        # React flight row "<id>:T<hexlen>,<text>"
        ref = m.group(1)
        j = allj.find('\n' + ref + ':T')
        if j < 0 and allj.startswith(ref + ':T'):
            j = -1
        k = allj.find(',', j + 1)
        n = int(allj[j + 1 + len(ref) + 2:k], 16)
        content = allj[k + 1:k + 1 + n * 4]  # length is in bytes; trim below
        enc = content.encode('utf-8')[:n]
        content = enc.decode('utf-8', errors='ignore')
    return {'url': url, 'raw': raw, 'doc': doc, 'html': content}
