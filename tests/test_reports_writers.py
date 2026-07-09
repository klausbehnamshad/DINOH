"""Tests for oh_eval.reports — the CSV/LaTeX writers (tempdir-based)."""

import pandas as pd
import pytest

from oh_eval.reports import (
    write_validation_report,
    write_task1_reports,
    write_task2_reports,
    write_segmentation_latex,
)


def _validation_rows():
    return [
        {"record_id": "r1", "language": "por", "valid": True, "n_errors": 0, "errors": ""},
        {"record_id": "r2", "language": "deu", "valid": True, "n_errors": 0, "errors": ""},
    ]


def _task1_summary():
    return pd.DataFrame([
        {"model": "m", "language": "por", "field": "record_id", "accuracy": 1.0, "n": 4},
    ])


def _task2_summary():
    df = pd.DataFrame([
        {"model": "m", "language": "por", "mean_window_diff": 0.143, "mean_pk": 0.143, "mean_count_diff": 1.0, "n": 4},
        {"model": "m", "language": "deu", "mean_window_diff": 0.143, "mean_pk": 0.143, "mean_count_diff": 1.0, "n": 4},
    ])
    return df.set_index(["model", "language"])


def test_write_validation_report_columns_stable(tmp_path):
    path = write_validation_report(_validation_rows(), tmp_path / "val.csv")
    assert path.exists()
    df = pd.read_csv(path)
    assert list(df.columns) == ["record_id", "language", "valid", "n_errors", "errors"]
    assert len(df) == 2


def test_write_validation_report_accepts_dataframe(tmp_path):
    path = write_validation_report(pd.DataFrame(_validation_rows()), tmp_path / "val.csv")
    assert pd.read_csv(path).shape[0] == 2


def test_write_task1_reports(tmp_path):
    raw = pd.DataFrame([{"model": "m", "language": "por", "field": "record_id", "match": True}])
    raw_path, summary_path = write_task1_reports(raw, _task1_summary(), tmp_path)
    assert raw_path.name == "task1_metadata_raw.csv"
    assert summary_path.name == "task1_metadata_summary.csv"
    summary = pd.read_csv(summary_path)
    assert list(summary.columns) == ["model", "language", "field", "accuracy", "n"]


def test_write_task2_reports_preserves_index_columns(tmp_path):
    raw = pd.DataFrame([{"n_gold": 4, "n_pred": 3, "model": "m", "language": "por"}])
    raw_path, summary_path = write_task2_reports(raw, _task2_summary(), tmp_path)
    assert summary_path.name == "task2_segmentation_summary.csv"
    summary = pd.read_csv(summary_path)
    # (model, language) index must come back as the first two columns
    assert summary.columns[0] == "model"
    assert summary.columns[1] == "language"
    assert set(summary["language"]) == {"por", "deu"}


def test_write_segmentation_latex_contains_por(tmp_path):
    path = write_segmentation_latex(_task2_summary(), tmp_path / "seg.tex")
    text = path.read_text(encoding="utf-8")
    assert "por" in text
    assert "tabular" in text
    assert "WindowDiff" in text or "window" in text.lower() or "0.143" in text


def test_creates_missing_directory(tmp_path):
    nested = tmp_path / "deep" / "reports"
    path = write_validation_report(_validation_rows(), nested / "v.csv")
    assert path.exists()
