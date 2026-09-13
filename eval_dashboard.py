"""
eval_dashboard.py
=================
Streamlit dashboard for the C²DH Oral History Workflow Evaluation.
Run from the project root:

    streamlit run eval_dashboard.py

Reads reports/ directory for CSV data.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path


def _stretch() -> dict:
    """Full-width kwarg that works across Streamlit versions (width='stretch' >=1.49);
    avoids the deprecated use_container_width (removed after 2025-12-31)."""
    try:
        major, minor = (int(p) for p in st.__version__.split('.')[:2])
        if (major, minor) >= (1, 49):
            return {'width': 'stretch'}
    except Exception:
        pass
    return {'use_container_width': True}

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="C²DH OH Eval",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: -0.02em;
    }
    .metric-card {
        background: #f4f1eb;
        border-left: 4px solid #1a1a2e;
        padding: 1.2rem 1.5rem;
        border-radius: 2px;
        margin-bottom: 1rem;
    }
    .metric-number {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2.5rem;
        font-weight: 600;
        color: #1a1a2e;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #666;
        margin-top: 0.3rem;
    }
    .position-card {
        background: #1a1a2e;
        color: #f4f1eb;
        padding: 1rem 1.4rem;
        border-radius: 2px;
        margin-bottom: 0.6rem;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .position-card strong {
        font-family: 'IBM Plex Mono', monospace;
        color: #c8b560;
        display: block;
        margin-bottom: 0.2rem;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .stub-banner {
        background: #fff3cd;
        border-left: 4px solid #c8b560;
        padding: 0.8rem 1.2rem;
        border-radius: 2px;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }
    .lang-badge {
        display: inline-block;
        background: #1a1a2e;
        color: #f4f1eb;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        padding: 0.15rem 0.5rem;
        border-radius: 2px;
        margin: 0.15rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────────

REPORTS = Path("reports")
CORPUS  = Path("data/corpus_synthetic.json")

# ISO 639-3 -> display names / short codes (single source of truth).
LANG_MAP = {
    "deu": "German", "eng": "English", "fra": "French",
    "ita": "Italian", "spa": "Spanish", "ltz": "Luxembourgish",
    "por": "Portuguese",
}
SHORT = {
    "deu": "DE", "eng": "EN", "fra": "FR", "ita": "IT",
    "spa": "ES", "ltz": "LB", "por": "PT",
}
LANG_ORDER = ["deu", "eng", "fra", "ita", "spa", "ltz", "por"]

def order_langs(langs):
    return sorted(langs, key=lambda l: (LANG_ORDER.index(l) if l in LANG_ORDER else 99, l))

@st.cache_data
def load_corpus():
    if not CORPUS.exists():
        return None
    try:
        return json.loads(CORPUS.read_text())
    except (json.JSONDecodeError, OSError):
        return None

@st.cache_data
def load_csv(name):
    p = REPORTS / name
    if not p.exists():
        return None
    # A corrupt/empty CSV must degrade to None (-> "missing or unreadable"
    # in the freshness banner) rather than crashing the whole dashboard.
    try:
        return pd.read_csv(p)
    except Exception:
        return None

corpus_data        = load_corpus()
validation_df      = load_csv("luxoh_validation_report.csv")
eval_validation_df = load_csv("oh_eval_validation_report.csv")
task1_df           = load_csv("task1_metadata_summary.csv")
task2_df           = load_csv("task2_segmentation_summary.csv")


def compute_staleness(corpus, validation_df, eval_validation_df, task1_df, task2_df):
    """Compare the reports against the corpus and return a list of warnings.

    Catches the failure mode where reports were generated from an older corpus
    (e.g. before Portuguese was added) and never regenerated.
    """
    warnings = []
    if corpus is None:
        return ["Corpus file not found — cannot assess report freshness."]

    corpus_langs = set(r["language"] for r in corpus["records"])
    corpus_n = len(corpus["records"])

    # Missing report files are themselves a staleness problem.
    required = {
        "luxoh_validation_report.csv": validation_df,
        "oh_eval_validation_report.csv": eval_validation_df,
        "task1_metadata_summary.csv": task1_df,
        "task2_segmentation_summary.csv": task2_df,
    }
    for fn, df in required.items():
        if df is None or not (REPORTS / fn).exists():
            warnings.append(f"Report missing or unreadable: {fn} — rerun the notebook.")

    for df, label in [(validation_df, "Metadata validation"),
                      (eval_validation_df, "Eval-contract validation")]:
        if df is not None:
            if len(df) != corpus_n:
                warnings.append(
                    f"{label} report covers {len(df)} records, "
                    f"but the corpus now has {corpus_n}."
                )
            if "language" in df.columns:
                missing = corpus_langs - set(df["language"].unique())
                if missing:
                    names = ", ".join(LANG_MAP.get(l, l) for l in order_langs(missing))
                    warnings.append(f"{label} report is missing language(s): {names}.")

    for df, label in [(task1_df, "Task 1 (metadata)"), (task2_df, "Task 2 (segmentation)")]:
        if df is not None and "language" in df.columns:
            missing = corpus_langs - set(df["language"].unique())
            if missing:
                names = ", ".join(LANG_MAP.get(l, l) for l in order_langs(missing))
                warnings.append(f"{label} report is missing language(s): {names}.")

    # Timestamp check: any report older than the corpus is suspect.
    if CORPUS.exists():
        corpus_mtime = CORPUS.stat().st_mtime
        stale = [
            fn for fn in (
                "luxoh_validation_report.csv",
                "oh_eval_validation_report.csv",
                "task1_metadata_summary.csv",
                "task2_segmentation_summary.csv",
            )
            if (REPORTS / fn).exists() and (REPORTS / fn).stat().st_mtime < corpus_mtime
        ]
        if stale:
            warnings.append(
                "Report file(s) older than the corpus — rerun the notebook: "
                + ", ".join(stale) + "."
            )
    return warnings


staleness_warnings = compute_staleness(
    corpus_data, validation_df, eval_validation_df, task1_df, task2_df
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎙️ C²DH OH Eval")
    st.markdown("**Multilingual Goldstandard Evaluation**")
    st.markdown("---")
    if corpus_data:
        _ver = corpus_data.get("version")
        _n = len(corpus_data["records"])
        _langs = order_langs(set(r["language"] for r in corpus_data["records"]))
        _badges = " · ".join(SHORT.get(l, l.upper()) for l in _langs)
        st.markdown(f"**Version:** {('v' + str(_ver)) if _ver else '—'}")
        st.markdown(f"**Corpus:** {_n} synthetic records")
        st.markdown(f"**Languages:** {_badges}")
    else:
        st.markdown("**Version:** —")
        st.markdown("**Corpus:** _not found_")
        st.markdown("**Languages:** —")
    st.markdown("**Schema:** Metadata (LuxOH-CMDI) + Eval contract")
    st.markdown("**Backends:** Stub (Grid'5000 pending)")
    st.markdown("---")
    st.markdown("**Project:** DINOH (2024–2027)")
    st.markdown("**PI:** Klaus Behnam Shad")
    st.markdown("**Affiliation:** C²DH, Université du Luxembourg")
    st.caption("DINOH Evaluation — synthetic evaluation procedures; OHPIPE is a separate component.")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Overview", "Task 1 — Metadata", "Task 2 — Segmentation", "Methodological positions"],
        label_visibility="collapsed"
    )

# ── Report freshness banner (shown on every page) ───────────────────────────────

if staleness_warnings:
    st.error(
        "**Reports are out of sync with the corpus.** Rerun "
        "`notebooks/cdh_oh_eval_v1.ipynb` (Restart & Run All) to regenerate them.\n\n"
        + "\n".join(f"- {w}" for w in staleness_warnings)
    )
else:
    st.success("Reports are in sync with the current corpus.")

# ── OVERVIEW ───────────────────────────────────────────────────────────────────

if page == "Overview":
    st.markdown("# Evaluation Dashboard")
    st.markdown("### C²DH Oral History Workflow — Multilingual Goldstandard")

    st.markdown("""
    <div class="stub-banner">
    ⚠️ <strong>Stub run:</strong> Model backends are deterministic placeholders.
    Real inference is future work; the current notebook uses the documented placeholder registry.
    Task scores demonstrate the placeholder scoring path; they establish neither pipeline correctness nor model performance.
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    n_records   = len(corpus_data["records"]) if corpus_data else "—"
    n_langs     = len(set(r["language"] for r in corpus_data["records"])) if corpus_data else "—"
    n_valid     = validation_df["valid"].sum() if validation_df is not None else "—"
    n_evalvalid = eval_validation_df["valid"].sum() if eval_validation_df is not None else "—"
    n_models    = task1_df["model"].nunique() if task1_df is not None else "—"

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{n_records}</div>
            <div class="metric-label">Synthetic records</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{n_langs}</div>
            <div class="metric-label">Languages</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{n_valid}/{n_records}</div>
            <div class="metric-label">Metadata valid</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{n_evalvalid}/{n_records}</div>
            <div class="metric-label">Eval-contract valid</div>
        </div>""", unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{n_models}</div>
            <div class="metric-label">Placeholder model entries</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Language breakdown
    st.markdown("### Corpus — per-language breakdown")

    if corpus_data:
        from collections import Counter
        lang_map = LANG_MAP
        counts = Counter(r["language"] for r in corpus_data["records"])
        lang_df = pd.DataFrame([
            {"ISO 639-3": k, "Language": lang_map.get(k, k), "Records": v,
             "Thematic axes": "Border/mobility · Labour biography",
             "Registers": "Colloquial · Reflective"}
            for k, v in sorted(counts.items())
        ])
        st.dataframe(lang_df, **_stretch(), hide_index=True)

        st.markdown("**Language badges:**")
        badges = "".join(
            f'<span class="lang-badge">{lang_map.get(k, k).upper()[:3]} ({k})</span>'
            for k in sorted(counts.keys())
        )
        st.markdown(badges, unsafe_allow_html=True)

    st.markdown("---")

    # Thematic design
    st.markdown("### Corpus design — thematic axes × registers")
    design_df = pd.DataFrame({
        "Slot": ["01", "02", "03", "04"],
        "Thematic axis": ["Border / mobility", "Border / mobility", "Labour biography", "Labour biography"],
        "Register": ["Colloquial", "Reflective", "Colloquial", "Reflective"],
        "Purpose": [
            "Tests model on informal narration of border crossing",
            "Tests model on analytical retrospection",
            "Tests model on working-class oral history registers",
            "Tests model on educated self-reflection on career"
        ]
    })
    st.dataframe(design_df, **_stretch(), hide_index=True)

# ── TASK 1 ─────────────────────────────────────────────────────────────────────

elif page == "Task 1 — Metadata":
    st.markdown("# Task 1 — Metadata Extraction")
    st.markdown("Given an interview transcript, extract Metadata fields.")

    st.markdown("""
    <div class="stub-banner">
    ⚠️ Stub run: all models return gold values with small perturbations.
    Accuracy of 1.0 reflects stub behaviour, not real model performance.
    </div>
    """, unsafe_allow_html=True)

    if task1_df is not None:
        models = task1_df["model"].unique().tolist()
        selected_model = st.selectbox("Select model", models)

        filtered = task1_df[task1_df["model"] == selected_model]

        st.markdown(f"### Exact-match accuracy — `{selected_model}`")
        pivot = filtered.pivot_table(
            index="language", columns="field", values="accuracy"
        ).round(2)
        st.dataframe(pivot,
                     **_stretch())

        st.caption("Each row reports one language. No pooled cross-language accuracy is shown.")

        st.markdown("### Methodological note on free-text fields")
        st.info(
            "Fields `title` and `abstract` are flagged for **manual qualitative review** "
            "because this harness has no validated automatic scoring rule for these fields. "
            "Text similarity alone would not establish descriptive adequacy or interpretive validity."
        )
    else:
        st.warning("No Task 1 data found. Run the notebook to generate reports/task1_metadata_summary.csv")

# ── TASK 2 ─────────────────────────────────────────────────────────────────────

elif page == "Task 2 — Segmentation":
    st.markdown("# Task 2 — L1 Thematic Segmentation")
    st.markdown("Given a transcript, propose L1 segment boundaries. Evaluated with **WindowDiff** and **Pk**.")

    st.markdown("""
    <div class="stub-banner">
    ⚠️ Stub run: every model returns the gold segmentation with the final two segments
    merged (a single missed boundary). WindowDiff/Pk therefore reflect one boundary error
    per transcript, not model performance. A future real-inference protocol needs independent validation.
    </div>
    """, unsafe_allow_html=True)

    if task2_df is not None:
        st.markdown("### Mean WindowDiff and Pk — all models × languages")
        st.markdown("Lower indicates closer boundary agreement with the supplied reference. There is no universal 0.5 random baseline; these are placeholder scores.")

        pivot2 = task2_df.pivot_table(
            index="language", columns="model", values="mean_window_diff"
        ).round(3)
        st.markdown("**WindowDiff (lower = better)**")
        st.dataframe(pivot2,
                     **_stretch())

        st.markdown("---")
        _n_other = (len(set(r["language"] for r in corpus_data["records"]) - {"ltz"})
                    if corpus_data else None)
        _other_phrase = f"the {_n_other} other languages" if _n_other else "the other languages"
        st.markdown("### Luxembourgish — low-resource language caveat")
        st.info(
            "**`ltz` (Luxembourgish)** is treated as a low-resource language with **separate reporting**. "
            "No pooled cross-language scores are produced. Models are not expected to perform "
            f"comparably on Luxembourgish and on {_other_phrase}."
        )

        st.markdown("### Portuguese — v1.1 addition")
        st.info(
            "**`por` (Portuguese)** was added in v1.1 to reflect the demographic reality of Luxembourg. "
            "Portuguese-descent speakers constitute a major segment of the population, and any "
            "evaluation of OH infrastructure that omits Portuguese would be ethnographically incomplete."
        )
    else:
        st.warning("No Task 2 data found. Run the notebook to generate reports/task2_segmentation_summary.csv")

# ── METHODOLOGICAL POSITIONS ───────────────────────────────────────────────────

elif page == "Methodological positions":
    st.markdown("# Methodological positions")
    st.markdown(
        "These positions are deliberate design choices, not oversights. "
        "They are documented in Section 10 of the evaluation notebook."
    )

    _n_syn = len(corpus_data["records"]) if corpus_data else "all"
    positions = [
        ("Goldstandard is a human artefact",
         "AI use is bounded to suggestion and segmentation. The `suggested_*` / `selected_*` distinction "
         "from qda-mini-workflow is preserved as a structural principle. Final interpretation "
         "remains with the researcher."),
        ("L3 (Oberthema) excluded",
         "L3 belongs to the hermeneutic act of the researcher. AI evaluation of L3 is excluded "
         "by methodological choice, not technical constraint."),
        ("No pooled cross-language scores",
         "Per-language reporting only. Pooling scores across seven typologically distinct languages "
         "— including low-resource Luxembourgish — would obscure meaningful variation."),
        ("Free-text fields: manual review only",
         "Title and abstract are flagged for qualitative review. No automatic scoring rule "
         "for descriptive adequacy or interpretive validity has been validated here."),
        ("Researcher-in-the-loop is structural",
         "The annotation model distinguishes reference selections from proposals. "
         "This evaluation dashboard does not enforce project approval or a production review process."),
        ("Open-weight models only",
         "The notebook lists candidate models but uses a placeholder backend. No real model "
         "inference is performed. Future hosting and data flows require project-specific assessment; "
         "the choice of open weights does not establish legal compliance."),
        ("Synthetic corpus, explicitly declared",
         f"All {_n_syn} records carry `synthetic: true`. No real interview material is used in this "
         "evaluation set. Should the dataset be redistributed, this declaration must travel with it."),
    ]

    for title, body in positions:
        st.markdown(f"""
        <div class="position-card">
            <strong>{title}</strong>
            {body}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### What this notebook deliberately does *not* do")
    not_doing = [
        "Human reference annotations; AI-assisted synthetic transcript drafting",
        "No active learning or auto-tuning loop",
        "No L3 evaluation",
        "No embedding-similarity scoring of free-text fields",
        "No pooled cross-language F1",
    ]
    for item in not_doing:
        st.markdown(f"- {item}")
