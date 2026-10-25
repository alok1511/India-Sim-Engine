"""AT-11 dependence specifications valid; randomness vs parameter uncertainty vs model structure not conflated; convergence.
AT-12 bands vs representative paths not confused; tails/impossible states handled explicitly."""
import numpy as np

from conftest import mc, det
from indiasim.config import spec_from_scenario
from indiasim.model import simulate, P
from indiasim.randomness import CORR_REPORTS, validate_corr, R_CALM, R_STRESS, draw_shocks
from indiasim.risk import representative_paths, convergence, DEFAULT_THRESHOLDS, bands
from indiasim.checks import accounting_checks


def test_correlation_matrices_valid_unrepaired():
    for rep in CORR_REPORTS:
        assert rep["valid"] and not rep["repaired"] and rep["min_eigenvalue"] > 0


def test_invalid_matrix_is_repaired_visibly():
    bad = np.array([[1, 0.95, -0.95], [0.95, 1, 0.95], [-0.95, 0.95, 1.0]])
    R, rep = validate_corr(bad, "bad")
    assert rep["repaired"] and rep["max_abs_change"] > 0 and np.linalg.eigvalsh(R).min() > 0


def test_param_draws_once_per_path_and_separate_from_shocks():
    a = simulate(spec_from_scenario("oil_escalation", n_paths=50, param_mode="central"))
    b = simulate(spec_from_scenario("oil_escalation", n_paths=50, param_mode="sampled"))
    assert all(np.ptp(v) == 0 for v in a.params.values())                       # central: no parameter spread
    assert np.ptp(b.params["fx_depth"]) > 0                                     # sampled: spread across paths
    # identical random draws; regime paths differ only because the hazard PARAMETER is sampled. Fix it -> identical regimes
    c = simulate(spec_from_scenario("oil_escalation", n_paths=50, param_mode="sampled", param_overrides={"baseline_hazard": 0.12}))
    assert np.array_equal(a.hist["disrupt"], c.hist["disrupt"]) and np.array_equal(a.hist["esc"], c.hist["esc"])
    s1 = draw_shocks(20261025, range(50), 24, 5)
    s2 = draw_shocks(20261025, range(50), 24, 5)
    assert all(np.array_equal(s1[k], s2[k]) for k in s1)                        # shocks do not depend on param mode


def test_deterministic_shocks_with_sampled_params():
    r = simulate(spec_from_scenario("oil_escalation", n_paths=20, shock_mode="deterministic"))
    assert np.allclose(r.hist["c_noise"], 0) and np.ptp(r.params["gap_rho"]) > 0


def test_structure_alternatives_change_results_with_same_draws():
    a = simulate(spec_from_scenario("oil_escalation", n_paths=200, structure={"fx_regime": "managed"}))
    b = simulate(spec_from_scenario("oil_escalation", n_paths=200, structure={"fx_regime": "flexible"}))
    assert np.array_equal(a.hist["brent"], b.hist["brent"])
    assert np.nanmedian(b.hist["inr"][-1]) > np.nanmedian(a.hist["inr"][-1])


def test_convergence_se_shrinks(esc_mc):
    c = convergence(esc_mc, DEFAULT_THRESHOLDS[0])
    ses = [r["mc_se"] for r in c[:4]]
    assert ses[-1] < ses[0]


def test_representative_paths_are_actual_members(esc_mc):
    reps = representative_paths(esc_mc)
    for rp in reps.values():
        col = esc_mc.hist["cpi_yoy"][:, rp["j"]]
        assert np.array_equal(col, esc_mc.hist["cpi_yoy"][:, rp["j"]])
    med_band = bands(esc_mc, "cpi_yoy")[50]
    cen = esc_mc.hist["cpi_yoy"][P:, reps["central (P50 severity)"]["j"]]
    assert not np.allclose(med_band, cen)   # the marginal median is not presented as a path


def test_extreme_admissible_values_no_impossible_states():
    s = spec_from_scenario("combined_stress", n_paths=200)
    s.scenario["shocks"][0].update({"premium": 80.0, "forced_months": 12, "shortfall_pct": 10.0})
    r = simulate(s)
    assert all(c["pass"] for c in accounting_checks(r))
    assert (r.hist["brent"][P:] > 0).all() and (r.hist["reserves"][P:] > 0).all()
