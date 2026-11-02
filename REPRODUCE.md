# How this repository was made (Vietnam)

This file is written by the build on 2026-11-02, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Cơ sở dữ liệu quốc gia về pháp luật (vbpl.vn), Bộ Tư pháp | <https://vbpl.vn> | 2026-11-02 | Official text; Luật Sở hữu trí tuệ 2005 Điều 15 khoản 2: legal normative documents are not objects of copyright protection. |
| Công báo nước Cộng hòa xã hội chủ nghĩa Việt Nam (congbao.chinhphu.vn), Văn phòng Chính phủ | <https://congbao.chinhphu.vn> | 2026-11-02 | Official gazette; the consolidated texts (văn bản hợp nhất) of the Office of the National Assembly are legal normative documents (Luật Sở hữu trí tuệ Điều 15). The site asks that "congbao.chinhphu.vn" be named as the source when its information is republished. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `hien-phap` | Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (2013) | 1 | 2014-01-01 to 2014-01-01 |
| `bo-luat-hinh-su` | Bộ luật Hình sự (Luật số 100/2015/QH13) | 4 | 2018-01-01 to 2026-01-01 |
| `bo-luat-dan-su` | Bộ luật Dân sự (Luật số 91/2015/QH13) | 1 | 2017-01-01 to 2017-01-01 |
| `bo-luat-to-tung-dan-su` | Bộ luật Tố tụng dân sự (Luật số 92/2015/QH13) | 1 | 2016-07-01 to 2016-07-01 |
| `bo-luat-to-tung-hinh-su` | Bộ luật Tố tụng hình sự (Luật số 101/2015/QH13) | 1 | 2018-01-01 to 2018-01-01 |
| `luat-doanh-nghiep` | Luật Doanh nghiệp (Luật số 59/2020/QH14) | 1 | 2021-01-01 to 2021-01-01 |
| `bo-luat-lao-dong` | Bộ luật Lao động (Luật số 45/2019/QH14) | 1 | 2021-01-01 to 2021-01-01 |

The build made 10 commits:

| Commits | Kind |
| ---: | --- |
| 7 | first version of an act |
| 3 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `tuong-lai`: laws not yet in force on 2026-11-02.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 10 laws in the record.
- 19 tags.

## Dates

Each commit is dated at noon (Asia/Ho_Chi_Minh) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Luật Ban hành văn bản quy phạm pháp luật 2015, Điều 151: the date of entry into force is stated in the document itself, not earlier than 45 days after adoption or signing (urgent cases excepted). Every act built here states its own date. https://vbpl.vn/van-ban/chi-tiet/luat-ban-hanh-van-ban-quy-pham-phap-luat-so-80-2015-qh13--70800

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `c87f965c79f9a69c3f73d0e6def8d91c777261e529fd71ab88fee3fa92922ad6` (4338063 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- Hiến pháp 2013: the text as adopted (vbpl.vn "văn bản gốc", ItemID 32801) is in force from 2014-01-01 (its own Điều 120 and Nghị quyết 64/2013/QH13); vbpl gives effFrom 2014-01-01.
- Hiến pháp: the 2025 version is a replay of Nghị quyết 203/2025/QH15 Điều 1 (5 instructions, each replacing a whole article or one clause) on the 2013 text; it takes effect on the day it was adopted, 2025-06-16, per its own Điều 2 khoản 1. Điều 2 khoản 2 (end of district-level units from 2025-07-01) changes no words of the Constitution.
- vbpl.vn prints a footnote number after the article heading inside the quoted replacement text ("Điều 91. Mặt trận..." for Điều 9 + note 1); the replay drops that marker.
- Bộ luật Hình sự 2015: the first version is the text as enacted (vbpl.vn), dated 2018-01-01, the day the Code took effect (Nghị quyết 41/2017/QH14); it never applied by itself, because Luật 12/2017/QH14 amended it with effect from the same day, so the amended text follows as a second version on that day.
- BLHS: Chương XII repealed by 59/2024/QH15 from 2026-01-01: its articles art-090..art-107 (18) are removed.
- Bộ luật Dân sự 2015: one version, as enacted, in force 2017-01-01 (its Điều 688). vbpl.vn lists it as "Còn hiệu lực" with no amending act and no consolidated text, so no later version is built.
- Bộ luật Tố tụng dân sự 2015: as enacted, in force 2016-07-01 (its Điều 517; vbpl effFrom). Later amending laws are not yet applied.
- Bộ luật Tố tụng hình sự 2015: as enacted, in force 2018-01-01 (the date set by Nghị quyết 41/2017/QH14 after Nghị quyết 144/2016/QH13 postponed the original 2016-07-01; vbpl effFrom). Later amending laws (02/2021/QH15, 99/2025/QH15) are not yet applied.
- Luật Doanh nghiệp 2020: as enacted, in force 2021-01-01 (its Điều 217; vbpl effFrom). Later amending laws (03/2022/QH15, 76/2025/QH15) are not yet applied.
- Bộ luật Lao động 2019: as enacted, in force 2021-01-01 (its Điều 220; vbpl effFrom). Later amending laws are not yet applied.
- Units: one file per Điều (article), with the heading line "# Điều N. Title" and one line per khoản/điểm/paragraph; the preamble ("Lời nói đầu" or the "Căn cứ" recitals) is loi-mo-dau, the part/chapter/section headings are kept in order in cau-truc, and the adoption line is ket-thuc. Signature blocks are dropped.
- Amendments: a code with later amending laws is built from the official consolidated texts (văn bản hợp nhất, VBHN) of the Office of the National Assembly as printed in the Công báo. Every footnote of a VBHN names the amending law (and its in-force day) behind an article, clause or phrase; the article is then taken from the VBHN, in full, as a new version on that day, credited to that law. Articles no footnote credits keep the vbpl.vn text. When a later VBHN also carries a change by a later law, the earliest VBHN that holds the first law but no later change to that article is used. Footnotes that only quote an amending law (for example its own in-force clause) credit nothing.
- Consolidated-text normalisation: Unicode NFC, U+00D0 (Ð) read as Đ, footnote marks removed, the covers and contents pages of the gazette issues and "(Tiếp theo / Xem tiếp Công báo số ...)" lines dropped, and the closing authentication block (XÁC THỰC VĂN BẢN HỢP NHẤT) dropped.
- Normalisation: NBSP to space, runs of spaces collapsed, curly quotes to straight, en and em dashes to "-", publisher rule lines ("———") removed; vbpl splits some headings over two <p> elements marked data-merged, which are joined with a space.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code with Claude Opus 5.5 (claude-opus-5-5) wrote Lexifina's code. No model wrote or edited any legal text; every unit is parsed by code from vbpl.vn pages or Công báo Word files.
