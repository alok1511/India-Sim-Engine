"""AT-09 branch replay keeps pre-branch history, uses matched future draws; unchanged-policy replay reproduces original."""
import numpy as np

from indiasim.config import spec_from_scenario
from indiasim.model import P
from indiasim.analysis import branch, divergence_report

SPEC = spec_from_scenario("oil_escalation", n_paths=1)


def test_pre_branch_identical_and_draws_matched():
    o, a = branch(SPEC, 21, 4, {"gov_fuel": "full_passthrough"})
    for v in o.hist:
        assert np.allclose(o.hist[v][: P + 4], a.hist[v][: P + 4], equal_nan=True), v
    for v in ("brent", "us10y", "dxy", "risk_off", "gdem", "food_shock", "disrupt", "esc"):
        assert np.array_equal(o.hist[v], a.hist[v]), v          # exogenous future identical
    assert not np.allclose(o.hist["retail_fuel"][P + 4:], a.hist["retail_fuel"][P + 4:])
    d = divergence_report(o, a)
    assert d["pre_branch_history_identical"] and d["first_divergence"] == "2027-02"


def test_unchanged_policy_replay_reproduces_original():
    o, a = branch(SPEC, 21, 4, {"gov_fuel": SPEC.policies["gov_fuel"]})
    for v in o.hist:
        assert np.array_equal(o.hist[v], a.hist[v], equal_nan=True), v


def test_override_persists_from_month_onward():
    o, a = branch(SPEC, 2, 3, {"rbi_mpc": "hold"})
    assert np.allclose(np.diff(a.hist["repo"][P + 2:, 0]), 0)
