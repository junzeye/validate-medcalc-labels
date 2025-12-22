# Validating MedCalc-Bench Labels

Repository for the paper **"Scalably Enhancing the Clinical Validity of a Task Benchmark with Physician Oversight"**.

> ⚠️ **This repository is actively being updated.**

## Overview

This repository contains the data artifacts from our physician-in-the-loop validation and systematic relabeling of [MedCalc-Bench](https://openreview.net/pdf?id=VXohja0vrQ), a [benchmark](https://web.archive.org/web/20250905181753/https://github.com/ncbi-nlp/MedCalc-Bench) for evaluating LLMs on clinical score computation. We show that a non-trivial fraction of original labels diverge from physician judgment, and that training on revised labels yields meaningful performance difference in downstream RL alignment.

**Note:** Our work examines the [MedCalc-Bench dataset](https://github.com/ncbi-nlp/MedCalc-Bench/tree/72748cc0c454ac9d9531494e6180940de03d8470/dataset) released with its 2024 NeurIPS publication (now renamed to "v1.0"), which was the official version available when we ran the LLM pipeline experiments in July–August 2025. A revised ["v1.2"](https://huggingface.co/datasets/ncbi/MedCalc-Bench-v1.2/tree/acb17912657c084f5bf08b8fd029812f84630497) was recently released by the benchmark creators in November 2025 but did not specify how they changed the data generation methodology; so it is not covered by our analysis.

## Repository Structure

```
data/
├── phase1/                           # Initial audit experiments
│   ├── test_audit_pipeline_raw.jsonl # Audits produced by an agentic LLM pipeline
│   └── phase1_MD_check/             
│       └── test_spotcheck.xlsx       # Physician spot-check annotations
│
└── phase2/                           # Extensive relabeling experiments
    ├── train_relabel_pipeline_raw.jsonl # New labels produced by another agentic LLM pipeline
    ├── test_relabel_pipeline_raw.jsonl  # New labels produced by another agentic LLM pipeline
    └── phase2_MDs_blind_eval/           # Parsed new test labels & licensed physicians' single-blind score evaluations of 50 sampled labels
        ├── y_new_and_sampled_MD_evals.xlsx    # juxtaposed old new labels, new labels, and sampled, independent physician labels
        └── y_final_MD_evals_incorporated.xlsx # Final test set labels, incorporating physician feedback
```

### Phase 1: Audit Pipeline
Initial automated audit using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding) to flag potential label errors in MedCalc-Bench, with physician spot-checks to validate flagged instances. Results in `phase1/test_audit_pipeline_raw.jsonl` were collected from the Phase 1 pipeline in July 2025, using 5x1047=5235 API calls to the Gemini 2.5 Pro API endpoint for the language model backbone.

### Phase 2: Relabeling Pipeline
Independent relabeling of train and test sets from scratch using another agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding + Python tool use) we set up, followed by systematic review of divergent cases to produce corrected labels by three licensed physicians. Results in `phase2/train_relabel_pipeline_raw.jsonl` and `phase2/test_relabel_pipeline_raw.jsonl` were collected from the Phase 2 pipeline in August 2025, also using Gemini API calls. Final test set labels in `phase2/y_final_MD_evals_incorporated.xlsx` were incorporated with physician feedback; we recommend using labels in the column `y_final` for downstream alignment experiments.


## Citation

```bibtex
# Citation coming soon
```

## License

See [LICENSE](LICENSE) for details.
