"""Interop export for DINOH: WebVTT chapters + OHMS-compatible XML index.

Turns DINOH segmentation/metadata output into two viewer-friendly standard
formats so results can be played back / indexed in common tools (any HTML5
player for WebVTT; the OHMS / Aviary ecosystem for the XML index) without
leaving the governance layer.

GOVERNANCE — the export is itself access-aware (allowlist / default-deny)
=========================================================================
Full text is emitted ONLY for records that are BOTH::

    accessRights == "open"  AND  consent_status == "public"

Everything else (accessRights restricted/closed; consent_status
research-only/teaching/embargoed) exports *structure only*: timecodes plus
neutral segment titles, nothing more.

NEVER exported, under ANY access level — deliberate, tested decisions
--------------------------------------------------------------------
* ``analytical_annotations`` — the L2 interpretive layer carried on
  ``timecoded_segments``. That is analysis IP, not distribution/index data,
  so :func:`normalize_segments` intentionally maps only ``{start, end,
  title}`` and drops L2. (See ``test_analytical_annotations_never_exported``.)
* ``anchor_quote`` — a direct-quote field flagged ``x-pii: flag`` on analysis
  ``units``. Emitted only when the open+public allowlist passes; otherwise
  never. (See ``test_redaction_anchor_quote_never_leaks``.)

The module is stdlib-only (no pandas) and reuses ``timecode_to_seconds`` from
``oh_eval.metrics`` so timecode parsing has a single source of truth.
"""

from __future__ import annotations

from typing import Optional
from xml.etree import ElementTree as ET

from .metrics import timecode_to_seconds

# ── Redaction allowlist ──────────────────────────────────────────────────────
# Full text only for this exact pair; default-deny for everything else.
FULLTEXT_ACCESS_RIGHTS = "open"
FULLTEXT_CONSENT_STATUS = "public"


def fulltext_allowed(meta: dict) -> bool:
    """True iff the record's access markers permit emitting full text.

    Allowlist, not denylist: only ``accessRights == "open"`` AND
    ``consent_status == "public"`` unlock synopsis / anchor_quote / transcript.
    A missing marker is treated as *not* allowed.
    """
    return (
        meta.get("accessRights") == FULLTEXT_ACCESS_RIGHTS
        and meta.get("consent_status") == FULLTEXT_CONSENT_STATUS
    )


# ── Timecodes ────────────────────────────────────────────────────────────────
def seconds_to_webvtt(seconds: float) -> str:
    """Format seconds as a WebVTT timestamp ``HH:MM:SS.mmm``.

    Raises ``ValueError`` for negative input so a malformed upstream timecode
    surfaces as an error rather than a silently wrong cue.
    """
    if seconds < 0:
        raise ValueError(f"Negative time: {seconds!r}")
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    m = (total_s // 60) % 60
    h = total_s // 3600
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


# ── Segment normalisation ────────────────────────────────────────────────────
def normalize_segments(segments: list[dict]) -> list[dict]:
    """Reduce heterogeneous segment/unit dicts to a canonical export shape.

    Accepts either representation:

    * ``timecoded_segments`` items — ``{start, end, label, analytical_annotations}``
    * analysis ``units`` items — ``{start, end, topic, anchor_quote, ...}``

    and returns, per item, ONLY::

        {"start": str, "end": str, "title": str, "anchor_quote": str|None}

    ``title`` comes from ``label`` (segments) or ``topic`` (units). Every other
    field — crucially the L2 ``analytical_annotations`` and all analysis extras
    (``frame``, ``confidence``, ``char_span`` …) — is intentionally dropped;
    only ``anchor_quote`` is carried through, and it is gated downstream.

    Raises ``ValueError`` if an item lacks a non-empty ``start`` or ``end``.
    """
    out: list[dict] = []
    for seg in segments:
        start = seg.get("start")
        end = seg.get("end")
        if start is None or str(start).strip() == "":
            raise ValueError(f"Segment missing 'start' timecode: {seg!r}")
        if end is None or str(end).strip() == "":
            raise ValueError(f"Segment missing 'end' timecode: {seg!r}")
        title = seg.get("label")
        if title is None:
            title = seg.get("topic")
        anchor = seg.get("anchor_quote")  # present only on analysis units
        out.append({
            "start": str(start),
            "end": str(end),
            "title": "" if title is None else str(title),
            "anchor_quote": None if anchor is None else str(anchor),
        })
    return out


# ── WebVTT ───────────────────────────────────────────────────────────────────
def segments_to_webvtt(meta: dict, segments: list[dict],
                       *, allow_fulltext: Optional[bool] = None) -> str:
    """Render segments as a WebVTT chapter track.

    Cue payload is the neutral segment *title* only — never ``anchor_quote`` or
    transcript — so the VTT is safe to ship at any access level. ``meta`` and
    ``allow_fulltext`` are accepted for signature symmetry with the OHMS export;
    the VTT body does not vary by access level (titles are non-sensitive labels).
    """
    norm = normalize_segments(segments)
    lines = ["WEBVTT", ""]
    title = meta.get("title")
    if title:
        lines += [f"NOTE {title}", ""]
    for i, seg in enumerate(norm, start=1):
        start = seconds_to_webvtt(timecode_to_seconds(seg["start"]))
        end = seconds_to_webvtt(timecode_to_seconds(seg["end"]))
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(seg["title"])
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


# ── OHMS XML index ───────────────────────────────────────────────────────────
def record_to_ohms_xml(meta: dict, segments: list[dict],
                       *, allow_fulltext: Optional[bool] = None) -> str:
    """Render an OHMS-style ``cdoc`` XML index.

    Header fields come from the metadata record; one ``point`` per segment.
    Under the open+public allowlist, the interview-level ``abstract`` is emitted
    as the record ``synopsis`` and each unit's ``anchor_quote`` as the point's
    ``partial_transcript``. Outside the allowlist, neither is written — only
    time + neutral title survive.

    Structure follows the OHMS ``cdoc`` convention; full XSD validation against
    the official OHMS schema is a pre-publication follow-up (see module/plan).
    Built with ``xml.etree`` so output is always well-formed and escaped.
    """
    if allow_fulltext is None:
        allow_fulltext = fulltext_allowed(meta)
    norm = normalize_segments(segments)

    root = ET.Element("cdoc")
    record = ET.SubElement(root, "record")

    def _field(parent: ET.Element, tag: str, value) -> None:
        el = ET.SubElement(parent, tag)
        el.text = "" if value is None else str(value)

    _field(record, "record_id", meta.get("record_id"))
    _field(record, "title", meta.get("title"))
    _field(record, "date", meta.get("interview_date"))
    _field(record, "interviewer", meta.get("interviewer"))
    _field(record, "language", meta.get("language"))
    _field(record, "coverage", meta.get("spatial"))
    # Usage/rights carried verbatim so downstream tooling can re-check the gate.
    _field(record, "usage", meta.get("accessRights"))
    _field(record, "consent_status", meta.get("consent_status"))
    kws = meta.get("keywords") or []
    _field(record, "keywords", ", ".join(str(k) for k in kws))
    # Interview-level synopsis (abstract) only under the allowlist.
    _field(record, "synopsis", meta.get("abstract") if allow_fulltext else "")

    index = ET.SubElement(record, "index")
    for seg in norm:
        point = ET.SubElement(index, "point")
        _field(point, "time", str(int(round(timecode_to_seconds(seg["start"])))))
        _field(point, "title", seg["title"])
        # Direct-quote (PII) only under the allowlist; otherwise omitted entirely.
        if allow_fulltext and seg.get("anchor_quote"):
            _field(point, "partial_transcript", seg["anchor_quote"])

    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


# ── Dublin Core (helper / OHMS header source) ────────────────────────────────
def to_dublin_core(meta: dict, *, allow_fulltext: Optional[bool] = None) -> dict:
    """Map a metadata record onto Dublin Core terms.

    ``dc:description`` (the abstract) is gated behind the allowlist; the rest are
    structural bibliographic fields and are always included.
    """
    if allow_fulltext is None:
        allow_fulltext = fulltext_allowed(meta)
    dc = {
        "dc:identifier": meta.get("record_id"),
        "dc:title": meta.get("title"),
        "dc:date": meta.get("interview_date"),
        "dc:creator": meta.get("interviewer"),
        "dc:language": meta.get("language"),
        "dc:coverage": meta.get("spatial"),
        "dc:subject": list(meta.get("keywords") or []),
        "dc:rights": meta.get("accessRights"),
    }
    dc["dc:description"] = meta.get("abstract") if allow_fulltext else None
    return dc
