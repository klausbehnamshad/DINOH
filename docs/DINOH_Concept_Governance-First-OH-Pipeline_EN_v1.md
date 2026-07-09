<!--
  DINOH — A Governance-First Pipeline for AI-Assisted Oral History
  Concept & Architecture · English · v1 (2026-07-01)
  C²DH, University of Luxembourg. Prepared for publication (DINOH web presence /
  "Digital Infrastructure & Methods"). Register: layered public → methods → governance,
  written to remain scientifically citable. Not legal advice.
  Fact-check corrections (2026-07-01): the data model is described with its two-level vocabulary — the discipline-agnostic Interview Metadata Model (IMM-Core) and its LuxOH Implementation Profile (schema `luxoh_minimal_metadata`); the §15 reference carries the exact Zenodo deposit title. The pseudonymisation baseline (§2) is caveated with the SRB / EDPS line (Gen. Court T-557/20; CJEU C-413/23 P, EDPS v SRB, 4 Sept 2025), scoped to downstream recipients since the controller retains the re-identification means. Code identifiers (`luxoh_minimal_metadata`) are unchanged — they denote the LuxOH profile and are load-bearing for manifest-recompute hashes.
-->

# DINOH — A Governance-First Pipeline for AI-Assisted Oral History

### Concept & Architecture

**Project:** DINOH — *Digital Infrastructure for Oral History* · Luxembourg Centre for Contemporary and Digital History (C²DH), University of Luxembourg
**Document:** Concept & architecture note, version 1 (2026-07-01) · English
**Register:** A single document written on two levels — a plain-language account for a general and institutional audience, and a methods-and-governance specification precise enough to cite. Technical identifiers are given verbatim where they matter for reproducibility.

> **Communication rule for the whole document — *enforces · verifies · decides*.** The system *enforces* technical and accountability duties and *verifies* the evidence attached to a run. Whether an interview is lawful to process, whether a text is truly anonymous, and whether an output may be released remain **human decisions**. Nothing below should be read as the software adjudicating law or truth.

> **Not legal advice.** Legal references (GDPR, the Luxembourg Law of 1 August 2018, CNPD guidance, CJEU case law) are cited as the governance frame the pipeline is designed *around*. Lawfulness, the necessity of a data-protection impact assessment, and any release are determined by the **controller** and advised by the **Data Protection Officer (DPO)** — not by this pipeline and not by its author.

> **Scope of this public repository — design, not enforced here.** This repository ships the **evaluation core** (the multilingual benchmark on synthetic data), this **concept & architecture note**, and the interoperability exporters (WebVTT / OHMS). The **governance / enforcement engine** described below — the default-deny gates, attestation, run manifests, BIND / ACCOUNT (Article-9 inference), quarantine review, controller-release and withdrawal machinery — is documented here as **design**. Its implementation is **not included in, and not executed by, this public repository**; it is part of the internal DINOH pipeline. Where the text says the engine "enforces", "checks", "rejects", or "re-routes", that describes that internal design — not a capability shipped in this repo.

---

## Maturity legend (used throughout)

Every capability in this document carries an honest maturity label. We never draw target capability as if it were built.

| Label | Meaning |
|---|---|
| **Implemented** | Committed code, exercised by the test suite, runs on synthetic/fixture data. |
| **Validated** | Implemented *and* checked against an explicit adversarial or gold reference (e.g. red-team tests, a hand-made gold standard). |
| **Specified** | Designed and written down (schema, plan, tested scaffold) but **not yet wired** into the live run path. |
| **Planned** | Scoped as a next step; not yet specified in executable form. |

A recurring, load-bearing distinction in this project is between a *tested module* and an *operational workflow*: some components (for example withdrawal propagation, and the human output review) exist as **specified**, test-covered code but are deliberately **not yet part of the enforced run path**. Saying so plainly is part of the method.

---

## 1. Abstract

DINOH studies recorded life stories from across the borders of the Greater Region. Working with such testimony computationally raises a problem that transcription accuracy alone never solves: how to analyse deeply personal narratives in a way that is faithful to the speakers, defensible under European and Luxembourg data-protection law, and transparent enough to be scholarship rather than a black box.

This document describes the pipeline built to meet that problem. Its central design choice is **governance-first**: the machinery is a sequence of checkpoints whose default answer is *no*. Material moves forward only when consent covers the intended use, the processing route keeps data inside the permitted (local / EU) boundary, an interpretive claim can point to the exact passage it rests on, and a human — not a model — signs the release. The engine's job is to be **honest about what it sees and to stop**; a person's job is to decide.

Three properties distinguish the system from a generic "AI-for-transcripts" tool. First, **the pipeline does not begin at audio**. Audio and video are the epistemic source, but transcription is upstream; the enforced engine operates on *text and coded analysis objects* whose provenance it records. Second, **interpretation is treated as data that can itself become sensitive**: coding an interview can *produce* special-category (Article 9) personal data even when the raw sentence looked innocuous, so the pipeline makes that inference visible and routes it to a human. Third, **every refusal is auditable**: each "no" is a fixed reason code, every run is hashed into a manifest, and the release claim is *recomputed rather than trusted*.

The system is real code at mixed, honestly-labelled maturity. The entry gates, the evidence-binding layer (BIND), the sensitivity-inference layer (ACCOUNT) with same-run enforcement *on the wired downstream path*, the release evaluation, and the hash-chained run manifest are **implemented** and test-covered. Two *separate* measurement harnesses are kept apart: a multilingual **task-quality benchmark** scores AI-*suggested* metadata and thematic segmentation against a human gold standard (per language, never pooled), while a **privacy harness** measures de-identification (direct-PII) recall on synthetic data. They answer different questions and are not the same benchmark. What the pipeline does *not* do — decide anonymity, choose a lawful basis, complete an impact assessment, or authorise release — is left, by design, to accountable people.

---

## 2. Why oral history needs a governance-first pipeline

Oral history sits on a careful relationship between a testimony and the person who interprets it. That relationship is exactly what naïve automation erodes. Three stakes are in tension, and the pipeline exists to hold them together rather than trade one for another.

**The epistemic stake.** A recording carries meaning that a transcript flattens: pauses, emphasis, hesitation, the situation of the conversation, code-switching between languages. Transcription is therefore never neutral — it is already interpretation (what counts as a word, how dialect or Luxembourgish or overlap or uncertainty is marked). The pipeline does not pretend otherwise. It keeps the recording epistemically central while treating each transcript as a *versioned, provenanced document* rather than as raw ground truth.

**The legal stake.** Under the GDPR the decisive line is not "open versus published" but **anonymous versus personal**. Pseudonymised or de-identified interviews *remain personal data* if a person can still be singled out by reasonably likely means (Recital 26; Art. 4(5)). The *SRB / EDPS* line (General Court T-557/20, *SRB v EDPS*; on appeal CJEU C-413/23 P, *EDPS v SRB*, 4 Sept 2025) makes identifiability recipient-relative — but in the DINOH controller setting the institution retains the re-identification means (keys, originals), so the baseline holds *for the controller*; SRB bears on a downstream recipient that lacks those means. Identifiability therefore remains a controller determination, not a tool output. The institution is the **controller** and must be able to *demonstrate* compliance (Art. 24; Art. 5(2)) — it cannot offload that to a tool or to an individual researcher. In Luxembourg this bites harder than elsewhere: the CNPD lists scientific/historical/statistical research on personal data on its **DPIA-obligation list** (Point 6, "as required in Article 65" of the Law of 1 August 2018; Deliberation 34/2019) — the listing is *independent of a high-risk screening and applies even to purely local processing*. This governance design therefore treats such processing as DPIA-listed by default; whether a DPIA is in fact required for a concrete project remains a controller/DPO determination, not a ruling made by the pipeline.

**The interpretive-sensitivity stake.** This is the subtle one, and it is where most tooling fails silently. Qualitative coding can *derive* protected information. A code such as "mentions the union" is, in law, an inference toward trade-union membership — a special category under Article 9 — even though the underlying sentence contained no protected term. The CJEU has read Article 9 broadly enough to cover data from which sensitive information can be *deduced* (Case C-184/20). It follows that the analytical layer is not a safe zone downstream of privacy control; it is a **generator** of sensitive personal data and must be governed as such.

A pipeline that honoured only the first stake would be a transcription toy. One that honoured only the second would be a compliance checklist. DINOH's argument is that credible computational oral history requires all three to be enforced *in the same run*, with the evidence to prove it after the fact.

---

## 3. Design principles

Six principles recur across every stage and explain why the architecture looks the way it does.

**Default-deny.** When a prerequisite is missing, ambiguous, or unverifiable, the pipeline refuses and records why. Unknown consent is treated exactly like withdrawn consent. "Technically possible to process" is never allowed to masquerade as "permitted to process."

**Enforce and verify, but do not decide.** The system enforces machine-checkable constraints (schema validity, processing route, evidence binding) and verifies references, status fields and hashes. It stops short of the judgements that belong to people: anonymity (Recital 26 is a human call), lawful basis, DPIA necessity, and release.

**Recompute, don't trust.** Claims attached to a run are not believed because they are asserted. The manifest validator re-derives the sensitive-inference result from the stored analysis object against the pinned catalogue and rejects a run whose release claim does not reproduce. Integrity is checked by recomputation and hashing, not by good faith.

**Builder ≠ approver.** The person who builds the pipeline is not the person who approves the processing it performs. The role boundary is explicit and deliberate: the controller decides (Art. 24), the DPO advises and monitors (Art. 39), researchers interpret, and the operator builds the technical gates.

**Special category by default.** Oral-history material is treated as *potentially* special-category unless a human determines otherwise. Life stories routinely touch health, belief, politics, ethnicity, migration and trauma; a voice is personal data and can become *biometric* special-category data if processed to identify a speaker (e.g. diarization). The conservative default is the safe one.

**Honest maturity.** Capability is labelled (implemented / validated / specified / planned) everywhere, and a tested module is never described as an operational workflow. Under-claiming is preferred to over-claiming — including in public and funder-facing materials.

---

## 4. System overview: four elements, one shared core

DINOH is organised as **four elements** over one code core. The old habit of numbering them A–D implied a sequence that contradicts the real data flow (the entry gate runs *before* the analysis engine), so the elements are named, not numbered.

| Element (short · long) | Role | Maturity |
|---|---|---|
| **Admission** — *Data Admission & Governance* | Entry layer: traffic-light classification of a dataset plus default-deny gates on every record. | **Implemented** |
| **Analysis** — *Analysis Workflow* | Qualitative content-analysis engine: text/record ingest → segmentation → coding → evaluation → controlled export with a manifest. Coding is by a human or a *declared* model; the demonstration coder is a transparent rule-based analyzer (no model inference). | **Implemented** for ingest, the transparent demo analysis, and downstream governance over prepared analysis objects; a **full local-model analysis service is planned**. |
| **Benchmark** — *Evaluation & Benchmarking* | Offline harness over a synthetic gold corpus; measures de-identification recall and segmentation quality — **not** the quality of historical interpretation. | **Validated (Stage 1)** |
| **Provenance** — *Interpretive Provenance & Accountability* | Cross-cutting layer over coded interpretations: bind evidence (BIND), infer sensitivity (ACCOUNT), and — planned — measure inter-coder reliability (ADJUDICATE). | **Emerging** (BIND validated; ACCOUNT implemented, partial; ADJUDICATE planned) |

The corrected end-to-end flow — with the three fixes this document insists on marked `[fix]` — is:

```
             ┌─ UPSTREAM (epistemic source; not the enforced engine) ─┐
  Audio / Video
      → Local transcription (Whisper / LuxASR / manual)   [fix: upstream, not the current engine]
      → Transcript / pipeline record (text + provenance + status metadata)
             └───────────────────────────────────────────────────────┘
      → Run-level ATTESTATION            (checked first)
      → Default-deny GATES               (G1 schema · G2 consent/purpose/embargo · G3 route/privacy)
      → run_context (B0)                 (the run anchor: one run_id binds all later artefacts)
      → CODING / analysis object         [fix: coding precedes BIND & ACCOUNT]
      → BIND                             (every claim bound to a span + codebook)
      → ACCOUNT                          (coding → Article-9 inference against a pinned catalogue)
      → SAME-RUN enforcement             (recompute the release subject; reject downgrade/suppression)
      → Quarantine REVIEW                (human-checked basis for release — TOM #11)
      → Controller RELEASE decision      [fix: release = review + human decision + revalidation, not "export"]
      → Release state                    (released / held / redaction-required / superseded / uncovered)
      → run_manifest 0.3.1               (hash-chained audit document; status: completed / quarantined / refused-admission)
      → Audit trail                      (later reconstructable: what · which version · which decisions · why)
      → Withdrawal / erasure             (tombstone + propagation to derivatives)   [specified scaffold, not yet wired]
      → Export / archive store           (only if released)
```

Two orthogonal axes cut across this flow and must never be conflated (Section 5): a **traffic light** for *data sensitivity*, and a set of **gates** for *mechanical admission*.

---

## 5. Two orthogonal axes: the traffic light and the gates

A frequent source of confusion in privacy tooling is collapsing "how sensitive is this dataset?" into "did the checks pass?" DINOH keeps them as separate axes.

### 5.1 The traffic light — data sensitivity (a human classification)

Each candidate dataset receives a provisional colour. The colour steers the *process*; it is not the software's ruling on legal status.

- 🟢 **Green — evidenced anonymous.** Eligible only after a documented human anonymity determination under Recital 26: a signed proof (referenced by hash in the run) plus controller sign-off, with the DPO informed. The gate verifies that the referenced evidence exists and matches its hash; it does **not** rule that the text is truly anonymous. Rare for real interviews — realistic mainly for synthetic data or non-interview open text.
- 🟡 **Yellow — pseudonymised / still personal.** Where most "anonymised" interview corpora actually sit. Requires a class-DPIA, a written DPO opinion, and a controller release on a named lawful basis (Art. 6; where special categories appear, an Art. 9 basis/derogation plus Art. 89 research safeguards), with conscious acceptance of residual re-identification and transparency risk — plus local-only processing and operational output quarantine before any run.
- 🔴 **Red — set aside.** Minors; own/again-restricted collections; health, religion, sexuality, migration status, trauma; small identifiable communities; restricted archives without explicit reuse/LLM permission. No generic pipeline use — only a bespoke, project-specific approval with an explicit controller decision and DPO involvement. Currently **parked entirely**.

### 5.2 The gates — mechanical default-deny (what the machine checks)

Orthogonally, every run passes through checks whose default is refusal. The order in code is fixed, and there is **no "G4"** — attestation is run-level and runs *first*.

- **Attestation gate** — run-level, checked first (declares route, purpose, wording; carries an evidence path + hash).
- **G1** — schema validity of each record.
- **G2** — consent, embargo, purpose admissibility.
- **G3** — processing route *and* privacy-status clearance.

Every failure emits a fixed, auditable **reason code** (the engine defines a closed vocabulary of them; Section 6.4 lists the load-bearing ones). Crucially, "passes the gate" ≠ "is legally green": the gate proves that *machine-checkable prerequisites* are present, which is necessary but never sufficient for lawful processing.

## 6. The pipeline, stage by stage

Each stage is given on two levels: *in plain words*, and *under the hood* with the real identifiers that live in the schemas, tests and provenance hashes. Where a stage corrects a common mis-drawing of the architecture, the correction is called out.

### 6.1 Upstream — audio/video and transcription (the source, not the current engine)

**In plain words.** An interview begins as a recording. That recording is the epistemically primary object; everything downstream is a representation of it.

**Under the hood.** *This is the first correction the diagram needs.* Audio and video are the **source**, and transcription — with Whisper, a Luxembourgish ASR service, or by hand — sits **upstream of, or beside,** the enforced engine. The committed pipeline does not transcribe live audio; it operates on *text or an already-coded analysis object* and records where each transcript came from. Transcription is therefore handled as a **provenance question**, not a processing step: which transcript version, which content hash, which ASR model and version, whether it was human-corrected or human-verified. A separate data-protection review of the local-AI stack (Section 9) treats model *provisioning* (one-time, personal-data-free weight download) as distinct from *processing* (inference on interview data, which must be egress-free), precisely so that "locally stored" is defensible for tools such as Whisper.

**Why it matters for the humanities.** The recording stays central to meaning, but the technical engine begins the moment a text or analytical form exists — and it inherits, rather than hides, the interpretive choices already made in transcription.

### 6.2 Ingest — the pipeline record

**In plain words.** A transcript enters the pipeline as a structured record: not "raw text," but text plus the metadata that makes it governable.

**Under the hood.** The unit of ingest is an `oh_pipeline_record`: transcript text together with language, date, source, consent status, privacy status, provenance and a transcript hash. In the demonstration surface the file is read *in memory only* — nothing is written to disk or sent anywhere. Validation is layered: the institutional minimum follows the **LuxOH Implementation Profile** of the openly published **Interview Metadata Model (IMM-Core)** (see Section 12), and the evaluation contract (`oh_eval_record`) supersets it with stricter nested requirements.

**Why it matters.** The transcript is admitted as a *research- and data-protection-relevant document with a purpose binding*, not as free-floating text — the precondition for everything that follows.

### 6.3 Attestation — the run's self-declaration (checked first)

**In plain words.** Before anything is processed, the run must declare the conditions under which it operates — and then live up to them.

**Under the hood.** An attestation states purpose (analysis / benchmark / research), route (`local-eu-model`, `human-only`), the absence of any external API or third-country transfer, non-use for training, and the DPO-pinned wording that applies. This is not a form the engine takes on faith: it compares hashes and exact wording, and if the attestation is missing or inconsistent the run is refused with a precise code — `attestation-missing`, `attestation-route-mismatch`, `attestation-purpose-mismatch`, `attestation-wording-mismatch`, `attestation-hash-mismatch`, or `attestation-fixture-on-real-data`. Attestation is **run-level and runs first** (there is no "G4").

**Why it matters.** Attestation is the technical form of *"I declare what I am doing, and the code holds me to being coherent about it."*

### 6.4 The default-deny gates — the consent-and-lawfulness checkpoint

**In plain words.** The gate does not ask "can we process this?" It asks "may we admit *this record*, for *this purpose*, into *this run*?" — and if anything is unclear, it refuses and says why.

**Under the hood.** The committed engine `run_gates` runs G1 (schema), G2 (consent + purpose + embargo), and G3 (processing route versus the EU-only policy, plus privacy-status clearance). Consent is default-deny: unknown is treated as withdrawn. The processing-route allow-list is load-bearing — `hosted-llm` was struck (2026-06-10) and is a **default-deny** block in the generic route (code-hard, not merely wording-dependent; overridable only by explicit reconfiguration, which re-triggers the processor/transfer checks), which by design makes third-country-transfer and processor questions moot for the generic route. Privacy status must be *earned*, not asserted: `privacy.status = cleared` requires audit and free-text-review references, or the gate emits `privacy-status-unearned` / `privacy-freetext-review-missing`.

The reason-code vocabulary is closed and auditable. The load-bearing codes:

| Category | Representative reason codes |
|---|---|
| Schema / encoding | `schema-invalid`, `utf-8` |
| Consent / purpose / embargo | `consent-withdrawn`, `consent-unknown`, `purpose-mismatch`, `embargo-active` |
| Route / transfer | `route-policy-disallowed`, `route-undeclared`, `route-dpa-missing`, `route-subprocessor-not-allowed`, `route-zero-retention-missing`, `hosted-llm` |
| Privacy status | `privacy-status-missing`, `privacy-status-not-cleared`, `privacy-status-unearned`, `privacy-freetext-review-missing` |
| Anonymity evidence | `anonymity-evidence-mismatch`, `anonymity-evidence-unresolved` |
| Attestation | `attestation-missing`, `attestation-invalid`, `attestation-incomplete`, `attestation-route-mismatch`, `attestation-purpose-mismatch`, `attestation-wording-mismatch`, `attestation-hash-mismatch`, `attestation-fixture-on-real-data` |
| Scope locks | `own-data-b-refused`, `codebook-anchor-own-data`, `non-overridable-code` |

**Why it matters.** The gate is a *methodological brake*. It prevents "practically available" from being mistaken for "usable in research and in law," and it converts every refusal into a citable, machine-readable fact.

### 6.5 run_context (B0) — the run anchor

**In plain words.** Everything a run produces must demonstrably belong to *that* run.

**Under the hood.** `run_context` mints a `run_id` and binds later artefacts (review, decision, manifest) to the same run. The manifest carries a `run_context_ref` (path + hash + schema version) so that a reviewer, a decision and a release cannot be silently stitched together from different contexts.

**Why it matters.** This is the archival signature of a processing act. It is not the document alone that counts, but the concrete *run context* it belongs to.

### 6.6 Coding — the analysis object

**In plain words.** The interview is broken into units and, for each, we note what it is *about*, how it is framed, the rhetorical move, and the speaker's discursive position — the close reading an oral historian already performs, made explicit and consistent.

**Under the hood.** *This is the second correction: coding precedes BIND and ACCOUNT.* An `oh_analysis_object` is already a coding of a record. Per unit it can carry topic, frame, rhetorical form, discursive position, a confidence value, time anchors or character spans, and coder information (human / LLM / rule-based). Topic and frame are kept as **separate dimensions** — a pilot finding was that they often pull apart, and that disagreement is a data point, not an error. In the public demonstration this layer is a **transparent, rule-based illustration over the project's real controlled vocabulary** — deliberately *no black-box model* — whereas in real use the coding comes from human annotators or a declared model.

**Why it matters.** This is the interpretive core, and the pipeline is careful about what it claims: it does not decide the "truth" of an interview. It *manages and checks* codings as scholarly assertions with provenance.

### 6.7 BIND — every claim points to its evidence

**In plain words.** An interpretation is admissible only if it is anchored to the exact passage it came from and stays within the agreed vocabulary. No free-floating claims.

**Under the hood.** The committed engine `run_bind` checks that each coding has a **span** (timecode or character range) and that each code is **in the codebook, per dimension** (topic is not silently mixed with frame). Violations are real codes: `claim-span-unbound`, `code-out-of-codebook`. Scope and side-channel guards refuse codings of own-data/minors and reject codebook anchors drawn from a locked data region (`involves-minors-refused`, `codebook-anchor-own-data`). Maturity: **validated**.

**Why it matters.** BIND is the executable answer to *"where in the material does this rest?"* and *"is this code even allowed here?"* It forces interpretation to be citable and locatable — the precondition of accountable close reading.

### 6.8 ACCOUNT — catching hidden special-category data (Article 9)

**In plain words.** Some codings look harmless but quietly reveal protected information — health, belief, political opinion, ethnicity, trade-union membership. The pipeline flags these so a person looks before anything is shared.

**Under the hood.** The committed engine annotates an Article-9 inference for each coding checked against an **approved, hash-pinned sensitivity catalogue** (`code_sensitivity_catalog`). It writes an `art9_inference` **only on a real, controller-approved catalogue hit** (`tag_source = sensitivity_catalog`). The decisive subtlety: **the absence of a tag does not mean "cleared."** An unmatched coding is `pending` review, not green — the honest states include `clear-no-rule` (no catalogue rule applied) rather than a false all-clear, and the engine rejects malformed or stale inferences (`malformed-art9-inference`, `stale-art9-inference`, `unsupported-tag-source`). Maturity: **implemented (partial; a B-series of increments is in progress)**.

**Why it matters.** ACCOUNT makes visible that *interpretation itself can generate* personal — even special-category — data. It is not only the raw text that is sensitive; the analytical coding can become sensitive, which is exactly the reading of Article 9 that the CJEU adopted in C-184/20.

### 6.9 SAME-RUN enforcement — recompute, don't trust

**In plain words.** Sensitive interpretation that appears in the analysis object cannot quietly vanish at release time.

**Under the hood.** This is one of the strongest properties of the current architecture. If a release subject claims to come from ACCOUNT, the manifest validator requires it to be **recomputable from the same run, the same stored analysis object, and the same pinned catalogue**. It closes two failure classes: **T1 downgrade** (a weaker or divergent subject is presented — caught because the recomputation from the persisted run object does not match) and **T0 suppression** (a required Article-9 subject is missing entirely — caught by a completeness check over every Article-9 unit the recomputation produces). The validator therefore *recomputes* the release claim rather than believing it; a ref-consistent but ACCOUNT-false subject is rejected. **Scope, stated precisely:** this enforcement is active on the wired downstream path (`run_downstream`) and fires *whenever a run carries an `account` block* — the manifest validator recomputes ACCOUNT-derived release subjects only when that block is present, so legacy or headless CLI-built release manifests without an account block are not yet covered (the standalone manifest builder still notes that the ACCOUNT→release derivation is not engine-forced on that path). Maturity: **implemented in the account-bearing `run_downstream` path** (committed as ACCOUNT "Option B" increments: same-run recompute, then completeness / T0-suppression, with T0/T1 proven in `tests/test_downstream_e2e.py`); **global coverage across every manifest path is specified**, not yet universal.

**Why it matters.** It guarantees that the governance of interpretation is not merely decorative: what the analysis made sensitive stays visible through to the release decision.

### 6.10 Quarantine review — the human-checked basis for release

**In plain words.** Nothing a machine flags is auto-resolved. A person reviews the outputs before release is even considered.

**Under the hood.** A `quarantine_review` artefact gathers the checked outputs, findings, a re-identification check and the release-subject references, cross-bound to the manifest by the same `run_context_ref` and attestation. It is the *basis* for release, not the release itself. This is technical-and-organisational measure **TOM #11**. Honest maturity: the **gate-hook and input free-text review exist; the full operational output-review workflow is not yet live** — so in its current state it *blocks* every yellow run rather than releasing it. Saying this plainly matters more than a green light.

**Why it matters.** It is a curated inspection protocol: what is up for release, which risks were seen, what remains open, which subjects are affected.

### 6.11 Controller release decision — the four-eyes act

**In plain words.** The institution — not the researcher, not the tool — makes the final release decision, and it takes two people.

**Under the hood.** *This is the third correction: release is not "export to a store."* A `controller_release_decision` (release / hold / redact) feeds the committed `evaluate_release` engine and must correspond to the specific review, the specific output and the specific subjects, under a four-eyes principle (reviewer ≠ controller). In the public demonstration the release *engine* runs live on committed code inside a throwaway directory; the controller's *decision* is clearly marked as prepared/synthetic — the engine is real, the institutional act is not simulated as if it were genuine.

**Why it matters.** The pipeline does not replace responsibility; it forces responsibility to be exercised in a documented, technically consistent way.

### 6.12 Release states — a controlled threshold, not a button

**In plain words.** "Released" is a state reached after scrutiny, not an export command.

**Under the hood.** `evaluate_release` reports per-output states — `released`, `superseded`, `uncovered`, `held`, `redaction-required` — with reason codes such as `release-output-held`, `release-output-uncovered`, `release-output-redaction-required`, and a lineage guard `release-superseded-output-still-released`. If anything is held or uncovered, the run does **not** go green: it becomes `quarantined`.

**Why it matters.** Release is a controlled threshold between research analysis and any onward sharing, export or archival — a decision surface, not a toggle.

### 6.13 run_manifest 0.3.1 — the computable audit document

**In plain words.** Each run produces one document that proves what happened.

**Under the hood.** `MANIFEST_VERSION = "0.3.1"`. The manifest records the run id; the git commit and dirty status; a corpus hash; schema hashes; the gate-report hash and BIND-report hash; a release block; an (additive) account block with the pinned catalogue reference; inputs/outputs; and an overall `run_status` of `completed`, `quarantined`, or `refused-admission`. The validator does **not** trust the manifest — it recomputes hashes and release consistency (Section 6.9). Version lineage is explicit: 0.3.0 added the run-context reference, the release block and the `quarantined` status; 0.3.1 added the optional, additive account block (the same-run ACCOUNT recomputation of Section 6.9 fires only when this block is present).

**Why it matters.** The manifest is not documentation written after the fact; it is a **computationally verifiable research record**.

### 6.14 Audit trail — reconstructable accountability

**In plain words.** Later, one can reconstruct the whole story of a run.

**Under the hood.** From the manifest and its referenced artefacts one can recover which record and version was processed, under which schemas, with which gate decisions, which coding, which catalogue, which review, which controller decision, which output, and why it was released or quarantined.

**Why it matters.** This is methodological transparency plus accountability. It does not claim *truth* — it guarantees *traceability*.

### 6.15 Withdrawal and erasure — governance that reaches derivatives

**In plain words.** If a person withdraws, it is not enough to change the original file; the derivatives must be addressed too.

**Under the hood.** A specified module implements a five-step withdrawal propagation (Art. 17): a **tombstone** copy of the record (free-text content removed, structure kept so the record stays schema-valid and countable, `consent.status = withdrawn` so G2 refuses all future runs); **crypto-shredding** of the pseudonym-mapping key; a **manifest scan** for every affected run; a **hash-chained propagation log** (tampering with any entry breaks the chain); and a **proof reference** from the record to that log. Honest maturity and honest limits: this is a **specified, test-covered scaffold that `run_gates` does not yet call** — it must be wired as a run hook before yellow processing — and it *cannot* recall already-published aggregates or quotes, nor provider-side caches where zero-retention is not secured. Those belong in the consent text, not in code.

**Why it matters.** Research data is not static. Rights and governance can act back on the corpus after the fact, and the system is built to make that propagation *provable* rather than merely promised.

## 7. Interpretation as personal data — the pseudonymisation stream

Running parallel to the coding layer is a data-protection work-stream for the text itself, because de-identification is a documented processing step with residual risk, not a magic filter.

Structured fields are handled by policy: a field can be pseudonymised, kept, redacted, or flagged, and the decision is recorded (`field-policy-applied`). Free text is harder and is treated accordingly: it needs named-entity recognition *and* human review, and `privacy.status = cleared` may never be merely asserted — it must be backed by audit and free-text-review references, or the gate refuses the run. The honest empirical basis for that insistence is that automated free-text de-identification recall is low enough that it cannot be relied upon on its own; **human review is load-bearing**, which is precisely why the output-review measure (TOM #11) is a required precondition and not an optional nicety.

The governing posture is **special category by default** (Section 3). Voice is personal data and becomes *biometric* special-category data when processed to identify a speaker; diarization and voice-matching move in that direction and are assessed as such. Life-history material routinely contains health, religion, political opinion, trade-union membership, migration and family detail — and, as ACCOUNT makes explicit, the *coding* can render implicit sensitivity into explicit derived data. Treating the material as potentially special-category unless a human decides otherwise is the conservative, defensible default.

---

## 8. Local-AI architecture and the data-protection boundary

The dashed boundary in every DINOH diagram — local / EU infrastructure, no external API, no third-country transfer — is not decoration. In the gates, `hosted-llm` is a hard, non-overridable block unless explicitly reconfigured, so "local / EU" is a *technical and organisational* commitment, not a label.

An internal DPO- and IS-facing review sharpened the wording of this boundary, and the concept adopts its structure. The **master guarantee** is stated as a runtime property rather than an architectural boast: *no interview or other personal data is disclosed to any recipient outside University of Luxembourg infrastructure, at any stage.* Today this is *enforced in code* by the default-deny route block (local/EU routes only; `hosted-llm` refused unless explicitly reconfigured) and *pursued* through the provisioning and processing controls below — several of which (weight-hash verification, host allow-list, egress logging) are verification and hardening steps, **not yet end-to-end runtime-enforced in the run manifest**. The master guarantee is thus a design commitment backed by one hard control today and a defined path to the rest — not a claim that every control is already proven at runtime. The remaining properties separate two phases that are easy to conflate:

- **Provisioning (outside the processing window; carries no personal data).** Model weights — Whisper-class ASR, open-weight LLMs — are obtained *once*, ahead of processing, on UL infrastructure, then pinned and stored locally with a recorded version and SHA-256 hash. This matters because, by default, open-weight tools download weights from a public repository on first use; naming provisioning as a separate, personal-data-free phase is what makes "locally stored" true even for the very first run.
- **Processing (inference on interview data; must be egress-free).** Inference runs only from the locally stored, hash-verified copy, with offline mode enforced (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `local_files_only`), telemetry and update checks disabled, and outbound connections blocked by default (allow-list only to UL endpoints; on-device inference with no network). Absence of egress is *enforced and logged*, not merely assumed.

Honest status. The run manifest today records the git commit and dirty status, corpus hash and schema/report hashes (Section 6.13). Recording **model name + version + weight-file hash + execution host**, and having the default-deny gate verify that hash against an approved allow-list, is a **specified** extension drawn directly from the review — the right next hardening step, not a current guarantee. The distinction between "on-device" (air-gapped) and "UL-internal service" (a network call inside the trust boundary) is likewise stated deliberately, because a model on a UL server is "local" only in the trust-boundary sense.

On models specifically: open-weight families such as Mistral, Llama, Qwen and Gemma are candidate local engines for analysis or benchmarking. They are **interchangeable tools**, and the methodologically decisive questions are not brand names but: *what did the model see, under which prompt, at which version, with what gold-standard exposure, and through which review chain?* A candid reading of current maturity is important here: the committed downstream engine **proves governance** — hashing, gates, BIND, ACCOUNT, release — but it does not by itself prove that a full local-model inference on real interview data is already an operational service. That separation is intentional and is stated rather than blurred.

---

## 9. Evaluation and trust — the multilingual benchmark

Element **Benchmark** answers a narrow, honest question: when a tool proposes structure for an interview, how good is the proposal, and can we measure it in a way we trust? It is an *offline harness over a synthetic gold corpus* — privacy and task-quality assurance, explicitly **not** a quality gate on historical interpretation.

**A human reference.** The gold standard is made by a researcher, by hand, segment by segment. AI is bounded to suggestion and segmentation; the final reading of a testimony remains a scholarly act. Critically, **no AI-generated targets are used as ground truth** — otherwise one would be measuring AI against AI with no independent yardstick.

**What is measured, and how.** Two task-quality evaluations are defined: *minimal metadata extraction* (title, language, place, keywords, a short abstract), scored by exact agreement with the human reference field by field; and *L1 thematic segmentation*, scored with **WindowDiff** and **Pk**, the two established segmentation metrics from the literature. Separately, a Stage-1 *privacy-safeguard* harness measures **de-identification (direct-PII) recall** on synthetic data with seeded identifiers. Results are always broken down by language and **never pooled** into a single average that would hide where a model struggles.

**Language treated with care.** Oral history in Luxembourg is multilingual by nature. The benchmark spans seven languages (German, English, French, Italian, Spanish, Luxembourgish, Portuguese), and **Luxembourgish is handled as a first-class low-resource track** with its own reporting, so that strong English performance can never mask weak Luxembourgish performance. The deepest interpretive layer — the overarching meaning a historian draws from a testimony (L3) — is deliberately left outside automated scoring; fields that resist mechanical comparison are flagged for human review rather than scored by proxy.

**A note on reliability.** Inter-coder reliability (κ / α / AC1), the planned ADJUDICATE leg of the provenance layer, is an internal accuracy safeguard (Art. 5(1)(d)) and accountability record (Art. 5(2)) — *reliability is not truth*, and it is not an Article 16 rectification determination. All interview material in the current dataset is **synthetic**, marked `synthetic: true` at record level, which is what allows the method to be developed and published openly without exposing real testimony.

---

## 10. Legal and institutional framing

The pipeline is built *around* a legal frame; it does not adjudicate it. The frame and the role boundary matter as much as the code.

**What the frame is.** The decisive GDPR distinction is anonymous versus personal (Recital 26; Art. 4(5)); the deceased are outside the GDPR (Recital 27) but a dataset is anonymous only if no living third party remains identifiable. The controller must be able to demonstrate compliance (Art. 24; Art. 5(2)). Special categories and research safeguards engage Articles 9 and 89; transparency for reused research data is handled via Art. 14(5)(b)/89; data-subject rights include erasure (Art. 17). In Luxembourg, the CNPD lists scientific/historical/statistical research on personal data on its **DPIA-obligation list** (Point 6, "as required in Article 65" of the Law of 1 August 2018; Deliberation 34/2019) — including local processing — and residual high risk can trigger prior consultation (Art. 36). This governance design treats such processing as DPIA-listed by default, to be confirmed by the DPO/legal for the concrete project; the pipeline does not itself decide DPIA necessity. The broad reading of Article 9 to cover *inferable* sensitive data (CJEU C-184/20) is the legal anchor for ACCOUNT.

**What the code can enforce.** No hosted-LLM route; no undeclared or disallowed route; no missing or inconsistent attestation; no unearned privacy clearance; no release without the referenced review evidence; no silent green run when an output is held or uncovered. These are mechanical, testable, and non-overridable where the policy says so.

**What the code cannot decide.** Whether a lawful basis actually holds in a given case; whether a specific release is lawful; whether a DPIA is required; whether a text is truly anonymous. These are human determinations, and the architecture is designed to *surface and document* them, not to substitute for them.

**Who decides.** The controller decides and documents (Art. 24); the DPO advises and monitors (Art. 39); researchers interpret; the operator builds the gates. DPO and Information Security are human verification roles — the code produces evidence and turns inconsistencies red, but the institutional decision stays human. This is the *builder ≠ approver* boundary, stated as an architectural commitment rather than an aspiration.

## 11. What is real, what is a demonstration

Trust is built by drawing this line explicitly rather than letting a demo imply more than it delivers.

**Real, committed engine (implemented / validated).** The entry gates, BIND, ACCOUNT/Article-9 with same-run enforcement, the release evaluation, and the hash-chained run manifest. The reason codes shown are emitted by the actual pipeline code, on synthetic data, in a throwaway folder; the repository itself is never modified by a demonstration run.

**Transparent demonstration (no model).** The metadata, keywords, abstract and segment coding in the interview walkthrough are a rule-based illustration over the project's real controlled vocabulary. The *shape* mirrors a real annotation pass; the labels are suggestions, not a black-box model's output.

**Synthetic but fed through the real engine.** In the governance demonstration, the controller's quarantine review and release decision are prepared for the demo, while the release *engine* runs live on the committed code and the release subject is derived from the same prepared analysis object through the committed ACCOUNT engine. The engine is real; the human governance acts are clearly marked as synthetic.

The one sentence to close the honesty ledger: *the governance decisions are real code — gates, BIND, ACCOUNT and the release engine all run live; the content analysis in the demonstration is an honest illustration of the output format; and the human decisions in the last steps are labelled synthetic.* We would rather under-claim than over-claim.

---

## 12. Reproducibility, openness and the public micro-light

The system is engineered so that its *publishable* part can be extracted cleanly. `src/oh_eval/` is one Python package but two non-overlapping clusters: an **evaluation core** (`corpus`, `schema`, `metrics`, `reports`) and a **pipeline/governance** cluster (`gates`, `attestation`, `run_context`, `bind`, `account`, `release_subject`, `quarantine_review`, `controller_release_decision`, `release_evaluation`, `manifest`, `withdrawal`). There are currently **no imports between the two clusters in either direction**, which keeps a public extraction of the evaluation core clean. The logic that is easy to get wrong — timecode parsing, segmentation masses, metric computation, manifest recomputation — is covered by a test suite, and the analysis notebook imports the same package, so notebook and tests cannot drift apart.

The data model is explicit and versioned. Thirteen JSON schemas govern the artefacts, including `oh_pipeline_record`, `oh_analysis_object`, `oh_attestation` (+ wording), `code_sensitivity_catalog`, `run_context`, `release_subject`, `quarantine_review`, `controller_release_decision`, `run_manifest`, and — for evaluation — `luxoh_minimal_metadata`, `oh_eval_record` and `oh_eval_object`. The minimal-metadata schema (`luxoh_minimal_metadata`) is the **LuxOH Implementation Profile** of the openly published, discipline-agnostic **Interview Metadata Model — Core Profile (IMM-Core)** (Behnam Shad, v1.0, 2 June 2026; CC-BY 4.0; DOI 10.5281/zenodo.20507329), and is vendored here for a self-contained, reproducible run.

**Openness with boundaries.** A curated public *micro-light* of the **evaluation** part only is planned (target ~Q4 2026) as a separate release — fresh repository, its own Zenodo DOI, a minimal reproducible **synthetic-only** example corpus, and a public-release checklist. Everything else — the external-data governance package, the compliance dossiers, the provenance internals — stays internal. **No real interview data lives in the repository**; all interview excerpts are synthetic and carry a `synthetic: true` flag at record level, and this declaration must travel with the data if it is ever redistributed.

---

## 13. Maturity at a glance

| Component | Element | Maturity |
|---|---|---|
| Traffic-light classification + default-deny gates (attestation, G1/G2/G3) | Admission | **Implemented** |
| Analysis workflow: text/record ingest, transparent (rule-based) demo analysis, controlled export + manifest | Analysis | **Implemented** |
| Multilingual task-quality benchmark (metadata exact-match; segmentation WindowDiff/Pk; 7 languages) | Benchmark | **Validated (Stage 1)** |
| Privacy-safeguard benchmark (direct-PII de-identification recall, synthetic seeded data) | Benchmark | **Validated (Stage 1)** |
| BIND — per-dimension evidence + codebook binding; scope / minor guards | Provenance | **Validated** |
| ACCOUNT — Article-9 inference vs pinned catalogue; same-run recompute + completeness (T0/T1) | Provenance | **Implemented** on the account-bearing `run_downstream` path; global manifest coverage **specified** |
| Hash-chained `run_manifest` 0.3.1 with recompute-based validation | (cross-cutting) | **Implemented** |
| Output quarantine + human free-text review (TOM #11) as an operational workflow | Admission/Provenance | **Specified** (gate-hook + input review exist; output-review not yet live) |
| Withdrawal / erasure propagation (tombstone + crypto-shred + hash-chained log) | (cross-cutting) | **Specified** (tested scaffold; not yet wired to `run_gates`) |
| Model identity + weight-hash + host recorded in manifest and gate-verified | Admission | **Specified** (from DPO/IS review) |
| ADJUDICATE — inter-coder reliability (κ / α / AC1) | Provenance | **Planned** |
| Full local-model inference on real interview data as an operational service | Analysis | **Planned** |

---

## 14. Glossary

- **Default-deny** — when a prerequisite is missing or ambiguous (e.g. unknown consent), the answer is "no" until established.
- **Reason code** — a short, fixed string the engine emits when it refuses something (e.g. `consent-withdrawn`), so every "no" is auditable.
- **Attestation** — a run-level, signed declaration of *how* a run is processed (route, purpose, wording), checked first, with an evidence path and hash.
- **Traffic light** — a human classification of *data sensitivity* (green / yellow / red), orthogonal to the gates.
- **Gate (G1/G2/G3)** — a mechanical admission check of *a record*; distinct from the traffic light.
- **Span / binding** — the timecode or character range tying an interpretation to the exact passage (enforced by BIND).
- **Analysis object** — a coded representation of a record (`oh_analysis_object`): units with topic, frame, position, confidence, spans and coder info.
- **Article 9 (GDPR)** — special categories of personal data (health, beliefs, politics, ethnicity, trade-union membership, sex life, genetic, biometric); can be *inferred* from coding (CJEU C-184/20).
- **ACCOUNT** — the engine that writes an Article-9 inference only on an approved, hash-pinned catalogue hit; absence of a tag means *pending*, not *cleared*.
- **Same-run enforcement / recompute, don't trust** — the release claim must be recomputable from the same run, analysis object and pinned catalogue; catches downgrade (T1) and suppression (T0).
- **Quarantine review (TOM #11)** — the human-checked basis for release; a precondition, not the release itself.
- **Four-eyes principle** — a release needs two distinct people: reviewer ≠ controller.
- **Release state** — `released` / `held` / `redaction-required` / `superseded` / `uncovered`; anything held or uncovered leaves the run `quarantined`.
- **Run manifest** — the hash-chained audit document of a run (`run_manifest` 0.3.1); validated by recomputation, `run_status` ∈ {completed, quarantined, refused-admission}.
- **Tombstone / crypto-shredding** — withdrawal primitives: a structure-preserving redacted record, and discarding the pseudonym-mapping key.
- **Provisioning vs processing** — one-time, personal-data-free weight download versus egress-free inference on interview data.
- **QCA** — qualitative content analysis (Mayring), the analytic tradition the Analysis element operationalises.
- **DPIA** — data-protection impact assessment; in Luxembourg, personal research data is on the CNPD DPIA-obligation list (Art. 65 / Point 6), so this design treats it as DPIA-listed by default — necessity confirmed by the controller/DPO, not by the pipeline.
- **Controller / DPO** — the controller decides and documents (Art. 24); the DPO advises and monitors (Art. 39).

---

## 15. References and sources

*Legal references frame the design and are to be confirmed by the DPO / Legal; they are not a legal opinion.*

- Regulation (EU) 2016/679 (GDPR): Recitals 26–27; Articles 4, 5, 6, 9, 14, 17, 24, 35, 36, 39, 89.
- Luxembourg, Law of 1 August 2018 (organisation of the CNPD and implementation of the GDPR), Article 65.
- CNPD, list of processing operations subject to a DPIA, Point 6 ("as required in Article 65"; Deliberation 34/2019). https://cnpd.public.lu/en/professionnels/obligations/AIPD/liste-dpia.html
- CJEU, Case C-184/20, *OT v Vyriausioji tarnybinės etikos komisija*, judgment of 1 August 2022 (broad reading of Article 9 to cover data from which special-category information can be *inferred*).
- Mayring, P. *Qualitative Content Analysis: Theoretical Foundation, Basic Procedures and Software Solution.*
- Pevzner, L., & Hearst, M. A. (2002). A critique and improvement of an evaluation metric for text segmentation. *Computational Linguistics*, 28(1), 19–36. (WindowDiff.)
- Beeferman, D., Berger, A., & Lafferty, J. (1999). Statistical models for text segmentation. *Machine Learning*, 34(1–3), 177–210. (Pk; the metric was first introduced by the same authors in 1997.)
- Behnam Shad, K. *IMM-Core: Interview Metadata Model — Core Profile* (v1.0, 2 June 2026; software/model deposit). Zenodo, CC-BY 4.0. DOI 10.5281/zenodo.20507329. (LuxOH-CMDI is its first registered Implementation Profile; the `luxoh_minimal_metadata` schema follows that profile.)
- Research-infrastructure context: CLARIN and DARIAH (European research infrastructures for language resources and the arts & humanities); Oral History Association (OHA) ethics guidance.
- Internal project sources: the committed `src/oh_eval/` engine and `schemas/`; the pipeline-C compliance package; the interpretive-provenance (BIND/ACCOUNT) layer; and the DPO/IS review of the local-AI processing documentation.

---

## 16. Colophon

**DINOH — Digital Infrastructure for Oral History.** Luxembourg Centre for Contemporary and Digital History (C²DH), University of Luxembourg. Author / operator: **Klaus Behnam Shad** (principal investigator; builder ≠ legal approver). Concept & architecture note, version 1, 1 July 2026.

This document describes a research infrastructure and its governance design at honestly-labelled maturity. It is **not legal advice**; lawfulness, DPIA necessity and release remain with the controller, advised by the DPO. All interview material referenced is **synthetic**. Technical identifiers (schema `$id`s, route enums, reason codes, manifest version) are reproduced verbatim because they live in schemas, tests and provenance hashes and must not be paraphrased.



