# Benchmark Card — DINOH evaluation benchmark

Scoring logic: `src/oh_eval/metrics.py` · corpus: [`DATA_CARD.md`](./DATA_CARD.md)

## What it measures

Two *narrow, assistive* tasks a computational tool might help with, always
scored against a **human** gold standard. Results are **reported per language
and never pooled**, so strong performance in a high-resource language cannot mask
weak performance in a lower-resourced one.

### Task 1 — Minimal metadata extraction

Per-field comparison, by field type:

- **Exact-match fields** (verbatim string equality): `record_id`,
  `interview_date`, `interviewer`, `language`, `spatial`, `consent_status`,
  `accessRights`. Of these, `consent_status`, `accessRights`, `language` are
  controlled-vocabulary fields.
- **List field** `keywords`: set-based **precision / recall / F1**.
- **Free-text fields** `title`, `abstract`: **not auto-scored.** They are flagged
  `review_required` for manual qualitative review. Auto-scoring free text against
  a human gold is methodologically circular at this stage, so it is deliberately
  excluded rather than approximated by a proxy metric.

### Task 2 — Thematic segmentation

**WindowDiff** and **Pk** (the two standard segmentation metrics, via `segeval`),
computed over **timecode-derived boundary masses on a shared unit axis**: each
segment's end timecode is projected to an offset proportional to its position in
the interview timeline, and gold and prediction are mapped with the *same*
duration so their boundaries are comparable. The document end is a shared
boundary, not a hypothesised one. This measures **boundary placement**, not a
naive segment-count difference.

## Scoring integrity

- A **malformed or missing timecode** in a prediction is recorded as a per-record
  `error`, never silently mis-scored, and never aborts the whole run.
- `segeval` is the single pip-only dependency and degrades gracefully if absent
  (segmentation scores return `None` with a note rather than crashing).
- The scoring logic is extracted from the notebook into a pure, unit-tested
  module, exercised by the test suite (`test_corpus`, `test_export`,
  `test_metrics`, `test_reports`, `test_reports_writers`, `test_schema`) and run
  in CI on Python 3.10 and 3.11.

## Models

The benchmark targets **open-weight** models whose behaviour can be inspected and
reproduced. Model outputs are proposals to be measured — not authoritative
interpretation, which remains a scholarly act.

## Intended use

A **benchmark *infrastructure*** release: a reproducible corpus, schema, scoring
method, and export path on which inter-annotator validation and additional
languages can be layered. It is an invitation to other oral-history projects to
extend it, not a finished model leaderboard.

## Limitations

- **Single-annotator gold standard** — no inter-annotator agreement is reported
  yet. A second-annotator pass on a subset is the next planned step; until then
  this is *not* a definitive benchmark of model quality.
- **Small, synthetic corpus** (n = 28) — see `DATA_CARD.md`.
- **Free text is left to human review by design** — the benchmark does not claim
  to score interpretive quality.
- **OHMS XSD validation** against the official schema is a known follow-up; the
  exporter produces well-formed, escaped OHMS-style XML but is not yet validated
  against the published XSD.
