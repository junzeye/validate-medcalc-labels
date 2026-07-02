# Data Guide

This folder follows the three-phase stewardship pipeline described in the paper. For plug-and-play evaluation, use **`medcalc_v1_corrected.csv`** with the prompt templates in this folder; see the [root README](../README.md) for instructions and schema notes.

## Phase 1: Metadata-informed audit (`phase1/`)

An agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding) reviews each original test label *with* its full derivation metadata, flagging potential label errors. A physician author (perioperative medicine & anesthesiology) spot-checked flagged instances (`phase1_MD_check/test_spotcheck.xlsx`).

- `test_audit_pipeline_raw.jsonl`: raw audits, collected July 2025 (5 independent runs × 1,047 instances = 5,235 Gemini 2.5 Pro calls).
- `original_test_labels.csv`: the v1.0 test instances and labels that were audited.

## Phase 2: Independent recomputation (`phase2/`)

A separate agentic pipeline (Gemini 2.5 Pro + knowledge grounding + Python tool use) recomputes each score from the case report and calculator question alone, with no access to original labels or metadata, reducing anchoring bias.

- `test_y_new_pipeline_raw.jsonl`, `train_y_new_pipeline_raw.jsonl`: raw recomputed labels, collected August 2025 (>6 runs × 6,230 instances ≈ 37,380 Gemini 2.5 Pro calls).
- `original_test_labels.csv`, `original_train_labels.csv`: the v1.0 instances and labels examined.

## Phase 3: Physician validation (`phase3/`)

Three licensed physicians (pediatric critical care; perioperative medicine & anesthesiology; radiation oncology) independently computed gold-standard labels on 50 sampled instances, quantifying how well the original and recomputed labels align with physician judgment.

- `y_new_and_sampled_MD_evals.xlsx`: original, recomputed, and physician labels side by side.
- `y_final_MD_evals_incorporated.xlsx`: final maintained test labels after physician feedback; use column `y_final` for downstream experiments.

Reproduce the validation metrics with `python scripts/reproduce_phase3_metrics.py` (from the repo root). See `phase3/README.md` for column naming.

## Controlled RL experiment (`RL/`)

Data for two GRPO training runs on the same Qwen3-8B base model, differing only in whether rewards are computed against original or recomputed labels.

- `train_new_labels.parquet` / `train_original_labels.parquet`: training instances for the new-label and original-label arms.
- `test_new_labels.parquet`: held-out test set (both arms graded against recomputed labels).
- `uniform_system_prompt.txt`: system prompt used during training.
