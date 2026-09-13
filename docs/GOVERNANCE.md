# Governance and current scope

Status: 13 September 2026. This page describes the scope of the public DINOH Evaluation repository.

DINOH brings together OHPIPE, DINOH Evaluation, the Interview Metadata Model (IMM) and shared
methods. [OHPIPE](https://github.com/klausbehnamshad/ohpipe) is distributed separately as an
experimental transcript-workflow preview. Its release notes and tests define its current scope;
earlier DINOH architecture diagrams do not establish what that preview implements.

## Project responsibilities come before processing

The pipeline is intended for projects whose applicable data-protection, ethics and access
requirements have already been addressed. Before operational processing, the controller or joint
controllers determine the permitted purposes, material, environment, access and outputs, with
ethics review where required and timely DPO involvement as applicable. Responsibilities continue
throughout the project; changed purposes, inputs or outputs may require renewed assessment.

The DPO advises and monitors compliance. The DPO is not a substitute for the controller's
responsibility, and the software neither performs a legal assessment nor grants project or ethics
approval. See the [EDPB explanation of the DPO's role](https://www.edpb.europa.eu/sme/be-compliant/data-protection-officer_en).

Pseudonymisation does not by itself establish anonymity. Titles, metadata, quotations and
interpretive annotations may identify people. A declared access marker, a schema-valid record or
a recorded human decision is not independent evidence that processing or publication is lawful.

## What the evaluation code demonstrates

- The corpus contains 28 synthetic records, four per language across seven languages. Transcript
  texts were drafted with AI assistance and edited by the author; reference annotations were
  authored by one researcher. There is no measured inter-annotator agreement.
- The notebook backend is a placeholder and deliberately receives reference answers for smoke
  testing. Its task scores are not model-performance evidence. A future real-inference experiment
  must separate reference answers from model inputs and validate its methodology independently.
- OHMS includes abstracts and anchor quotations according to declared access/consent metadata
  only when no override is supplied. `allow_fulltext=True` overrides that decision;
  `allow_fulltext=False` omits those fields. Other metadata and titles remain present.
- WebVTT emits supplied record and segment titles regardless of access status and ignores
  `allow_fulltext`. Neither exporter assesses identifying content or authorises publication.
- OHMS XML has not been validated against the official XSD. No tested external-portal connector
  is provided. Provenance and structural conformance do not establish scientific validity.

See the [README](../README.md), [data card](../DATA_CARD.md), [evaluation card](../BENCHMARK_CARD.md)
and [export implementation](../src/oh_eval/export.py) for the corresponding details.

## Historical documents

The older concept note, walkthrough script, terminology inventory, files under `website/` and
`DINOH_architecture_diagram.svg` are retained as historical design material. They include older
names, legal discussion, maturity labels and descriptions of components absent from this repository.
They are not current operating instructions, legal assessments, evidence of model performance or
verified specifications of the separate OHPIPE preview. This scope notice supersedes those uses.

The v1.0.0 Zenodo archive is a separate historical snapshot. These corrections to `main` do not
retroactively change that archive. The [README citation section](../README.md#citation) distinguishes
the archived version from later development commits.
