"""AT-15 unsupported calibration/current-data/forecast claims are absent; AT-16 historical evaluation (NOT RUN)."""
import re
from pathlib import Path

import pytest

from indiasim.config import load_params

ROOT = Path(__file__).resolve().parents[1]


def test_no_parameter_claims_estimated_status():
    for k, v in load_params()["params"].items():
        assert v["status"] in {"external", "judgmental", "illustrative", "derived"}, k


def test_ui_labels_frequencies_and_disclaims_validation():
    app = (ROOT / "app" / "streamlit_app.py").read_text()
    assert "NO validated forecasting skill" in app
    assert "not live" in app.lower()
    for line in app.splitlines():
        if re.search(r"forecast probabilit", line, re.I):
            assert re.search(r"\bnot\b|\bno\b", line, re.I), line


def test_docs_do_not_claim_live_or_validated():
    for p in list((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
        if not p.exists():
            continue
        for line in p.read_text().lower().splitlines():
            for bad in ("validated forecast", "live data", "real-time data", "predicts with"):
                if bad in line:   # allowed only in negated / disclaiming statements
                    assert re.search(r"\bno\b|\bnot\b|unvalidated|pending|until|only route|blocked", line), (p.name, line[:120])


@pytest.mark.skip(reason="NOT RUN: no real-time data vintages assembled for a past episode (e.g. 2022 oil shock); "
                         "a retrospective test without vintages would leak future information. See docs/BACKLOG.md B-01.")
def test_historical_out_of_sample_evaluation():
    pass
