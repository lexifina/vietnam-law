# Tools

The scripts behind this Vietnam-only run of global-law's vulnerability detectors. They run inside a copy of
[global-law/vulnerabilities/scripts](https://github.com/lexifina/global-law/tree/main/vulnerabilities/scripts) (Python 3.11+,
`pip install duckdb pyarrow`), with a bare clone of this repository at `sources/corpus/vietnam-law.git`, a blobless bare
clone of global-law at `sources/global-law.git`, and a `pins.json` that names only vietnam-law and its commit.
`build_vulns.py`, `flags_chart.py`, `late_ext_select.py`, `late_ext_rebut.py` and `measure_missed.py` sit two folders above
the scripts, next to `config.json`.

| Script | What it does |
| --- | --- |
| `run.sh` | Indexes the history and texts, maps paths to today's folders, adds this repository's history rows, and runs the detectors (`bash run.sh <shards>`) |
| `map_moved.py` | Rewrites every file path from before 11 November 2026, when act folders were renamed (`bo-luat-lao-dong/art-154.md` to `bo-luat/2019/45-2019-qh14/art-154.md`), to its folder today through `data/paths.json`, so each act has one folder through its whole history |
| `add_root.py` | Builds the history rows from this repository's own commits (global-law replays it only up to an earlier commit), so the history detectors read every change |
| `run_triage.sh` | The model review: the 40 strongest flags per category, the 40 strongest lapsed time limits in law texts, and the empty periods (none here) |
| `late_ext_select.py` | Chooses the empty periods for global-law's review of that category (there were none here) |
| `late_ext_rebut.py` | Adds the second, arguing-against pass to the empty-period review, as `triage.py` does for the other categories |
| `build_vulns.py` | Builds `data/flags.csv`, `data/reviewed.csv` and `data/by_category.csv` from the findings and the model review |
| `flags_chart.py` | Draws the chart at the top of the READMEs, in Vietnamese and English, light and dark |
| `config.json` | The repository, the Vietnamese category names, the paths that are not law, and the chart's labels |
| `patch_detectors.py` | Fixes blind spots found in runs on several country repositories in the copy of global-law's scripts (`python -X utf8 patch_detectors.py <scripts dir>`; a fix already in place is skipped) |
| `patch_detectors_vi.py` | The Vietnamese fixes made for this run, in the same form (`python -X utf8 patch_detectors_vi.py <scripts dir>`) |
| `redo.py` | Runs `patch_detectors.py`, then again only the scans and detectors the fixes change, the model review of lapsed time limits, references to deleted provisions and empty periods, and the build (`python -X utf8 redo.py <run folder> [--keep-reviews]`; `EMBED_FONTS` names the script that embeds the chart's fonts); not needed here, as the fixes were in place before the first run |
| `measure_missed.py` | Counts the places where "đến", "cho đến", "đến hết", "trước" or "chậm nhất" comes shortly before a date, month or year, which of them the time-limit search reads, and the forms of those it does not (the numbers in the READMEs) |

The model review needs `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` and `LLM_AUTH` set for an OpenAI-compatible Responses API.
It was run as `bash run_triage.sh '^(data|tools)/'`.

Changes made for this repository:

- `patch_detectors_vi.py` taught the detectors Vietnamese. Dates (`ingest/textscan.py`): "ngày 31 tháng 12 năm 2020", the end
  of a year ("hết năm 2020", "cuối năm 2020"), the words "đến", "cho đến" (but not "tính đến", "as at"), "chậm nhất" and
  "trước", with "hết", "là", "vào" or "ngày" between word and date; "chậm nhất" and "trước" count as deadlines
  (`detectors/text_detectors.py` ranks them as such, and the empty-period detector leaves them out). Before this, the search
  read none of this repository's time limits. References (`ingest/refscan.py`): "Điều 12", "khoản 2 Điều 5", "điểm a khoản 1
  Điều 3", lists with "và" or "hoặc" and ranges "từ Điều 8 đến Điều 26"; a reference followed by another act's name ("Điều 15
  của Luật Sở hữu trí tuệ", "khoản 2 Điều 7 Bộ luật Hình sự", but not "Luật này") is left out. Amounts: "5.000.000 đồng",
  "100 triệu đồng", only after the number ("hợp đồng 12 tháng" is a contract, not 12 đồng).
- `map_moved.py` was added to `run.sh` after `ingest/extract.py`. Without it, every act's history ended at the folder move
  of 11 November 2026 (a commit of kind `documentation`, which the detectors do not read): the reference scan found no
  current article with a history, and no lapsed time limit had a last change.
- `build_vulns.py` matches a lapsed time limit to its review by the first 400 characters of its context, not 80: two flags
  in Article 219 of the Labour Code quote the same sentence and differed only after the 80th character, so one review was
  lost and the other was given to both.
- `build_vulns.py` links an article deleted before the folder move under its old folder, through `data/paths.json`
  (Articles 91, 93 to 95, 100 and 107 of the Penal Code, deleted from 1 January 2026 by the Juvenile Justice Law
  59/2024/QH15); before, those six links were empty.
- `config.json` counts this repository's English README (`README.en.md`) as not law; the text scan skips `README.md` but
  read the English one.
