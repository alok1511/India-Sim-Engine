"""Branch/replay, strategy comparison, cost-absorption, reverse stress test and after-action review."""
from __future__ import annotations

import copy
import itertools

import numpy as np

from .config import RunSpec, POLICY_OPTIONS
from .model import simulate, P, month_label
from .risk import path_metrics, Threshold, hit_vector

KEY_VARS = ["brent", "inr", "reserves", "repo", "cpi_yoy", "core_yoy", "gap", "retail_fuel", "omc_margin", "fd_proj", "g10", "credit_yoy"]


# ---------------------------------------------------------------- branch & replay
def single_path_spec(spec: RunSpec, path_index: int) -> RunSpec:
    s = copy.deepcopy(spec)
    s.n_paths, s.path_offset = 1, int(path_index)
    return s


def branch(spec: RunSpec, path_index: int, month: int, choices: dict):
    """Replay one path from `month` with alternative actor choices. History before `month` is fixed because
    all innovations are pre-drawn for the path (matched random draws) and decisions before `month` are unchanged."""
    base = single_path_spec(spec, path_index)
    alt = copy.deepcopy(base)
    ov = dict(alt.overrides)
    ov[int(month)] = {**ov.get(int(month), {}), **choices}
    alt.overrides = ov
    return simulate(base), simulate(alt)


def divergence_report(orig, alt, j=0) -> dict:
    """What changed, when, and the cost split. Pre-branch history must be identical (asserted)."""
    first = None
    for t in range(1, orig.T + 1):
        if any(not np.isclose(orig.hist[v][P + t, j], alt.hist[v][P + t, j], atol=1e-10, equal_nan=True) for v in KEY_VARS):
            first = t
            break
    branch_months = sorted(alt.spec.overrides)
    pre_ok = True
    if branch_months:
        b0 = branch_months[0]
        for v in orig.hist:
            if not np.allclose(orig.hist[v][: P + b0, j], alt.hist[v][: P + b0, j], equal_nan=True):
                pre_ok = False
                break
    rows = []
    for t in sorted({b for b in (first, (first or 1) + 2, (first or 1) + 5, 12, orig.T) if b and b <= orig.T}):
        rows.append({"month": month_label(t), **{v: (round(float(orig.hist[v][P + t, j]), 2), round(float(alt.hist[v][P + t, j]), 2)) for v in KEY_VARS}})
    same_draws = np.allclose(orig.hist["brent"][:, j], alt.hist["brent"][:, j]) and np.allclose(orig.hist["food_shock"][:, j], alt.hist["food_shock"][:, j])
    note = ("Exogenous drivers (oil, global, food) are identical in both runs: matched random draws, so divergence is caused by the decision change."
            if same_draws else "Exogenous drivers differ: the intervention changed the shock process itself  - investigate before interpreting the difference.")
    return {"first_divergence": month_label(first) if first else None, "pre_branch_history_identical": pre_ok,
            "matched_draws_note": note, "table": rows, "burden_original": burden_table(orig, j), "burden_branch": burden_table(alt, j)}


# ---------------------------------------------------------------- who absorbs the cost
def burden_table(res, j=None) -> dict:
    """Cost absorption over the horizon. j=None -> median across paths."""
    H, prm = res.hist, res.params
    excise_rev0 = H["excise_rev"][P] if np.any(H["excise_rev"][P]) else H["excise"][P] * prm["litres_month"] * 1e-3

    def per_path(k):
        s = slice(P + 1, None)
        fiscal_cost = (H["comp"][s, k] + H["fert"][s, k] + H["interest_x"][s, k] - (H["excise_rev"][s, k] - H["excise"][P, k] * prm["litres_month"][k] * 1e-3)
                       - H["capex_cut"][s, k]).sum()
        return {
            "Households: retail fuel change to horizon (%)": 100 * (H["retail_fuel"][-1, k] / H["retail_fuel"][P, k] - 1),
            "Households: peak headline CPI (% y/y)": np.nanmax(H["cpi_yoy"][s, k]),
            "OMCs: cumulative net uncompensated loss (Rs lakh cr)": H["cum_omc_loss"][-1, k],
            "Central govt: cumulative oil-related fiscal cost (Rs lakh cr)": fiscal_cost,
            "Central govt: capex cut (Rs lakh cr)": H["capex_cut"][s, k].sum(),
            "Central govt: FY27 deficit (% GDP)": H["fd_proj"][P + 5, k] if res.T >= 5 else np.nan,
            "RBI: reserves drawn (USD bn, t0 minus minimum)": H["reserves"][P, k] - np.nanmin(H["reserves"][s, k]),
            "Rupee: peak depreciation vs t0 (%)": 100 * (np.nanmax(H["inr"][s, k]) / H["inr"][P, k] - 1),
            "Economy: cumulative output-gap loss (pp-months)": np.minimum(H["gap"][s, k], 0).sum(),
            "Economy: minimum quarterly GDP growth (% y/y)": np.nanmin(H["gdp_yoy"][s, k]) if np.isfinite(H["gdp_yoy"][s, k]).any() else np.nan,
            "Borrowers: peak repo (%)": np.nanmax(H["repo"][s, k]),
            "Borrowers: peak 10Y (%)": np.nanmax(H["g10"][s, k]),
        }
    n = H["brent"].shape[1]
    if j is not None:
        return {k: float(v) for k, v in per_path(j).items()}
    all_ = [per_path(k) for k in range(n)]
    return {key: float(np.nanmedian([a[key] for a in all_])) for key in all_[0]}


# ---------------------------------------------------------------- strategy comparison (common random numbers)
def compare_strategies(base: RunSpec, bundles: dict) -> dict:
    """Run each policy bundle with identical seeds/paths/parameters (common random numbers) so paired differences
    isolate the policy effect conditional on the model. No 'best' policy is computed: trade-offs are reported."""
    results, metrics = {}, {}
    for name, pol in bundles.items():
        s = copy.deepcopy(base)
        s.policies = {**base.policies, **pol}
        r = simulate(s)
        results[name] = r
        metrics[name] = path_metrics(r)
    ref = list(bundles)[0]
    table = []
    for name in bundles:
        row = {"bundle": name}
        for k in ["peak_cpi", "peak_inr", "min_reserves", "min_gdp_yoy", "peak_repo", "cum_omc_loss", "fd_fy27", "peak_g10"]:
            x = metrics[name][k]
            row[k + " (median)"] = float(np.nanmedian(x))
            row[k + " (P90 adverse)"] = float(np.nanpercentile(x, 10 if k in ("min_reserves", "min_gdp_yoy") else 90))
            if name != ref:
                row[k + " (paired median diff vs " + ref + ")"] = float(np.nanmedian(x - metrics[ref][k]))
        row["burden"] = burden_table(results[name])
        table.append(row)
    return {"results": results, "metrics": metrics, "table": table, "reference": ref,
            "note": "Common random numbers: same shocks and parameter draws for every bundle. Differences are conditional on the model."}


# ---------------------------------------------------------------- reverse stress test
DEFAULT_GRID = {"oil_premium": [0, 20, 40, 60], "forced_months": [1, 3, 6], "global_risk": [0.0, 1.0, 2.0], "food": [0.0, 4.0, 8.0]}


def _stress_scenario(base_sc: dict, oil_premium, forced_months, global_risk, food):
    sc = copy.deepcopy(base_sc)
    sc["shocks"] = [x for x in sc.get("shocks", []) if x["type"] not in ("oil_escalation", "global_tightening", "food_supply")]
    if oil_premium > 0:
        sc["shocks"].append({"type": "oil_escalation", "start": 1, "premium": float(oil_premium), "forced_months": int(forced_months),
                             "hazard_after": 0.2, "shortfall_pct": 3.0 * oil_premium / 40, "freight_extra": 6.0 * oil_premium / 40,
                             "crack_extra": 8.0 * oil_premium / 40, "risk_impulse": oil_premium / 40})
    if global_risk > 0:
        sc["shocks"].append({"type": "global_tightening", "start": 1, "months": 9, "us10y": 0.5 * global_risk, "dxy_pct": 3.0 * global_risk,
                             "risk": global_risk, "gdem": -global_risk})
    if food > 0:
        sc["shocks"].append({"type": "food_supply", "start": 3, "months": 5, "magnitude": float(food)})
    sc["id"] = f"rst_{oil_premium}_{forced_months}_{global_risk}_{food}"
    return sc


def reverse_stress(base: RunSpec, conditions: list[Threshold], grid: dict | None = None, n_paths: int = 1,
                   policy_grid: dict | None = None, min_freq: float = 0.5) -> dict:
    """Search shock combinations (and optionally actor responses) for which ALL conditions occur.
    n_paths=1 -> deterministic central path; >1 -> frequency over paths must reach min_freq.
    Output = DISCOVERED FAILURE PATHWAYS, not likelihoods of those pathways."""
    grid = grid or DEFAULT_GRID
    policy_grid = policy_grid or {}
    keys = list(grid)
    pkeys = list(policy_grid)
    found, tested = [], 0
    for combo in itertools.product(*[grid[k] for k in keys]):
        g = dict(zip(keys, combo))
        if g["oil_premium"] == 0 and g["forced_months"] != grid["forced_months"][0]:
            continue
        for pcombo in itertools.product(*[policy_grid[k] for k in pkeys]) if pkeys else [()]:
            s = copy.deepcopy(base)
            s.scenario = _stress_scenario(base.scenario, **g)
            s.policies = {**base.policies, **dict(zip(pkeys, pcombo))}
            if n_paths == 1:
                s.n_paths, s.param_mode, s.shock_mode = 1, "central", "deterministic"
            else:
                s.n_paths = n_paths
            r = simulate(s)
            tested += 1
            hits = np.logical_and.reduce([hit_vector(r, c) for c in conditions])
            freq = float(hits.mean())
            if (n_paths == 1 and hits.all()) or (n_paths > 1 and freq >= min_freq):
                size = g["oil_premium"] / 40 + g["global_risk"] / 1.5 + g["food"] / 6 + (g["forced_months"] / 3 if g["oil_premium"] else 0) * 0.25
                found.append({**g, **dict(zip(pkeys, pcombo)), "frequency": freq, "shock_size_index": round(size, 2)})
    found.sort(key=lambda d: d["shock_size_index"])
    return {"pathways": found, "tested": tested, "conditions": [c.describe() for c in conditions],
            "label": "Discovered failure pathways under model assumptions; NOT the likelihood of these pathways.",
            "mode": "deterministic central path" if n_paths == 1 else f"{n_paths}-path frequency >= {min_freq}"}


# ---------------------------------------------------------------- after-action review
def after_action(res, intent: dict) -> dict:
    """intent: {metric: (op, level)} e.g. {'peak_cpi': ('<', 6.0)}. Compares intended vs simulated (median & P90)."""
    m = path_metrics(res)
    rows = []
    for k, (op, lvl) in intent.items():
        x = m[k]
        ok = (x < lvl) if op == "<" else (x > lvl)
        rows.append({"metric": k, "intended": f"{op} {lvl}", "median": float(np.nanmedian(x)),
                     "share_of_paths_meeting_intent": float(np.mean(ok)), "label": "conditional model frequency"})
    b = burden_table(res)
    biggest = sorted(b.items(), key=lambda kv: -abs(kv[1]) if np.isfinite(kv[1]) else 0)[:4]
    return {"intent_vs_outcome": rows, "trade_offs": b, "largest_moves": biggest,
            "follow_up": ["Which assumption, if wrong, flips the intent result? (see sensitivity ranking)",
                          "Who absorbed the cost that the policy kept off households/inflation?",
                          "Does the result survive the alternative model structure (anchored vs adaptive; managed vs flexible)?",
                          "What observable signpost would tell us early that this path is unfolding?"]}


def policy_label(actor, opt):
    return POLICY_OPTIONS[actor][opt]
