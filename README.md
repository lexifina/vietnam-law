# Vietnam: law history in git

The law of Vietnam as a git history: one file per provision (Điều), one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every line; `git log` lists every change to a provision.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `vn/`. The official language is Vietnamese; the texts here are in Vietnamese and nothing is translated.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `hien-phap/` | Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam (the Constitution, 2013) | 2 | As adopted, in force 1 January 2014; Nghị quyết 203/2025/QH15 (16 June 2025) |
| `bo-luat-hinh-su/` | Bộ luật Hình sự (the Penal Code, Law 100/2015/QH13) | 4 | As enacted and as amended by Luật 12/2017/QH14, both 1 January 2018; Luật 86/2025/QH15 (1 July 2025); Luật Tư pháp người chưa thành niên 59/2024/QH15 (1 January 2026) |
| `bo-luat-dan-su/` | Bộ luật Dân sự (the Civil Code, Law 91/2015/QH13) | 1 | As enacted, in force 1 January 2017 |
| `bo-luat-to-tung-dan-su/` | Bộ luật Tố tụng dân sự (the Civil Procedure Code, Law 92/2015/QH13) | 8 | As enacted, in force 1 July 2016; seven amending laws, 2021 to 2025 |
| `bo-luat-to-tung-hinh-su/` | Bộ luật Tố tụng hình sự (the Criminal Procedure Code, Law 101/2015/QH13) | 5 | As enacted, in force 1 January 2018; Luật 02/2021/QH15, 34/2024/QH15, 99/2025/QH15 and 59/2024/QH15, 2021 to 2026 |
| `luat-doanh-nghiep/` | Luật Doanh nghiệp (the Enterprise Law, Law 59/2020/QH14) | 3 | As enacted, in force 1 January 2021; Luật 03/2022/QH15 (1 March 2022); Luật 76/2025/QH15 (1 July 2025) |
| `bo-luat-lao-dong/` | Bộ luật Lao động (the Labour Code, Law 45/2019/QH14) | 2 | As enacted, in force 1 January 2021; Luật Công nghiệp công nghệ số 71/2025/QH15 (1 January 2026) |

## Dates

- Each commit is dated on the day the version took effect, as stated in the act itself (vbpl.vn gives the same date). Amendments are dated by the in-force day the consolidated text gives for each amending law.

## How it is checked

- Each version is read back from git on its in-force day and must match `corpus.json`: no mismatches, no trailer errors, no merge commits, no backwards or future dates.
- Texts as enacted come from the Ministry of Justice database (vbpl.vn) "văn bản gốc" (original text) pages.
- Amended articles come from the official consolidated texts (văn bản hợp nhất) of the Office of the National Assembly, as printed in the Công báo (congbao.chinhphu.vn). Each footnote of a consolidated text names the law that amended an article and the day it took effect; that article is then taken from the consolidated text in full, credited to that law, on that day. Articles no footnote credits keep the text as enacted.

## What it does not show

- **The Civil Code's amendments by other laws**, if any: vbpl.vn and the Công báo list no consolidated text of the Civil Code, so it is shown as enacted.
- **Three articles of the Criminal Procedure Code** (Điều 37, 42 and 45) were amended by Luật 99/2025/QH15 (1 July 2025) and again by Luật 59/2024/QH15 (1 January 2026); no consolidated text shows them between the two, so both changes are shown on 1 January 2026.
- **The Penal Code's text as enacted** never applied by itself: Luật 12/2017/QH14 amended it with effect from the same day, 1 January 2018. Both are shown on that day, the amended text last.
- All other laws are not included.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

No AI model wrote or changed legal text.

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [vbpl.vn](https://vbpl.vn) (Ministry of Justice) | Official legal database | original texts | Used: the text of every act |
| [congbao.chinhphu.vn](https://congbao.chinhphu.vn) (Office of the Government) | Official gazette | consolidated texts | Used: the consolidated texts (văn bản hợp nhất) behind every amendment. Nguồn: congbao.chinhphu.vn |
| [quochoi.vn](https://quochoi.vn) | National Assembly | n/a | Not used (JavaScript cookie challenge) |

## Licence

Vietnamese legal normative documents are not protected by copyright (Luật Sở hữu trí tuệ, Điều 15 khoản 2, quoted in `LICENSE`). The arrangement, tables, commit messages and tools are by Lexifina, under the terms in `LICENSE`. This repository is not legal advice and not an official publication.

## Tiếng Việt

Lịch sử pháp luật Việt Nam trong git: mỗi điều một tệp, mỗi luật một commit vào ngày có hiệu lực. Hiện có Hiến pháp 2013 (cả lần sửa đổi năm 2025), Bộ luật Hình sự 2015, Bộ luật Dân sự 2015, Bộ luật Tố tụng dân sự 2015, Bộ luật Tố tụng hình sự 2015, Luật Doanh nghiệp 2020 và Bộ luật Lao động 2019, mỗi văn bản từ ngày có hiệu lực, cùng các lần sửa đổi đến năm 2026. Các lần sửa đổi lấy từ văn bản hợp nhất đăng Công báo.
