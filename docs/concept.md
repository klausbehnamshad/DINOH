# DINOH Evaluation — purpose and scope

DINOH is a research infrastructure bringing together OHPIPE, DINOH Evaluation, the Interview
Metadata Model (IMM) and shared methods for oral-history research. This repository contains the
evaluation component; [OHPIPE](https://github.com/klausbehnamshad/ohpipe) is a separate experimental
transcript-workflow preview.

DINOH Evaluation makes a scoring procedure inspectable using 28 synthetic records in seven
languages. The transcript texts were drafted with AI assistance and edited by the author; a
single researcher supplied the reference annotations. The notebook uses a placeholder backend
that deliberately receives reference answers for smoke testing. No real model inference or
model-performance comparison is reported.

The two tasks are descriptive metadata comparison and thematic boundary comparison. Controlled
fields use exact matching, keyword lists use set precision/recall/F1, and title/abstract fields
are flagged for human review. Segmentation uses WindowDiff and Pk. Language-specific reporting
helps make variation visible; representation of seven languages does not establish performance
on authentic multilingual interviews.

The export functions demonstrate WebVTT and OHMS-style conversion. Supplied metadata, including
titles, may identify people; access markers and an optional override do not establish permission
to publish. See [Governance and current scope](GOVERNANCE.md) for the exact boundary and the roles
of the controller or joint controllers and the DPO.

Independent annotation, real inference with reference answers excluded from model inputs,
representative material and a justified evaluation protocol remain future work. Provenance and
successful software tests alone do not establish scientific validity.

The older architecture note and diagrams are retained as historical design documents with
status notices. For current usage, limitations and citation, start with the [README](../README.md),
[data card](../DATA_CARD.md) and [evaluation card](../BENCHMARK_CARD.md).
