# The DINOH Pipeline — A Plain-Language Walkthrough Script
### For oral historians and humanities scholars · with technical notes for the curious

*Purpose of this document:* a script you can read from (or paraphrase) to explain, in everyday English,
what our oral-history processing pipeline does and why — while still giving the technically-minded in the
room the real mechanics. Each stage has three lines: **In plain words**, **Under the hood**, and
**Say this** (a sentence you can speak out loud).

---

## The one-paragraph version

> *"When we work with oral-history interviews, the hard part isn't the transcription — it's doing it in a
> way that respects the people who spoke to us and the law that protects them. Our pipeline is a series of
> checkpoints. An interview only moves forward if consent covers what we're about to do, if the data stays
> where it's allowed to stay, and if a human — not a machine — signs off before anything is released.
> The machine's job is to be honest about what it sees and to **stop**; the human's job is to decide."*

Internally we call the governance framework **DINOH**. The demo app shows one interview travelling through it.

---

## How the demo is laid out (one app, three tabs)

Run `streamlit run apps/dinoh_cockpit.py` — the merged **DINOH Cockpit**. (The single-surface apps
`apps/interview_walkthrough.py` and `apps/governance_cockpit.py` still exist as a fallback and show
the same surfaces.)

- **Tab 1 — "Interview walkthrough":** drag in a `.txt` transcript (or click a prepared sample). It runs
  through the **real entry gates** and produces a generated analysis (metadata, segment coding, keywords,
  abstract, an Article-9 pre-screen).
- **Tab 2 — "Gate scenarios":** six one-click scenarios over the full synthetic corpus, each making exactly
  one real reason code fire (consent withdrawn / unknown, embargo, purpose, cloud route) — plus a
  bring-your-own-(synthetic)-data sub-tab.
- **Tab 3 — "Governance chain (BIND+ACCOUNT+RELEASE live)":** pick one of two *prepared coded interviews*
  (a clean one, and one with a hidden sensitive code). It runs live through the deeper engine stages
  **BIND**, **ACCOUNT** and the **Release** evaluation (clean → released; hidden Art-9 → held by the
  controller, run quarantined).

> **Say this:** *"Tab one is the journey of a raw transcript; tab two shows every way the gate can say
> ‘no’; tab three zooms into the governance engine itself, on a worked example."*

---

## Stage by stage

### 1 · Ingest
**In plain words:** we take in an interview — a recording or, here, a text transcript.
**Under the hood:** the file is read in memory only; nothing is written to disk or sent anywhere. For the
demo it's synthetic material; real material would already be transcribed and consented.
**Say this:** *"Everything happens on this machine. Dropping a file in doesn't send it anywhere."*

### 2 · Entry gates — the consent & lawfulness checkpoint
**In plain words:** before anything else, we ask four questions. Did the speaker consent? Does that consent
cover *this* use (research vs. teaching vs. public)? Is the data being processed somewhere it's allowed to
be? And is there a signed declaration of how it's processed?
**Under the hood:** the committed engine `run_gates` runs G1 (schema), G2 (consent + purpose + embargo),
G3 (processing route vs. an EU-only policy) and an attestation check. A failure produces a precise,
auditable **reason code** — e.g. `consent-withdrawn`, `route-policy-disallowed`, `attestation-route-mismatch`.
Default-deny: unknown consent is treated like withdrawn.
**Say this:** *"If consent is missing, withdrawn, or doesn't cover what we're about to do, the interview
stops here — automatically, and it tells us exactly why."*

> **Strong moment:** switch the processing route to **"Cloud (hosted LLM)"** — the gate refuses it
> (`route-policy-disallowed`). *"The data is stopped before it could ever leave the EU."*

### 3 · Analysis & coding — turning narrative into structured interpretation
**In plain words:** we break the interview into segments and, for each, note what it's *about* (topic),
*how* it's framed, the rhetorical move, and the speaker's discursive position — the kind of close reading an
oral historian already does, made explicit and consistent.
**Under the hood:** topic and frame are kept as **separate dimensions** (a finding from the pilot: they
often pull apart, and that disagreement is a data point, not an error). In the demo's first tab this layer
is a **transparent rule-based demonstration** over our real controlled vocabulary — *no black-box model*.
In real use, this coding comes from human annotators (or a declared model), not a heuristic.
**Say this:** *"This is our close reading, written down in a shared format so humans and machines can use
the same categories — and so two coders can disagree visibly."*

### 4 · BIND — every claim must point to its evidence
**In plain words:** an interpretation is only allowed if it's anchored to the exact passage it came from,
and only uses categories from the agreed codebook. No free-floating claims.
**Under the hood:** committed engine `run_bind`. It checks each coding has a **span** (timecode or character
range) and that each code is **in the codebook, per dimension**. Violations are real codes:
`claim-span-unbound`, `code-out-of-codebook`. Special guards refuse codings of own-data/minors.
**Say this:** *"Every interpretation has to show its receipt — the exact moment in the interview it rests
on — and stay within our shared vocabulary."*

### 5 · ACCOUNT — catching hidden special-category data (Article 9 GDPR)
**In plain words:** some codings, though they look harmless, quietly reveal protected information — health,
beliefs, political opinion, ethnic origin, trade-union membership. The pipeline flags these so a human looks
before anything is shared.
**Under the hood:** committed engine `annotate_art9_inference` checks each coding against an **approved,
hash-pinned sensitivity catalogue**. It writes an Article-9 tag **only on a real, controller-approved
catalogue hit** (`tag_source=sensitivity_catalog`). Crucially: **the absence of a tag does NOT mean
"cleared"** — an un-matched coding is **`pending` review**, not green.
**Say this:** *"A code like 'mentions the union' is, in law, special-category data. The system catches that
and routes it to a person. And 'no flag' never means 'safe' — it means 'not yet reviewed'."*

> **Strong moment (Tab 2):** the *clean* example stays **`pending`** (honest, not "clear"); the *hidden
> Art-9* example surfaces a real `trade_union_membership` inference. Same-looking inputs, different outcomes
> — that's the engine actually reasoning, not a canned answer.

### 6 · Human review — the quarantine
**In plain words:** nothing a machine flags is auto-resolved. A human reviewer clears each output first.
**Under the hood:** a quarantine review (TOM #11) must be signed before release is even considered.
**Say this:** *"The machine's job is to stop and ask. A person always reviews before release."*

### 7 · Controller & release — the four-eyes decision
**In plain words:** the institution — not the researcher, not the tool — makes the final release decision,
and it takes two people (four eyes).
**Under the hood:** a controller release decision feeds `evaluate_release` (committed engine
`oh_eval.release_evaluation`), which reports states like `released`, `superseded`, `blocked` and an overall
`release_complete`, with reason codes such as `release-output-held` / `release-output-uncovered`. *(Tab 2 now
runs this release engine **live** on the committed code, inside a throwaway temp directory — the clean
example releases and the run completes; the hidden-Art-9 example is held by the controller and the run is
quarantined. The release **engine** is real; the controller's quarantine review and release **decision** are
synthetic, prepared for the demo, and the release subject is derived from the same prepared coded object via
the committed ACCOUNT engine — same-run derivation demonstrated, not engine-enforced.)*
**Say this:** *"Release is an institutional decision under the four-eyes principle. The release engine runs
for real, but the app never releases anything by itself — a person decides."*

---

## What is real, what is a demonstration (say this if asked — it builds trust)

- **Real, committed engine:** the entry gates, BIND, ACCOUNT/Article-9, **and the Release evaluation**. The
  reason codes you see are emitted by the actual pipeline code, on synthetic data, in a throwaway folder —
  the repository is never modified.
- **Transparent demonstration (no model):** the metadata/keywords/abstract and the segment coding in the
  first tab. The shape mirrors a real annotation pass; the labels are suggestions over our real vocabulary.
- **Synthetic, prepared (but fed through the real engine):** the controller's quarantine review and release
  decision in Tab 2. The release *engine* runs live on the committed code; the controller *decisions* are
  prepared for the demo — not a real governance act.

> **Say this:** *"I'd rather under-claim than over-claim. The governance decisions are real code — gates,
> BIND, ACCOUNT and the release engine all run live; the content analysis here is an honest demonstration of
> the output format; and the controller's decisions in the last step are clearly marked as synthetic."*

---

## The four moments worth landing

1. **Data stays in the EU** — the cloud route is refused at the gate.
2. **Hidden sensitivity is caught** — an innocuous code implies Article-9 data and is routed to a human.
3. **"No flag" ≠ "cleared"** — un-matched codings are *pending review*, never silently green.
4. **A human always decides** — nothing is released automatically; release is a four-eyes institutional act.

---

## Mini-glossary (for the technically curious)

- **Reason code** — a short, fixed string the engine emits when it refuses something (e.g.
  `consent-withdrawn`), so every "no" is auditable.
- **Attestation** — a signed declaration of *how* a run is processed (route, model, purpose); the gate
  checks the run against it.
- **Span / binding** — the timecode or character range tying an interpretation to the exact passage.
- **Article 9 (GDPR)** — special categories of personal data (health, beliefs, politics, ethnicity,
  trade-union membership, sex life, genetic, biometric) that get extra protection.
- **Four-eyes principle** — a release needs two distinct people: the reviewer ≠ the controller.
- **Default-deny** — when in doubt (e.g. unknown consent), the answer is "no" until established.

---

*One honest sentence to close on:* **"The point of all this isn't the AI — it's that the system is built to
stop, to explain itself, and to hand the decision to a human who is accountable."**
