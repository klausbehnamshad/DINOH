# Contributing to DINOH (evaluation release)

Thanks for your interest. This repository is the **public, synthetic-data evaluation release** of the DINOH project. Contributions, questions, and reuse by other oral-history institutes and universities are very welcome.

## Scope

This repo covers the **evaluation core**, the **concept & architecture note**, and the **WebVTT/OHMS exporters**. It does **not** contain DINOH's internal governance/enforcement engine, and issues or pull requests about that engine cannot be actioned here. No real interview data belongs in this repository — the corpus is and must remain **synthetic**.

## Ways to contribute

- **Report issues** — bugs, unclear docs, metric questions, or export interoperability problems (WebVTT / OHMS).
- **Improve the benchmark** — additional synthetic records, language coverage, or metric reporting. Please keep new corpus data synthetic and mark it as such.
- **Discuss the method** — the per-language, human-referenced evaluation design is meant to be debated and refined.

## Ground rules

1. **Synthetic data only.** Never add real testimonies, real personal data, real dataset identifiers, or real individuals' names as interviewer/annotator metadata. Use pseudonyms such as `[INTERVIEWER_1]` / `[ANNOTATOR_1]`.
2. **Keep the evaluation core independent.** The core (`corpus`, `schema`, `metrics`, `reports`, `export`) must not import governance/pipeline modules.
3. **Tests stay green.** Run `pytest` before opening a pull request; add tests for new behaviour.
4. **Reproducibility.** The notebook must run clean via *Restart Kernel & Run All*, regenerating `reports/`.

## Development setup

```bash
conda env create -f environment.yml && conda activate dinoh   # or: pip install -r requirements.txt
pytest
```

## Getting in touch

Open an issue, or contact **Klaus Behnam Shad** at the Luxembourg Centre for Contemporary and Digital History (C²DH), University of Luxembourg.

*By contributing, you agree that your contributions are licensed under the repository's MIT License.*
