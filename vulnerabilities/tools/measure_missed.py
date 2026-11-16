"""Measure what textscan.limits() reads and misses in Vietnamese: every past date, month or year (before the pin's date) with
an "until" or deadline word ("đến", "cho đến", "đến hết", "trước", "chậm nhất") up to 25 characters before it, in the law
texts at the pin. Prints counts by form, and samples.   python -X utf8 measure_missed.py"""
import collections, json, random, re, subprocess, sys
sys.path.insert(0, "gl/vulnerabilities/scripts")
from ingest import textscan
G = "gl/vulnerabilities/scripts/sources/corpus/vietnam-law.git"; PIN = "851db24da020e03409223e1cb1e30a0178298dad"
TODAY = "2026-11-16"
cfg = json.load(open("config.json", encoding="utf-8"))
NOT_LAW = tuple(cfg["not_law"])
DATE = re.compile(r"(?i)(?P<full>\b(?:ngày\s+)?\d{1,2}\s+tháng\s+\d{1,2},?\s+năm\s+(?P<y1>\d{4}))|(?P<num>\b\d{1,2}\s?/\s?\d{1,2}\s?/\s?(?P<y2>\d{4}))"
                  r"|(?P<month>\btháng\s+\d{1,2}\s+năm\s+(?P<y3>\d{4}))|(?P<year>\bnăm\s+(?P<y4>(?:18|19|20)\d{2})\b)")
WORD = re.compile(r"(?i).*(?P<w>\b(?:cho đến hết|cho đến|đến hết|tính đến|đến|trước|chậm nhất là|chậm nhất|kể từ|từ)\b)[^.;:\n]{0,25}$")
files = [l for l in subprocess.run(["git", "-C", G, "ls-tree", "-r", "--name-only", PIN], capture_output=True)
         .stdout.decode("utf-8").splitlines() if textscan.is_law_file(l) and not l.startswith(NOT_LAW)]
cat = subprocess.Popen(["git", "-C", G, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def read(p):
    cat.stdin.write(f"{PIN}:{p}\n".encode()); cat.stdin.flush()
    h = cat.stdout.readline().split()
    if len(h) < 3: return ""
    d = cat.stdout.read(int(h[2])); cat.stdout.read(1)
    return d.decode("utf-8", "replace")


cnt, samples = collections.Counter(), collections.defaultdict(list)
for p in files:
    t = read(p)
    got_dates = collections.Counter(d for d, _ in textscan.limits(t))
    for m in DATE.finditer(t):
        y = int(m.group("y1") or m.group("y2") or m.group("y3") or m.group("y4"))
        if y > int(TODAY[:4]):
            continue
        w = WORD.search(t[max(0, m.start() - 40):m.start()])
        if not w:
            continue
        word = re.match(r"(?i)cho đến hết|cho đến|đến hết|tính đến|đến|trước|chậm nhất là|chậm nhất|kể từ|từ", w.group("w")).group(0).lower()
        kind = next(k for k in ("full", "num", "month", "year") if m.group(k))
        if word in ("từ", "kể từ"):
            cnt[("start word (not a limit)", kind)] += 1
            continue
        if word == "tính đến":
            cnt[("'tính đến' (as at, left out)", kind)] += 1
            continue
        if kind in ("full", "num"):
            dm = re.findall(r"\d+", m.group(0))
            iso = f"{int(dm[-1]):04d}-{int(dm[1]):02d}-{int(dm[0]):02d}"
            if iso not in got_dates:
                cnt[("MISSED", kind, word)] += 1
                samples[("MISSED", kind, word)].append(t[max(0, m.start() - 60):m.end() + 10].replace("\n", " "))
            else:
                cnt[("read", kind, word)] += 1
        elif kind == "month":
            cnt[("month only: 'tháng M năm Y'", word)] += 1
            samples[("month", word)].append(t[max(0, m.start() - 40):m.end() + 5].replace("\n", " "))
        else:
            hh = re.search(r"(?i)(hết|cuối)\s+$", t[max(0, m.start() - 8):m.start()])
            cnt[("year: 'hết/cuối năm Y' (read)" if hh else "year only: 'năm Y'", word)] += 1
            if not hh:
                samples[("year", word)].append(t[max(0, m.start() - 40):m.end() + 5].replace("\n", " "))
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print(f"{v:6d}  {k}")
random.seed(1)
for k, v in samples.items():
    print("\n==", k)
    for s in random.sample(v, min(4, len(v))):
        print("   ", s)
