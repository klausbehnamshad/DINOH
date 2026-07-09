"""Report writers — CSV and LaTeX export for the evaluation.

Reporting is inherently tabular, so pandas is used here (unlike ``metrics``,
which stays pure). These functions own the file names, the path handling, and
the index conventions, so the report formats are testable in isolation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

SEG_LATEX_CAPTION = (
    "L1 segmentation: mean WindowDiff and Pk per model and language (v1 stub run)."
)
# Cross-Reference-Label der Segmentierungs-Tabelle. Umbenannt 2026-07-06 im Zuge des
# DINOH-Rename (vormals "tab:c2dh-oh-eval-segmentation-v1"); kein In-Repo-\ref haengt daran.
# Falls ein externes Manuskript noch den alten Label referenziert, dort einmalig nachziehen.
SEG_LATEX_LABEL = "tab:dinoh-segmentation-v1"


def _as_df(rows) -> pd.DataFrame:
    return rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)


def write_validation_report(rows, path) -> Path:
    """Write a validation report (DataFrame or list of dicts) to ``path``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _as_df(rows).to_csv(path, index=False)
    return path


def write_task1_reports(raw_df, summary_df, reports_dir) -> tuple[Path, Path]:
    """Write the Task 1 (metadata) raw and summary CSVs. Both index-free."""
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    raw_path = reports_dir / "task1_metadata_raw.csv"
    summary_path = reports_dir / "task1_metadata_summary.csv"
    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    return raw_path, summary_path


def write_task2_reports(raw_df, summary_df, reports_dir) -> tuple[Path, Path]:
    """Write the Task 2 (segmentation) raw and summary CSVs.

    The summary keeps its ``(model, language)`` index, which becomes the first
    two CSV columns.
    """
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    raw_path = reports_dir / "task2_segmentation_raw.csv"
    summary_path = reports_dir / "task2_segmentation_summary.csv"
    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path)  # preserve (model, language) index
    return raw_path, summary_path


def write_segmentation_latex(summary_df, path,
                             caption: str = SEG_LATEX_CAPTION,
                             label: str = SEG_LATEX_LABEL) -> Path:
    """Write the Task 2 summary as a LaTeX table."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    latex = summary_df.reset_index().to_latex(
        index=False, caption=caption, label=label, float_format="%.3f",
    )
    path.write_text(latex, encoding="utf-8")
    return path
