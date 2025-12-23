# Validating MedCalc-Bench Labels

Repository for the paper **"Scalably Enhancing the Clinical Validity of a Task Benchmark with Physician Oversight"**.

> ⚠️ **This repository is actively being updated.**

## Overview

This repository contains the data artifacts from a case study on scalable benchmark maintenance using [MedCalc-Bench](https://openreview.net/pdf?id=VXohja0vrQ), a [benchmark](https://web.archive.org/web/20250905181753/https://github.com/ncbi-nlp/MedCalc-Bench) for evaluating LLMs on clinical score computation. We demonstrate a physician-in-the-loop maintenance pipeline that combines agentic LLM verifiers with automated triage to concentrate scarce clinician attention on contentious instances.

We do not position our relabeling as a replacement for the benchmark; instead, we use MedCalc-Bench as a case study to argue that LLM-assisted benchmarks in safety-critical domains must be treated as _living documents_ with transparent, repeatable, and systematic maintenance protocols. Our results show that a non-trivial fraction of original labels diverge from physician judgment, and that training on maintained labels yields meaningful performance differences in downstream RL alignment.

**Note:** Our work examines the [MedCalc-Bench dataset](https://github.com/ncbi-nlp/MedCalc-Bench/tree/72748cc0c454ac9d9531494e6180940de03d8470/dataset) released with its 2024 NeurIPS publication (now renamed to "v1.0"), which was the official version available when we ran the LLM pipeline experiments in July–August 2025. A revised ["v1.2"](https://huggingface.co/datasets/ncbi/MedCalc-Bench-v1.2/tree/acb17912657c084f5bf08b8fd029812f84630497) was released by the benchmark creators in November 2025. Ongoing revisions by benchmark creators are expected and healthy; our results are intended to motivate transparent revision methodology and routine re-auditing, rather than to claim priority over any particular correction.

## Repository Structure

```
data/
├── phase1/                           # Initial audit experiments
│   ├── test_audit_pipeline_raw.jsonl # Audits produced by an agentic LLM pipeline
│   └── phase1_MD_check/             
│       └── test_spotcheck.xlsx       # Physician spot-check annotations
│
└── phase2/                           # Maintenance pipeline case study
    ├── train_y_new_pipeline_raw.jsonl   # Recomputed labels from agentic LLM pipeline
    ├── test_y_new_pipeline_raw.jsonl    # Recomputed labels from agentic LLM pipeline
    └── phase2_MDs_blind_eval/           # Maintained test labels & licensed physicians' independent computations of 50 sampled (C,q) instances
        ├── y_new_and_sampled_MD_evals.xlsx    # Juxtaposed original labels, recomputed labels, and sampled physician labels
        └── y_final_MD_evals_incorporated.xlsx # Maintained test set labels, incorporating physician feedback

scripts/
└── reproduce_phase2_metrics.py       # Reproduces Table 3 (Phase 2 physician validation metrics)
```

> **Note:** More reproduction scripts are being ported from Jupyter notebooks; check back for updates.

### Phase 1: Audit Pipeline
Initial automated audit demonstrating scalable error detection using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding) to flag potential label divergences, with physician spot-checks to validate flagged instances. Results in `phase1/test_audit_pipeline_raw.jsonl` were collected from the Phase 1 pipeline in July 2025, using 5×1047=5235 API calls to the Gemini 2.5 Pro API endpoint for the language model backbone.

### Phase 2: Maintenance Pipeline
Independent recomputation of train and test sets using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding + Python tool use), followed by systematic clinician adjudication of divergent cases by three licensed physicians. This phase demonstrates the full maintenance workflow: agentic verification → conservative triage → clinician review. Results in `phase2/train_y_new_pipeline_raw.jsonl` and `phase2/test_y_new_pipeline_raw.jsonl` were collected from the Phase 2 pipeline in August 2025. Maintained test set labels in `phase2/y_final_MD_evals_incorporated.xlsx` incorporate physician feedback; we recommend using labels in the column `y_final` for downstream alignment experiments.


## Citation

```bibtex
@misc{scalably2025,
  title         = {Scalably Enhancing the Clinical Validity of a Task Benchmark with Physician Oversight},
  author        = {Ye, Junze and Tawfik, Daniel and Goodell, Alex J. and Kotha, Nikhil V. and Buyyounouski, Mark K. and Bayati, Mohsen},
  year          = {2025},
  eprint        = {2512.19691v1},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2512.19691v1}
}
```

## License

See [LICENSE](LICENSE) for details.
