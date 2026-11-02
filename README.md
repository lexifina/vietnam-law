# Vietnam: law history in git

The law of Vietnam as a git history: one file per provision (Điều), one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every line; `git log` lists every change to a provision.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `vn/`. The official language is Vietnamese; the texts here are in Vietnamese and nothing is translated.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `hien-phap/` | Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (the Constitution, 2013) | 1 | As adopted 28 November 2013, in force 1 January 2014 |
| `bo-luat-dan-su/` | Bộ luật Dân sự (the Civil Code, Law 91/2015/QH13) | 1 | As enacted, in force 1 January 2017 |
| `bo-luat-to-tung-dan-su/` | Bộ luật Tố tụng dân sự (the Civil Procedure Code, Law 92/2015/QH13) | 1 | As enacted, in force 1 July 2016 |
| `bo-luat-to-tung-hinh-su/` | Bộ luật Tố tụng hình sự (the Criminal Procedure Code, Law 101/2015/QH13) | 1 | As enacted, in force 1 January 2018 |
| `luat-doanh-nghiep/` | Luật Doanh nghiệp (the Enterprise Law, Law 59/2020/QH14) | 1 | As enacted, in force 1 January 2021 |
| `bo-luat-lao-dong/` | Bộ luật Lao động (the Labour Code, Law 45/2019/QH14) | 1 | As enacted, in force 1 January 2021 |

## Dates

- Each commit is dated on the day the version took effect, as stated in the act itself (vbpl.vn gives the same date). Every act here is the text as enacted.

## How it is checked

- Each version is read back from git on its in-force day and must match `corpus.json`: no mismatches, no trailer errors, no merge commits, no backwards or future dates.
- The text comes from the Ministry of Justice database (vbpl.vn) "văn bản gốc" (original text) pages. It was not compared with an official consolidated text.

## What it does not show

- **The 2025 constitutional amendments** (Nghị quyết 203/2025/QH15 of 16 June 2025). The Constitution shown is the 2013 text as adopted, not the text in force today.
- **Later amendments to the codes.** None are applied yet: each code is its text as enacted. Known amending laws not yet applied include Luật 02/2021/QH15 and 99/2025/QH15 (Criminal Procedure Code), 03/2022/QH15 and 76/2025/QH15 (Enterprise Law) and 85/2025/QH15 (Civil Procedure Code).
- **The Penal Code (Bộ luật Hình sự 2015).** Its text as enacted never took effect by itself: Luật 12/2017/QH14 amended it before both took effect on 1 January 2018. It will be added with that amendment applied.
- All other laws are not included.
- **Consolidated texts (văn bản hợp nhất)** are not used.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

No AI model wrote or changed legal text.

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [vbpl.vn](https://vbpl.vn) (Ministry of Justice) | Official legal database | original texts | Used: the text of every act |
| [congbao.chinhphu.vn](https://congbao.chinhphu.vn) | Official gazette | signed PDFs | Not read |
| [quochoi.vn](https://quochoi.vn) | National Assembly | n/a | Not used (JavaScript cookie challenge) |

## Licence

Vietnamese legal normative documents are not protected by copyright (Luật Sở hữu trí tuệ, Điều 15 khoản 2, quoted in `LICENSE`). The arrangement, tables, commit messages and tools are by Lexifina, under the terms in `LICENSE`. This repository is not legal advice and not an official publication.

## Tiếng Việt

Lịch sử pháp luật Việt Nam trong git: mỗi điều một tệp, mỗi luật một commit vào ngày có hiệu lực. Hiện có Hiến pháp 2013 (nguyên bản, hiệu lực 1/1/2014), Bộ luật Dân sự 2015 (hiệu lực 1/1/2017), Bộ luật Tố tụng dân sự 2015 (1/7/2016), Bộ luật Tố tụng hình sự 2015 (1/1/2018), Luật Doanh nghiệp 2020 và Bộ luật Lao động 2019 (1/1/2021), đều là văn bản gốc. Sửa đổi Hiến pháp năm 2025 chưa được đưa vào vì chưa đối chiếu được với văn bản hợp nhất chính thức.
