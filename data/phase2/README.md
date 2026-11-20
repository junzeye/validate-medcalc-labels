# Phase 2: Independent recomputation

Each case was recomputed by Gemini 2.5 Pro several times. The new label `y_new` comes from **five runs per case**, but the raw files hold more than five records for some cases. This note explains which five were used and how they were combined.

## Files

| File | Contents |
|------|----------|
| `test_y_new_pipeline_raw.jsonl` | Raw pipeline outputs for the test split: 6,317 records over 1,047 cases |
| `train_y_new_pipeline_raw.jsonl` | Raw pipeline outputs for the train split: 30,250 records over 5,183 cases |
| `phase2_run_manifest.csv` | One row per raw record, marking the five selected per case |
| `original_test_labels.csv`, `original_train_labels.csv` | The v1.0 instances and labels examined |

Each raw record has a `key` of the form `<split>-<uid>-<hash>`, e.g. `test-334-4bdb5c`. The `uid` is the `Unique ID` in the original label CSVs.

## Why some cases have more than five records

When we ran the experiment in 2025, Gemini's batch API calls sometimes had server-side failure (no output, or a response with no final answer), so we oversampled.

- **Test:** 6 runs per case were requested up front. Five cases still had fewer than five usable runs and were resubmitted with 7 more runs each (13 records in total).
- **Train:** 5 runs per case were requested, and failed runs were resubmitted over several rounds.

## Which five runs were used

Read each JSONL from top to bottom. For each case, keep the **first five records with a parseable answer** and ignore the rest.

A record is parseable when the last text part of the response contains `<answer>...</answer>` and the content reads as a number, a date, a `(weeks, days)` tuple, or `unknown`. No record was kept or dropped because of its answer's value.

`phase2_run_manifest.csv` records the outcome, so you do not need to re-implement the rule:

| Column | Description |
|--------|-------------|
| `split`, `uid`, `key` | Identify the record |
| `released_file`, `line_number` | Where the record sits in the raw JSONL (1-based line) |
| `status` | `valid`, `no_output`, `no_answer_tag`, `no_closing_tag`, or `unparseable` |
| `selected` | `True` for the five runs used for the case |
| `sample_rank` | 1 to 5 for selected runs, in selection order |
| `answer_raw` | Text inside the final `<answer>` tag |
| `parsed_value` | Value used downstream for selected runs (dates as `YYYY/MM/DD`, week-day tuples as total days) |

To load the five selected runs per case:

```python
import json
import pandas as pd

manifest = pd.read_csv("phase2_run_manifest.csv")
selected = manifest[(manifest["split"] == "test") & manifest["selected"]]
keys = set(selected["key"])

with open("test_y_new_pipeline_raw.jsonl") as f:
    runs = [record for record in map(json.loads, f) if record["key"] in keys]
```

## From five runs to one label

The five `parsed_value`s of a case are combined as follows:

1. Round numeric values to 2 decimal places, then count identical values. `unknown` counts as a value.
2. If at least 4 of the 5 agree, that value is `y_new`.
3. If exactly 3 agree, the value is `y_new` only if at least one of the other two is within ±5% of it (±1 day for dates).
4. Otherwise the case gets no `y_new` and is left out of the relabeled data.

This yields `y_new` for 887 of 1,047 test cases and 4,593 of 5,183 train cases. These are the labels in `../RL/test_new_labels.parquet`, `../RL/train_new_labels.parquet`, and the `y_new` column of the Phase 3 workbooks (where `unknown` appears as `N/A`).
