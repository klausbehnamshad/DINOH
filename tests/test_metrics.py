"""Unit tests for oh_eval.metrics.

These lock in the metric behaviour that was the most fragile part of the
notebook: timecode parsing, mass construction, and the segmentation metric.
"""

import pytest

from oh_eval import metrics
from oh_eval.metrics import (
    timecode_to_seconds,
    segments_to_masses,
    evaluate_segmentation,
    evaluate_metadata,
)


# ── A small synthetic gold record (4 contiguous timecoded segments) ──────────
def gold_record(transcript_len: int = 1000) -> dict:
    return {
        "record_id": "2025-09-12_CDH_0001",
        "language": "deu",
        "transcript": "x" * transcript_len,
        "timecoded_segments": [
            {"start": "00:00:00", "end": "00:00:30", "label": "a"},
            {"start": "00:00:30", "end": "00:01:00", "label": "b"},
            {"start": "00:01:00", "end": "00:01:40", "label": "c"},
            {"start": "00:01:40", "end": "00:02:00", "label": "d"},
        ],
    }


def merge_last_two(segs: list[dict]) -> list[dict]:
    """Replicates the segmentation stub's single missed-boundary error."""
    if len(segs) >= 3:
        return segs[:-2] + [{
            "start": segs[-2]["start"], "end": segs[-1]["end"], "label": segs[-2]["label"],
        }]
    return segs


def drop_last(segs: list[dict]) -> list[dict]:
    return segs[:-1] if len(segs) > 1 else segs


# ── timecode parsing ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("tc,expected", [
    ("00:00:00", 0),
    ("00:00:35", 35),
    ("00:02:00", 120),
    ("01:00:00", 3600),
    ("02:00", 120),   # MM:SS
    ("45", 45),       # SS
])
def test_timecode_to_seconds(tc, expected):
    assert timecode_to_seconds(tc) == expected


@pytest.mark.parametrize("bad", ["bad", "", "1:2:3:4", "ab:cd", "12:xx"])
def test_timecode_bad_raises(bad):
    with pytest.raises(ValueError):
        timecode_to_seconds(bad)


# ── mass construction invariants ─────────────────────────────────────────────
def test_masses_sum_to_total():
    rec = gold_record(1000)
    segs = rec["timecoded_segments"]
    masses = segments_to_masses(segs, 1000, timecode_to_seconds(segs[-1]["end"]))
    assert sum(masses) == 1000


def test_masses_reflect_durations_not_uniform():
    """The third segment is longer (40s vs 30/30/20), so its mass must differ
    from a naive even split (which would give 250 each)."""
    rec = gold_record(1200)
    segs = rec["timecoded_segments"]
    masses = segments_to_masses(segs, 1200, 120.0)
    assert masses == [300, 300, 400, 200]
    assert len(set(masses)) > 1  # not uniform


def test_masses_empty_segments():
    assert segments_to_masses([], 500) == [500]


def test_masses_zero_total_units_guarded():
    assert sum(segments_to_masses(gold_record()["timecoded_segments"], 0)) == 1


def test_masses_fallback_even_split_without_timeline():
    # Zero-duration timeline (all timecodes identical) -> even split fallback.
    segs = [{"start": "0", "end": "0", "label": x} for x in "abcd"]
    masses = segments_to_masses(segs, 100, total_duration=0)
    assert sum(masses) == 100
    assert len(masses) == 4


# ── segmentation metric semantics ────────────────────────────────────────────
@pytest.mark.skipif(not metrics.SEGEVAL_AVAILABLE, reason="segeval not installed")
def test_identical_segmentation_scores_zero():
    rec = gold_record()
    pred = {"segments": rec["timecoded_segments"]}
    out = evaluate_segmentation(rec, pred)
    assert out["window_diff"] == 0.0
    assert out["pk"] == 0.0


@pytest.mark.skipif(not metrics.SEGEVAL_AVAILABLE, reason="segeval not installed")
def test_drop_last_segment_is_a_noop_boundary_error():
    """Regression: dropping the FINAL segment is not a real boundary error under
    offset-based masses (the document end is a shared boundary). This is exactly
    why the stub was changed away from drop-last."""
    rec = gold_record()
    pred = {"segments": drop_last(rec["timecoded_segments"])}
    out = evaluate_segmentation(rec, pred)
    assert out["window_diff"] == 0.0


@pytest.mark.skipif(not metrics.SEGEVAL_AVAILABLE, reason="segeval not installed")
def test_merge_last_two_is_a_real_boundary_error():
    rec = gold_record()
    pred = {"segments": merge_last_two(rec["timecoded_segments"])}
    out = evaluate_segmentation(rec, pred)
    assert out["window_diff"] > 0.0
    assert out["count_diff"] == 1
    assert out["n_pred"] == 3


@pytest.mark.skipif(not metrics.SEGEVAL_AVAILABLE, reason="segeval not installed")
def test_malformed_pred_timecode_recorded_as_error():
    """A model emitting a bad timecode must not abort the run — it is recorded
    as an error for that record."""
    rec = gold_record()
    pred = {"segments": [{"start": "00:00:00", "end": "bad", "label": "x"}]}
    out = evaluate_segmentation(rec, pred)
    assert out["window_diff"] is None
    assert out["pk"] is None
    assert "error" in out


@pytest.mark.skipif(not metrics.SEGEVAL_AVAILABLE, reason="segeval not installed")
def test_pred_missing_end_recorded_as_error():
    rec = gold_record()
    pred = {"segments": [{"start": "00:00:00", "label": "x"}]}  # no 'end'
    out = evaluate_segmentation(rec, pred)
    assert out["window_diff"] is None
    assert "error" in out


def test_segmentation_reports_counts_without_segeval(monkeypatch):
    monkeypatch.setattr(metrics, "SEGEVAL_AVAILABLE", False)
    rec = gold_record()
    out = evaluate_segmentation(rec, {"segments": merge_last_two(rec["timecoded_segments"])})
    assert out["window_diff"] is None
    assert out["note"] == "segeval not installed"
    assert out["count_diff"] == 1


# ── metadata metric ──────────────────────────────────────────────────────────
def test_metadata_exact_match():
    gold = {"record_id": "r1", "title": "T", "language": "deu"}
    out = evaluate_metadata(gold, dict(gold))
    assert out["record_id"]["match"] is True
    assert out["language"]["match"] is True


def test_metadata_mismatch_detected():
    gold = {"record_id": "r1", "language": "deu"}
    pred = {"record_id": "r1", "language": "eng"}
    out = evaluate_metadata(gold, pred)
    assert out["language"]["match"] is False


def test_metadata_keyword_prf():
    gold = {"keywords": ["a", "b", "c", "d"]}
    pred = {"keywords": ["a", "b"]}  # truncated, like the stub
    out = evaluate_metadata(gold, pred)
    kw = out["keywords"]
    assert kw["precision"] == 1.0
    assert kw["recall"] == 0.5
    assert kw["f1"] == pytest.approx(2 / 3)


def test_metadata_keyword_both_empty_is_perfect():
    out = evaluate_metadata({"keywords": []}, {"keywords": []})
    assert out["keywords"]["f1"] == 1.0


def test_metadata_free_text_flagged_not_scored():
    out = evaluate_metadata({"abstract": "long text"}, {"abstract": ""})
    assert out["abstract__free"]["review_required"] is True
    assert out["abstract__free"]["gold_len"] == 9
    assert out["abstract__free"]["pred_len"] == 0


def test_title_is_free_text_only_not_exact_scored():
    """Regression: title must not be auto-scored as an exact-match field
    (README/dashboard promise free-text fields are reviewed qualitatively)."""
    assert "title" not in metrics.EXACT_MATCH_FIELDS
    assert "title" in metrics.FREE_TEXT_FIELDS
    out = evaluate_metadata({"title": "A real title"}, {"title": "Different"})
    assert "title" not in out               # no exact-match outcome
    assert out["title__free"]["review_required"] is True
