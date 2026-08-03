# `reports/` — smoke-test output, not model results

**Do not read the files in this directory as measurements of model quality, and do not quote
numbers from them.**

The evaluation harness in this repository currently runs against a **stubbed model backend**:
`MODEL_REGISTRY` holds placeholder entries and `run_model()` returns a deterministic placeholder
(see §5 of `notebooks/cdh_oh_eval_v1.ipynb`). The files here are what that placeholder produces
when it is pushed through the real scoring path.

That is why:

- every field accuracy in `task1_metadata_summary.csv` reads `1.0`;
- `task2_segmentation_summary.csv` reports the same WindowDiff and Pk for every model and every
  language;
- the three model identifiers differ but their rows do not.

Those are properties of the placeholder, not findings about Gemma, Mistral or OLMo.

## Why these files are shipped anyway

The substance of this release is the scoring path: the per-field-type metric design, the
timecode-derived boundary masses, the per-record error handling, the schema validation and the
report writers. All of that is easier to review with its output present than absent — and the
output regenerates deterministically from a clean checkout, which is itself a property worth being
able to check.

## What is in here

| File | What it is |
|---|---|
| `task1_metadata_raw.csv` · `task1_metadata_summary.csv` | Per-field comparison for the metadata task, raw and aggregated per language |
| `task2_segmentation_raw.csv` · `task2_segmentation_summary.csv` · `.tex` | WindowDiff and Pk for the segmentation task, plus a LaTeX table |
| `luxoh_validation_report.csv` · `oh_eval_validation_report.csv` | Schema validation of the synthetic corpus against the two JSON schemas — **these are real results**, they say whether every record validates |

The two validation reports are the exception: they exercise the schemas against the corpus and
their content is meaningful.

## When this notice goes away

When the model backend is wired to real inference. Until then, see the status notes in
[`../README.md`](../README.md) and [`../BENCHMARK_CARD.md`](../BENCHMARK_CARD.md).
