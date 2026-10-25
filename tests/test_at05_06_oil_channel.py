"""AT-05 controlled oil increase raises gross USD crude spending with volumes fixed; downstream effects are CONDITIONAL on
policy. AT-06 offsets and alternative actor choices interrupt/alter the adverse chain without erasing costs.
Declared expectations before running:
 * fixed volumes: crude_bill_esc > crude_bill_ref in every month Brent_esc > Brent_ref;
 * full pass-through: retail fuel and energy CPI rise; freeze: retail unchanged and OMC margin falls instead;
 * budget compensation: OMC loss is shifted to the deficit (comp > 0; FY27 deficit higher than freeze);
 * remittance offset: with remit_oil > 0, remittances are higher 6+ months after the oil rise; with remit_oil = 0, equal;
 * benchmark (RBI MSM 17): +USD10/bbl -> CA worse by roughly USD1.0-1.7bn/month at current volumes (MSM: ~USD12.5bn/yr
   at 2018 volumes);
 * benchmark (MSM 17 / RBI Bulletin 2025): under FULL pass-through, a ~10% oil rise lifts peak headline CPI by 0.25-1.0pp."""
import numpy as np

from conftest import det
from indiasim.model import P
from indiasim.config import spec_from_scenario
from indiasim.model import simulate

FIX = {"vol_elast_price": 0.0, "vol_elast_act": 0.0}


def test_gross_usd_crude_spend_rises_with_price_volumes_fixed():
    ref, esc = det("reference", param_overrides=FIX), det("oil_escalation", param_overrides=FIX)
    s = slice(P + 1, P + 4)  # forced window: shortfall reduces volume, so compare price-only months after it as well
    hi = esc.hist["brent"][P + 1:, 0] > ref.hist["brent"][P + 1:, 0]
    vol_same = np.isclose(esc.hist["crude_vol"][P + 1:, 0], ref.hist["crude_vol"][P + 1:, 0])
    m = hi & vol_same
    assert m.sum() >= 3
    assert (esc.hist["crude_bill"][P + 1:, 0][m] > ref.hist["crude_bill"][P + 1:, 0][m]).all()


def test_downstream_depends_on_pricing_policy():
    full = det("oil_escalation", policies={"gov_fuel": "full_passthrough"})
    frz = det("oil_escalation", policies={"gov_fuel": "freeze_omc_absorb"})
    comp = det("oil_escalation", policies={"gov_fuel": "freeze_budget_comp"})
    t = P + 2
    assert full.hist["retail_fuel"][t, 0] > full.hist["retail_fuel"][P, 0] * 1.1
    assert np.isclose(frz.hist["retail_fuel"][t, 0], frz.hist["retail_fuel"][P, 0])
    assert frz.hist["omc_margin"][t, 0] < full.hist["omc_margin"][t, 0] - 10
    assert np.nanmax(full.hist["cpi_yoy"][P:, 0]) > np.nanmax(frz.hist["cpi_yoy"][P:, 0]) + 1.0
    # cost moved, not erased
    assert frz.hist["cum_omc_loss"][-1, 0] > full.hist["cum_omc_loss"][-1, 0] + 1.0
    assert comp.hist["comp"][P + 1:, 0].sum() > 1.0
    assert comp.hist["fd_proj"][P + 5, 0] > frz.hist["fd_proj"][P + 5, 0] + 0.3


def test_remittance_offset_switchable():
    on = det("oil_escalation", param_overrides={"remit_oil": 0.3})
    off = det("oil_escalation", param_overrides={"remit_oil": 0.0})
    assert (on.hist["remit"][P + 8:P + 12, 0] > off.hist["remit"][P + 8:P + 12, 0]).all()
    assert np.allclose(off.hist["remit"][P + 1:, 0], off.hist["remit"][P, 0])


def test_ca_sensitivity_benchmark_msm():
    base = det("reference", param_overrides=FIX)
    import copy
    s = spec_from_scenario("reference", n_paths=1, param_mode="central", shock_mode="deterministic",
                           param_overrides={**FIX, "oil_disrupt_prem": 45.0})   # +USD10 anchor -> ~+USD10 Brent at t>=1
    hi = simulate(s)
    t = P + 4
    dbrent = hi.hist["brent"][t, 0] - base.hist["brent"][t, 0]
    dca = (hi.hist["oil_net"][t, 0] - base.hist["oil_net"][t, 0]) / dbrent * 10
    assert -1.7 <= dca <= -1.0, dca


def test_full_passthrough_cpi_benchmark():
    """Sustained ~10-14% higher Brent (anchor +USD11.7, instant adjustment). Effect normalised to a 10% rise must lie in
    0.25-1.0pp of peak headline CPI within 12 months (MSM 17: 49-106bp per USD10 at USD65, i.e. per ~15%)."""
    kw = dict(policies={"gov_fuel": "full_passthrough"})
    base = det("reference", param_overrides={"oil_kappa": 1.0}, **kw)
    hi = det("reference", param_overrides={"oil_kappa": 1.0, "oil_anchor": 82.0 + 11.7}, **kw)
    rise = (hi.hist["brent"][P + 1:P + 13, 0] / base.hist["brent"][P + 1:P + 13, 0] - 1).mean()
    assert 0.08 < rise < 0.16
    d = np.nanmax(hi.hist["cpi_yoy"][P:P + 13, 0] - base.hist["cpi_yoy"][P:P + 13, 0])
    d_norm = d * 0.10 / rise
    assert 0.25 <= d_norm <= 1.0, (d, rise, d_norm)


def test_ceasefire_reverses_oil_but_not_all_costs():
    cf, esc = det("ceasefire"), det("oil_escalation")
    assert cf.hist["brent"][P + 4, 0] < 100
    assert esc.hist["cum_omc_loss"][-1, 0] > cf.hist["cum_omc_loss"][-1, 0]
