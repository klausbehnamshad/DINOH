# DINOH Evaluation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21273366.svg)](https://doi.org/10.5281/zenodo.21273366)
![License: MIT](https://img.shields.io/badge/License-MIT-informational)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-v1.0.1%20(draft)-orange)
[![CI](https://github.com/klausbehnamshad/DINOH/actions/workflows/ci.yml/badge.svg)](https://github.com/klausbehnamshad/DINOH/actions/workflows/ci.yml)

**Synthetic examples and evaluation methods under development for computational assistance in oral history.**

DINOH is a digital research infrastructure developed at the **Luxembourg Centre for Contemporary and Digital History (C²DH), University of Luxembourg**. It brings together **OHPIPE**, its transcript-workflow component, **DINOH Evaluation**, the **Interview Metadata Model (IMM)** and shared methods for oral-history research. This repository contains **DINOH Evaluation**, a separate component for inspecting evaluation procedures using synthetic records and researcher-authored reference annotations. OHPIPE is available separately as an [experimental public preview](https://github.com/klausbehnamshad/ohpipe/releases/tag/v0.1.0a1), with its own test results and limitations.

The synthetic transcript texts were drafted with AI assistance and edited by the author. The reference annotations are human-authored; see the [data card](DATA_CARD.md) for provenance and limitations.

The current model backend is a **placeholder**. The included scoring outputs demonstrate the procedure; they are **not measurements of model performance**. The reference annotations provide a basis for specific comparison tasks, not a general standard for interpreting oral histories.

---

> ## ⚠️ This harness has not measured anything yet — please read before citing
>
> The model backend is **stubbed**. `MODEL_REGISTRY` holds placeholder entries and `run_model()`
> returns a deterministic placeholder, so the downstream evaluation logic can be exercised end to
> end without a compute connection (see §5 of the notebook).
>
> **The task scores under `reports/` are smoke-test output, not
> model-performance evidence.** That is why every accuracy reads `1.0` and every WindowDiff is
> constant across models and languages. Those files are shipped so the scoring path is inspectable
> and reproducible, not because they say anything about models.
>
> **Please do not cite this as a benchmark of model quality or quote its task scores as model
> results.** The separate schema-validation reports describe whether the synthetic records
> conform to the schemas; they do not measure model quality either.
>
> What *is* real and tested: the synthetic corpus with human-authored reference annotations, the schemas, the metric design, the
> scoring-integrity rules, the export path and the test suite. **This release makes measurement
> possible; it does not report model measurements.** See [Status](#status) for the next validation steps.

---

## Scope of this repository — please read first

This is an **open, synthetic-data** release of the **evaluation core** and the **concept**.
Concretely, it contains:

- the multilingual **evaluation harness** (code, synthetic gold-standard corpus, two JSON schemas,
  notebook, dashboard);
- **historical concept and architecture documents** (`docs/`, `website/` and the architecture SVG),
  retained with explicit status notices. Their maturity labels and implementation claims are not
  evidence about the current releases; see [Governance and current scope](docs/GOVERNANCE.md);
- **interoperability exporters** to **WebVTT** and **OHMS** (Oral History Metadata Synchronizer).

It **does not** contain or execute OHPIPE. Descriptions of gates, attestation, run manifests,
BIND/ACCOUNT, quarantine, controller release and withdrawal in the historical concept documents
are design context, not guarantees of this evaluation repository or of the separate OHPIPE
preview. No real interview data is included; every corpus record is synthetic.

For specifications, see [`DATA_CARD.md`](./DATA_CARD.md) (dataset) and
[`BENCHMARK_CARD.md`](./BENCHMARK_CARD.md) (tasks, metrics and current status); for release
history, [`CHANGELOG.md`](./CHANGELOG.md).

---

## What the harness is built to measure

Two tasks that a computational tool might assist with, always scored against a **human** gold
standard:

1. **Minimal metadata extraction** — given an interview, can a model correctly fill a small set of
   descriptive fields (title, language, place, keywords, short abstract)? Scored field by field, by
   field type: exact agreement for controlled vocabulary, precision/recall/F1 for keyword lists,
   and **no automatic score at all** for free text (`title`, `abstract`), which is flagged for
   human review instead.
2. **Thematic segmentation** — can a model divide an interview into coherent thematic sections,
   with boundaries where a human reader would place them? Scored with **WindowDiff** and **Pk**,
   the two standard segmentation metrics, over timecode-derived boundary masses on a shared unit
   axis.

Results are designed to be **always reported per language and never pooled** into a single average
— so strong performance in English cannot mask weak performance in a lower-resourced language. The
gold standard spans **seven languages: German, English, French, Italian, Spanish, Luxembourgish and
Portuguese**, over 28 synthetic interview records, four per language.

Scoring integrity is part of the design, not an afterthought: a malformed or missing timecode in a
prediction is recorded as a per-record `error`, never silently mis-scored, and never aborts the
run.

## What makes it different

- **The reference is human.** The gold standard is annotated by a researcher, not generated by
  another model. AI is measured on a narrow, assistive contribution — not on interpretation, which
  remains a scholarly act.
- **Proposal and selection stay separate.** Model output is carried as `suggested_*`, curated
  values as `selected_*`, and the two remain distinguishable even when the values are identical,
  because they carry different epistemic status.
- **Language is treated with care.** Luxembourg's oral history is multilingual by nature;
  Luxembourgish and Portuguese are poorly served by mainstream tools. Every language is reported on
  its own terms. Seven languages are *represented* here — multilinguality is not yet *evaluated*
  (the synthetic corpus does not reproduce deep code-switching, authentic disfluency or dialect
  variation).
- **The harness knows its limits.** The deepest layer of interpretation is deliberately left
  outside automated scoring; fields that resist mechanical comparison are flagged for human review
  rather than scored by proxy.

## Interoperability (WebVTT + OHMS)

The examples export synthetic evaluation records as **WebVTT** and **OHMS XML**. See `examples/` for the synthetic exports and demonstration viewer.

When `record_to_ohms_xml()` is called without an explicit override (`allow_fulltext=None`), inclusion of the abstract and anchor quotations depends on the record's declared `accessRights == "open"` and `consent_status == "public"` values. Passing `allow_fulltext=True` overrides that metadata decision. Other metadata and segment titles remain in the output. Callers are responsible for appropriate inputs and invocation.

The WebVTT function emits supplied record and segment titles regardless of access status; it ignores `allow_fulltext`. Neither function assesses whether a title or another field identifies a person. These are format exporters for controlled synthetic examples, not an authorisation mechanism or a general privacy filter.

The OHMS output has **not yet been validated against the published OHMS XSD**. No connector or tested mapping to an external portal is provided here.

## Quick start

**With conda (recommended — matches the pinned demo environment):**

```bash
git clone https://github.com/klausbehnamshad/DINOH.git
cd DINOH
conda env create -f environment.yml
conda activate dinoh
python -m ipykernel install --user --name dinoh --display-name "Python (dinoh)"
```

**Or with pip in a virtual environment:**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Run the harness** — regenerates the report data using the placeholder backend
(see the status note above; the outputs are smoke tests, not results):

```bash
jupyter notebook notebooks/cdh_oh_eval_v1.ipynb   # then: Restart Kernel & Run All
```

**Run the tests** (evaluation core only — no pipeline imports):

```bash
pip install pytest
pytest            # pythonpath/testpaths are configured in pyproject.toml
```

**Optional — launch the dashboard** (reads `reports/`, warns if out of sync with the corpus):

```bash
pip install streamlit
streamlit run eval_dashboard.py
```

## Repository layout

```
src/oh_eval/     evaluation core: corpus · schema · metrics · reports · export
tests/           evaluation-core tests (no pipeline dependencies)
data/            corpus_synthetic.json  (synthetic gold standard)
schemas/         luxoh_minimal_metadata · oh_eval_record
notebooks/       cdh_oh_eval_v1.ipynb   (the narrative surface)
reports/         smoke-test output of the scoring path — NOT model results
examples/        WebVTT + OHMS exports (28 records) + viewer.html
docs/            concept & architecture note · plain-language walkthrough · terminology
eval_dashboard.py
```

## Data & transparency

All interview material is **synthetic** — written for methodological testing, representing no real
person, testimony, or event; every record is marked accordingly. Future backend work targets **open-weight** models; the current entries are placeholders.
The descriptive fields follow a
published minimal-metadata schema (the **LuxOH Implementation Profile** of the discipline-agnostic
**Interview Metadata Model — Core Profile (IMM-Core)**).

The task reports are versioned outputs of the placeholder scoring path. They do not document a
model-performance experiment. Notebook execution also produces schema-validation reports.
This evaluation repository does not enforce a complete model/prompt/corpus run manifest;
historical architecture descriptions are not proof of that capability in another component.

## Anticipated questions

**Are the numbers in `reports/` model results?** No. The task scores come from the placeholder
backend and should not be quoted as model-performance evidence. The schema-validation reports
separately describe record conformance. [The report notice](reports/README.md) explains the distinction.

**Why ship them at all, then?** Because the scoring logic, the schema validation and the export
path are the substance of this release, and they are easier to review with their outputs present
than absent. `reports/README.md` repeats the warning next to the files.

**Why only synthetic data?** These examples make the evaluation procedure inspectable without publishing interview testimony. Real interview processing belongs within the applicable institutional framework. Required data-protection, ethics and access reviews precede processing; the controller or joint controllers remain responsible. This repository neither establishes nor verifies that authorisation. See [Governance](docs/GOVERNANCE.md) for responsibilities and methodological limits.

**Where is OHPIPE?** Its [separate repository](https://github.com/klausbehnamshad/ohpipe) contains an experimental transcript workflow. It is not distributed here, and its preview does not claim complete historical contract conformance. The exporters in this repository demonstrate limited format conversion on synthetic examples; they grant no authorisation and provide no general privacy filter. See [Interoperability](#interoperability-webvtt--ohms) for their exact behaviour.

**One annotator isn't a benchmark.** Correct — and neither is a stubbed backend. This is an
evaluation *infrastructure* release: a reproducible corpus, schema, scoring method and export path.
Real inference and inter-annotator agreement are the next steps, and an open invitation to
collaborate (see [Status](#status)).

## Citation

The verified Zenodo archive is **v1.0.0**, published on 9 July 2026. The current `main` branch,
including these documentation corrections, is a later development snapshot and is not that
archived version. The examples below and the preferred citation in [`CITATION.cff`](./CITATION.cff)
identify the archive. If your work uses later changes, also record the exact Git commit.

**Author** — Klaus Behnam Shad, Luxembourg Centre for Contemporary and Digital History (C²DH),
University of Luxembourg. ORCID: [0000-0002-3601-9024](https://orcid.org/0000-0002-3601-9024).

### APA (7th edition)

> Behnam Shad, K. (2026). *DINOH — a Digital, AI-assisted Infrastructure for Oral History: Public
> evaluation release (multilingual benchmark)* (Version v1.0.0) [Computer software].
> Zenodo. https://doi.org/10.5281/zenodo.21273367

### BibTeX

```bibtex
@software{behnam_shad_dinoh_2026,
  author    = {Behnam Shad, Klaus},
  title     = {{DINOH --- a Digital, AI-assisted Infrastructure for Oral History:
                public evaluation release (multilingual benchmark)}},
  version   = {v1.0.0},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21273367},
  url       = {https://doi.org/10.5281/zenodo.21273367},
  orcid     = {0000-0002-3601-9024},
  license   = {MIT}
}
```

*(For BibTeX styles without a `@software` entry type, `@misc` with the same fields works; the
`orcid` field is a biblatex extension and is ignored by styles that do not know it.)*

### Which DOI to use

The badge uses the **concept DOI**
[10.5281/zenodo.21273366](https://doi.org/10.5281/zenodo.21273366), which always resolves to the
latest archived version. The citations above instead pin the verified archive with its version DOI:

| Version | Released | Version DOI |
| --- | --- | --- |
| `v1.0.0` | 2026-07-09 | [10.5281/zenodo.21273367](https://doi.org/10.5281/zenodo.21273367) |

The archived title includes the historical word “benchmark”; this does not make its placeholder
scores model-performance evidence. Cite it as evaluation infrastructure.

The metadata profile is published separately: Behnam Shad, K. *IMM-Core: Interview Metadata Model —
Core Profile* (v1.0, 2026). Zenodo, CC-BY 4.0. DOI
[10.5281/zenodo.20507329](https://doi.org/10.5281/zenodo.20507329).

## Status

Early stage (**v1.0.1**, development draft). The next priorities are:

1. **Real inference**, replacing the stubbed backend, so that scores discriminate between systems.
2. **Independent annotation and agreement analysis.** The reference currently comes from one researcher.

These steps alone would not establish a reliable benchmark. Task validity, separation of reference
answers from model inputs, representative material and uncertainty also need explicit evaluation.

We are sharing the concept and the harness now to invite discussion and refinement with other
oral-history institutes and universities — including on both of the points above.

## Contact

**Klaus Behnam Shad** — Luxembourg Centre for Contemporary and Digital History (C²DH), University
of Luxembourg.

## License

Code and synthetic data are released under the **MIT License** (see [`LICENSE`](./LICENSE)). The
synthetic corpus may be redistributed and adapted under the same terms; it contains no real
personal data.

---

*The controller or joint controllers remain responsible for lawful processing. The DPO advises
and monitors; software checks do not confer permission. See [Governance](docs/GOVERNANCE.md).*
