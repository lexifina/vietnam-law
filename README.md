# Vietnam: law history in git

The law of Vietnam as a git history: one file per article (Điều), one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every line; `git log` lists every change to an article; picking a date gives the text in force that day.

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is Vietnam's national law, which global-law reads at `vietnam/national/acts/`.

**What is in it now:** 162 acts of the National Assembly (Quốc hội), each from its text as enacted with its amendments to 2026: the Constitution of 2013, six codes (bộ luật: the Civil, Penal, Civil Procedure, Criminal Procedure, Labour and Maritime Codes) and 155 laws (luật), with 513 versions in force from 1 April 2000 to 1 October 2026. [`REPRODUCE.md`](REPRODUCE.md) lists every act with its versions and first and last days; [`data/laws.csv`](data/laws.csv) lists the 280 laws the record names (the acts and the laws that amended them), with their dates and vbpl.vn pages.

Each act is a folder named from its number, `<kind>/<year>/<number>/`, with one file per article: `bo-luat/2019/45-2019-qh14/art-154.md` is Điều 154 of the Bộ luật Lao động, the Labour Code (Luật số 45/2019/QH14); the Constitution is in `constitution/hien-phap/`. `loi-mo-dau.md` holds the preamble, `cau-truc.md` the part, chapter and section headings, `ket-thuc.md` the closing line, and each act's `README.md` lists its articles and how often each changed. Until 11 November 2026 each folder was named by the act's id (`bo-luat-lao-dong/`); [`data/paths.json`](data/paths.json) maps each id to its folder, and the version tags (`bo-luat-lao-dong/2026-07-01`) keep the ids.

The text is in Vietnamese, as vbpl.vn and the Công báo publish it. An English translation is not part of this record.

## Questions as git commands

| Question | Command |
| --- | --- |
| Every change to Article 154 (foreign workers who need no work permit) of the Labour Code | `git log -p --follow --word-diff -- bo-luat/2019/45-2019-qh14/art-154.md` |
| Which law wrote each line of Article 154? | `git blame bo-luat/2019/45-2019-qh14/art-154.md` |
| Every version of the Labour Code, with the day each took effect | `git log --format="%h %(trailers:key=In-force,valueonly,separator=) %an" -- bo-luat/2019/45-2019-qh14 bo-luat-lao-dong ":!*/README.md"` |
| Article 154 as in force on 1 January 2025 | `python tools/on.py 2025-01-01 bo-luat/2019/45-2019-qh14 154` |

The list of versions names the folder by both its names; it also shows the correction of 1 January 2026 (see Dates) and the commit of 11 November 2026 that moved the folder without changing its text, which `git log --follow` shows too.

**Outside git**, we also host this record publicly, for free:

- **[Ask Claude about Vietnamese law](https://global-law.lexifina.com/v1/try_claude?country=vietnam)**: opens Claude with a first question ready.
- **[Ask ChatGPT](https://global-law.lexifina.com/v1/try_chatgpt?country=vietnam)**: the same question in ChatGPT.
- **[Call the API in your browser](https://global-law.lexifina.com/v1/search_law?query=ngh%E1%BB%89+h%E1%BA%B1ng+n%C4%83m&jurisdictions=vietnam)**: a search of Vietnamese law for "nghỉ hằng năm" (annual leave), returned as JSON. See the [documentation here](https://lexifina.com/api/global-law).

Both assistants read the record through the free Global law connector (MCP, `https://global-law.lexifina.com/mcp`); the first time, the chat gives you the link that adds it. Ask in Vietnamese or in English.

**Host it yourself easily.** All it takes is git and Python, and the tools run on your machine:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add vietnam/national/acts
python3 tools/law.py show 2026-01-01 vietnam/national/acts/bo-luat/2019/45-2019-qh14/art-154.md
```

Opened in Claude Code, Cursor, VS Code or Codex, the clone also starts a local MCP server with the same tools ([MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md)).

## Dates

Each commit is dated at noon, Asia/Ho_Chi_Minh, on the day the version took effect, and carries it in its `In-force:` trailer:

- an act as enacted: the day its own final articles set, which vbpl.vn also gives (the Criminal Procedure Code: 1 January 2018, as Nghị quyết 41/2017/QH14 set after the first day was postponed);
- an amendment: the day the consolidated text's footnote gives for the amending law; a law that amends several acts on one day is one commit;
- where two laws changed an article and no consolidated text shows it between them, both changes are shown on the later law's day (46 articles, listed in `REPRODUCE.md`). The Penal Code as enacted and as amended by Luật 12/2017/QH14 are both dated 1 January 2018, the amended text last.

Each act's first version is credited to the act itself, and each change to the amending law the consolidated text names, with an address that cannot exist (`blld-45-2019-qh14@vbpl.invalid`): 369 commits, credited to 260 laws. One correction, the Labour Code's Điều 59 and 61 as amended by Luật Giáo dục nghề nghiệp 124/2025/QH15 from 1 January 2026, first left out, is appended as its own commit (`Kind: correction`), credited to Lexifina, which is also the committer of every commit.

## How it is checked

- Each text as enacted is vbpl.vn's original text (văn bản gốc). An amended article is taken whole from the official consolidated text (văn bản hợp nhất) of the Office of the National Assembly, printed in the Công báo, whose footnote names the amending law; articles no footnote credits keep the text as enacted.
- `tools/check_repo.py` reads every version back from git on the day it took effect and on the day before, compares it file by file with the corpus it was built from, and checks the trailers, with no merge commits and no commit dated in the future. [`REPRODUCE.md`](REPRODUCE.md) gives the corpus's sha256 and the builders' blob hashes, and records that, for the published build, that check had not yet been run and no second build had been compared.
- History is append-only: acts added after the first build come after it, each in in-force order, and a text found wrong later is fixed by a correction commit, never by rewriting.

## What it does not show

- **Most Vietnamese law.** Only the Constitution, codes and laws of the National Assembly are here; ordinances, resolutions, decrees, circulars, local regulations, case law, treaties and bills are not. A law is left out when a change cannot be dated from the consolidated texts available.
- **Repeals of whole laws.** A law replaced by a later one keeps its last text, as if still in force: Luật Chứng khoán 70/2006/QH11 (replaced by 54/2019/QH14 from 2021), Luật Kinh doanh bảo hiểm 24/2000/QH10 (by 08/2022/QH15 from 2023), Luật Quản lý thuế 38/2019/QH14 (by 108/2025/QH15 from 1 July 2026) and at least three others. Repealed chapters are removed.
- **The Civil Code's amendments**, if any: vbpl.vn lists no amending act and no consolidated text for it, so it is shown as enacted.
- **Amendments not yet in force.** [`data/versions.json`](data/versions.json) lists 28 later versions, to 1 March 2027; they are not commits yet.
- **Amending laws no footnote credits.** A law a consolidated text lists, but credits with no change to an article, has no version (`REPRODUCE.md` names them).

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [vbpl.vn](https://vbpl.vn) (Cơ sở dữ liệu quốc gia về pháp luật, Bộ Tư pháp) | National legal database | the text as enacted | The text of every act as enacted, its in-force day and the laws that amended it |
| [congbao.chinhphu.vn](https://congbao.chinhphu.vn) (Công báo, Văn phòng Chính phủ) | Official gazette | consolidated texts | The consolidated texts (văn bản hợp nhất) behind every amendment. Nguồn: congbao.chinhphu.vn |

## Licence

See [`LICENSE`](LICENSE). Legal normative documents are not protected by copyright in Vietnam (Luật Sở hữu trí tuệ 50/2005/QH11, Điều 15 khoản 2, quoted in `LICENSE`). Lexifina's arrangement of the history, its commit messages, tables and tools are dedicated to the public domain under CC0 1.0.

No AI model wrote, translated or corrected legal text, and none runs at build time; the scripts were written by Claude Code (see [`REPRODUCE.md`](REPRODUCE.md)).

## Tiếng Việt

Lịch sử pháp luật Việt Nam trong git: mỗi điều một tệp, mỗi luật một commit vào ngày có hiệu lực, và tác giả của commit là luật đã sửa đổi văn bản. Hiện có 162 văn bản của Quốc hội: Hiến pháp năm 2013, sáu bộ luật và 155 luật, mỗi văn bản từ bản gốc cùng các lần sửa đổi đến năm 2026, tổng cộng 513 phiên bản. Các lần sửa đổi lấy từ văn bản hợp nhất đăng Công báo. Văn bản có hiệu lực vào một ngày: `python tools/on.py 2025-01-01 bo-luat/2019/45-2019-qh14 154`; `git blame bo-luat/2019/45-2019-qh14/art-154.md` cho biết luật nào đã viết từng dòng.

## More

From [lexifina/global-law](https://github.com/lexifina/global-law):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): every feature, and what every corpus must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): questions and answers · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): proposing changes · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): the MCP server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): how it was built · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): how current each corpus is · [Monitoring](https://github.com/lexifina/global-law/tree/main/monitoring): whether updates are running · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): how each official source is watched for changes
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): how fast the tools are, measured
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): charts and bridges across the world's law
- [Vulnerabilities](https://github.com/lexifina/global-law/tree/main/vulnerabilities): mistakes in legislation as published
