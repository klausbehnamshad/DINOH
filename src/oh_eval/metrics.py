"""Evaluation metrics for the C²DH Oral History benchmark.

Pure, dependency-light metric logic extracted from the evaluation notebook so it
can be unit-tested and reused (CI, HPC runs) without executing the notebook. The
module intentionally has no pandas dependency; aggregation/reporting stay in the
notebook and ``oh_eval.reports``.

Two task families:

* ``evaluate_metadata`` — per-field comparison of extracted Metadata fields.
* ``evaluate_segmentation`` — WindowDiff/Pk over timecode-derived boundary masses.
"""

from __future__ import annotations

from typing import Optional

try:  # segeval is the one pip-only dependency; degrade gracefully if absent.
    import segeval
    SEGEVAL_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without segeval
    segeval = None
    SEGEVAL_AVAILABLE = False


# ── Field configuration (Metadata) ──────────────────────────────────────────
# NB: free-text fields (title, abstract) are flagged for manual qualitative
# review, never auto-scored, so they are deliberately NOT in EXACT_MATCH_FIELDS.
CONTROLLED_FIELDS = ["consent_status", "accessRights", "language"]
EXACT_MATCH_FIELDS = [
    "record_id", "interview_date", "interviewer",
    "language", "spatial", "consent_status", "accessRights",
]
LIST_FIELDS = ["keywords"]
FREE_TEXT_FIELDS = ["title", "abstract"]


# ── Timecodes & segmentation masses ─────────────────────────────────────────
def timecode_to_seconds(tc: str) -> int:
    """Parse ``'HH:MM:SS'`` / ``'MM:SS'`` / ``'SS'`` into seconds.

    Raises ``ValueError`` for anything unparseable (e.g. a model emitting a free
    text timecode), so the caller can record it as a scoring error instead of
    silently mis-scoring or crashing the whole run.
    """
    raw = str(tc).strip()
    parts = raw.split(":")
    if not raw or len(parts) > 3:
        raise ValueError(f"Unparseable timecode: {tc!r}")
    try:
        nums = [int(p) for p in parts]
    except ValueError as e:
        raise ValueError(f"Unparseable timecode: {tc!r}") from e
    if any(n < 0 for n in nums):
        raise ValueError(f"Negative timecode component: {tc!r}")
    while len(nums) < 3:
        nums = [0] + nums
    h, m, s = nums
    return h * 3600 + m * 60 + s


def _segment_end(seg: dict) -> str:
    """Return a segment's ``end`` timecode or raise if absent/empty.

    A missing ``end`` is treated as an error rather than silently defaulting to
    ``"0"`` (which previously could surface as a misleading 0.0 score).
    """
    end = seg.get("end")
    if end is None or str(end).strip() == "":
        raise ValueError(f"Segment missing 'end' timecode: {seg!r}")
    return end


def segments_to_masses(segments: list[dict], total_units: int,
                       total_duration: Optional[float] = None) -> list[int]:
    """Map timecoded segment boundaries onto a shared unit axis and return
    segeval masses.

    Each segment's END timecode is projected to a character offset proportional
    to its position in the interview timeline (``total_duration`` seconds). The
    document end is a shared boundary and is not treated as a hypothesised
    boundary. Gold and prediction must be mapped with the *same*
    ``total_duration`` so their offsets are comparable; both then sum to
    ``total_units``.

    Raises ``ValueError`` if a segment lacks a parseable ``end`` timecode.

    This replaces the earlier even-split heuristic, which measured segment-count
    differences rather than boundary placement.
    """
    if total_units <= 0:
        total_units = 1
    if not segments:
        return [total_units]
    if not total_duration or total_duration <= 0:
        total_duration = timecode_to_seconds(_segment_end(segments[-1]))
    if total_duration <= 0:
        # No usable timeline -> fall back to an even split.
        n = len(segments)
        base = total_units // n
        masses = [base] * n
        masses[-1] += total_units - sum(masses)
        return masses
    bounds = []
    for seg in segments:
        off = int(round(timecode_to_seconds(_segment_end(seg)) / total_duration * total_units))
        off = max(0, min(off, total_units))
        if 0 < off < total_units:
            bounds.append(off)
    bounds = sorted(set(bounds)) + [total_units]
    masses, prev = [], 0
    for b in bounds:
        masses.append(b - prev)
        prev = b
    return masses


def evaluate_segmentation(gold_record: dict, prediction: dict) -> dict:
    """Compute WindowDiff and Pk between gold and predicted segmentation.

    All timecode parsing and mass construction happen inside the guarded block,
    so a malformed *prediction* (bad/missing timecode from a model) is recorded
    as an ``error`` for that record rather than aborting the whole benchmark.
    """
    transcript = gold_record.get("transcript", "")
    total = max(len(transcript), 1)
    gold_segments = gold_record.get("timecoded_segments", [])
    pred_segments = prediction.get("segments", [])

    result = {
        "n_gold": len(gold_segments),
        "n_pred": len(pred_segments),
        "count_diff": abs(len(gold_segments) - len(pred_segments)),
        "window_diff": None,
        "pk": None,
    }
    if not SEGEVAL_AVAILABLE:
        result["note"] = "segeval not installed"
        return result
    if not gold_segments or not pred_segments:
        return result
    try:
        # Shared timeline: the gold segmentation covers the whole interview, so
        # its final end timecode defines the duration for both segmentations.
        total_duration = timecode_to_seconds(_segment_end(gold_segments[-1]))
        gold_masses = segments_to_masses(gold_segments, total, total_duration)
        pred_masses = segments_to_masses(pred_segments, total, total_duration)
        result["window_diff"] = round(float(segeval.window_diff(tuple(pred_masses), tuple(gold_masses))), 3)
        result["pk"] = round(float(segeval.pk(tuple(pred_masses), tuple(gold_masses))), 3)
    except Exception as e:
        result["window_diff"] = None
        result["pk"] = None
        result["error"] = str(e)
    return result


# ── Metadata extraction ─────────────────────────────────────────────────────
def evaluate_metadata(gold: dict, prediction: dict,
                      exact_match_fields: Optional[list[str]] = None,
                      list_fields: Optional[list[str]] = None,
                      free_text_fields: Optional[list[str]] = None) -> dict:
    """Per-field comparison. Returns a dict with per-field outcomes.

    Exact-match fields are compared verbatim; list fields (keywords) get
    set precision/recall/F1; free-text fields are *not* auto-scored — they are
    flagged for manual qualitative review (auto-scoring against a human gold is
    methodologically circular at this stage).
    """
    exact_match_fields = exact_match_fields if exact_match_fields is not None else EXACT_MATCH_FIELDS
    list_fields = list_fields if list_fields is not None else LIST_FIELDS
    free_text_fields = free_text_fields if free_text_fields is not None else FREE_TEXT_FIELDS

    outcomes: dict = {}
    for field_ in exact_match_fields:
        g = gold.get(field_, "")
        p = prediction.get(field_, "")
        outcomes[field_] = {"gold": g, "pred": p, "match": g == p}
    for field_ in list_fields:
        g = set(gold.get(field_, []))
        p = set(prediction.get(field_, []))
        if not g and not p:
            precision = recall = f1 = 1.0
        else:
            tp = len(g & p)
            precision = tp / len(p) if p else 0.0
            recall = tp / len(g) if g else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        outcomes[field_] = {
            "gold": sorted(g), "pred": sorted(p),
            "precision": precision, "recall": recall, "f1": f1,
        }
    for field_ in free_text_fields:
        g = gold.get(field_, "")
        p = prediction.get(field_, "")
        outcomes[field_ + "__free"] = {
            "gold_len": len(g), "pred_len": len(p),
            "review_required": True,
        }
    return outcomes
