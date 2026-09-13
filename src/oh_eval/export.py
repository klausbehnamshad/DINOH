"""Format exporters for DINOH synthetic examples: WebVTT and OHMS-style XML.

These functions do not assess identifying content or authorise publication.
OHMS uses declared accessRights == "open" and consent_status == "public" to
decide whether to include abstracts and anchor quotations only when
allow_fulltext is None. Explicit True overrides that metadata decision;
False omits those fields. Other metadata and titles are still emitted.

WebVTT emits supplied record and segment titles regardless of access markers
and ignores allow_fulltext. Titles are not checked for personal information.
The analytical_annotations field is not mapped into either export; that is
not a guarantee that other fields lack interpretive or personal data.
OHMS output has not been validated against the official XSD.

Timecode parsing uses oh_eval.metrics.timecode_to_seconds."""

from __future__ import annotations

from typing import Optional
from xml.etree import ElementTree as ET

from .metrics import timecode_to_seconds

# ── Default metadata decision ──────────────────────────────────────────────────────
# Used only when no explicit allow_fulltext value is supplied.
FULLTEXT_ACCESS_RIGHTS = "open"
FULLTEXT_CONSENT_STATUS = "public"


def fulltext_allowed(meta: dict) -> bool:
    """Return the default text-inclusion decision from declared metadata.

    Only accessRights == "open" and consent_status == "public" produce True.
    Callers can override this decision. It neither establishes project
    authorisation nor inspects the text."""
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
    """Render supplied titles as a WebVTT chapter track.

    Cue payload contains the segment title; the record title becomes a NOTE
    when present. Anchor quotations and transcript fields are not mapped.
    Access markers and allow_fulltext do not change the output. Titles may
    identify people and require appropriate input selection and review."""
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
    """Render an OHMS-style cdoc XML index.

    With allow_fulltext=None, declared open+public metadata controls whether
    the abstract becomes synopsis and anchor_quote becomes partial_transcript.
    Explicit True/False overrides that decision. Other metadata and segment
    titles are emitted independently and may contain identifying information.

    ElementTree serializes the output. Official OHMS XSD validation remains
    outstanding; no tested external-portal connector is provided."""
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
    # Declared rights are carried verbatim; they do not establish authorisation.
    _field(record, "usage", meta.get("accessRights"))
    _field(record, "consent_status", meta.get("consent_status"))
    kws = meta.get("keywords") or []
    _field(record, "keywords", ", ".join(str(k) for k in kws))
    # Synopsis follows the resolved metadata decision or caller override.
    _field(record, "synopsis", meta.get("abstract") if allow_fulltext else "")

    index = ET.SubElement(record, "index")
    for seg in norm:
        point = ET.SubElement(index, "point")
        _field(point, "time", str(int(round(timecode_to_seconds(seg["start"])))))
        _field(point, "title", seg["title"])
        # Quote follows the resolved decision or override; no content inspection.
        if allow_fulltext and seg.get("anchor_quote"):
            _field(point, "partial_transcript", seg["anchor_quote"])

    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


# ── Dublin Core (helper / OHMS header source) ────────────────────────────────
def to_dublin_core(meta: dict, *, allow_fulltext: Optional[bool] = None) -> dict:
    """Map a metadata record onto Dublin Core terms.

    dc:description follows the metadata decision when allow_fulltext=None and
    otherwise the explicit override. Other bibliographic fields are always
    included and may contain identifying information."""
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
