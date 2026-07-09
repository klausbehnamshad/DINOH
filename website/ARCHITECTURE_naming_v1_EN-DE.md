# DINOH research infrastructure — architecture & naming (v2)

*Canonical communication architecture. Public materials may use the short names; technical, grant and expertise materials should also carry the precise scientific labels and maturity status.*

**Date:** 2026-06-18 · **Decision:** name components by function, distinguish lifecycle from assurance and human authority, and never use a machine check as shorthand for legal compliance.

---

## ENGLISH

### The model in one line

A **two-step data lifecycle** — *Admission → Analysis* — with a separate **assurance layer** and explicit **human authority**.

```text
DATA LIFECYCLE
candidate data ──▶ ADMISSION ──▶ prepared records ──▶ ANALYSIS ──▶ controlled outputs
                    │                                  │
                    └──────────── evidence ─────────────┘

ASSURANCE
run attestation · record gates · privacy-safeguard benchmark · manifests · provenance

HUMAN AUTHORITY
researchers interpret · controller decides and releases · DPO advises
```

### Canonical names

| Public short name | Scientific / technical label | Role | Current maturity |
|---|---|---|---|
| **Admission** | **Data Admission & Governance** | Classifies candidate datasets and verifies machine-checkable entry requirements. A technical pass is evidence of gate passage, not a legal determination. | Gate and attestation core implemented and tested; governance decisions remain human. |
| **Analysis** | **Analysis Workflow** | Processes admitted records through segmentation, AI-assisted coding, evaluation and controlled export. Admission gates sit at the boundary, not inside both components. | Partially implemented; no claim of a complete production workflow for all oral-history data. |
| **Benchmark** | **Evaluation & Benchmarking** | Currently evaluates privacy safeguards: Stage-1 direct-PII detection/de-identification recall on seeded synthetic data. It does **not** measure QCA coding quality. | Harness implemented; synthetic Stage-1 results validated; real-sample Stage 2 remains governance-gated. |
| **Provenance** | **Interpretive Provenance & Accountability** | Binds interpretations to source material, codebooks and responsible actors; makes derived sensitivity and release decisions auditable. | Partial: core binding/scope controls exist; further accountability and adjudication functions are specified or planned. |

### Why renamed

The old letters looked like a sequence (A → B → C), although the real lifecycle places admission before analysis, runs privacy benchmarking offline, and treats provenance as cross-cutting. Functional names expose these different relationships instead of forcing them into one false pipeline.

### Checks inside Admission

The code first verifies the **run-level attestation**, then applies three per-record gates:

1. **G1 — schema**
2. **G2 — consent and purpose**
3. **G3 — processing route and privacy evidence**

There is no `G4` in the code. Internal development documents may still use `C4` as a historical workstream label for the attestation mechanism; public materials call it the **run-level attestation check**, not G4.

### Communication rule

Use three distinct formulations:

- **The system enforces:** schema constraints, route allow-lists, default-deny refusal and evidence/hash consistency.
- **The system verifies documented prerequisites:** consent/purpose declarations, privacy status, audit references, free-text-review references and attestation content.
- **People decide:** anonymity, lawful basis, DPIA conclusions, interpretation and release.

---

## DEUTSCH

### Das Modell in einem Satz

Ein **zweistufiger Datenlebenszyklus** — *Zugang → Analyse* — mit einer getrennten **Sicherungsschicht** und ausdrücklich ausgewiesener **menschlicher Entscheidungshoheit**.

```text
DATENLEBENSZYKLUS
Kandidatendaten ──▶ ZUGANG ──▶ vorbereitete Records ──▶ ANALYSE ──▶ kontrollierte Outputs
                       │                                  │
                       └──────────── Evidenz ──────────────┘

SICHERUNG
Lauf-Attestierung · Record-Gates · Datenschutz-Prüfstand · Manifeste · Provenienz

MENSCHLICHE ENTSCHEIDUNGSHOHEIT
Forschende interpretieren · Controller entscheidet und gibt frei · DPO berät
```

### Kanonische Namen

| Öffentlicher Kurzname | Wissenschaftlich-technische Bezeichnung | Rolle | Aktueller Reifegrad |
|---|---|---|---|
| **Zugang** | **Datenzugang und Governance** | Klassifiziert Kandidatendatensätze und prüft maschinenprüfbare Eintrittsvoraussetzungen. Ein technisches Bestehen ist ein Gate-Nachweis, keine rechtliche Feststellung. | Gate- und Attestierungskern implementiert und getestet; Governance-Entscheidungen bleiben menschlich. |
| **Analyse** | **Analyseworkflow** | Verarbeitet zugelassene Records durch Segmentierung, KI-gestütztes Codieren, Evaluation und kontrollierten Export. Die Zugangsgates liegen an der Grenze, nicht zugleich in beiden Komponenten. | Partiell implementiert; kein Anspruch auf einen vollständigen Produktivworkflow für sämtliche Oral-History-Daten. |
| **Prüfstand** | **Evaluation und Benchmarking** | Evaluiert derzeit Datenschutz-Schutzmaßnahmen: Stufe-1-Recall direkter PII-Erkennung/De-Identifikation auf eingestreuten synthetischen Daten. Er misst **nicht** die Qualität des QCA-Codierens. | Harness implementiert; synthetische Stufe-1-Ergebnisse validiert; Realstichproben-Stufe 2 bleibt governance-gebunden. |
| **Provenienz** | **Interpretative Provenienz und Rechenschaft** | Bindet Deutungen an Quellenmaterial, Codebücher und verantwortliche Akteure; macht abgeleitete Sensitivität und Freigaben auditierbar. | Partiell: zentrale Bindungs-/Scope-Kontrollen existieren; weitere Accountability- und Adjudikationsfunktionen sind spezifiziert oder geplant. |

### Warum umbenannt

Die alten Buchstaben sahen wie eine Reihenfolge aus (A → B → C), obwohl der reale Lebenszyklus den Zugang vor die Analyse stellt, Datenschutz-Benchmarking offline ausführt und Provenienz als Querschnitt behandelt. Funktionsnamen machen diese unterschiedlichen Beziehungen sichtbar, statt sie in eine falsche Pipeline zu pressen.

### Prüfungen innerhalb des Zugangs

Der Code prüft zuerst die **Attestierung auf Laufebene** und danach drei Record-Gates:

1. **G1 — Schema**
2. **G2 — Consent und Zweck**
3. **G3 — Verarbeitungsroute und Privacy-Evidenz**

Im Code existiert kein `G4`. Interne Entwicklungsdokumente können `C4` weiterhin als historischen Workstream-Namen für den Attestierungsmechanismus enthalten; öffentlich heißt er **Attestierungsprüfung auf Laufebene**, nicht G4.

### Kommunikationsregel

Drei Aussageklassen müssen getrennt bleiben:

- **Das System erzwingt:** Schema-Constraints, Route-Allow-Lists, Default-deny-Verweigerung und Evidenz-/Hash-Konsistenz.
- **Das System prüft dokumentierte Voraussetzungen:** Consent-/Zweckangaben, Privacy-Status, Audit-Referenzen, Freitext-Review-Referenzen und Attestierungsinhalt.
- **Menschen entscheiden:** Anonymität, Rechtsgrundlage, DSFA-Ergebnis, Interpretation und Freigabe.

---

## Historical mapping

`A → Benchmark` · `B → Analysis` · `C → Admission` · `D → Provenance`

The mapping is for historical continuity only. Machine identifiers, reason codes, schemas, evidence paths and append-only history remain unchanged.
