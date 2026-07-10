# Changelog

All notable changes to this repository are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- Aligned `pyproject.toml` version with the release version (`1.0.0`).

### Fixed
- Declared `jinja2` as a dependency (required by the LaTeX report writer via
  pandas `Styler.to_latex`). It was previously an implicit environment
  dependency, so the test suite failed on a clean install / in CI.

## [1.0.0] — 2026-07-08

### Added
- Initial **public evaluation release** (synthetic data only).
- Multilingual evaluation benchmark: per-language metadata extraction
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

[Unreleased]: https://github.com/klausbehnamshad/DINOH/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/klausbehnamshad/DINOH/releases/tag/v1.0.0
