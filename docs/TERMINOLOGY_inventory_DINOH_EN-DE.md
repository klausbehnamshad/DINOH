# DINOH — Terminology & Title Inventory (EN + DE)
### Canonical naming for visualisation, video & public materials · Terminologie-Referenz für Visualisierung, Video & öffentliche Materialien

**Project / Projekt:** DINOH — *Digital, AI-assisted Infrastructure for Oral History* · C²DH, University of Luxembourg
**Core / Kern:** local-only LLM workflow for qualitative content analysis (Mayring / QCA) — no internet egress, no external APIs · *lokaler LLM-Workflow für qualitative Inhaltsanalyse — kein Internet-Egress, keine externen APIs*
**Status of this scheme / Status:** consolidated from `MEGAPROMPT_naming-architecture-visuals` + signed-off `REVIEW_naming-folders-visuals` (HI). Short names = lay register; long names = canonical scientific taxonomy.
**Date / Stand:** 2026-06-19 · **Author / Autor:** Klaus Behnam Shad (PI / operator — builder ≠ legal approver)

> Communication rule for every figure / **Kommunikationsregel für jede Abbildung:** **enforces / verifies / decides** — the system *enforces* technical & accountability duties and *verifies* evidence, but lawfulness and anonymity remain **human decisions**. · *Das System erzwingt technische Pflichten und verifiziert Nachweise; über Rechtmäßigkeit und Anonymität entscheidet der Mensch.*

---

## 1. The four elements / Die vier Elemente  (old A–D → unified / alt A–D → einheitlich)

| Old | Short name (EN · DE) | Long name (EN / DE) | Role / Rolle | Maturity* |
|---|---|---|---|---|
| **C** | **Admission · Zugang** | Data Admission & Governance / Datenzugang und Governance | Entry layer: traffic-light classification + default-deny gates / *Eintritt: Ampel-Klassifikation + default-deny-Gates* | Implemented |
| **B** | **Analysis · Analyse** | Analysis Workflow / Analyseworkflow | QCA engine: ingestion → segmentation → LLM-assisted coding → evaluation → export + manifest / *QCA-Engine* | Implemented |
| **A** | **Benchmark · Prüfstand** | Evaluation & Benchmarking / Evaluation und Prüfstand | Offline harness on synthetic gold corpus; measures **de-identification recall**, not QCA quality / *misst De-ID-Recall, nicht Codier-Qualität* | Validated (Stage 1) |
| **D** | **Provenance · Provenienz** | Interpretive Provenance & Accountability / Interpretative Provenienz und Rechenschaft | Cross-cutting layer over coded interpretations / *Querschicht über codierte Interpretationen* | Emerging |

\* Maturity scale / Reifegrad-Skala: **implemented · validated · specified · planned**. Values are the operator's current read — confirm before external/grant use. · *Werte = aktueller Stand des Operators; vor externer Nutzung bestätigen.*

**Old → new map / Alt → neu:** `A → Benchmark · B → Analysis · C → Admission · D → Provenance`.
The old letters implied a sequence that contradicts the real flow (the gate, old "C", runs *before* the engine, old "B"). · *Die alten Buchstaben suggerierten eine Reihenfolge, die dem echten Datenfluss widerspricht.*

---

## 2. The three registers / Die drei Register  (canonical scientific model)

```
Data lifecycle / Datenlebenszyklus :  Candidate data → Admission decision → Prepared records → Analysis → Controlled outputs
Assurance layer / Assurance-Schicht :  Attestation · record gates · benchmark evidence · manifests · provenance
Human authority / Menschliche Autorität :  Researchers · Controller · DPO · release / review decisions
```

Roles / Rollen: **Controller decides** (Art. 24) · **DPO advises** (Art. 39) · **builder ≠ approver** (PI / operator builds, does not approve).

---

## 3. Two orthogonal axes — NOT renamed / Zwei orthogonale Achsen — NICHT umbenannt

**Traffic light / Ampel** (data sensitivity / Daten-Sensitivität):
- 🟢 **green / grün** — evidenced anonymous (signed proof + hash) + controller sign-off; *the gate verifies the referenced evidence & its hash — it does not rule that the text is truly anonymous (Recital 26 is a human call)*
- 🟡 **yellow / gelb** — pseudonymised / still personal; needs DSFA → DPO opinion → controller release **and** operational output quarantine (TOM #11)
- 🔴 **red / rot** — refused

**Gates** (mechanical default-deny / mechanische default-deny-Checks):
- **Attestation gate** — run-level, **checked first** / *lauf-weit, läuft zuerst*
- **G1** — schema / Schema-Validität
- **G2** — consent · embargo · purpose / Consent · Embargo · Zweck
- **G3** — processing route + privacy status / Route + Privacy-Status

> ⚠️ There is **no “G4”**. Early diagrams invented it and placed attestation last; attestation is run-level and runs **first**. · *Es gibt kein „G4"; die Attestation läuft zuerst.*

---

## 4. Provenance internals / Provenance-Innenleben  (the “Additional Layer for B–C”)

| Engine | Role / Rolle | Maturity |
|---|---|---|
| **BIND** | Binds each coding to its evidence + codebook (per dimension); scope & minor-sensitivity gates / *bindet Codierung an Evidenz + Codebook; Scope-/Kind-Gates* | Validated |
| **ACCOUNT** | code → sensitivity (Art. 9 inference); `art9_inference`; `art9-inference-upgrade`; traffic-light re-evaluation on output; release gate / *Art-9-Inferenz + Release-Gate* | Implemented (partial / B-series in progress) |
| **ADJUDICATE** | Reliability / inter-coder agreement / *Reliabilität / Inter-Coder-Agreement* | Planned |

**ACCOUNT roadmap / Roadmap:** A1 → A1.1 → A2a *(committed)* → **A2b = release semantics** ( **B0** *(committed)* · B1a/B1b · B2 · B3 · B4 ) → A2c.

---

## 5. Frozen machine identifiers / Eingefrorene Maschinen-Identifier
*Show as code tokens in visuals; never rename (they live in schemas, tests, CI and provenance hashes). · In Visuals als Code-Tokens zeigen; nie umbenennen.*

- Route enums / Route-Enums: `local-eu-model`, `human-only` (`hosted-llm` struck / gestrichen 2026-06-10)
- Gate reason codes / Gate-Reason-Codes (26): `consent-withdrawn`, `route-policy-disallowed`, `privacy-status-not-cleared`, `anonymity-evidence-*`, …
- Schema `$id`s & fields: `oh_pipeline_record`, `processing_route`, `privacy.status`, …
- `C4` internal token (attestation gate + C1–C4 PR-workstream)
- Everything under `green-line_2026-06-14/` (paths are inside attestation hashes)

---

## 6. Artifact level / Artefakt-Ebene  (reference)

**Modules / Module (`src/oh_eval/`):** `gates` · `account` · `bind` · `attestation` · `manifest` · `run_context` · `release_subject` · `quarantine_review` · `withdrawal` · `corpus` · `metrics` · `reports` · `schema` · `_safeio`
**Schemas (`schemas/`):** `oh_pipeline_record` · `oh_analysis_object` · `oh_attestation` · `oh_attestation_wording` · `oh_eval_object` · `oh_eval_record` · `luxoh_minimal_metadata` · `run_manifest` · `run_context` · `release_subject` · `quarantine_review` · `code_sensitivity_catalog`

---

## 7. Usage notes for visuals / Hinweise für Visuals
- Primary label = short name; subtitle = long name. · *Großes Label = Kurzname; Untertitel = Langname.*
- Always carry a maturity legend; never draw target capability as built. · *Immer Reifegrad-Legende; Zielarchitektur nie als gebaut zeigen.*
- Keep traffic light and gates as **separate** axes. · *Ampel und Gates getrennt halten.*
- Public explainer (lay, two tracks) and expertise/grant dossier are **different deliverables** — don't make one figure serve both. · *Öffentliches Erklärstück und Fach-/Antragsdossier sind verschiedene Deliverables.*
- For standalone SVG export: inline styles, literal hex colours (no `var()`), `font-family` on the `<svg>`, valid `<title>`/`<desc>`. · *Für Standalone-SVG: Styles inline, feste Hex-Farben, Font am `<svg>`, gültige `<title>`/`<desc>`.*
