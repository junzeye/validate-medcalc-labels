# Improving MedCalc-Bench Labels with Physician Oversight

Code and data from our physician-in-the-loop cleanup of the ground-truth labels of [MedCalc-Bench](https://openreview.net/forum?id=VXohja0vrQ#discussion) (NeurIPS 2024 Oral; featured in [MedHELM](https://crfm.stanford.edu/helm/medhelm/latest/#/leaderboard/medcalc_bench)), a widely used benchmark for LLM medical score computation.

**TL;DR:** More than 25% of the original MedCalc-Bench v1.0 test labels diverge from physician judgment. We release physician-validated corrected labels as a drop-in replacement (`data/medcalc_v1_corrected.csv`), produced by a three-phase stewardship pipeline that uses agentic LLM verifiers and automated triage to concentrate scarce physician attention on the most contentious instances. Label quality matters downstream: re-evaluating frontier LLMs against the corrected labels changes measured accuracy, and RL training (GRPO) with corrected vs. original reward labels produces measurably different models.

## 🚀 Quick start: evaluate on the corrected labels

- Point your existing MedCalc-Bench v1.0 harness at **`data/medcalc_v1_corrected.csv`**. Column names match v1.0 (with `Row Number` renamed to `Unique ID`), keeping the subset needed for evaluation: `Unique ID`, `Calculator Name`, `Question`, `Patient Note`, `Ground Truth Answer`, `Lower Limit`, `Upper Limit`.
- Use `data/system_prompt.txt` and `data/user_prompt_template.txt` (or `data/tool_use_prompt_template.txt` for tool-using LLMs). The prompts instruct the model to output `N/A` when the patient note lacks sufficient information — some corrected labels are abstentions.
- The file contains **887 of the original 1,047 test instances**: we prioritize precision and only release labels where our physician-validated pipeline has high confidence. If you need all 1,047, merge with the originals (`data/phase1/original_test_labels.csv`) on `Unique ID` (= `Row Number` in v1.0).

<div align="center">
  <br>
  <img src="media/llm_comparison_50ex.png" alt="Comparison of Frontier LLMs on MedCalc-Bench with our physician-produced labels" width="85%">
  <br>
</div>
<div align="left">
  <sub><b>Figure 1.</b> Frontier LLM accuracy on the 50 test instances labeled directly by Stanford physicians. Responses collected via API (February 20–23, 2026) with server-side tool use (web search + Python), "high" reasoning effort, and a shared prompt template. Error bars are 95% CIs.</sub>
</div>

<div align="center">
  <br>
  <img src="media/llm_comparison_full.png" alt="Frontier LLM accuracy on all 887 corrected MedCalc-Bench labels" width="85%">
  <br>
</div>
<div align="left">
  <sub><b>Figure 2.</b> Same setup as Figure 1, scored against all 887 corrected labels (the 50 physician labels plus 837 pipeline-produced labels). Error bars are 95% CIs.</sub>
</div>

## 🔍 How the labels were produced

Three phases, each documented with raw data in `data/` (see `data/readme.MD`):

1. **Audit** (`data/phase1/`) — agentic LLM verifiers review each original label and its derivation metadata, flagging clinically suspect instances.
2. **Independent recomputation** (`data/phase2/`) — a separate agentic pipeline recomputes each score from the patient note and calculator question alone (no access to original labels, avoiding anchoring); supermajority voting across independent runs yields high-confidence labels.
3. **Physician validation** (`data/phase3/`) — physicians independently recompute the most contentious instances, validating both label sets and producing the final maintained labels. Four board-licensed physicians from three specialties at Stanford Medicine provided annotations and adjudication. Reproduce the validation metrics with `python scripts/reproduce_phase3_metrics.py`.

## 🗂️ Repository structure

```
data/
├── medcalc_v1_corrected.csv   # Recommended: final corrected test labels (drop-in for v1.0)
├── *.txt                      # System / user / tool-use prompt templates
├── phase1/                    # Audit: original labels + raw pipeline audits + MD spot-checks
├── phase2/                    # Recomputation: original labels + raw recomputed labels (train & test)
├── phase3/                    # Physician validation: MD labels + final adjudicated labels
└── RL/                        # Controlled RL experiment data (parquet) + training system prompt

scripts/
├── reproduce_phase3_metrics.py   # Reproduces physician validation metrics
└── run_RL_exp.sh                 # Entry point for the controlled RL experiment

verl/         # Modified verl framework used for the RL experiment
appendix_G/   # Pointer to the self-contained Appendix G reproduction repo
```

## 🔬 Reproducing the RL experiment

Two GRPO training runs on the same Qwen3-8B base model, identical except for whether rewards are computed against original or recomputed labels; both arms are evaluated on the same held-out test set graded against recomputed labels.

- **Hardware:** 8× H100 (80GB) or equivalent.
- **Software:** [verl 0.4.0](https://verl.readthedocs.io/en/v0.4.0/) with the vLLM backend, installed as a conda environment. The `verl/` directory is our modified copy of [verl](https://github.com/volcengine/verl); key changes are the MedCalc reward function (`verl/utils/reward_score/medcalc.py`) and the Qwen3-8B training configs (`verl/trainer/config_medcalc/`).

```bash
conda activate verl_venv   # your verl environment
chmod +x scripts/run_RL_exp.sh
./scripts/run_RL_exp.sh    # runs both training arms
```

## 📋 Dataset versioning

We examine the [MedCalc-Bench release](https://github.com/ncbi-nlp/MedCalc-Bench/tree/72748cc0c454ac9d9531494e6180940de03d8470/dataset) accompanying its NeurIPS 2024 publication (now "v1.0"), the official version when we ran our pipeline in July–August 2025; the benchmark creators released [v1.2](https://huggingface.co/datasets/ncbi/MedCalc-Bench-v1.2/tree/acb17912657c084f5bf08b8fd029812f84630497) in November 2025. The exact v1.0 instances we studied are preserved as `original_*_labels.csv` in the phase folders. Ongoing revisions by benchmark creators are expected and healthy; our results are meant to motivate transparent, versioned revision methodology, not to claim priority over any particular correction.

## 📝 Citation

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

## ⚖️ License

See [LICENSE](LICENSE) for details.
