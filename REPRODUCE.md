# How this repository was made (Vietnam)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Cơ sở dữ liệu quốc gia về pháp luật (vbpl.vn), Bộ Tư pháp | <https://vbpl.vn> | 2026-10-28 | Official text; Luật Sở hữu trí tuệ 2005 Điều 15 khoản 2: legal normative documents are not objects of copyright protection. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `hien-phap` | Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (2013) | 1 | 2014-01-01 to 2014-01-01 |
| `bo-luat-dan-su` | Bộ luật Dân sự (Luật số 91/2015/QH13) | 1 | 2017-01-01 to 2017-01-01 |

The build made 2 commits:

| Commits | Kind |
| ---: | --- |
| 2 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `tuong-lai`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 3 laws in the record.
- 4 tags.

## Dates

Each commit is dated at noon (Asia/Ho_Chi_Minh) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Luật Ban hành văn bản quy phạm pháp luật 2015, Điều 151: the date of entry into force is stated in the document itself, not earlier than 45 days after adoption or signing (urgent cases excepted). Every act built here states its own date. https://vbpl.vn/van-ban/chi-tiet/luat-ban-hanh-van-ban-quy-pham-phap-luat-so-80-2015-qh13--70800

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `fdf5ad400ed30b57682c9dba59ca5ffb1fc84d006cf2215b417737cf5de155be` (671486 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3e59cb6f05eccb94a9ec14431a7f6781221e83ef`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- Hiến pháp 2013: the text as adopted (vbpl.vn "văn bản gốc", ItemID 32801) is in force from 2014-01-01 (its own Điều 120 and Nghị quyết 64/2013/QH13); vbpl gives effFrom 2014-01-01.
- vbpl.vn prints a footnote number after the article heading inside the quoted replacement text ("Điều 91. Mặt trận..." for Điều 9 + note 1); the replay drops that marker.
- Bộ luật Dân sự 2015: one version, as enacted, in force 2017-01-01 (its Điều 688). vbpl.vn lists it as "Còn hiệu lực" with no amending act and no consolidated text, so no later version is built.
- Units: one file per Điều (article), with the heading line "# Điều N. Title" and one line per khoản/điểm/paragraph; the preamble ("Lời nói đầu" or the "Căn cứ" recitals) is loi-mo-dau, the part/chapter/section headings are kept in order in cau-truc, and the adoption line is ket-thuc. Signature blocks are dropped.
- Normalisation: NBSP to space, runs of spaces collapsed, curly quotes to straight, en and em dashes to "-", publisher rule lines ("———") removed; vbpl splits some headings over two <p> elements marked data-merged, which are joined with a space.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code with Claude Opus 5.5 (claude-opus-5-5) wrote Lexifina's code. No model wrote or edited any legal text; every unit is parsed by code from vbpl.vn.
