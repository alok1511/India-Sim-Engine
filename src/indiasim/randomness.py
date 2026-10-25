"""All randomness is drawn up front, per path, from SeedSequence([seed, path_index]).

Consequences (by design):
* path i is identical whether run alone or inside a 5,000-path batch (deterministic regeneration);
* a branch/replay that changes only actor choices reuses exactly the same future innovations
  (matched random draws), so divergence is attributable to the intervention;
* parameter draws (outer loop, once per path) use a separate child stream from shocks (inner).
"""
from __future__ import annotations

import numpy as np

DRIVERS = ["oil", "us10y", "dxy", "risk", "gdem"]

# Correlations of driver innovations. Calm vs disruption ("stress") regime. Judgmental.
R_CALM = np.array([
    # oil   us10y  dxy   risk  gdem
    [1.00, 0.10, -0.20, 0.00, 0.30],
    [0.10, 1.00, 0.30, 0.20, 0.20],
    [-0.20, 0.30, 1.00, 0.40, -0.20],
    [0.00, 0.20, 0.40, 1.00, -0.50],
    [0.30, 0.20, -0.20, -0.50, 1.00],
])
R_STRESS = np.array([
    [1.00, 0.15, 0.10, 0.40, -0.10],   # precautionary demand: oil rises with risk-off
    [0.15, 1.00, 0.30, 0.10, 0.10],
    [0.10, 0.30, 1.00, 0.60, -0.30],
    [0.40, 0.10, 0.60, 1.00, -0.60],
    [-0.10, 0.10, -0.30, -0.60, 1.00],
])


def validate_corr(R: np.ndarray, name: str) -> tuple[np.ndarray, dict]:
    """Check symmetry, unit diagonal, PSD. Repair (eigenvalue clipping + rescale) only if needed, and report it."""
    report = {"name": name, "symmetric": bool(np.allclose(R, R.T)), "unit_diag": bool(np.allclose(np.diag(R), 1.0))}
    w, V = np.linalg.eigh((R + R.T) / 2)
    report["min_eigenvalue"] = float(w.min())
    report["repaired"] = False
    if w.min() <= 1e-8:
        w2 = np.clip(w, 1e-6, None)
        R2 = V @ np.diag(w2) @ V.T
        d = np.sqrt(np.diag(R2))
        R2 = R2 / np.outer(d, d)
        report["repaired"] = True
        report["max_abs_change"] = float(np.abs(R2 - R).max())
        R = R2
    report["valid"] = report["symmetric"] and report["unit_diag"] and np.linalg.eigvalsh(R).min() > 0
    return R, report


CHOL = {}
CORR_REPORTS = []
for _nm, _R in (("calm", R_CALM), ("stress", R_STRESS)):
    _Rv, _rep = validate_corr(_R, _nm)
    CHOL[_nm] = np.linalg.cholesky(_Rv)
    CORR_REPORTS.append(_rep)


def path_streams(seed: int, path_index: int):
    ss = np.random.SeedSequence([int(seed), int(path_index)])
    p_ss, s_ss = ss.spawn(2)
    return np.random.Generator(np.random.PCG64(p_ss)), np.random.Generator(np.random.PCG64(s_ss))


def draw_shocks(seed: int, path_indices, T: int, t_df: float) -> dict:
    """Standardised innovations, shape (T+1, n) (index 0 unused = t0)."""
    n = len(path_indices)
    out = {k: np.zeros((T + 1, n)) for k in ["z_oil", "z_us", "z_dxy", "z_risk", "z_gdem", "chi2", "u_reg", "u_esc",
                                             "e_fx", "e_gap", "e_g10", "e_food"]}
    for j, pi in enumerate(path_indices):
        _, rng = path_streams(seed, pi)
        z = rng.standard_normal((T + 1, 5))
        out["z_oil"][:, j], out["z_us"][:, j], out["z_dxy"][:, j], out["z_risk"][:, j], out["z_gdem"][:, j] = z.T
        out["chi2"][:, j] = rng.chisquare(t_df, T + 1)
        out["u_reg"][:, j] = rng.random(T + 1)
        out["u_esc"][:, j] = rng.random(T + 1)
        out["e_fx"][:, j] = rng.standard_normal(T + 1)
        out["e_gap"][:, j] = rng.standard_normal(T + 1)
        out["e_g10"][:, j] = rng.standard_normal(T + 1)
        out["e_food"][:, j] = rng.standard_normal(T + 1)
    return out


def sample_params(params_cfg: dict, seed: int, path_indices, mode: str, overrides: dict | None = None) -> dict:
    """Return {name: array(n)}. Sampled params are drawn ONCE per path (structural meaning), in a fixed name order."""
    n = len(path_indices)
    names = sorted(params_cfg)
    out = {nm: np.full(n, float(params_cfg[nm]["value"])) for nm in names}
    if mode == "sampled":
        for j, pi in enumerate(path_indices):
            rng, _ = path_streams(seed, pi)
            for nm in names:
                p = params_cfg[nm]
                d = p.get("dist", "fixed")
                if d == "uniform":
                    out[nm][j] = rng.uniform(p["low"], p["high"])
                elif d == "triangular":
                    out[nm][j] = rng.triangular(p["low"], p["value"], p["high"])
    for k, v in (overrides or {}).items():
        out[k] = np.full(n, float(v))
    return out
