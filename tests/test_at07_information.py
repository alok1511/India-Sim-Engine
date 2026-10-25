"""AT-07 actors cannot use future or unpublished information.
Expectation: a food shock that starts in December 2026 (an MPC month) cannot change the December or January repo decision,
because December CPI is only published mid-January and usable from February."""
import numpy as np

from conftest import det
from indiasim.config import spec_from_scenario
from indiasim.model import simulate, P, mpc_observe


def test_mpc_blind_to_unpublished_shock_end_to_end():
    ref = det("reference")
    sc = spec_from_scenario("reference", n_paths=1, param_mode="central", shock_mode="deterministic")
    sc.scenario["shocks"] = [{"type": "food_supply", "start": 2, "months": 6, "magnitude": 30.0}]
    shocked = simulate(sc)
    assert shocked.hist["cpi_yoy"][P + 2, 0] > ref.hist["cpi_yoy"][P + 2, 0] + 0.5     # CPI does move in Dec
    assert np.array_equal(shocked.hist["repo"][: P + 4, 0], ref.hist["repo"][: P + 4, 0])  # Dec and Jan decisions identical
    assert shocked.hist["mpc_target"][P + 4, 0] > ref.hist["mpc_target"][P + 4, 0]      # Feb meeting sees Dec CPI


def test_observation_function_ignores_rows_at_or_after_cutoff():
    r = det("oil_escalation")
    H = {k: v.copy() for k, v in r.hist.items()}
    i = P + 8
    before = [x.copy() for x in mpc_observe(H, i)]
    for v in ("cpi_yoy", "core_yoy", "exp_infl", "gdp_yoy", "inr"):
        H[v][i:] += 50.0          # tamper with the current month and the future
    H["cpi_yoy"][i - 1] += 50.0   # last month's CPI is not yet published
    H["core_yoy"][i - 1] += 50.0
    after = mpc_observe(H, i)
    for a, b in zip(before, after):
        assert np.array_equal(a, b, equal_nan=True)


def test_trace_decisions_report_published_values():
    from indiasim.trace import build_trace
    r = det("oil_escalation")
    ev = build_trace(r, 0, "x")
    for e in ev:
        if e["type"] == "decision" and e.get("actor") == "RBI MPC":
            assert np.isclose(e["observed"]["CPI (latest published, % y/y)"], round(r.hist["cpi_yoy"][P + e["t"] - 2, 0], 2))
