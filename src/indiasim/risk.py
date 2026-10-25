"""Probabilistic risk metrics on Monte Carlo results.

Interpretation labels (shown everywhere a number is displayed):
  CONDITIONAL MODEL FREQUENCY - share of simulated paths under the selected scenario, structure, actor rules
                                and parameter ranges. NOT a validated forecast probability.
  EXPLORATORY SCENARIO        - a single plausible path with no probability attached.
  VALIDATED FORECAST          - requires out-of-sample evaluation; NOT available in this version.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from .model import P, month_label, fiscal_year

LABEL_FREQ = "Conditional model frequency (not a validated forecast probability)"
LABEL_EXPL = "Exploratory scenario path (no probability attached)"


@dataclass
class Threshold:
    id: str
    var: str
    op: str            # '>' | '<'
    level: float
    kind: str          # 'any' (any month in horizon) | 'endpoint' | 'duration' (>= min_months consecutive)
    unit: str = ""
    min_months: int = 3
    recover_months: int = 3   # consecutive months back on the safe side to count as recovered
    label: str = ""
    observe: str = "monthly"  # 'monthly' | 'quarterly' (GDP prints) | 'fy_end' (fiscal year-end values)

    def describe(self) -> str:
        what = {"any": "at any month in the horizon", "endpoint": "at the horizon end",
                "duration": f"for at least {self.min_months} consecutive months"}[self.kind]
        return f"{self.label or self.var} {self.op} {self.level} {self.unit} {what} ({self.observe} observations)"


DEFAULT_THRESHOLDS = [
    Threshold("T-CPI6", "cpi_yoy", ">", 6.0, "any", "% y/y", label="Headline CPI above RBI upper tolerance (6%)"),
    Threshold("T-CPI6-3M", "cpi_yoy", ">", 6.0, "duration", "% y/y", min_months=3, label="CPI >6% for 3+ months"),
    Threshold("T-INR100", "inr", ">", 100.0, "any", "INR/USD", label="Rupee weaker than 100/USD"),
    Threshold("T-RES650", "reserves", "<", 650.0, "any", "USD bn", label="Reserves below USD650bn"),
    Threshold("T-GDP6", "gdp_yoy", "<", 6.0, "any", "% y/y", label="Quarterly GDP growth below 6%", observe="quarterly"),
    Threshold("T-G10-8", "g10", ">", 8.0, "any", "%", label="10Y G-sec above 8%"),
    Threshold("T-FD48", "fd_proj", ">", 4.8, "any", "% GDP", label="FY fiscal deficit above 4.8% of GDP", observe="fy_end"),
]


def _obs_matrix(res, th: Threshold):
    """(n, k) observed values and their month indices, respecting native frequency."""
    X = res.panel(th.var)[:, 1:]           # months 1..T
    months = np.arange(1, res.T + 1)
    if th.observe == "quarterly":
        keep = ~np.isnan(X).all(axis=0)
        return X[:, keep], months[keep]
    if th.observe == "fy_end":
        keep = np.array([month_label(t).endswith("-03") for t in months])
        return X[:, keep], months[keep]
    return X, months


def _breach(X, th):
    return X > th.level if th.op == ">" else X < th.level


def _max_run(b):
    best = cur = 0
    for x in b:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def evaluate_threshold(res, th: Threshold) -> dict:
    X, months = _obs_matrix(res, th)
    n = X.shape[0]
    B = _breach(X, th) & ~np.isnan(X)
    if th.kind == "endpoint":
        hit = B[:, -1]
    elif th.kind == "duration":
        hit = np.array([_max_run(B[j]) >= th.min_months for j in range(n)])
    else:
        hit = B.any(axis=1)
    first = np.array([months[np.argmax(B[j])] if B[j].any() else np.nan for j in range(n)])
    dur_max = np.array([_max_run(B[j]) for j in range(n)], dtype=float)
    months_beyond = B.sum(axis=1).astype(float)
    # recovery: after first breach, first index where `recover_months` consecutive observations are safe
    rec_time = np.full(n, np.nan); censored = np.zeros(n, bool)
    k = th.recover_months if th.observe == "monthly" else 1
    for j in range(n):
        if not B[j].any():
            continue
        f = int(np.argmax(B[j]))
        found = False
        for s in range(f + 1, B.shape[1] - k + 1):
            if not B[j, s:s + k].any():
                rec_time[j] = months[s + k - 1] - months[f]
                found = True
                break
        censored[j] = not found
    p = hit.mean()
    lo, hi = wilson(hit.sum(), n)
    n_breach = int(B.any(axis=1).sum())
    return {"threshold": asdict(th), "description": th.describe(), "n_paths": int(n), "frequency": float(p),
            "ci95": [lo, hi], "label": LABEL_FREQ,
            "first_passage": first, "max_duration": dur_max, "months_beyond": months_beyond,
            "recovery_time": rec_time, "censored": censored,
            "summary": {
                "median_first_passage_month": _nanmed(first), "mean_months_beyond_given_breach": _nanmean(np.where(B.any(1), months_beyond, np.nan)),
                "n_breached": n_breach, "n_recovered": int((~np.isnan(rec_time)).sum()),
                "n_not_recovered_by_horizon": int(censored.sum()),
                "share_not_recovered_given_breach": float(censored.sum() / n_breach) if n_breach else float("nan"),
                "median_recovery_months_among_recovered": _nanmed(rec_time)}}


def joint_frequency(res, ths: list[Threshold], same_month=True) -> dict:
    """Joint stress. same_month=True: all breached in the same month (monthly vars only); else: each breached at some point."""
    if same_month:
        Bs = [_breach(res.panel(t.var)[:, 1:], t) for t in ths]
        hit = np.logical_and.reduce(Bs).any(axis=1)
        desc = " AND ".join(t.label or t.var for t in ths) + " in the SAME month"
    else:
        hit = np.logical_and.reduce([hit_vector(res, t) for t in ths])
        desc = " AND ".join(t.label or t.var for t in ths) + " each at some point"
    lo, hi = wilson(hit.sum(), len(hit))
    return {"description": desc, "frequency": float(hit.mean()), "ci95": [lo, hi], "label": LABEL_FREQ, "hit": hit}


def hit_vector(res, th: Threshold) -> np.ndarray:
    X, _ = _obs_matrix(res, th)
    B = _breach(X, th) & ~np.isnan(X)
    if th.kind == "endpoint":
        return B[:, -1]
    if th.kind == "duration":
        return np.array([_max_run(b) >= th.min_months for b in B])
    return B.any(axis=1)


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0, c - h)), float(min(1, c + h))


def _nanmed(a):
    a = np.asarray(a, float)
    return float(np.nanmedian(a)) if np.isfinite(a).any() else float("nan")


def _nanmean(a):
    a = np.asarray(a, float)
    return float(np.nanmean(a)) if np.isfinite(a).any() else float("nan")


def bands(res, var, qs=(5, 25, 50, 75, 95)):
    import warnings
    X = res.panel(var)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # GDP is quarterly: non-quarter months are all-NaN by design
        return {q: np.nanpercentile(X, q, axis=0) for q in qs}


def path_metrics(res) -> dict:
    """Per-path summary metrics used for severity scoring, shortfall and sensitivity."""
    import warnings
    warnings.filterwarnings("ignore", message="All-NaN slice")
    g = res.panel("gdp_yoy")[:, 1:]
    fy = [fiscal_year(t) for t in range(res.T + 1)]
    fy27_end = [t for t in range(1, res.T + 1) if fy[t] == "FY27" and month_label(t).endswith("-03")]
    out = {
        "peak_cpi": np.nanmax(res.panel("cpi_yoy")[:, 1:], axis=1),
        "peak_inr": np.nanmax(res.panel("inr")[:, 1:], axis=1),
        "min_reserves": np.nanmin(res.panel("reserves")[:, 1:], axis=1),
        "min_gdp_yoy": np.nanmin(g, axis=1) if np.isfinite(g).any() else np.full(g.shape[0], np.nan),
        "min_gap": np.nanmin(res.panel("gap")[:, 1:], axis=1),
        "peak_repo": np.nanmax(res.panel("repo")[:, 1:], axis=1),
        "peak_g10": np.nanmax(res.panel("g10")[:, 1:], axis=1),
        "cum_omc_loss": res.panel("cum_omc_loss")[:, -1],
        "fd_fy27": res.panel("fd_proj")[:, fy27_end[0]] if fy27_end else np.full(res.panel("fd_proj").shape[0], np.nan),
        "peak_brent": np.nanmax(res.panel("brent")[:, 1:], axis=1),
        "end_cpi": res.panel("cpi_yoy")[:, -1], "end_inr": res.panel("inr")[:, -1],
    }
    return out


ADVERSE_SIGN = {"peak_cpi": 1, "peak_inr": 1, "min_reserves": -1, "min_gdp_yoy": -1, "min_gap": -1, "peak_g10": 1}


def severity_scores(metrics) -> np.ndarray:
    zs = []
    for k, s in ADVERSE_SIGN.items():
        x = metrics[k]
        sd = np.nanstd(x)
        zs.append(s * (x - np.nanmean(x)) / (sd if sd > 0 else 1))
    return np.nanmean(np.vstack(zs), axis=0)


def representative_paths(res) -> dict:
    """ACTUAL simulated paths (not marginal medians stitched together) chosen by a severity score."""
    m = path_metrics(res)
    s = severity_scores(m)
    order = np.argsort(s)
    pick = {}
    for name, q in (("benign (P10 severity)", 10), ("central (P50 severity)", 50), ("adverse (P90 severity)", 90), ("tail (P98 severity)", 98)):
        target = np.nanpercentile(s, q)
        j = int(np.nanargmin(np.abs(s - target)))
        pick[name] = {"j": j, "path_index": res.path_indices[j], "severity": float(s[j]), "severity_pct": q}
    return pick


def expected_shortfall(x, alpha=0.10, adverse="low"):
    """Mean of the worst alpha share of paths (ES). adverse='low' for growth, 'high' for inflation/INR."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not len(x):
        return float("nan")
    k = max(1, int(np.floor(alpha * len(x))))
    srt = np.sort(x)
    return float(srt[:k].mean() if adverse == "low" else srt[-k:].mean())


def convergence(res, th: Threshold, splits=(0.125, 0.25, 0.5, 1.0)) -> list[dict]:
    """Running estimate and MC standard error by sample size. Narrow MC error != small model uncertainty."""
    hit_any = hit_vector(res, th)
    n = len(hit_any)
    out = []
    for f in splits:
        k = max(2, int(n * f))
        p = hit_any[:k].mean()
        out.append({"n": k, "estimate": float(p), "mc_se": float(np.sqrt(p * (1 - p) / k))})
    half = n // 2
    for nm, part in (("first half", hit_any[:half]), ("second half", hit_any[half:])):
        p = part.mean() if len(part) else float("nan")
        out.append({"n": f"{nm} ({len(part)})", "estimate": float(p), "mc_se": float(np.sqrt(p * (1 - p) / max(len(part), 1)))})
    return out


def sensitivity_rank(res, metric: str, top=10) -> list[dict]:
    """Spearman rank correlation between each SAMPLED parameter and a path metric (global, sampling-based)."""
    from scipy.stats import spearmanr
    m = path_metrics(res)[metric]
    out = []
    for name, v in res.params.items():
        if np.ptp(v) == 0 or not np.isfinite(m).all():
            continue
        rho = spearmanr(v, m).statistic
        if np.isfinite(rho):
            out.append({"param": name, "spearman": float(rho)})
    return sorted(out, key=lambda d: -abs(d["spearman"]))[:top]


def mixture(results_by_scenario: dict, weights: dict, th: Threshold) -> dict:
    """Aggregate across scenarios ONLY with explicit, visible weights. Returns weighted frequency and per-scenario parts."""
    tot = sum(weights.values())
    if tot <= 0:
        raise ValueError("weights must be positive")
    parts = {k: evaluate_threshold(r, th)["frequency"] for k, r in results_by_scenario.items()}
    agg = sum(weights[k] / tot * parts[k] for k in parts)
    return {"aggregate": agg, "parts": parts, "weights": {k: weights[k] / tot for k in parts},
            "label": "Judgment-weighted mixture of conditional model frequencies. Weights are assumptions, not evidence."}
