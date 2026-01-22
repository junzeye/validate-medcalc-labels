# Validating MedCalc-Bench Labels

GitHub repository for the paper **"Scalable Stewardship of an LLM-Assisted
Clinical Benchmark with Physician Oversight"** ([arXiv:2512.19691v2](https://arxiv.org/abs/2512.19691v2)).

## Overview

This repository contains the data artifacts and code from our case study on scalable benchmark stewardship using [MedCalc-Bench](https://openreview.net/pdf?id=VXohja0vrQ), a widely used clinical [benchmark](https://web.archive.org/web/20250905181753/https://github.com/ncbi-nlp/MedCalc-Bench) for evaluating LLMs on clinical score computation. We demonstrate a physician-in-the-loop stewardship pipeline that combines agentic LLM verifiers with automated triage to concentrate scarce clinician attention on contentious instances.

We do not position our relabeling as a replacement for the benchmark; instead, we use MedCalc-Bench as a case study to argue that LLM-assisted benchmarks in safety-critical domains must be treated with systematic and physician-in-the-loop stewardship protocols. Our results show that a non-trivial fraction of original labels diverge from physician judgment, and that training on maintained labels yields meaningful performance differences in downstream RL alignment.

**Note:** Our work examines the [MedCalc-Bench dataset](https://github.com/ncbi-nlp/MedCalc-Bench/tree/72748cc0c454ac9d9531494e6180940de03d8470/dataset) released with its 2024 NeurIPS publication (now renamed to "v1.0"), which was the official version available when we ran the LLM pipeline experiments in July–August 2025. A revised ["v1.2"](https://huggingface.co/datasets/ncbi/MedCalc-Bench-v1.2/tree/acb17912657c084f5bf08b8fd029812f84630497) was recently released by the benchmark creators in November 2025. For reproducibility, we include the original v1.0 instances and labels examined in our Phase 1 and Phase 2 studies as `original_test_labels.csv` and `original_train_labels.csv` in the respective data folders. Ongoing revisions by benchmark creators are expected and healthy; our results are intended to motivate transparent and standardized revision methodology, rather than to claim priority over any particular correction.

## Repository Structure

```
data/
├── phase1/                           # Phase 1: Metadata-informed audit
│   ├── original_test_labels.csv      # Original v1.0 test instances and labels
│   ├── test_audit_pipeline_raw.jsonl # Audits produced by agentic LLM pipeline
│   └── phase1_MD_check/             
│       └── test_spotcheck.xlsx       # Physician spot-check annotations
│
├── phase2/                           # Phase 2: Independent recomputation
│   ├── original_test_labels.csv      # Original v1.0 test instances and labels
│   ├── original_train_labels.csv     # Original v1.0 train instances and labels
│   ├── train_y_new_pipeline_raw.jsonl   # Recomputed labels (train set)
│   └── test_y_new_pipeline_raw.jsonl    # Recomputed labels (test set)
│
├── phase3/                           # Phase 3: Physician validations
│   ├── y_new_and_sampled_MD_evals.xlsx    # Original labels, recomputed labels, and physician labels
│   └── y_final_MD_evals_incorporated.xlsx # Final updated test labels incorporating physician feedback
│
└── RL/                               # Controlled RL experiment data
    ├── train_new_labels.parquet      # Training set with recomputed labels
    ├── train_original_labels.parquet # Training set with original labels
    ├── test_new_labels.parquet       # Test set with recomputed labels
    └── uniform_system_prompt.txt     # System prompt used for RL training

scripts/
├── reproduce_phase3_metrics.py       # Reproduces physician validation metrics
└── run_RL_exp.sh                     # Entry point for controlled RL experiment

verl/                                 # Modified verl framework for RL experiments
```

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

### Running the Experiment

**Hardware requirements:** 8× H100 GPUs (80GB each)

**Software requirements:** Install the `verl` framework (0.4.0) with vLLM inference backend as a conda environment. Refer to the [official installation guide](https://verl.readthedocs.io/en/v0.4.0/) for details.

```bash
# Assume you have created a conda environment as `verl_venv`.
conda activate verl_venv
chmod +x scripts/run_RL_exp.sh
# Run the controlled RL experiment
./scripts/run_RL_exp.sh
```

The script runs two independent training jobs (combined in one script for convenience):
1. **New-label arm**: Trains with rewards computed against recomputed labels
2. **Original-label arm**: Trains with rewards computed against original labels

Both models are evaluated on the same held-out test set, with accuracy graded against recomputed labels.

### Implementation

The `verl/` directory contains our modified version of the [verl](https://github.com/volcengine/verl) distributed RL training framework. Key modifications include:
- Custom reward function for MedCalc score matching (`verl/utils/reward_score/medcalc.py`)
- Configuration files for the experiment (`verl/trainer/config_medcalc/`)

## Citation

```bibtex
@misc{scalably2025,
  title         = {Scalable Stewardship of an LLM-Assisted Clinical Benchmark with Physician Oversight},
  author        = {Ye, Junze and Tawfik, Daniel and Goodell, Alex J. and Kotha, Nikhil V. and Buyyounouski, Mark K. and Bayati, Mohsen},
  year          = {2025},
  eprint        = {2512.19691v2},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2512.19691v2}
}
```

## License

See [LICENSE](LICENSE) for details.
