# Evaluation Card — DINOH evaluation harness

Scoring logic: `src/oh_eval/metrics.py` · corpus: [`DATA_CARD.md`](./DATA_CARD.md)

> ## Status: this harness has not measured anything yet
>
> The model backend is **stubbed**. `MODEL_REGISTRY` holds placeholder entries and
> `run_model()` returns a deterministic placeholder, so the downstream evaluation logic can be
> exercised end to end without a compute connection. **The task scores in `reports/` are
> smoke-test output, not model-performance evidence.** The schema-validation reports separately
> describe record conformance. Every task-field accuracy reads 1.0 and every WindowDiff is constant across models and languages. Real
> inference is wired in when the compute path is provisioned.
>
> What is real and tested today: the corpus, the schemas, the metric design, the scoring
> integrity rules and the export path. **This release makes measurement possible. It does not
> report measurements.**
>
> Please do not cite this as a benchmark of model quality or quote its task scores as model results.

## What it is for

Two *narrow, assistive* tasks a computational tool might help with, always scored against a
**human** gold standard. Results are designed to be **reported per language and never pooled**,
so strong performance in a high-resource language cannot mask weak performance in a
lower-resourced one.

### Task 1 — Minimal metadata extraction

Per-field comparison, by field type:

- **Exact-match fields** (verbatim string equality): `record_id`, `interview_date`,
  `interviewer`, `language`, `spatial`, `consent_status`, `accessRights`. Of these,
  `consent_status`, `accessRights`, `language` are controlled-vocabulary fields.
- **List field** `keywords`: set-based **precision / recall / F1**.
- **Free-text fields** `title`, `abstract`: **not auto-scored.** They are flagged
  `review_required` for manual qualitative review. This harness has no validated automatic
  scoring rule for these fields; text similarity alone would not establish descriptive adequacy
  or interpretive validity.

### Task 2 — Thematic segmentation

**WindowDiff** and **Pk** (via `segeval`), computed over **timecode-derived boundary masses on
a shared unit axis**: each segment's end timecode is projected to an offset proportional to its
position in the interview timeline, and gold and prediction are mapped with the *same* duration
so their boundaries are comparable. The document end is a shared boundary, not a hypothesised
one. This measures **boundary placement**, not a naive segment-count difference.

## Scoring integrity

- A **malformed or missing timecode** in a prediction is recorded as a per-record `error`,
  never silently mis-scored, and never aborts the whole run.
- `segeval` is the single pip-only dependency and degrades gracefully if absent (segmentation
  scores return `None` with a note rather than crashing).
- The scoring logic is extracted from the notebook into a pure, unit-tested module, exercised
  by the test suite (`test_corpus`, `test_export`, `test_metrics`, `test_reports`,
  `test_reports_writers`, `test_schema`) and run in CI on Python 3.10 and 3.11.

## Models

The harness targets **open-weight** models whose behaviour can be inspected and reproduced.
Model outputs are proposals to be measured — not authoritative interpretation, which remains a
scholarly act. The proposal/selection distinction is structural: model output is carried as
`suggested_*`, curated values as `selected_*`, and the two stay distinguishable even when the
values are identical, because they carry different epistemic status.

## Intended use

A release of **evaluation infrastructure**: a reproducible corpus, schema, scoring method and
export path on which inter-annotator validation, real inference and additional languages can be
layered. It is an invitation to other oral-history projects to extend it — not a model
leaderboard, and not yet a comparative measurement.

## Limitations

- **No results yet** — the model backend is stubbed; see the status block above.
- **Single-annotator gold standard** — no inter-annotator agreement is reported. A
  second-annotator pass on a subset is the next planned step. Until both that and real
  inference are in place, this cannot rank model quality.
- **Small, synthetic corpus** (n = 28) — see `DATA_CARD.md`.
- **Seven languages are represented; multilinguality is not evaluated.** The corpus does not
  reproduce deep code-switching, authentic disfluency or dialect variation.
- **Free text is left to human review by design** — the harness does not claim to score
  interpretive quality.
- **OHMS XSD validation** against the official schema is a known follow-up; the exporter
  produces well-formed, escaped OHMS-style XML but is not yet validated against the published
  XSD. There is no connector or tested mapping to any external portal.

## Next validation steps

Two immediate priorities remain open:

1. **Real inference**, replacing the stubbed backend, so that scores discriminate between
   systems.
2. **Independent annotation and agreement analysis** on a documented sample.

These steps alone do not establish benchmark validity. A future experiment also needs justified
tasks, representative material, uncertainty reporting and separation of reference answers from
model inputs. The current placeholder deliberately receives the gold record; that smoke-test
arrangement must not be reused as a real model-evaluation protocol.

Until then the honest description is: *an evaluation harness with a human gold standard, a
schema-bound metric design and a tested scoring path.*
