# Edge cases

[Tiếng Việt](EDGE-CASES.md) · **English**

The six flags that survived the model review, each checked by hand, the eight references to deleted articles, which the model set aside and which were also read by hand, and what the other flags are. Back to [the vulnerabilities README](README.en.md).

## Open: possible slips, to be confirmed against the amending law (3, all among the references the model set aside)

| Act | What the record says | Why it may be a slip |
| --- | --- | --- |
| [Luật Viễn thông](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/luat/2023/24-2023-qh15/art-029.md) (24/2023/QH15), Article 29(2)(c) | Article 8 (the national telecommunications development plan) was deleted from 1 March 2026, credited to the Planning Law 112/2025/QH15 ([the change](https://github.com/lexifina/vietnam-law/commit/578a34e04cf8e891e5b57a593888d73b45dd7bc1)) | Providers of data-centre and cloud services must still comply with "khoản 3 Điều 8" among other provisions; clause 3 of Article 8 had them build their own plans from the information and communications infrastructure plan. 112/2025 amended Articles 13, 25, 34 and others of this law at the same time, but not Article 29. The Cybersecurity Law 116/2025/QH15 then amended point (b) of the same clause from 1 July 2026 ([the change](https://github.com/lexifina/vietnam-law/commit/95b97ce52a2a3b0b44ddfb709c535877ababac0d)) and left point (c). |
| [Luật Trồng trọt](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/luat/2018/31-2018-qh14/art-050.md) (31/2018/QH14), Article 50(1)(c) | Article 49 (advertising fertilisers) was deleted from 1 January 2026, credited to Law No. 146/2025/QH15, which amends 15 laws on agriculture and the environment ([the change](https://github.com/lexifina/vietnam-law/commit/96de8c4cb37788538da7ea87d113277f4ce06c40)) | Fertiliser producers still have the right to "quảng cáo phân bón theo quy định tại Điều 49 của Luật này". 146/2025 changed 37 articles of this law, Article 49 among them, but not Article 50, which has its 2020 text. |
| [Luật đầu tư theo phương thức đối tác công tư](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/luat/2020/64-2020-qh14/art-101.md) (64/2020/QH14), Article 101(1)(b) | Article 23 (the contents of a decision approving a PPP project) was deleted from 1 July 2025, credited to Law No. 90/2025/QH15 ([the change](https://github.com/lexifina/vietnam-law/commit/5eb62174fca22ed0142422b6ea6949257374de4c)) | A project whose feasibility study was approved before 1 January 2021 and whose investor has not yet been chosen must still have "nội dung quy định tại khoản 6 Điều 23" approved. 90/2025 amended clauses 4, 5(d) and 7 of Article 101 in the same change and left this reference. It is a transitional rule, so few projects may still fall under it. |

Each of the three rests on the deletion recorded here, taken from the consolidated texts this repository follows; the amending laws themselves are not in this repository, and this repository's version of 1 July 2025 of the Militia and Self-Defence Forces Law shows that a deletion here can be a build error (below), so each still needs the amending law in the Công báo.

## Explained by how this repository is built (4)

| Flags | What the record says | What happened |
| --- | --- | --- |
| Same-day conflicts (3): the [Penal Code](https://github.com/lexifina/vietnam-law/tree/851db24da020e03409223e1cb1e30a0178298dad/bo-luat/2015/100-2015-qh13) (100/2015/QH13), [Article 113](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/bo-luat/2015/100-2015-qh13/art-113.md), [Article 281](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/bo-luat/2015/100-2015-qh13/art-281.md) and [Article 309](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/bo-luat/2015/100-2015-qh13/art-309.md) | the Code as enacted on 27 November 2015 ([the commit](https://github.com/lexifina/vietnam-law/commit/db6ac1620c7751ad3870672ab394aaa14f881a78)) and Law No. 12/2017/QH14 of 20 June 2017, which amended it ([the commit](https://github.com/lexifina/vietnam-law/commit/c7512dd8b63c0a9d1027d3e9ae779753ee89143f)), both take effect on 1 January 2018 | Law No. 12/2017/QH14 amended the Code before the Code took effect, so the text in force from 1 January 2018 is the amended one. This repository records both versions on that day, the amended one second, as its README says. No two texts were ever in force together. |
| Repeal gap (1): [Luật Dân quân tự vệ](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/luat/2019/48-2019-qh14/art-038.md) (48/2019/QH14), Article 38 | deleted from 1 July 2025, credited to Law No. 98/2025/QH15 ([the change](https://github.com/lexifina/vietnam-law/commit/32a4d8687cd3f6cd36f951fb26d57b6d67a3ecef)); back from 1 September 2026, credited to Law No. 14/2026/QH16 ([the change](https://github.com/lexifina/vietnam-law/commit/61cac055eb3d3a709c3515e19dff487fbce90c0e)) | The returning text is the old one, with "Ban chỉ huy quân sự cấp xã" dropped from clause 6 and "trụ sở hoặc nơi làm việc" shortened to "trụ sở làm việc" in clause 8. The change of 1 July 2025 also put provisions on military service into 21 article files of this law (see [Problems found in this repository](README.en.md#problems-found-in-this-repository)), so the deletion is most likely part of a faulty build of that version rather than a repeal. The model judged it an artefact. |

## Lawful (2)

| Act | What the record says | Why it is lawful |
| --- | --- | --- |
| [Luật Thuế tài nguyên](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/luat/2009/45-2009-qh12/art-010.md) (45/2009/QH12), Article 10(3) | investment projects and oil and gas contracts "signed before 1 July 2010" | The date says which contracts keep the resource-tax terms of their licence or contract; it is the day the law took effect (Article 10(1)), not a limit on the rule. |
| [Bộ luật Lao động](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/bo-luat/2019/45-2019-qh14/art-219.md) (45/2019/QH14), Article 219 | two flags: 15 years of work in areas with an allowance coefficient of 0.7 or more "before 1 January 2021" | Article 219 rewrote the pension conditions of Articles 54 and 55 of the Social Insurance Law 58/2014/QH13; the date says which years of work count. Law 58/2014/QH13 itself ended on 1 July 2025 (Article 140 of the Social Insurance Law 41/2024/QH15), whose Article 64 keeps the same cut-off. The two flags are the same words in clauses 1 and 2 of the new Article 54; the model reviewed both. |

## Another act's amount (1)

| Flag | What the record says | What happened |
| --- | --- | --- |
| Stale amount: [Luật Đấu thầu](https://github.com/lexifina/vietnam-law/blob/851db24da020e03409223e1cb1e30a0178298dad/luat/2023/22-2023-qh15/art-023.md) (22/2023/QH15), Article 23 | Law No. 57/2024/QH15 replaced "100 triệu đồng" with "300 triệu đồng" in point m (direct contracting for small packages) from 15 January 2025; "100 triệu đồng" still stands in Article 317 of the Civil Procedure Code and Articles 70 and 78 of the Consumer Protection Law 19/2023/QH15 | Those are a different threshold: consumer cases worth under 100 million đồng go to the simplified procedure. The detector compares amounts across the whole repository. |

## The eight references to deleted articles

Besides the three open cases above:

- **Misread by the detector (3):** Article 99 of the PPP Law (two flags, Articles 6 and 15) and Article 84 of the Water Resources Law 28/2023/QH15 (Article 56) amend other laws ("Sửa đổi, bổ sung khoản 2 Điều 15 như sau"), so the article numbers belong to the Law on Bidding and the other laws named in the clause, not to the act that holds them.
- **Spent (1):** Article 114(2) of the Education Law 43/2019/QH14 repealed the 2005 Education Law "except as provided in Article 115", the transitional rule for teacher-training students admitted before that law took effect on 1 July 2020, which Law No. 123/2025/QH15 deleted from 1 January 2026.
- **Lawful (1):** Article 27 of the Law on Treaties 108/2016/QH13 applies "Articles 8 to 26"; Article 19, inside the range, was deleted by Law No. 137/2025/QH15 from 1 January 2026, and a range may span a repealed article.

## The other flags

- **Lapsed time limits:** 116, of which 74 follow "trước" (before), 21 "đến hết" or "cho đến hết", 12 "đến" or "cho đến", 5 "chậm nhất là" and 4 other forms. Most are cut-offs in transitional rules (applications filed, contracts signed, contributions paid before a date) or time limits that ran out as planned. Of the 40 reviewed, 27 were judged lawful, 11 artefacts and 2 survived (above). One flag is in this repository's English README.
- **Same-day conflicts:** 239. 202 are the Penal Code's two versions of 1 January 2018 (above); of those, 40 were reviewed: 25 judged lawful, 11 artefacts, 4 candidate defects of which 3 survived. The other 37 are acts amended before or on the day they took effect: the Air Defence Law 49/2024/QH15 by 98/2025/QH15 (12), the Law on Preventing and Combating Human Trafficking 53/2024/QH15 by 86/2025/QH15 (9), the Trade Union Law 50/2024/QH15 by 97/2025/QH15 (8), the Social Insurance Law 41/2024/QH15 by the Inspection Law 84/2025/QH15 (4), and four acts once each.
- **Stale amounts:** besides the one above, two in the Penal Code, where Law No. 12/2017/QH14 changed the amounts of one offence and the same figures still stand in other offences (judged lawful and an artefact).

## Problems found in this repository

See [the README](README.en.md#problems-found-in-this-repository): 21 article files of the Militia and Self-Defence Forces Law hold provisions on military service, and the Children's Law holds a 2024 amnesty decision as its first articles and preamble.
