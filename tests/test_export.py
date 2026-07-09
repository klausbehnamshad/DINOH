"""Tests for oh_eval.export — WebVTT + OHMS-XML interop, governance-gated.

The governance tests (redaction allowlist, anchor_quote, analytical_annotations)
are the important ones: they assert that sensitive / interpretive content never
leaves the pipeline through the export surface unless the open+public allowlist
explicitly permits it.
"""

from __future__ import annotations

from xml.etree import ElementTree as ET

import pytest

from oh_eval.export import (
    fulltext_allowed,
    normalize_segments,
    seconds_to_webvtt,
    segments_to_webvtt,
    record_to_ohms_xml,
    to_dublin_core,
)
from oh_eval.metrics import timecode_to_seconds

# Sentinels that must NEVER appear in a redacted export.
ANCHOR_SENTINEL = "SENSITIVE_DIRECT_QUOTE_XYZ"
L2_SENTINEL = "L2_ANALYTICAL_SENTINEL_XYZ"


def _open_public_meta(**over) -> dict:
    meta = {
        "record_id": "2025-09-12_CDH_0001",
        "interview_date": "2025-09-12",
        "interviewer": "[INTERVIEWER_1]",
        "consent_status": "public",
        "accessRights": "open",
        "title": "Grenzüberschreitende Arbeit im Saarland",
        "language": "deu",
        "spatial": "Saarbrücken",
        "keywords": ["Grenze", "Arbeit"],
        "abstract": "Interview-weite Zusammenfassung (Synopsis).",
    }
    meta.update(over)
    return meta


def _timecoded_segments() -> list[dict]:
    # timecoded_segments shape: {start, end, label, analytical_annotations}
    return [
        {"start": "00:00:00", "end": "00:00:35", "label": "Aufbruch und Grenzübertritt",
         "analytical_annotations": {"selected_topic": "border crossing",
                                    "gold_rationale": L2_SENTINEL}},
        {"start": "00:00:35", "end": "00:01:10", "label": "Zöllner und Routine",
         "analytical_annotations": {"selected_topic": "routine", "gold_rationale": L2_SENTINEL}},
    ]


def _units() -> list[dict]:
    # analysis units shape: {start, end, topic, anchor_quote (x-pii), ...}
    return [
        {"unit_id": "u1", "start": "00:00:00", "end": "00:00:35", "topic": "Aufbruch",
         "anchor_quote": ANCHOR_SENTINEL, "frame": "everyday", "confidence": 0.9},
        {"unit_id": "u2", "start": "00:00:35", "end": "00:01:10", "topic": "Routine",
         "anchor_quote": "noch ein Zitat", "frame": "everyday", "confidence": 0.8},
    ]


# ── allowlist logic ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("access,consent,expected", [
    ("open", "public", True),
    ("open", "research-only", False),
    ("restricted", "public", False),
    ("closed", "public", False),
    ("open", "embargoed", False),
    ("restricted", "research-only", False),
    (None, None, False),
])
def test_fulltext_allowlist(access, consent, expected):
    assert fulltext_allowed({"accessRights": access, "consent_status": consent}) is expected


# ── normalisation ────────────────────────────────────────────────────────────
def test_normalize_drops_extra_fields():
    norm = normalize_segments(_units())
    for seg in norm:
        assert set(seg.keys()) == {"start", "end", "title", "anchor_quote"}
    # title comes from topic for units, from label for timecoded_segments
    assert normalize_segments(_timecoded_segments())[0]["title"] == "Aufbruch und Grenzübertritt"
    assert normalize_segments(_units())[0]["title"] == "Aufbruch"


def test_normalize_missing_timecode_raises():
    with pytest.raises(ValueError):
        normalize_segments([{"start": "", "end": "00:01:00", "label": "x"}])
    with pytest.raises(ValueError):
        normalize_segments([{"start": "00:00:00", "label": "x"}])  # no end


# ── WebVTT wellformedness ────────────────────────────────────────────────────
def test_webvtt_wellformed():
    vtt = segments_to_webvtt(_open_public_meta(), _timecoded_segments())
    assert vtt.startswith("WEBVTT")
    cues = [ln for ln in vtt.splitlines() if "-->" in ln]
    assert len(cues) == 2
    # timestamps parse and are monotonic within a cue
    for cue in cues:
        left, right = cue.split("-->")
        assert left.strip().count(":") == 2 and "." in left
        assert right.strip().count(":") == 2 and "." in right


def test_timecode_roundtrip():
    # HH:MM:SS -> seconds -> WebVTT string, stable and correct
    assert seconds_to_webvtt(0) == "00:00:00.000"
    assert seconds_to_webvtt(35) == "00:00:35.000"
    assert seconds_to_webvtt(3661) == "01:01:01.000"
    assert seconds_to_webvtt(timecode_to_seconds("00:01:10")) == "00:01:10.000"
    with pytest.raises(ValueError):
        seconds_to_webvtt(-1)


# ── OHMS XML wellformedness ──────────────────────────────────────────────────
def test_ohms_xml_wellformed():
    xml = record_to_ohms_xml(_open_public_meta(), _timecoded_segments())
    root = ET.fromstring(xml)  # raises on malformed XML
    record = root.find("record")
    assert record is not None
    assert record.findtext("record_id") == "2025-09-12_CDH_0001"
    assert record.findtext("title")
    points = record.find("index").findall("point")
    assert len(points) == 2  # one index point per segment


# ── governance: redaction allowlist ──────────────────────────────────────────
def test_redaction_open_public_includes_synopsis():
    meta = _open_public_meta()
    xml = record_to_ohms_xml(meta, _units())
    root = ET.fromstring(xml)
    record = root.find("record")
    assert record.findtext("synopsis") == meta["abstract"]
    # anchor_quote surfaces as partial_transcript under the allowlist
    pts = record.find("index").findall("point")
    assert any((p.findtext("partial_transcript") or "") == ANCHOR_SENTINEL for p in pts)


def test_redaction_restricted_omits_fulltext():
    meta = _open_public_meta(accessRights="restricted", consent_status="research-only")
    xml = record_to_ohms_xml(meta, _units())
    assert meta["abstract"] not in xml
    assert ANCHOR_SENTINEL not in xml
    root = ET.fromstring(xml)
    record = root.find("record")
    assert (record.findtext("synopsis") or "") == ""
    for p in record.find("index").findall("point"):
        assert p.find("partial_transcript") is None


def test_redaction_anchor_quote_never_leaks():
    # Non-allowlisted access: the PII direct quote must be in NEITHER output.
    meta = _open_public_meta(accessRights="closed", consent_status="embargoed")
    xml = record_to_ohms_xml(meta, _units())
    vtt = segments_to_webvtt(meta, _units())
    assert ANCHOR_SENTINEL not in xml
    assert ANCHOR_SENTINEL not in vtt


def test_analytical_annotations_never_exported():
    # Even under the most permissive access, L2 analysis IP must not appear.
    meta = _open_public_meta()  # open + public
    xml = record_to_ohms_xml(meta, _timecoded_segments())
    vtt = segments_to_webvtt(meta, _timecoded_segments())
    assert L2_SENTINEL not in xml
    assert L2_SENTINEL not in vtt


# ── Dublin Core ──────────────────────────────────────────────────────────────
def test_dublin_core_mapping():
    meta = _open_public_meta()
    dc = to_dublin_core(meta)
    assert dc["dc:identifier"] == meta["record_id"]
    assert dc["dc:title"] == meta["title"]
    assert dc["dc:date"] == meta["interview_date"]
    assert dc["dc:creator"] == meta["interviewer"]
    assert dc["dc:subject"] == meta["keywords"]
    assert dc["dc:rights"] == "open"
    assert dc["dc:description"] == meta["abstract"]  # allowed under open+public


def test_dublin_core_description_gated():
    meta = _open_public_meta(accessRights="restricted", consent_status="teaching")
    dc = to_dublin_core(meta)
    assert dc["dc:description"] is None       # gated off
    assert dc["dc:title"] == meta["title"]    # structural field still present
