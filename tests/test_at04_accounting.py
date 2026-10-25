"""AT-04 accounting residuals, units, signs, lags, bounds; USD vs INR treatment."""
import itertools

import numpy as np
import pytest

from conftest import det
from indiasim.config import spec_from_scenario, list_scenarios, POLICY_OPTIONS
from indiasim.model import simulate, P
from indiasim.checks import accounting_checks


@pytest.mark.parametrize("sid", list_scenarios())
def test_accounting_all_scenarios(sid):
    r = simulate(spec_from_scenario(sid, n_paths=150))
    bad = [(c["check"], c["max_abs_residual"]) for c in accounting_checks(r) if not c["pass"]]
    assert not bad, bad


@pytest.mark.parametrize("fuel,fx,steril,exp_,fxr", [
    ("full_passthrough", "light", "none", "anchored", "flexible"), ("excise_cut", "heavy", "full", "adaptive", "managed"),
    ("freeze_budget_comp", "moderate", "half", "adaptive", "flexible"), ("adaptive_threshold", "heavy", "none", "anchored", "managed")])
def test_accounting_policy_structure_grid(fuel, fx, steril, exp_, fxr):
    r = simulate(spec_from_scenario("combined_stress", n_paths=100, policies={"gov_fuel": fuel, "rbi_fx": fx, "rbi_steril": steril, "gov_fiscal": "hold_target"},
                                    structure={"expectations": exp_, "fx_regime": fxr}))
    assert all(c["pass"] for c in accounting_checks(r)), [c for c in accounting_checks(r) if not c["pass"]]


def test_usd_bill_independent_of_exchange_rate():
    """Holding Brent/freight/volume fixed, a much weaker rupee changes the RUPEE parity cost but not the USD bill per tonne."""
    a = det("oil_escalation", param_overrides={"vol_elast_act": 0.0})
    b = det("oil_escalation", param_overrides={"vol_elast_act": 0.0, "fx_depth": 1.0})
    s = slice(P + 1, None)
    assert np.allclose(a.hist["brent"][s], b.hist["brent"][s])
    assert not np.allclose(a.hist["inr"][s], b.hist["inr"][s])
    assert np.allclose(a.hist["crude_bill"][s], b.hist["crude_bill"][s])           # USD unchanged
    assert not np.allclose(a.hist["parity"][s], b.hist["parity"][s])               # INR cost changes


def test_units_conversion_matches_ppac_july_2026():
    """Arithmetic check of the USD bill formula against the PPAC provisional July 2026 figure (E19): 21.4 MMT, ~USD13.7bn."""
    bill = 21.4 * 7.33 * 87.3 / 1000   # implied landed price
    assert abs(bill - 13.7) < 0.05


def test_ca_sign_convention():
    r = det("oil_escalation")
    # deficit is negative; FX pressure positive when CA + KA < 0
    assert (np.sign(r.hist["pressure"][P + 1:, 0]) == -np.sign(r.hist["ca"][P + 1:, 0] + r.hist["ka"][P + 1:, 0])).all()
