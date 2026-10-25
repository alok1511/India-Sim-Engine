"""The browser engine (web/engine.js) must reproduce the Python engine exactly when given the same parameters and
random draws. Tolerance: 1e-9 relative + 1e-9 absolute on every variable, every month, every path."""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from indiasim.config import spec_from_scenario, list_scenarios, load_params
from indiasim.model import simulate
from indiasim.randomness import draw_shocks

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

CASES = [(sid, {}, {}) for sid in list_scenarios()] + [
    ("oil_escalation", {"gov_fuel": "full_passthrough", "rbi_mpc": "fx_defence", "rbi_fx": "light", "rbi_steril": "none"}, {"expectations": "anchored"}),
    ("combined_stress", {"gov_fuel": "partial_50", "gov_fiscal": "hold_target", "rbi_mpc": "look_through"}, {"fx_regime": "flexible"}),
    ("oil_escalation", {"gov_fuel": "excise_cut", "rbi_mpc": "hold", "rbi_steril": "full"}, {}),
    ("reference", {"gov_fuel": "adaptive_threshold", "rbi_fx": "moderate"}, {}),
    ("food_stress", {"gov_fuel": "freeze_budget_comp", "gov_fiscal": "hold_target"}, {"expectations": "anchored", "fx_regime": "flexible"}),
]


def _run_js(tmp_path, spec, params, shocks):
    case = {"spec": spec.to_dict(), "params": params, "shocks": shocks}
    case["spec"]["overrides"] = {str(k): v for k, v in spec.overrides.items()}
    inp, out = tmp_path / "case.json", tmp_path / "out.json"
    inp.write_text(json.dumps(case))
    subprocess.run(["node", str(ROOT / "tests" / "js_parity_runner.js"), str(inp), str(out)], check=True)
    return json.loads(out.read_text())


def _compare(py, js, n):
    worst = (0.0, None)
    for j in range(n):
        for v, arr in js[j].items():
            if v not in py.hist:
                continue
            a = py.hist[v][:, j]
            b = np.array([np.nan if x is None else x for x in arr])
            assert np.array_equal(np.isnan(a), np.isnan(b)), (v, j)
            m = ~np.isnan(a)
            err = np.max(np.abs(a[m] - b[m]) / (1e-9 + 1e-9 * np.abs(a[m]))) if m.any() else 0
            if err > worst[0]:
                worst = (err, v)
    assert worst[0] <= 1.0, f"max scaled error {worst[0]:.2f} on {worst[1]}"


@pytest.mark.parametrize("sid,pol,st", CASES)
def test_stochastic_paths_match(tmp_path, sid, pol, st):
    spec = spec_from_scenario(sid, n_paths=12, path_offset=40, policies=pol, structure=st)
    if sid == "oil_escalation" and pol.get("rbi_mpc") == "hold":
        spec.overrides = {4: {"gov_fuel": "full_passthrough"}, 9: {"rbi_fx": "light"}}
    py = simulate(spec)
    idx = py.path_indices
    params = [{k: float(v[j]) for k, v in py.params.items()} for j in range(len(idx))]
    df = float(load_params()["params"]["oil_t_df"]["value"])
    sh = draw_shocks(spec.seed, idx, spec.horizon, df)
    shocks = [{k: sh[k][:, j].tolist() for k in sh} for j in range(len(idx))]
    _compare(py, _run_js(tmp_path, spec, params, shocks), len(idx))


@pytest.mark.parametrize("sid", list_scenarios())
def test_deterministic_central_matches(tmp_path, sid):
    spec = spec_from_scenario(sid, n_paths=1, param_mode="central", shock_mode="deterministic", horizon=24)
    py = simulate(spec)
    params = [{k: float(v[0]) for k, v in py.params.items()}]
    _compare(py, _run_js(tmp_path, spec, params, [{}]), 1)
