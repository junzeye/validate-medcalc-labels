# Validating MedCalc-Bench Labels

Repository for the paper **"Scalably Enhancing the Clinical Validity of a Task Benchmark with Physician Oversight"**.

> ⚠️ **This repository is actively being updated.**

## Overview

This repository contains the data artifacts from our physician-in-the-loop audit and systematic relabeling of [MedCalc-Bench](https://openreview.net/pdf?id=VXohja0vrQ), a [benchmark](https://web.archive.org/web/20250905181753/https://github.com/ncbi-nlp/MedCalc-Bench) for evaluating LLMs on clinical score computation. We show that a non-trivial fraction of original labels diverge from physician judgment, and that training on corrected labels yields meaningful performance difference in downstream RL alignment.

**Note:** Our audit targets the [MedCalc-Bench dataset](https://github.com/ncbi-nlp/MedCalc-Bench/tree/72748cc0c454ac9d9531494e6180940de03d8470/dataset) released with its 2024 NeurIPS publication (now renamed to "v1.0"), which was the official version available when we ran the LLM pipeline experiments in July–August 2025. A revised ["v1.2"](https://huggingface.co/datasets/ncbi/MedCalc-Bench-v1.2/tree/acb17912657c084f5bf08b8fd029812f84630497) was recently released by the benchmark creators in November 2025 but did not specify how they changed the data generation methodology; so it is not covered by our analysis.

## Repository Structure

```
data/
├── phase1/                         # Initial audit experiments
│   ├── test_audit_pipeline_raw.jsonl
│   └── phase1_MD_check/            # Physician spot-check annotations
│       └── test_spotcheck.xlsx
│
└── phase2/                         # Extensive relabeling experiments
    ├── train_relabel_pipeline_raw.jsonl
    ├── test_relabel_pipeline_raw.jsonl
    └── phase2_MDs_blind_eval/      # Physicians' single-blind score evaluations
        ├── y_new_and_sampled_MD_evals.xlsx
        └── y_final_MD_evals_incorporated.xlsx # Final test set labels, incorporating physician feedback (we recommend using this version for downstream alignment experiments)
```

### Phase 1: Audit Pipeline
Initial automated audit using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding) to flag potential label errors in MedCalc-Bench, with physician spot-checks to validate flagged instances. Results were collected from the pipeline in July 2025.

### Phase 2: Relabeling Pipeline
Independent relabeling of train and test sets from scratch using an agentic LLM pipeline (Gemini 2.5 Pro + knowledge grounding + Python tool use), with systematic review of divergent cases to produce corrected labels by three licensed physicians. Results were collected from the pipeline in August 2025.


## Citation

```bibtex
# Citation coming soon
```

## License

See [LICENSE](LICENSE) for details.
