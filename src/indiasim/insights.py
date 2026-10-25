"""Deterministic takeaways generated from computed results (no free-text invention)."""
from __future__ import annotations

import numpy as np

from .model import month_label
from .risk import path_metrics, evaluate_threshold, DEFAULT_THRESHOLDS


def _q(x, q):
    x = np.asarray(x, float)
    return float(np.nanpercentile(x, q)) if np.isfinite(x).any() else float("nan")


def overview_takeaways(res) -> list[str]:
    m = path_metrics(res)
    n = res.spec.n_paths
    out = []
    b = res.panel("brent")
    out.append(f"Brent: median path peaks at USD{_q(m['peak_brent'], 50):.0f}/bbl (P10-P90 of path peaks USD{_q(m['peak_brent'], 10):.0f}-{_q(m['peak_brent'], 90):.0f}); "
               f"median at horizon USD{_q(b[:, -1], 50):.0f}.")
    out.append(f"Rupee: median peak {_q(m['peak_inr'], 50):.1f}/USD (P90 {_q(m['peak_inr'], 90):.1f}); reserves trough median USD{_q(m['min_reserves'], 50):.0f}bn "
               f"(P10 USD{_q(m['min_reserves'], 10):.0f}bn) from USD{res.panel('reserves')[0, 0]:.0f}bn.")
    out.append(f"Inflation: median path peak CPI {_q(m['peak_cpi'], 50):.1f}% (P90 {_q(m['peak_cpi'], 90):.1f}%); repo peaks at a median {_q(m['peak_repo'], 50):.2f}%.")
    if np.isfinite(m["min_gdp_yoy"]).any():
        out.append(f"Growth: weakest quarter median {_q(m['min_gdp_yoy'], 50):.1f}% y/y (P10 {_q(m['min_gdp_yoy'], 10):.1f}%).")
    out.append(f"OMC net uncompensated losses by horizon: median Rs{_q(m['cum_omc_loss'], 50):.2f} lakh crore; FY27 central deficit median {_q(m['fd_fy27'], 50):.2f}% of GDP.")
    th = evaluate_threshold(res, DEFAULT_THRESHOLDS[0])
    out.append(f"{100 * th['frequency']:.0f}% of {n} simulated paths see CPI above 6% at some point (95% sampling interval "
               f"{100 * th['ci95'][0]:.0f}-{100 * th['ci95'][1]:.0f}%). This is a conditional model frequency, not a forecast probability.")
    return out


def compare_takeaways(cs: dict) -> list[str]:
    ref = cs["reference"]
    out = []
    for row in cs["table"]:
        if row["bundle"] == ref:
            continue
        d_cpi = row.get(f"peak_cpi (paired median diff vs {ref})", np.nan)
        d_gdp = row.get(f"min_gdp_yoy (paired median diff vs {ref})", np.nan)
        d_omc = row.get(f"cum_omc_loss (paired median diff vs {ref})", np.nan)
        d_fd = row.get(f"fd_fy27 (paired median diff vs {ref})", np.nan)
        out.append(f"{row['bundle']} vs {ref}: peak CPI {d_cpi:+.2f}pp, weakest-quarter growth {d_gdp:+.2f}pp, OMC losses {d_omc:+.2f} lakh cr, "
                   f"FY27 deficit {d_fd:+.2f}pp of GDP (paired medians, same shocks).")
    return out
