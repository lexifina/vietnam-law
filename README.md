# Vietnam: law history in git

The law of Vietnam as a git history: one file per provision (Điều), one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every line; `git log` lists every change to a provision.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `vn/`. The official language is Vietnamese; the texts here are in Vietnamese and nothing is translated.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `hien-phap/` | Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (the Constitution, 2013) | 1 | As adopted 28 November 2013, in force 1 January 2014 |
| `bo-luat-dan-su/` | Bộ luật Dân sự (the Civil Code, Law 91/2015/QH13) | 1 | As enacted, in force 1 January 2017 |

## Dates

- Each commit is dated on the day the version took effect. Both acts are the texts as enacted.

## How it is checked

- Each version is read back from git on its in-force day and must match `corpus.json`: no mismatches, no trailer errors, no merge commits, no backwards or future dates.
- The text comes from the Ministry of Justice database (vbpl.vn) "văn bản gốc" (original text) pages. It was not compared with an official consolidated text.

## What it does not show

- **The 2025 constitutional amendments** (Nghị quyết 203/2025/QH15 of 16 June 2025). The Constitution shown is the 2013 text as adopted, not the text in force today.
- **Amendments to the Civil Code.** None are applied; it is the 2015 text as enacted.
- **The Penal Code (Bộ luật Hình sự 2015)** and all other laws are not included.
- **Consolidated texts (văn bản hợp nhất)** are not used.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

No AI model wrote or changed legal text.

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [vbpl.vn](https://vbpl.vn) (Ministry of Justice) | Official legal database | original texts | Used: the text of both acts |
| [congbao.chinhphu.vn](https://congbao.chinhphu.vn) | Official gazette | signed PDFs | Not read |
| [quochoi.vn](https://quochoi.vn) | National Assembly | n/a | Not used (JavaScript cookie challenge) |

## Licence

Vietnamese legal normative documents are not protected by copyright (Law on Intellectual Property, Article 15; see `LICENSE` for the caveat). The arrangement, tables, commit messages and tools are by Lexifina, under the terms in `LICENSE`. This repository is not legal advice and not an official publication.

## Tiếng Việt

Lịch sử pháp luật Việt Nam trong git: mỗi điều một tệp, mỗi luật một commit vào ngày có hiệu lực. Hiện có Hiến pháp 2013 (nguyên bản, hiệu lực 1/1/2014) và Bộ luật Dân sự 2015 (nguyên bản, hiệu lực 1/1/2017). Sửa đổi Hiến pháp năm 2025 chưa được đưa vào vì chưa đối chiếu được với văn bản hợp nhất chính thức.
