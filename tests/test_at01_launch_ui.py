"""AT-01 fresh-start launch without credentials; AT-13 stale results and shared context. Uses Streamlit AppTest (no browser)."""
from pathlib import Path

import pytest

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")


@pytest.fixture(scope="module")
def app():
    at = AppTest.from_file(APP, default_timeout=600)
    at.run()
    return at


def test_fresh_launch_no_exception(app):
    assert not app.exception, [e.value for e in app.exception]
    assert len(app.metric) >= 6
    assert any("conditional model frequency" in i.value.lower() for i in app.info)


def test_changing_control_marks_results_stale_and_rerun_clears():
    at = AppTest.from_file(APP, default_timeout=600)
    at.run()
    at.selectbox(key="pol_gov_fuel").set_value("full_passthrough").run()
    assert any("STALE" in w.value and "full_passthrough" in w.value for w in at.warning)
    [b for b in at.button if b.label == "Run simulation"][0].click().run()
    assert not any("STALE" in w.value for w in at.warning)
    assert any("fuel=full_passthrough" in c.value for c in at.caption)


def test_strategy_button_produces_output():
    at = AppTest.from_file(APP, default_timeout=600)
    at.run()
    [b for b in at.button if b.label == "Run comparison"][0].click().run()
    assert not at.exception
    assert any("Common random numbers" in c.value or "bundles differ ONLY" in c.value for c in at.caption)
