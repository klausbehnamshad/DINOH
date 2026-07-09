"""Schema loading and validation for the C²DH Oral History benchmark.

Two contracts:

* **Metadata** (``luxoh_minimal_metadata.schema.json``) — the institutional
  minimum (the LuxOH-CMDI schema, maintained on GitLab / archived on Zenodo).
* **Evaluation record** (``oh_eval_record.schema.json``) — the research/benchmark
  contract: additionally requires ``synthetic: true``, a ``transcript``, the
  ``interpretive_layer``, and per-segment ``analytical_annotations``.

Some constraints are awkward or impossible to express in JSON Schema (draft-07),
so segment **contiguity** is checked in Python on top of the structural schema:
the first segment starts at the origin, each ``start < end``, and consecutive
segments meet (``segments[i].end == segments[i+1].start``).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import jsonschema

from .metrics import timecode_to_seconds

# ── Schema location ──────────────────────────────────────────────────────────
# src/oh_eval/schema.py -> repo root is parents[2]; schemas/ lives there.
_DEFAULT_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"

SCHEMA_FILES = {
    "luxoh": "luxoh_minimal_metadata.schema.json",
    "eval": "oh_eval_record.schema.json",
}


def _schema_dir() -> Path:
    """Resolve the schemas directory (relative to the package, with a cwd fallback)."""
    if _DEFAULT_SCHEMA_DIR.is_dir():
        return _DEFAULT_SCHEMA_DIR
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "schemas").is_dir():
            return candidate / "schemas"
    return _DEFAULT_SCHEMA_DIR


@lru_cache(maxsize=None)
def load_schema(kind: str = "eval") -> dict:
    """Load a schema by kind (``"eval"`` or ``"luxoh"``) or by explicit filename."""
    filename = SCHEMA_FILES.get(kind, kind)
    path = _schema_dir() / filename
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# ── Structural (JSON Schema) validation ──────────────────────────────────────
def _structural_errors(record: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    out = []
    for e in errors:
        loc = "/".join(str(p) for p in e.path) or "<root>"
        out.append(f"{loc}: {e.message}")
    return out


def validate_luxoh_record(record: dict) -> list[str]:
    """Validate against the Metadata schema (LuxOH-CMDI). Empty list = valid."""
    return _structural_errors(record, load_schema("luxoh"))


# ── Semantic contiguity (Python) ─────────────────────────────────────────────
def contiguity_errors(segments: list[dict]) -> list[str]:
    """Check L1 segment contiguity beyond what JSON Schema can express.

    Rules: the first segment starts at 00:00:00; every ``start < end``; and
    consecutive segments meet exactly (``end[i] == start[i+1]``). Segments with
    missing/malformed timecodes are left to the structural schema and skipped
    here (so errors are not reported twice).
    """
    errs: list[str] = []
    if not segments:
        return errs
    for s in segments:
        if "start" not in s or "end" not in s:
            return errs  # structural schema reports the missing field
    try:
        starts = [timecode_to_seconds(s["start"]) for s in segments]
        ends = [timecode_to_seconds(s["end"]) for s in segments]
    except ValueError:
        return errs  # structural schema reports the malformed timecode

    if starts[0] != 0:
        errs.append(f"first segment must start at 00:00:00 (got {segments[0]['start']!r})")
    for i, (st, en) in enumerate(zip(starts, ends)):
        if not st < en:
            errs.append(
                f"segment {i}: start {segments[i]['start']!r} is not before end {segments[i]['end']!r}"
            )
    for i in range(len(segments) - 1):
        if ends[i] != starts[i + 1]:
            errs.append(
                f"segments {i}->{i + 1} not contiguous: "
                f"end {segments[i]['end']!r} != next start {segments[i + 1]['start']!r}"
            )
    return errs


def validate_eval_record(record: dict) -> list[str]:
    """Validate against the evaluation contract: structural schema + contiguity.

    Empty list = valid.
    """
    errors = _structural_errors(record, load_schema("eval"))
    errors.extend(contiguity_errors(record.get("timecoded_segments", [])))
    return errors


# ── Corpus-level validation ──────────────────────────────────────────────────
def _as_records(corpus) -> list[dict]:
    if isinstance(corpus, dict) and "records" in corpus:
        return corpus["records"]
    if isinstance(corpus, list):
        return corpus
    raise TypeError("Expected a list of records or a dict with a 'records' key.")


def validate_corpus(corpus, kind: str = "eval") -> dict:
    """Validate every record in a corpus.

    Returns ``{record_id: [errors]}`` for *all* records (empty list = valid), so
    callers can both count failures and inspect them.
    """
    validate = validate_eval_record if kind == "eval" else validate_luxoh_record
    records = _as_records(corpus)
    report: dict = {}
    for i, record in enumerate(records):
        rid = record.get("record_id", f"<record #{i}>")
        report[rid] = validate(record)
    return report
