# Changelog

All notable changes to this repository are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed — public communication and scope (2026-09-13)

- Applied README V3 and aligned it with the separate public OHPIPE experimental preview.
- Corrected OHMS override, WebVTT-title and metadata descriptions in the README, data card,
  exporter docstrings and synthetic viewer. Export and scoring functions are unchanged.
- Added current governance scope and historical-status notices to earlier architecture material.
  Required project reviews precede processing; the controller or joint controllers remain
  responsible, while the DPO advises and monitors. No universal ethics procedure is implied.
- Distinguished the verified v1.0.0 Zenodo archive from later development snapshots; added its
  preferred citation without rewriting the archived release.
- Clarified notebook and dashboard limitations, synthetic-text provenance and the need to exclude
  reference answers from future real-inference inputs. Notebook executable cells, corpus, schemas
  and report data remain unchanged.
- Removed the dashboard's cross-language mean table to match the per-language reporting policy,
  corrected unsupported status/method claims and removed its external font import. Plain score
  tables also avoid an undeclared matplotlib dependency that broke both task pages on a fresh install.


### Changed — provenance of the synthetic transcripts (documentation only, 2026-09-10)

- **`DATA_CARD.md`** now states that the transcript texts were drafted with the assistance of a
  generative language model and edited by the author, and that the segmentation, metadata and
  analytical annotations are the human-authored reference. The earlier wording ("authored by hand
  for testing") described the annotation layer and was imprecise for the transcript text. Two
  interpretation notes were added: scores on model-drafted text describe the scoring path, not model
  performance on real interviews; the Luxembourgish transcripts are not evidence about authentic
  Luxembourgish. **No code, schema, corpus or report file was altered.**

## [1.0.1] — 2026-08-03

### Changed — honest-status pass (documentation only, no code or data changes)

The `v1.0.0` release described this repository as a *benchmark* without stating prominently that
the model backend is stubbed. The disclosure existed only inside the notebook (§5), so the
top-level documentation over-promised. This pass corrects that. **No code, schema, corpus or
report file was altered.**

- **README** now opens with a status notice: the harness has not measured anything yet, everything
  under `reports/` is smoke-test output of the scoring path, and no number from it should be
  quoted. The framing shifts from "benchmark" to "evaluation harness / evaluation infrastructure"
  throughout, and the `Status` section names the two conditions that would make it a benchmark
  (real inference; a second-annotator pass).
- **`BENCHMARK_CARD.md`** renamed in framing to an *Evaluation Card*: same status block at the
  top, plus an explicit "What would make this a benchmark" section. Limitations now lead with
  "no results yet".
- **`DATA_CARD.md`** replaces "Balance: 4 records per language" with "Distribution: evenly
  distributed by language only, not by difficulty, register, speaker profile or content", states
  single-annotator / no inter-annotator agreement in the summary table, and clarifies that seven
  languages are *represented* while multilinguality is not *evaluated* — the synthetic corpus does
  not reproduce deep code-switching, authentic disfluency or dialect variation.
- **`reports/README.md`** added: a warning next to the files themselves, explaining why every
  accuracy reads `1.0`, and noting that the two schema-validation reports are the exception — their
  content is meaningful.
- **README** additionally: notes that the OHMS output is not yet validated against the published
  OHMS XSD and that no connector or tested mapping to an external portal exists; adds the
  `suggested_*` / `selected_*` distinction to "What makes it different"; adds an
  anticipated-question pair on whether the numbers in `reports/` are results.

### Added
- `DATA_CARD.md` — dataset specification for the synthetic evaluation corpus.
- `BENCHMARK_CARD.md` — task, metric, and scoring-integrity specification.
- `CHANGELOG.md`.
- Continuous integration (GitHub Actions): the evaluation-core test suite runs on
  Python 3.10 and 3.11, with a status badge in the README.
- README **"Anticipated questions"** section (synthetic data, governance-engine
  scope, single-annotator framing).

### Changed
- Scoped the reproducibility claim in the README to the public evaluation
  artefacts; full run-manifest enforcement is attributed to the internal pipeline.
- Aligned `pyproject.toml` version with the release version (`1.0.1`), and updated
  `CITATION.cff` (version, release date, and title/abstract wording — the citation
  metadata described a scoring benchmark, which is what propagates to Zenodo).

### Fixed
- Declared `jinja2` as a dependency (required by the LaTeX report writer via
  pandas `Styler.to_latex`). It was previously an implicit environment
  dependency, so the test suite failed on a clean install / in CI.

## [1.0.0] — 2026-07-08

### Added
- Initial **public evaluation release** (synthetic data only).
- Multilingual evaluation harness: per-language metadata extraction
  (exact-match) and thematic segmentation (WindowDiff, Pk) across seven
  languages, over 28 synthetic records.
- Evaluation core (`src/oh_eval`): `corpus`, `schema`, `metrics`, `reports`,
  `export`.
- Access-aware interoperability exporters to **WebVTT** and **OHMS** (default-deny
  allow-list: full text only for `open` + `public`).
- Two JSON schemas, notebook, dashboard, synthetic corpus, and the concept &
  architecture note (`docs/`).
- Archived on Zenodo — concept DOI `10.5281/zenodo.21273366`
  (resolves to the latest version), version DOI `10.5281/zenodo.21273367`.

> **Note added later:** the model backend in this release is stubbed; the files under `reports/`
> are smoke-test output and were never model-performance results. This was disclosed in the
> notebook but not in the release documentation. See the Unreleased section above.

[Unreleased]: https://github.com/klausbehnamshad/DINOH/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/klausbehnamshad/DINOH/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/klausbehnamshad/DINOH/releases/tag/v1.0.0
