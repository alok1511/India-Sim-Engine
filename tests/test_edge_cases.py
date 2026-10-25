"""Edge cases: zero shock, brief vs persistent, simultaneous shocks, missing inputs, infeasible policies."""
import copy

import numpy as np
import pytest

from conftest import det
from indiasim.config import spec_from_scenario, RunSpec
from indiasim.model import simulate, P
from indiasim.risk import path_metrics


def test_zero_magnitude_shocks_equal_reference():
    ref = det("reference")
    for sid, zero in (("global_tightening", {"us10y": 0, "dxy_pct": 0, "risk": 0, "gdem": 0}), ("food_stress", {"magnitude": 0})):
        s = spec_from_scenario(sid, n_paths=1, param_mode="central", shock_mode="deterministic")
        s.scenario["shocks"][0].update(zero)
        r = simulate(s)
        for v in ("brent", "inr", "cpi_yoy", "gap", "repo"):
            assert np.allclose(r.hist[v], ref.hist[v], equal_nan=True), (sid, v)


def test_brief_vs_persistent_escalation():
    def run(fm, h):
        s = spec_from_scenario("oil_escalation", n_paths=1, param_mode="central", shock_mode="deterministic")
        s.scenario["shocks"][0].update({"forced_months": fm, "hazard_after": h})
        return simulate(s)
    brief, pers = run(1, 0.6), run(9, 0.1)
    assert pers.hist["cum_omc_loss"][-1, 0] > brief.hist["cum_omc_loss"][-1, 0]
    assert np.nanmin(pers.hist["reserves"][P:, 0]) < np.nanmin(brief.hist["reserves"][P:, 0])


def test_simultaneous_worse_than_each_alone():
    m = {sid: path_metrics(simulate(spec_from_scenario(sid, n_paths=300))) for sid in ("oil_escalation", "global_tightening", "combined_stress")}
    assert np.median(m["combined_stress"]["peak_inr"]) > max(np.median(m["oil_escalation"]["peak_inr"]), np.median(m["global_tightening"]["peak_inr"]))


def test_missing_and_invalid_inputs_rejected():
    s = spec_from_scenario("reference")
    bad = copy.deepcopy(s); bad.policies.pop("gov_fuel")
    assert any("missing policy" in e for e in bad.validate())
    bad2 = copy.deepcopy(s); bad2.scenario["shocks"] = [{"type": "meteor", "start": 1}]
    with pytest.raises(ValueError):
        simulate(bad2)
    bad3 = copy.deepcopy(s); bad3.overrides = {3: {"rbi_fx": "infinite"}}
    assert bad3.validate()


def test_infeasible_excise_cut_is_flagged_not_faked():
    r = det("oil_escalation", policies={"gov_fuel": "excise_cut"})
    assert (r.hist["excise"][P:] >= 0).all()
    assert r.hist["flag_excise_exhausted"][P + 1:].max() == 1     # headroom (~Rs1/l) cannot cover the loss
    assert r.hist["omc_margin"][P + 2, 0] < 0                      # losses remain visible
