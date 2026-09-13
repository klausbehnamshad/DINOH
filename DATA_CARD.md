# Data Card — DINOH synthetic evaluation corpus

`data/corpus_synthetic.json` · schema-validated against `schemas/oh_eval_record.schema.json`

## Summary

A small, fully **synthetic** corpus written for methodological testing of an oral-history
assistance pipeline. Its segmentation, metadata and analytical annotations are the human-authored
reference for the DINOH evaluation harness (see [`BENCHMARK_CARD.md`](./BENCHMARK_CARD.md)); the
transcript texts themselves were drafted with AI assistance and edited by the author (see *How it
was produced*). It contains **no real person, testimony, or event**.

| Property | Value |
|---|---|
| Records | **28** |
| Languages | **7** — German (`deu`), English (`eng`), French (`fra`), Italian (`ita`), Spanish (`spa`), Luxembourgish (`ltz`), Portuguese (`por`) |
| Distribution | **4 records per language, exactly** — evenly distributed by language only, not by difficulty, register, speaker profile or content |
| Annotation | **One annotator.** No inter-annotator agreement has been measured |
| Real personal data | **None** — every record is synthetic and marked `synthetic: true` |
| Access markers | All 28: `accessRights = "restricted"`, `consent_status = "research-only"` |
| Language codes | ISO 639-3 |
| License | MIT (see `LICENSE`); redistributable and adaptable |

## Composition

Each record carries a minimal-metadata block (following the **LuxOH Implementation Profile** of
the discipline-agnostic **Interview Metadata Model — Core Profile, IMM-Core**), a synthetic
transcript, a human-authored thematic segmentation, and consent/privacy/provenance blocks.
Fields present per record:

`record_id`, `interview_date`, `interviewer`, `interviewee_display`, `consent_status`,
`accessRights`, `title`, `language`, `spatial`, `keywords`, `abstract`, `transcript`,
`timecoded_segments` (thematic boundaries with labels and an L2 `analytical_annotations`
layer), `interpretive_layer`, `profile_version`, `consent`, `privacy`, `provenance`,
`synthetic`.

## How it was produced

The **transcript texts** were drafted with the assistance of a generative language model and
edited by the author. They are invented texts written for testing; they were not collected from
interviews. The **segmentation, metadata and analytical annotations** were authored by hand by a
single annotator and form the *human reference* against which AI proposals are to be scored. No
model output serves as the reference annotation. This separates human annotations from
model-drafted input texts; it does not rule out bias or contamination associated with those inputs.

Two consequences follow for interpretation. Model-drafted text may be easier for a model to
process than authentic speech, so any score on this corpus describes the scoring path and the
process, not model performance on real interviews. And the Luxembourgish transcripts are invented
text produced with AI assistance; they are not evidence about authentic Luxembourgish or about a
model's competence in it.

## Intended use

- Exercising the *narrow, assistive* pipeline components: minimal metadata extraction and
  thematic segmentation.
- Regression and integrity testing of the scoring path.
- Demonstrating format conversion. The 28 corpus records are all `restricted` + `research-only`.
  Their default OHMS exports omit abstracts and anchor quotations but retain other metadata and
  titles. WebVTT emits record and segment titles regardless of access status. The separately named
  `ILLUSTRATION_open-public` example demonstrates text inclusion on a synthetic record.
  An explicit OHMS `allow_fulltext=True` also enables text inclusion regardless of those markers.
  These examples do not establish a privacy barrier; see [the export scope](README.md#interoperability-webvtt--ohms).

## Out of scope / limitations

- **Not representative** of real oral-history complexity. Synthetic, AI-drafted text does not
  reproduce authentic disfluency, deep code-switching, emotional register, dialect variation, or
  archival messiness. Seven languages are *represented here*; multilinguality is not *evaluated*
  by this corpus.
- **Not a basis for claims about real interviewees or populations.**
- **Small (n = 28)** and **single-annotator** — suitable for method and regression testing, not
  for leaderboard-style model ranking.
- **Even by language, not balanced in any other sense.** Four records per language is a
  construction choice for per-language reporting; it does not mirror real corpus distributions
  and says nothing about difficulty, variety or speaker profile.
- No scores derived from this corpus currently reflect model behaviour — the harness's model
  backend is stubbed. See the status block in `BENCHMARK_CARD.md`.

## Ethics & privacy

The corpus is declared synthetic and is distributed under MIT. Real interview processing is
outside this evaluation repository's scope. Applicable project reviews precede processing;
the controller or joint controllers remain responsible, with the DPO advising and monitoring.
No software result establishes authorisation or anonymity. See [Governance](docs/GOVERNANCE.md).
