"""Accounting, unit and bound checks on a Result. Boundary of each check is stated."""
from __future__ import annotations

import numpy as np

from .model import P, GAP_CHANNELS, LITRE_FACTOR


def accounting_checks(res, tol=1e-8) -> list[dict]:
    H, prm = res.hist, res.params
    s = slice(P + 1, None)
    out = []

    def add(name, resid, boundary, tol_=tol):
        m = float(np.nanmax(np.abs(resid))) if np.size(resid) else 0.0
        out.append({"check": name, "max_abs_residual": m, "tolerance": tol_, "pass": bool(m <= tol_), "boundary": boundary})

    add("Current account = sum of components (USD bn)", H["ca"][s] - (H["oil_net"][s] + H["nonoil_bal"][s] + H["services"][s] + H["remit"][s] + H["prim_inc"][s]),
        "Monthly, model CA only; no seasonality; services/remittances aggregated")
    add("Net oil balance = product exports - crude - other energy", H["oil_net"][s] - (H["prod_exp"][s] - H["crude_bill"][s] - H["other_energy"][s]), "Energy trade only")
    add("Capital account = FDI + FPI + ECB/other + residual", H["ka"][s] - (H["fdi"][s] + H["fpi"][s] + H["ecb_other"][s] + H["resid_other"][s]),
        "Residual (incl. errors & omissions) is an explicit constant plug")
    add("BoP closure: CA + KA + price-induced flows = change in reserves (BoP)", H["ca"][s] + H["ka"][s] + H["fx_adjust"][s] + H["interv"][s],
        "Price-induced balancing flows are a model closure, not an observed BoP line")
    add("Reserves stock = previous - intervention + valuation", np.diff(H["reserves"][P:], axis=0) - (-H["interv"][s] + H["valuation"][s]),
        "Valuation from dollar index only; no gold-price or yield valuation")
    add("Liquidity change = -intervention x INR + sterilisation (Rs lakh crore)",
        np.diff(H["liq"][P:], axis=0) - (-H["interv"][s] * H["inr"][s] / 1000 + H["steril"][s]),
        "Only FX-driven liquidity; currency leakage and government cash balances omitted")
    add("Retail price = (margin + parity + excise + dealer) x (1+VAT)",
        H["retail_fuel"][s] - (H["omc_margin"][s] + H["parity"][s] + H["excise"][s] + prm["dealer_margin"]) * (1 + prm["vat_rate"]),
        "Single representative auto fuel (Delhi blend); ad-valorem state VAT", 1e-7)
    add("USD crude bill independent of INR (recomputed without exchange rate)",
        H["crude_bill"][s] - H["crude_vol"][s] * prm["bbl_per_t_crude"] * (H["brent"][s] + H["freight"][s]) / 1000,
        "Exchange rate affects INR cost (parity), never the USD bill")
    add("Fiscal deficit = expenditure - receipts", H["fd"][s] - (H["expend"][s] - H["receipts"][s]), "Centre only; states omitted")
    add("Debt accumulates deficit", np.diff(H["debt"][P:], axis=0) - H["fd"][s], "No valuation or cash-balance changes")
    add("Headline CPI index = weighted components", H["cpi_idx"][s] - (prm["w_food"] * H["food_idx"][s] + prm["w_energy"] * H["energy_idx"][s] + prm["w_core"] * H["core_idx"][s]),
        "Weights approximate; base-2024 weights not verified")
    add("CPI weights sum to one", np.array([prm["w_food"] + prm["w_energy"] + prm["w_core"] - 1.0]), "")
    add("Output gap = sum of channel contributions", H["gap"][s] - sum(H["c_" + c][s] for c in GAP_CHANNELS), "Exact for the linear gap system")
    add("OMC loss = max(0,-margin) x volume", H["omc_loss"][s] - np.maximum(0, -H["omc_margin"][s]) * prm["litres_month"] * LITRE_FACTOR, "Auto fuels only; LPG separate")
    # bounds: explicit failures, no silent clipping
    bounds = {"brent": (0, 1000), "inr": (0, 1000), "reserves": (0, 5000), "repo": (3.0, 9.0), "retail_fuel": (0, 1000)}
    for v, (lo, hi) in bounds.items():
        x = H[v][s]
        viol = np.maximum(lo - x, 0) + np.maximum(x - hi, 0)
        add(f"Bounds: {lo} <= {v} <= {hi}", viol, "Hard admissibility bounds; any violation is reported, never clipped", 0.0)
    add("WACR within SDF-MSF corridor", np.maximum(H["sdf"][s] - H["wacr"][s], 0) + np.maximum(H["wacr"][s] - H["msf"][s], 0),
        "Institutional corridor (binding months are flagged as constraint events)", 1e-12)
    finite = [v for v in ["brent", "inr", "cpi_yoy", "gap", "fd", "g10", "reserves"] if not np.isfinite(H[v][s]).all()]
    out.append({"check": "No NaN/inf in core state", "max_abs_residual": float(len(finite)), "tolerance": 0, "pass": not finite,
                "boundary": ", ".join(finite) or "all finite"})
    return out


def all_pass(checks) -> bool:
    return all(c["pass"] for c in checks)
