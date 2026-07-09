"""Corpus loading and minimal structural checks.

Deliberately small: loading and shape sanity only, no methodology and no schema
validation (that lives in ``oh_eval.schema``).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def load_corpus(path) -> dict:
    """Load a corpus JSON file and return the parsed object."""
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def records(corpus_data) -> list[dict]:
    """Return the record list from a corpus (dict with ``records`` or a bare list)."""
    if isinstance(corpus_data, dict) and "records" in corpus_data:
        return corpus_data["records"]
    if isinstance(corpus_data, list):
        return corpus_data
    raise TypeError("Expected a list of records or a dict with a 'records' key.")


def language_counts(recs) -> dict:
    """Return ``{language: count}`` for a list of records (sorted by language)."""
    counts = Counter(r.get("language", "<unknown>") for r in recs)
    return dict(sorted(counts.items()))


def validate_corpus_shape(corpus_data) -> list[str]:
    """Minimal structural checks (not schema validation). Empty list = OK.

    Checks: top level is a dict with a non-empty ``records`` list; every record
    is an object carrying ``record_id`` and ``language``; a declared ``n`` (if
    present) matches the actual count; and ``record_id`` values are unique.
    """
    if not isinstance(corpus_data, dict):
        return ["corpus must be a JSON object with a 'records' array"]
    if "records" not in corpus_data or not isinstance(corpus_data["records"], list):
        return ["corpus is missing a 'records' array"]

    recs = corpus_data["records"]
    errs: list[str] = []
    if not recs:
        errs.append("corpus 'records' is empty")

    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            errs.append(f"record #{i} is not an object")
            continue
        if "record_id" not in r:
            errs.append(f"record #{i} is missing 'record_id'")
        if "language" not in r:
            errs.append(f"record {r.get('record_id', f'#{i}')} is missing 'language'")

    if "n" in corpus_data and corpus_data["n"] != len(recs):
        errs.append(f"declared n={corpus_data['n']} does not match actual {len(recs)} records")

    ids = [r.get("record_id") for r in recs if isinstance(r, dict)]
    dupes = sorted({x for x in ids if x is not None and ids.count(x) > 1})
    if dupes:
        errs.append(f"duplicate record_id(s): {dupes}")

    return errs
