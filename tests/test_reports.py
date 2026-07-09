"""Tests on the generated validation reports.

Both validation reports (institutional LuxOH-CMDI and the evaluation contract) must
cover all 28 records with zero errors. These assert on the committed report
artefacts; they skip if the reports have not been generated yet.
"""

from pathlib import Path

import pandas as pd
import pytest

REPORTS = Path(__file__).resolve().parents[1] / "reports"

VALIDATION_REPORTS = [
    "luxoh_validation_report.csv",
    "oh_eval_validation_report.csv",
]


@pytest.mark.parametrize("name", VALIDATION_REPORTS)
def test_validation_report_is_complete_and_clean(name):
    path = REPORTS / name
    if not path.exists():
        pytest.skip(f"{name} not generated yet (run the notebook)")
    df = pd.read_csv(path).fillna({"errors": ""})
    assert len(df) == 28, f"{name}: expected 28 rows, got {len(df)}"
    assert bool(df["valid"].all()), f"{name}: some records are invalid"
    assert int(df["n_errors"].sum()) == 0, f"{name}: nonzero errors present"


@pytest.mark.parametrize("name", VALIDATION_REPORTS)
def test_validation_report_covers_seven_languages(name):
    path = REPORTS / name
    if not path.exists():
        pytest.skip(f"{name} not generated yet (run the notebook)")
    df = pd.read_csv(path)
    assert set(df["language"].unique()) == {"deu", "eng", "fra", "ita", "spa", "ltz", "por"}
