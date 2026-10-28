# How this repository was made (Vietnam)

This file is written by the build on 2026-10-28, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| Cơ sở dữ liệu quốc gia về pháp luật (vbpl.vn), Bộ Tư pháp | <https://vbpl.vn> | 2026-10-28 | 9 | Official text; Luật Sở hữu trí tuệ 2005 Điều 15 khoản 2: legal normative documents are not objects of copyright protection. |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `hien-phap` | Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (2013) | 2 | 2014-01-01 to 2025-06-16 |
| `bo-luat-dan-su` | Bộ luật Dân sự (Luật số 91/2015/QH13) | 1 | 2017-01-01 to 2017-01-01 |

The build made 3 commits:

| Commits | Kind |
| ---: | --- |
| 2 | first version of an act |
| 1 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `tuong-lai`: laws not yet in force on 2026-10-28.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 3 laws in the record.
- 6 tags.

## Dates

Each commit is dated at noon (Asia/Ho_Chi_Minh) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Luật Ban hành văn bản quy phạm pháp luật 2015, Điều 151: the date of entry into force is stated in the document itself, not earlier than 45 days after adoption or signing (urgent cases excepted). Every act built here states its own date. https://vbpl.vn/van-ban/chi-tiet/luat-ban-hanh-van-ban-quy-pham-phap-luat-so-80-2015-qh13--70800

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-28
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-28 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/vietnam-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `0c18dbed5669fbbe415e92b8c878f7d90907f44abf8f6f5fcacbb0035ddb77e4` (767462 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `5d40c3d38194a1920e89e6b0fc342f0171d10b0d` |
| check.py | `cd346c7ff9996d450240e3bab52bcae03b2bc865` |
| on.py | `644a6c0857fbcc72562032b58d57aa113fee0641` |
| fetch.py | `8a43076b60d251adf4eb02f0307b5458e9cfc687` |
| parse.py | `5635b23a9a3d18f04c256b058507c28d3ec00084` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

3 versions of 2 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

Not yet run for this build.

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- Hiến pháp 2013: the text as adopted (vbpl.vn "văn bản gốc", ItemID 32801) is in force from 2014-01-01 (its own Điều 120 and Nghị quyết 64/2013/QH13); vbpl gives effFrom 2014-01-01.
- Hiến pháp: the 2025 version is a replay of Nghị quyết 203/2025/QH15 Điều 1 (5 instructions, each replacing a whole article or one clause) on the 2013 text; it takes effect on the day it was adopted, 2025-06-16, per its own Điều 2 khoản 1. Điều 2 khoản 2 (end of district-level units from 2025-07-01) changes no words of the Constitution.
- vbpl.vn prints a footnote number after the article heading inside the quoted replacement text ("Điều 91. Mặt trận..." for Điều 9 + note 1); the replay drops that marker.
- Bộ luật Dân sự 2015: one version, as enacted, in force 2017-01-01 (its Điều 688). vbpl.vn lists it as "Còn hiệu lực" with no amending act and no consolidated text, so no later version is built.
- Units: one file per Điều (article), with the heading line "# Điều N. Title" and one line per khoản/điểm/paragraph; the preamble ("Lời nói đầu" or the "Căn cứ" recitals) is loi-mo-dau, the part/chapter/section headings are kept in order in cau-truc, and the adoption line is ket-thuc. Signature blocks are dropped.
- Normalisation: NBSP to space, runs of spaces collapsed, curly quotes to straight, en and em dashes to "-", publisher rule lines ("———") removed; vbpl splits some headings over two <p> elements marked data-merged, which are joined with a space.

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code with Claude Opus 5.5 (claude-opus-5-5) wrote fetch.py, vbpl.py and parse.py. No model wrote or edited any legal text; every unit is parsed by code from vbpl.vn.
