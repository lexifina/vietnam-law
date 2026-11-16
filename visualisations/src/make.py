"""Rebuild visualisations/phap-luat-viet-nam-qua-20-bieu-do.html from this repository.

    python visualisations/src/make.py [--repo PATH] [--ref REF]

Steps (all read-only on the repository; scratch output goes to visualisations/src/.build/):
  1. git log of REF with author dates, full messages and the files each commit adds, changes or deletes
                                                                     -> .build/commits.json
  2. data/ and REPRODUCE.md, written from their blobs                -> .build/repo/
  3. in a blobless (--filter=blob:none) clone, the texts of the acts (every version of every article, preamble and
     closing line) are downloaded in one batch, never the vulnerabilities/ folder
  4. prep.py reads those texts with `git cat-file --batch` and writes .build/data.json; build.py fills
     page.tpl.html with it.
Works in a blobless or --no-checkout clone, because everything is read from git objects.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..', '..')))
ap.add_argument('--ref', default=None, help='default: origin/main if present, else HEAD')
ap.add_argument('--out', default=os.path.join(HERE, '..', 'phap-luat-viet-nam-qua-20-bieu-do.html'))
a = ap.parse_args()
B = os.path.join(HERE, '.build')
os.makedirs(B, exist_ok=True)
ENV = dict(os.environ, GIT_NO_LAZY_FETCH='1')   # never download a blob by accident; step 3 fetches what it needs


def git(*args, env=ENV, inp=None):
    return subprocess.run(['git', '-C', a.repo, *args], check=True, capture_output=True, env=env, input=inp).stdout


ref = a.ref
if not ref:
    ref = 'origin/main' if subprocess.run(['git', '-C', a.repo, 'rev-parse', '--verify', '-q', 'origin/main'], capture_output=True).returncode == 0 else 'HEAD'
sha = git('rev-parse', ref).decode().strip()
print('ref', ref, sha)

# 1. commits: dates, author, message, trailers and raw changes (status, path, old blob, new blob), streamed line by line
rows, cur = [], None
p = subprocess.Popen(['git', '-C', a.repo, 'log', ref, '--format=@@C %H|%ad|%an|%ae', '--date=iso-strict', '--raw', '--no-abbrev', '--no-renames'],
                     stdout=subprocess.PIPE, env=ENV)
for raw in p.stdout:
    line = raw.decode('utf-8', 'replace').rstrip('\n')
    if line.startswith('@@C '):
        h, ad, an, ae = line[4:].split('|', 3)
        cur = {'h': h, 'ad': ad, 'an': an, 'ae': ae, 'ch': []}
        rows.append(cur)
    elif line.startswith(':') and cur:
        meta, path = line.split('\t', 1)
        q = meta.split()
        cur['ch'].append([q[4], path, q[2], q[3]])
p.wait()
msgs, cur, buf = {}, None, []
p = subprocess.Popen(['git', '-C', a.repo, 'log', ref, '--format=@@M %H%n%B'], stdout=subprocess.PIPE, env=ENV)
for raw in p.stdout:
    line = raw.decode('utf-8', 'replace').rstrip('\n')
    if line.startswith('@@M '):
        if cur: msgs[cur] = '\n'.join(buf)
        cur, buf = line[4:], []
    else:
        buf.append(line)
p.wait()
if cur: msgs[cur] = '\n'.join(buf)
for r in rows:
    body = msgs.get(r['h'], '').strip('\n')
    t = {}
    for l in body.split('\n'):
        m = re.match(r'^([A-Z][A-Za-z-]+): (.*)$', l)
        if m: t.setdefault(m.group(1), []).append(m.group(2))
    r['t'] = t
    r['subj'] = body.split('\n', 1)[0]
    r['body'] = body[:4000] if t.get('Kind', [''])[0] == 'law' else ''
json.dump(rows, open(os.path.join(B, 'commits.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('commits', len(rows))

# 2. data tables (data/ is small; it is fetched whole if the clone is blobless)
want = []
for l in git('ls-tree', '-r', ref, '--', 'data', 'REPRODUCE.md').decode('utf-8').splitlines():
    meta, path = l.split('\t', 1)
    want.append((meta.split()[2], path))


def fetch(oids):
    """download the blobs a blobless clone lacks, in one request"""
    if not oids: return
    have = git('cat-file', '--batch-check=%(objectname) %(objecttype)', inp=('\n'.join(oids) + '\n').encode()).decode().split('\n')
    missing = [l.split()[0] for l in have if l.endswith(' missing')]
    if missing:
        print('fetching', len(missing), 'blobs')
        git('-c', 'fetch.negotiationAlgorithm=noop', 'fetch', 'origin', '--no-tags', '--no-write-fetch-head', '--recurse-submodules=no',
            '--filter=blob:none', '--stdin', env=dict(os.environ, GIT_NO_LAZY_FETCH='0'), inp=('\n'.join(missing) + '\n').encode())


fetch([o for o, p in want])
for o, p in want:   # (git archive would read the whole tree, so each file is written from its blob)
    dest = os.path.join(B, 'repo', *p.split('/'))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'wb').write(git('cat-file', 'blob', o))

# 3. the texts of the acts: every blob a law commit added or changed (articles, preambles, structure, closing lines)
oids = set()
for r in rows:
    if r['t'].get('Kind', [''])[0] not in ('law', 'correction'): continue
    for st, path, old, new in r['ch']:
        if st != 'D': oids.add(new)
        if st == 'M': oids.add(old)
fetch(sorted(oids))
for l in git('ls-tree', '-r', ref, '--', 'bo-luat', 'luat', 'constitution').decode('utf-8').splitlines():
    meta, path = l.split('\t', 1)
    if not path.endswith('README.md'): oids.add(meta.split()[2])
fetch(sorted(oids))
open(os.path.join(B, 'head-tree.txt'), 'wb').write(git('ls-tree', '-r', ref, '--', 'bo-luat', 'luat', 'constitution'))

# 4. prep + build
env = dict(os.environ, HEAD_SHA=sha, REPO=a.repo, GIT_NO_LAZY_FETCH='1')
subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'prep.py'), B], check=True, env=env)
subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py'), os.path.join(B, 'data.json'), os.path.abspath(a.out)], check=True)
