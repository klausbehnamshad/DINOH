"""Tests for oh_eval.corpus — loading and minimal shape checks."""

import json
from pathlib import Path

import pytest

from oh_eval.corpus import (
    load_corpus,
    records,
    language_counts,
    validate_corpus_shape,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = REPO_ROOT / "data" / "corpus_synthetic.json"


def _corpus(n=2):
    recs = [
        {"record_id": f"2025-09-1{i}_CDH_000{i}", "language": "deu" if i % 2 else "eng"}
        for i in range(1, n + 1)
    ]
    return {"records": recs, "n": n, "version": "test"}


def test_records_from_dict_and_list():
    cd = _corpus()
    assert records(cd) is cd["records"]
    assert records(cd["records"]) == cd["records"]


def test_records_bad_type_raises():
    with pytest.raises(TypeError):
        records(42)


def test_language_counts_sorted():
    recs = [{"language": "deu"}, {"language": "eng"}, {"language": "deu"}]
    assert language_counts(recs) == {"deu": 2, "eng": 1}


def test_valid_shape_has_no_errors():
    assert validate_corpus_shape(_corpus(3)) == []


def test_shape_missing_records_key():
    assert validate_corpus_shape({"version": "x"})


def test_shape_not_a_dict():
    assert validate_corpus_shape([1, 2, 3])


def test_shape_declared_count_mismatch():
    cd = _corpus(2)
    cd["n"] = 5
    errs = validate_corpus_shape(cd)
    assert any("does not match" in e for e in errs)


def test_shape_duplicate_ids():
    cd = {"records": [
        {"record_id": "dup", "language": "deu"},
        {"record_id": "dup", "language": "eng"},
    ]}
    assert any("duplicate" in e for e in validate_corpus_shape(cd))


def test_shape_missing_fields():
    cd = {"records": [{"language": "deu"}, {"record_id": "r2"}]}
    errs = validate_corpus_shape(cd)
    assert any("record_id" in e for e in errs)
    assert any("language" in e for e in errs)


@pytest.mark.skipif(not CORPUS_PATH.exists(), reason="corpus not present")
def test_real_corpus_loads_and_is_well_shaped():
    cd = load_corpus(CORPUS_PATH)
    assert validate_corpus_shape(cd) == []
    assert len(records(cd)) == 28
    assert language_counts(records(cd)) == {
        "deu": 4, "eng": 4, "fra": 4, "ita": 4, "ltz": 4, "por": 4, "spa": 4
    }
