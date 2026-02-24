## Phase 1: Metadata-Informed Audit

Initial automated audit demonstrating scalable error detection using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding) to flag potential label divergences. In this phase, the pipeline has access to the full original metadata, including original labels and their derivation steps, enabling it to fact-check the existing labeling process. Physician (Alex Goodell, perioperative medicine & anesthesiology) spot-checks validate flagged instances.

Results in `data/phase1/test_audit_pipeline_raw.jsonl` were collected from the Phase 1 pipeline in July 2025, using 5×1047=5235 API calls to the Gemini 2.5 Pro API endpoint.

## Phase 2: Independent Recomputation

Independent recomputation of train and test sets using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding + Python tool use). Unlike Phase 1, this pipeline does not have access to original labels or their derivation metadata, reducing anchoring bias. This phase demonstrates first-principles relabeling where the pipeline derives scores independently from the case report and calculator specification alone.

Results in `data/phase2/train_y_new_pipeline_raw.jsonl` and `data/phase2/test_y_new_pipeline_raw.jsonl` were collected from the Phase 2 pipeline in August 2025, using more than 6x(1047+5183)=37,380 API calls to the Gemini 2.5 Pro API endpoint.

## Phase 3: Physician Validation

Systematic clinician adjudication where three licensed physicians (Daniel Tawfik, pediatric critical care medicine; Alexander Goodell, perioperative medicine & anesthesiology; Nikhil Kotha, radiation oncology) independently compute gold-standard labels on 50 sampled (C, q) instances. This phase quantifies alignment between original labels, recomputed labels, and physician judgment.

Key files in `data/phase3/`:
- `y_new_and_sampled_MD_evals.xlsx`: Juxtaposed original labels, recomputed labels, and physician labels
- `y_final_MD_evals_incorporated.xlsx`: Maintained test set labels after incorporating physician feedback; we recommend using labels in the column `y_final` for downstream experiments

To reproduce the physician validation metrics:
```bash
python scripts/reproduce_phase3_metrics.py
```

## Controlled RL Experiment

We conducted a controlled reinforcement learning experiment to isolate the causal effect of label quality on downstream model alignment. Two GRPO (Group Relative Policy Optimization) training runs were performed on the same Qwen3-8B base model, differing only in whether training rewards were computed against original labels or recomputed labels.

### Data

The `data/RL/` folder contains:
- `train_new_labels.parquet`: Training instances with recomputed labels (used in the new-label arm)
- `train_original_labels.parquet`: Training instances with original labels (used in the original-label arm)
- `test_new_labels.parquet`: Test set for evaluation (graded against recomputed labels in both arms)
- `uniform_system_prompt.txt`: System prompt template used during training
