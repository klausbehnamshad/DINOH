"""Tests for oh_eval.schema — the evaluation record contract.

A valid mini-record passes; targeted negatives exercise each enforced rule.
The real corpus is also checked so the contract and the goldstandard cannot
drift apart.
"""

import copy
import json
from pathlib import Path

import pytest

from oh_eval.schema import (
    load_schema,
    validate_eval_record,
    validate_luxoh_record,
    validate_corpus,
    contiguity_errors,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = REPO_ROOT / "data" / "corpus_synthetic.json"


def _annotation(topic="border crossing"):
    return {
        "selected_topic": topic,
        "selected_frame": "everyday routine",
        "selected_rhetorical_pattern": "enumeration",
        "selected_discursive_position": "habitualised commuter",
        "gold_rationale": "because reasons",
        "annotator_id": "[ANNOTATOR_1]",
        "alternative_codings": [],
    }


def valid_record():
    return {
        "record_id": "2025-09-12_CDH_0001",
        "interview_date": "2025-09-12",
        "interviewer": "[INTERVIEWER_1]",
        "consent_status": "research-only",
        "accessRights": "restricted",
        "title": "Synthetic DE-01",
        "interviewee_display": "DE-Speaker 01 (synthetic)",
        "language": "deu",
        "spatial": "Saarbrücken",
        "keywords": ["Grenze", "Arbeit"],
        "abstract": "A short synthetic abstract.",
        "synthetic": True,
        "transcript": "Some transcript text.",
        "interpretive_layer": {
            "narrative_arc": "from routine to reflection",
            "central_tension": "identity vs attribution",
            "positioning_summary": "actor and witness",
            "gold_rationale": "arc reasoning",
            "annotator_id": "[ANNOTATOR_1]",
        },
        "timecoded_segments": [
            {"start": "00:00:00", "end": "00:00:35", "label": "A", "analytical_annotations": _annotation()},
            {"start": "00:00:35", "end": "00:01:10", "label": "B", "analytical_annotations": _annotation("identity")},
        ],
    }


# ── schema loading ───────────────────────────────────────────────────────────
def test_load_schema_is_draft07():
    for kind in ("eval", "luxoh"):
        schema = load_schema(kind)
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"


# ── positive ─────────────────────────────────────────────────────────────────
def test_valid_record_passes_eval_and_luxoh():
    rec = valid_record()
    assert validate_eval_record(rec) == []
    assert validate_luxoh_record(rec) == []


# ── negatives: required eval-specific fields ─────────────────────────────────
def test_missing_synthetic_fails_eval_but_not_luxoh():
    rec = valid_record()
    del rec["synthetic"]
    assert validate_eval_record(rec)            # eval contract broken
    assert validate_luxoh_record(rec) == []     # still LuxOH-minimal valid


def test_synthetic_must_be_true():
    rec = valid_record()
    rec["synthetic"] = False
    errs = validate_eval_record(rec)
    assert any("synthetic" in e for e in errs)


def test_missing_transcript_fails():
    rec = valid_record()
    del rec["transcript"]
    assert any("transcript" in e for e in validate_eval_record(rec))


def test_empty_transcript_fails():
    rec = valid_record()
    rec["transcript"] = ""
    assert any("transcript" in e for e in validate_eval_record(rec))


def test_missing_interpretive_layer_fails():
    rec = valid_record()
    del rec["interpretive_layer"]
    assert any("interpretive_layer" in e for e in validate_eval_record(rec))


def test_interpretive_layer_missing_field_fails():
    rec = valid_record()
    del rec["interpretive_layer"]["central_tension"]
    assert any("interpretive_layer" in e for e in validate_eval_record(rec))


def test_interpretive_layer_extra_field_rejected():
    rec = valid_record()
    rec["interpretive_layer"]["unexpected"] = "x"
    assert validate_eval_record(rec)  # additionalProperties: false


# ── negatives: analytical annotations ────────────────────────────────────────
def test_missing_analytical_annotations_fails():
    rec = valid_record()
    del rec["timecoded_segments"][0]["analytical_annotations"]
    assert any("analytical_annotations" in e for e in validate_eval_record(rec))


def test_annotation_missing_field_fails():
    rec = valid_record()
    del rec["timecoded_segments"][0]["analytical_annotations"]["selected_topic"]
    assert any("selected_topic" in e for e in validate_eval_record(rec))


# ── negatives: timecodes ─────────────────────────────────────────────────────
def test_bad_timecode_format_fails():
    rec = valid_record()
    rec["timecoded_segments"][0]["end"] = "1:2"
    assert validate_eval_record(rec)


def test_out_of_range_timecode_fails():
    rec = valid_record()
    rec["timecoded_segments"][0]["end"] = "00:99:00"  # 99 minutes invalid
    assert validate_eval_record(rec)


# ── negatives: contiguity (Python semantic check) ────────────────────────────
def test_non_contiguous_segments_flagged():
    rec = valid_record()
    rec["timecoded_segments"][1]["start"] = "00:00:40"  # gold end was 00:00:35
    errs = validate_eval_record(rec)
    assert any("not contiguous" in e for e in errs)


def test_first_segment_must_start_at_origin():
    rec = valid_record()
    rec["timecoded_segments"][0]["start"] = "00:00:05"
    errs = validate_eval_record(rec)
    assert any("start at 00:00:00" in e for e in errs)


def test_start_not_before_end_flagged():
    segs = [
        {"start": "00:00:30", "end": "00:00:30", "label": "x", "analytical_annotations": _annotation()},
    ]
    errs = contiguity_errors(segs)
    assert any("not before end" in e for e in errs)


def test_contiguity_skips_when_timecode_missing():
    # Missing 'end' -> structural schema's job, contiguity stays silent.
    segs = [{"start": "00:00:00", "label": "x"}]
    assert contiguity_errors(segs) == []


# ── real corpus ──────────────────────────────────────────────────────────────
@pytest.mark.skipif(not CORPUS_PATH.exists(), reason="corpus file not present")
def test_real_corpus_passes_eval_contract():
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    report = validate_corpus(corpus, kind="eval")
    invalid = {rid: errs for rid, errs in report.items() if errs}
    assert invalid == {}, f"corpus records failing eval contract: {invalid}"
    assert len(report) == 28
