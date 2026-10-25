"""AT-03 no-shock deterministic case follows the specified baseline (independent re-implementation of key rules).
Declared expectations: (1) baseline disruption regime ends at month ceil(ln0.5/ln(1-0.12)) = 6; (2) Brent follows
log b_t = log b_{t-1} + k(log anchor - log b_{t-1}) with k=0.6 in the regime-change month; (3) the initial output gap
decays as gap0 * rho^t in its own channel; (4) noise channels are exactly zero; (5) stochastic runs DO vary."""
import math

import numpy as np

from conftest import det, mc
from indiasim.config import load_params, load_baseline
from indiasim.model import P


def test_regime_and_oil_path_match_independent_calc():
    r = det("reference")
    p = {k: v["value"] for k, v in load_params()["params"].items()}
    b0 = load_baseline()["values"]["brent"]["value"]
    end = math.ceil(math.log(0.5) / math.log(1 - p["baseline_hazard"]))
    assert end == 6
    d = r.hist["disrupt"][P:, 0]
    assert d[:end].sum() == end and d[end:].sum() == 0
    brent = [b0]
    for t in range(1, r.T + 1):
        dn = 1 if t < end else 0
        anchor = p["oil_anchor"] + p["oil_disrupt_prem"] * dn + p["oil_gdem_beta"] * r.hist["gdem"][P + t, 0]
        k = 0.6 if t == end else p["oil_kappa"]
        brent.append(math.exp(math.log(brent[-1]) + k * (math.log(anchor) - math.log(brent[-1]))))
    assert np.allclose(r.hist["brent"][P:, 0], brent, rtol=1e-12)


def test_initial_gap_decays_geometrically_and_noise_zero():
    r = det("reference")
    rho = load_params()["params"]["gap_rho"]["value"]
    g0 = load_baseline()["values"]["gap"]["value"]
    t = np.arange(r.T + 1)
    assert np.allclose(r.hist["c_init"][P:, 0], g0 * rho ** t)
    assert np.allclose(r.hist["c_noise"][P:, 0], 0)


def test_stochastic_variation_is_separate():
    r = mc("reference", 100)
    assert np.std(r.hist["brent"][-1]) > 1.0
    d = det("reference")
    d2 = det("reference")
    assert np.array_equal(d.hist["brent"], d2.hist["brent"])
