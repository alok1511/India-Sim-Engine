"""Monthly semi-structural model of India with explicit actors. Vectorised over paths.

Within-month ordering (documented in MODEL_SPEC.md section 4):
  0. Start-of-month decisions on PUBLISHED information: MPC (meeting months), fiscal rule.
  1. Regimes and global drivers (oil, US10Y, dollar, risk-off, world demand, food supply).
  2. External accounts in USD (use INR and activity of t-1: trade invoicing lag).
  3. Capital account (yields/depreciation of t-1; risk of t).
  4. FX market: pressure, RBI intervention (observes same-month market pressure), INR, reserves.
  5. Liquidity and overnight rate.
  6. Fuel pricing decision (OMCs/government observe same-month import parity) -> OMC margins.
  7. Prices and expectations.  8. Output gap (contributions).  9. Fiscal accounts.
 10. 10Y yield.  11. Credit and stress.  12. Activity index and quarterly GDP.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .config import RunSpec, load_baseline, load_params, POLICY_OPTIONS
from .randomness import CHOL, draw_shocks, sample_params

P = 24  # pre-sample months kept for lags / year-on-year bases
MPC_MONTHS = {12, 2, 4, 6, 8, 10}
QUARTER_END = {3, 6, 9, 12}
GOV_FUEL = list(POLICY_OPTIONS["gov_fuel"])
GOV_FIS = list(POLICY_OPTIONS["gov_fiscal"])
MPC_RULES = list(POLICY_OPTIONS["rbi_mpc"])
FX_OPTS = {"heavy": 0.75, "moderate": 0.5, "light": 0.25}
STERIL = {"none": 0.0, "half": 0.5, "full": 1.0}
GAP_CHANNELS = ["init", "rate", "fuel_hh", "omc", "input", "gdem", "risk", "stress", "food", "fiscal", "phys", "noise"]
ADMIN_ENERGY_TREND = 3.0   # % annual, administered energy items (LPG/electricity) - illustrative
US_INFL = 2.5              # % annual, for real-exchange-rate proxy - illustrative
LITRE_FACTOR = 1e-3        # (Rs/l) x (bn litres) -> Rs lakh crore


def month_label(t: int, t0="2026-10") -> str:
    y, m = map(int, t0.split("-"))
    k = y * 12 + (m - 1) + t
    return f"{k // 12}-{k % 12 + 1:02d}"


def cal_month(t: int) -> int:
    return int(month_label(t)[-2:])


def fiscal_year(t: int) -> str:
    y, m = map(int, month_label(t).split("-"))
    fy_end = y + 1 if m >= 4 else y
    return f"FY{str(fy_end)[-2:]}"


@dataclass
class Result:
    spec: RunSpec
    path_indices: list
    T: int
    hist: dict                       # var -> array (P+T+1, n)
    params: dict                     # name -> array(n)
    meta: dict = field(default_factory=dict)

    def idx(self, t: int) -> int:
        return P + t

    def series(self, var: str, j: int = 0, include_t0=True):
        a = self.hist[var][P:, j] if include_t0 else self.hist[var][P + 1:, j]
        return a

    def panel(self, var: str):
        """(n_paths, T+1) from t0 to horizon."""
        return self.hist[var][P:, :].T


def _offset_path(T, start, months, mag, decay=0.8):
    off = np.zeros(T + 1)
    for t in range(1, T + 1):
        if start <= t < start + months:
            off[t] = mag
        elif t >= start + months:
            off[t] = mag * decay ** (t - (start + months) + 1)
    return off


def scenario_paths(spec: RunSpec, prm_central: dict, T: int) -> dict:
    """Deterministic scenario offsets and escalation settings (shared by all paths)."""
    z = np.zeros(T + 1)
    sp = {"off_us": z.copy(), "off_dxy": z.copy(), "off_risk": z.copy(), "off_gdem": z.copy(), "off_food": z.copy(),
          "esc": None, "deesc_start": None}
    for s in spec.scenario.get("shocks", []):
        st = int(s["start"])
        if s["type"] == "global_tightening":
            m = int(s.get("months", 9))
            sp["off_us"] += _offset_path(T, st, m, s.get("us10y", 0.0))
            sp["off_dxy"] += _offset_path(T, st, m, s.get("dxy_pct", 0.0) / 100.0)
            sp["off_risk"] += _offset_path(T, st, m, s.get("risk", 0.0))
            sp["off_gdem"] += _offset_path(T, st, m, s.get("gdem", 0.0))
        elif s["type"] == "food_supply":
            sp["off_food"] += _offset_path(T, st, int(s.get("months", 5)), s.get("magnitude", 0.0), decay=0.6)
        elif s["type"] == "oil_escalation":
            sp["esc"] = dict(s)
            sp["off_risk"] += np.array([s.get("risk_impulse", 0.0) * 0.8 ** (t - st) if t >= st else 0.0 for t in range(T + 1)])
        elif s["type"] == "oil_deescalation":
            sp["deesc_start"] = st
    return sp


def _median_duration(h: float) -> int:
    return max(1, int(math.ceil(math.log(0.5) / math.log(1 - h)))) if 0 < h < 1 else 10 ** 6


def simulate(spec: RunSpec, path_indices=None, record_obs=True) -> Result:
    errs = spec.validate()
    if errs:
        raise ValueError("; ".join(errs))
    pcfg = load_params()["params"]
    base = load_baseline()
    b = {k: v["value"] for k, v in base["values"].items()}
    T = spec.horizon
    if path_indices is None:
        path_indices = list(range(spec.path_offset, spec.path_offset + spec.n_paths))
    n = len(path_indices)
    prm = sample_params(pcfg, spec.seed, path_indices, spec.param_mode, spec.param_overrides)
    central = {k: float(v["value"]) for k, v in pcfg.items()}
    det = spec.shock_mode == "deterministic"
    sh = draw_shocks(spec.seed, path_indices, T, central["oil_t_df"])
    if det:
        for k in sh:
            sh[k][:] = 0.0
        sh["chi2"][:] = central["oil_t_df"] - 2.0
        sh["u_reg"][:] = 1.0
        sh["u_esc"][:] = 1.0
    scp = scenario_paths(spec, central, T)
    L = P + T + 1
    H = {}

    def new(name, fill=0.0):
        H[name] = np.full((L, n), fill, dtype=float)
        return H[name]

    # ------------------------------------------------------------------ initial state & pre-sample
    brent = new("brent", b["brent"]); bh = base["brent_history"]
    for i, v in enumerate(bh):
        brent[P - len(bh) + 1 + i, :] = v
    brent[: P - len(bh) + 1, :] = bh[0]
    disrupt = new("disrupt", b["disrupt"]); esc = new("esc"); shortfall = new("shortfall")
    crack = new("crack", central["crack_base"] + prm["crack_disrupt"].mean() * b["disrupt"])
    crack[:] = prm["crack_base"] + prm["crack_disrupt"] * b["disrupt"]
    freight = new("freight"); freight[:] = prm["freight_base"] + prm["freight_disrupt"] * b["disrupt"]
    us10y = new("us10y", b["us10y"]); dxy = new("dxy", 0.0); risk = new("risk_off", b["risk_off"])
    gdem = new("gdem", 0.0); food_shock = new("food_shock", b["food_shock"])
    inr = new("inr", b["inr"]); dep = new("dep", 0.0); reserves = new("reserves", b["reserves"])
    repo = new("repo", b["repo"]); sdf = new("sdf", b["repo"] - 0.25); msf = new("msf", b["repo"] + 0.25)
    liq = new("liq", b["liq"]); wacr = new("wacr"); wacr[:] = np.clip(b["repo"] - prm["liq_wacr"] * b["liq"], b["repo"] - .25, b["repo"] + .25)
    g10 = new("g10", b["g10"]); exp_infl = new("exp_infl", b["exp_infl"]); deanchor = new("deanchor")
    retail = new("retail_fuel", b["retail_fuel"]); excise = new("excise", b["excise"])
    for nm in ["crude_vol", "crude_bill", "prod_exp", "other_energy", "oil_net", "nonoil_bal", "services", "remit", "prim_inc",
               "ca", "fdi", "fpi", "ecb_other", "resid_other", "ka", "pressure", "interv", "fx_adjust", "valuation", "steril",
               "parity", "crude_inr", "omc_margin", "omc_loss", "lpg_loss", "comp", "omc_burden", "cum_omc_loss",
               "food_mm", "energy_mm", "core_mm", "gap", "act", "gdp_yoy", "credit_idx", "credit_yoy", "stress",
               "ngdp", "tax", "excise_rev", "other_rec", "fert", "interest_x", "capex_cut", "receipts", "expend", "fd",
               "debt", "fy_cum_fd", "fy_cum_ngdp", "fd_proj", "fd_target", "lend", "real_lend",
               "dec_gov_fuel", "dec_gov_fis", "dec_mpc_delta", "dec_fx_phi", "mpc_meeting", "mpc_target",
               "obs_cpi", "obs_core", "obs_exp", "obs_gdp", "obs_dep3", "obs_fd_proj",
               "flag_excise_exhausted", "flag_res_floor", "flag_corridor", "flag_policy_switch",
               "cpi_yoy", "food_yoy", "energy_yoy", "core_yoy"]:
        new(nm)
    for ch in GAP_CHANNELS:
        new("c_" + ch)
    H["gdp_yoy"][:] = np.nan
    # price indices (t0 = 100), constant monthly rates consistent with reported y/y (synthetic history)
    for nm, yy in (("food_idx", b["food_yoy"]), ("energy_idx", b["energy_yoy"]), ("core_idx", b["core_yoy"])):
        a = new(nm)
        for i in range(L):
            a[i] = 100.0 * (1 + yy / 100) ** ((i - P) / 12)
        H[nm.replace("_idx", "_mm")][: P + 1] = 100 * math.log(1 + yy / 100) / 12
    w_f, w_e, w_c = prm["w_food"], prm["w_energy"], prm["w_core"]
    cpi_idx = new("cpi_idx"); cpi_idx[:] = w_f * H["food_idx"] + w_e * H["energy_idx"] + w_c * H["core_idx"]
    for nm in ("cpi", "food", "energy", "core"):
        src = H["cpi_idx"] if nm == "cpi" else H[nm + "_idx"]
        H[nm + "_yoy"][12:] = 100 * (src[12:] / src[:-12] - 1)
    # activity: synthetic pre-sample growth 7.5% (consistent with Q1 FY27 7.8%, FY26 7.4%)
    act = H["act"]
    for i in range(L):
        act[i] = (i - P) * math.log(1.075) / 12
    for i in range(P + 1):
        if cal_month(i - P) in QUARTER_END and i >= 14:
            H["gdp_yoy"][i] = 100 * (np.exp(act[i - 2:i + 1]).mean(0) / np.exp(act[i - 14:i - 11]).mean(0) - 1)
    H["gap"][:] = b["gap"]; H["c_init"][: P + 1] = b["gap"]
    H["credit_idx"][:] = np.array([(1 + b["credit_yoy"] / 100) ** ((i - P) / 12) for i in range(L)])[:, None]
    H["credit_yoy"][:] = b["credit_yoy"]
    # fiscal pre-sample: BE run-rate
    ngdp0m = b["ngdp_annual"] / 12
    H["ngdp"][:] = ngdp0m * np.exp(act - act[P]) * cpi_idx / 100
    sp_ratio = 53.5 / b["ngdp_annual"]
    exc_rev0 = b["excise"] * prm["litres_month"] * LITRE_FACTOR
    or_ratio = sp_ratio - b["fd_target"] / 100 - prm["tax_ratio"] - exc_rev0 / ngdp0m
    H["fd"][: P + 1] = b["fd_target"] / 100 * H["ngdp"][: P + 1]
    H["fd_target"][:] = b["fd_target"]; H["fd_proj"][: P + 1] = b["fd_target"]
    fy_start = P - 6  # April 2026
    H["fy_cum_fd"][P] = H["fd"][fy_start:P + 1].sum(0)
    H["fy_cum_ngdp"][P] = H["ngdp"][fy_start:P + 1].sum(0)
    H["debt"][:] = b["debt_ratio"] / 100 * b["ngdp_annual"]
    # t0 derived quantities
    i0 = P
    H["crude_inr"][: P + 1] = (brent[: P + 1] + freight[: P + 1]) * b["inr"] / 159
    H["parity"][: P + 1] = (brent[: P + 1] + crack[: P + 1] + freight[: P + 1]) * b["inr"] / 159
    marg0 = retail[i0] / (1 + prm["vat_rate"]) - prm["dealer_margin"] - excise[i0] - H["parity"][i0]
    H["omc_margin"][: P + 1] = marg0
    lpg_cost0 = prm["lpg_price"] + b["lpg_loss_cyl"]
    H["lpg_loss"][: P + 1] = prm["lpg_cyl_month"] * b["lpg_loss_cyl"] / 1e5
    H["omc_loss"][: P + 1] = np.maximum(0, -marg0) * prm["litres_month"] * LITRE_FACTOR
    burden0 = (prm["omc_normal_margin"] - marg0) * prm["litres_month"] * LITRE_FACTOR + H["lpg_loss"][i0]
    H["omc_burden"][: P + 1] = burden0
    H["lend"][:] = wacr[i0] + prm["lend_spread"]; H["real_lend"][:] = H["lend"][i0] - b["exp_infl"]
    # external t0 (USD bn per month) for reference
    us0, g10_0, exp0, brent0, inr0, repo0 = b["us10y"], b["g10"], b["exp_infl"], b["brent"], b["inr"], b["repo"]
    spread0 = g10_0 - us0
    gap0 = b["gap"]
    lend0 = H["lend"][i0].copy(); real_lend0 = H["real_lend"][i0].copy()
    remit_ref = brent[P - 6].copy()
    risk0, food0 = b["risk_off"], b["food_shock"]
    floor = prm["res_floor_months"] * prm["imports_month"]
    # t0 (and pre-sample) external accounts with the same equations (pre-sample INR/activity held at t0)
    q = slice(0, P + 1)
    H["crude_vol"][q] = prm["crude_vol0"]
    H["crude_bill"][q] = prm["crude_vol0"] * prm["bbl_per_t_crude"] * (brent[q] + freight[q]) / 1000
    H["prod_exp"][q] = prm["prod_vol0"] * prm["bbl_per_t_prod"] * (brent[q] + crack[q]) / 1000
    H["other_energy"][q] = prm["other_energy0"] * ((1 - prm["other_energy_oilshare"]) + prm["other_energy_oilshare"] * brent[q] / b["brent"])
    H["oil_net"][q] = H["prod_exp"][q] - H["crude_bill"][q] - H["other_energy"][q]
    H["nonoil_bal"][q] = prm["nonoil_bal0"]; H["services"][q] = prm["services0"]; H["remit"][q] = prm["remit0"]; H["prim_inc"][q] = prm["prim0"]
    H["ca"][q] = H["oil_net"][q] + H["nonoil_bal"][q] + H["services"][q] + H["remit"][q] + H["prim_inc"][q]
    H["fdi"][q] = prm["fdi0"]; H["fpi"][q] = prm["fpi_base"] - prm["fpi_risk"] * b["risk_off"]
    H["ecb_other"][q] = prm["ecb_other0"]; H["resid_other"][q] = prm["resid_other0"]
    H["ka"][q] = H["fdi"][q] + H["fpi"][q] + H["ecb_other"][q] + H["resid_other"][q]
    H["pressure"][q] = -(H["ca"][q] + H["ka"][q])
    H["interv"][q] = 0.5 * H["pressure"][q]; H["dec_fx_phi"][q] = 0.5  # pre-sample intervention share: assumption
    H["fx_adjust"][q] = H["pressure"][q] - H["interv"][q]
    # policy codes (vectors so branch overrides can be per-month)
    pol = spec.policies

    def policy_at(t, actor):
        return spec.overrides.get(t, {}).get(actor) or _active_override(spec.overrides, t, actor) or pol[actor]

    esc_cfg = scp["esc"]
    h_base = prm["baseline_hazard"]
    det_base_end = _median_duration(central["baseline_hazard"]) if det else None
    det_esc_end = None
    if det and esc_cfg:
        det_esc_end = esc_cfg["start"] + esc_cfg["forced_months"] + _median_duration(esc_cfg["hazard_after"]) - 1
    deesc = scp["deesc_start"]

    for t in range(1, T + 1):
        i = P + t
        cm = cal_month(t)
        # ============ 0. start-of-month decisions on published information ============
        # MPC (M-MPC-01): CPI for month m is available from start of m+2; GDP quarter q from end+3; markets t-1.
        rule = policy_at(t, "rbi_mpc")
        meeting = cm in MPC_MONTHS
        obs_cpi, obs_core, obs_exp, obs_gdp, obs_dep3 = mpc_observe(H, i)
        gap_obs = obs_gdp - 7.0  # MPC's perceived potential (judgmental)
        it = prm["r_neutral"] + 4 + prm["mpc_infl_coef"] * (0.5 * obs_cpi + 0.5 * obs_exp - 4) + prm["mpc_gap_coef"] * gap_obs
        if rule == "inflation_targeting":
            target = it
        elif rule == "fx_defence":
            target = it + np.where(obs_dep3 > prm["mpc_fx_trigger"], 0.5, 0.0)
        elif rule == "look_through":
            target = prm["r_neutral"] + 4 + prm["mpc_infl_coef"] * (0.5 * obs_core + 0.5 * obs_exp - 4) + 0.3 * gap_obs
        else:
            target = repo[i - 1].copy()
        diff = target - repo[i - 1]
        step = np.select([diff > 1.5, diff > 0.2, diff < -1.5, diff < -0.2], [0.5, 0.25, -0.5, -0.25], 0.0)
        if not meeting or rule == "hold":
            step = np.zeros(n)
        repo[i] = np.clip(repo[i - 1] + step, 3.0, 9.0)
        sdf[i] = repo[i] - 0.25; msf[i] = repo[i] + 0.25
        H["dec_mpc_delta"][i] = repo[i] - repo[i - 1]; H["mpc_meeting"][i] = 1.0 if meeting else 0.0
        H["mpc_target"][i] = target
        if record_obs:
            H["obs_cpi"][i] = obs_cpi; H["obs_core"][i] = obs_core; H["obs_exp"][i] = obs_exp
            H["obs_gdp"][i] = obs_gdp; H["obs_dep3"][i] = obs_dep3
        # Fiscal rule (M-FIS-02): uses own accounts to t-1 (CGA lag).
        fis = policy_at(t, "gov_fiscal")
        H["dec_gov_fis"][i] = GOV_FIS.index(fis)
        fy = fiscal_year(t)
        fd_tgt = b["fd_target"] if fy == "FY27" else prm["fd_target_fy28"]
        H["fd_target"][i] = fd_tgt
        new_fy = cm == 4
        months_left = (3 - cm) % 12 + 1  # incl. this month
        obs_proj = H["fd_proj"][i - 1]
        H["obs_fd_proj"][i] = obs_proj
        if fis == "hold_target" and not new_fy:
            fy_ngdp_proj = H["fy_cum_ngdp"][i - 1] + H["ngdp"][i - 1] * months_left
            overrun = np.maximum(0.0, (obs_proj - fd_tgt - 0.1) / 100 * fy_ngdp_proj)
            H["capex_cut"][i] = np.minimum(0.25 * prm["capex_month"], prm["fis_capex_cut"] * overrun / months_left)
        else:
            H["capex_cut"][i] = 0.0

        # ============ 1. regimes and global drivers ============
        prev_d, prev_e = disrupt[i - 1].copy(), esc[i - 1].copy()
        if det:
            d_now = np.where(prev_d == 1, 0.0 if t >= det_base_end else 1.0, 0.0)
        else:
            d_now = np.where(prev_d == 1, (sh["u_reg"][t] >= h_base).astype(float),
                             (sh["u_reg"][t] < prm["onset_hazard"]).astype(float))
        if deesc is not None and t >= deesc:
            d_now = np.where(t == deesc, 0.0, d_now)
        e_now = np.zeros(n)
        if esc_cfg:
            s0, fm = int(esc_cfg["start"]), int(esc_cfg["forced_months"])
            if s0 <= t < s0 + fm:
                e_now[:] = 1.0
            elif t >= s0 + fm:
                if det:
                    e_now[:] = 1.0 if t <= det_esc_end else 0.0
                else:
                    e_now = np.where(prev_e == 1, (sh["u_esc"][t] >= esc_cfg["hazard_after"]).astype(float), 0.0)
            if deesc is not None and t >= deesc:
                e_now[:] = 0.0
            d_now = np.maximum(d_now, e_now)  # escalation implies the disruption regime persists
            shortfall[i] = np.where((s0 <= t) & (t < s0 + fm), esc_cfg.get("shortfall_pct", 0.0), 0.0)
        disrupt[i] = d_now; esc[i] = e_now
        stress_reg = (d_now + e_now) > 0
        L_c, L_s = CHOL["calm"], CHOL["stress"]
        z = np.stack([sh["z_oil"][t], sh["z_us"][t], sh["z_dxy"][t], sh["z_risk"][t], sh["z_gdem"][t]])
        # explicit elementwise sums (not BLAS matmul) so a path is bit-identical alone or inside any batch size
        eps_s = np.stack([sum(L_s[k, m] * z[m] for m in range(5)) for k in range(5)])
        eps_c = np.stack([sum(L_c[k, m] * z[m] for m in range(5)) for k in range(5)])
        eps = np.where(stress_reg[None, :], eps_s, eps_c)
        t_scale = np.sqrt((central["oil_t_df"] - 2.0) / np.maximum(sh["chi2"][t], 1e-9))
        e_oil = eps[0] * t_scale
        # risk-off: ongoing disruption keeps it elevated (offset = risk0 x regime) + scenario offsets
        off_r_now = risk0 * d_now + scp["off_risk"][t]; off_r_prev = risk0 * prev_d + scp["off_risk"][t - 1]
        risk[i] = off_r_now + prm["risk_rho"] * (risk[i - 1] - off_r_prev) + prm["risk_sigma"] * eps[3]
        gdem[i] = scp["off_gdem"][t] + prm["gdem_rho"] * (gdem[i - 1] - scp["off_gdem"][t - 1]) + prm["gdem_sigma"] * eps[4]
        us10y[i] = scp["off_us"][t] + prm["us_anchor"] + (1 - prm["us_kappa"]) * (us10y[i - 1] - prm["us_anchor"] - scp["off_us"][t - 1]) + prm["us_sigma"] * eps[1]
        dxy[i] = dxy[i - 1] + (scp["off_dxy"][t] - scp["off_dxy"][t - 1]) + central["dxy_sigma"] * eps[2]
        food_shock[i] = scp["off_food"][t] + prm["food_rho"] * (food_shock[i - 1] - scp["off_food"][t - 1]) + prm["food_sigma"] * sh["e_food"][t]
        esc_prem = esc_cfg["premium"] if esc_cfg else 0.0
        anchor = prm["oil_anchor"] + prm["oil_disrupt_prem"] * d_now + esc_prem * e_now + prm["oil_gdem_beta"] * gdem[i]
        regime_change = (d_now != prev_d) | (e_now != prev_e)
        kap = np.where(regime_change, 0.6, prm["oil_kappa"])
        sig = np.where(stress_reg, prm["oil_sigma_stress"], prm["oil_sigma"])
        lb = np.log(brent[i - 1])
        brent[i] = np.exp(lb + kap * (np.log(np.maximum(anchor, 20.0)) - lb) + sig * e_oil)
        crack[i] = prm["crack_base"] + prm["crack_disrupt"] * d_now + (esc_cfg.get("crack_extra", 0.0) if esc_cfg else 0) * e_now
        freight[i] = prm["freight_base"] + prm["freight_disrupt"] * d_now + (esc_cfg.get("freight_extra", 0.0) if esc_cfg else 0) * e_now

        # ============ 2. external accounts (USD bn / month) ============
        H["crude_vol"][i] = prm["crude_vol0"] * (1 + prm["vol_elast_act"] * (H["gap"][i - 1] - gap0) / 100) \
            * (brent[i] / brent0) ** prm["vol_elast_price"] * (1 - shortfall[i] / 100)
        H["crude_bill"][i] = H["crude_vol"][i] * prm["bbl_per_t_crude"] * (brent[i] + freight[i]) / 1000      # M-EXT-01
        H["prod_exp"][i] = prm["prod_vol0"] * prm["bbl_per_t_prod"] * (brent[i] + crack[i]) / 1000           # M-EXT-02
        H["other_energy"][i] = prm["other_energy0"] * ((1 - prm["other_energy_oilshare"]) + prm["other_energy_oilshare"] * brent[i] / brent0)
        H["oil_net"][i] = H["prod_exp"][i] - H["crude_bill"][i] - H["other_energy"][i]                        # M-EXT-04
        rel_p = 100 * np.log(cpi_idx[i - 1] / 100) - US_INFL * (t - 1) / 12
        real_dep6 = 100 * (np.log(inr[i - 6:i]).mean(0) - math.log(inr0)) - rel_p
        H["nonoil_bal"][i] = prm["nonoil_bal0"] + prm["nonoil_gdem"] * gdem[i] + prm["nonoil_fx"] * real_dep6 \
            - prm["nonoil_gap"] * (H["gap"][i - 1] - gap0)                                                   # M-EXT-05
        H["services"][i] = prm["services0"] + prm["services_gdem"] * gdem[i]                                  # M-EXT-06
        H["remit"][i] = prm["remit0"] * (1 + prm["remit_oil"] * (brent[i - 6] / remit_ref - 1))              # M-EXT-07
        H["prim_inc"][i] = prm["prim0"] - prm["prim_us"] * (us10y[i] - us0)                                   # M-EXT-08
        H["ca"][i] = H["oil_net"][i] + H["nonoil_bal"][i] + H["services"][i] + H["remit"][i] + H["prim_inc"][i]  # M-EXT-09

        # ============ 3. capital account ============
        expdep = dep[i - 3:i].mean(0)
        H["fdi"][i] = prm["fdi0"]
        H["fpi"][i] = prm["fpi_base"] + prm["fpi_spread"] * ((g10[i - 1] - us10y[i - 1]) - spread0) - prm["fpi_risk"] * risk[i] \
            - prm["fpi_dep"] * expdep + prm["fpi_gap"] * (H["gap"][i - 1] - gap0)                              # M-CAP-01
        H["ecb_other"][i] = prm["ecb_other0"] - prm["ecb_us"] * (us10y[i] - us0)                              # M-CAP-02
        H["resid_other"][i] = prm["resid_other0"]
        H["ka"][i] = H["fdi"][i] + H["fpi"][i] + H["ecb_other"][i] + H["resid_other"][i]                       # M-CAP-03

        # ============ 4. FX market ============
        pressure = -(H["ca"][i] + H["ka"][i])                                                                  # M-FX-01
        H["pressure"][i] = pressure
        fxo = policy_at(t, "rbi_fx")
        phi = np.full(n, FX_OPTS[fxo])
        if spec.structure.get("fx_regime") == "flexible":
            phi = np.minimum(phi, 0.15)
        near = np.clip((reserves[i - 1] - floor) / (0.15 * floor), 0.1, 1.0)
        H["flag_res_floor"][i] = (near < 1.0).astype(float)
        phi_eff = np.where(pressure > 0, phi * near, 0.7)  # inflows: RBI rebuilds reserves
        interv = phi_eff * pressure                                                                            # M-FX-02
        interv = np.minimum(interv, np.maximum(reserves[i - 1] - 0.95 * floor, 0.0))
        H["interv"][i] = interv; H["dec_fx_phi"][i] = phi_eff
        resid = pressure - interv
        dep[i] = resid / prm["fx_depth"] + 0.3 * 100 * (dxy[i] - dxy[i - 1]) + prm["fx_sigma"] * sh["e_fx"][t]  # M-FX-03
        inr[i] = inr[i - 1] * np.exp(dep[i] / 100)
        H["valuation"][i] = -prm["res_nonusd_share"] * reserves[i - 1] * (dxy[i] - dxy[i - 1])
        reserves[i] = reserves[i - 1] - interv + H["valuation"][i]                                             # M-FX-04
        H["fx_adjust"][i] = resid                                                                              # M-FX-05

        # ============ 5. liquidity & overnight rate ============
        st_frac = STERIL[policy_at(t, "rbi_steril")]
        drain = interv * inr[i] / 1000.0
        H["steril"][i] = st_frac * drain
        liq[i] = liq[i - 1] - drain + H["steril"][i]                                                           # M-LIQ-01
        raw = repo[i] - prm["liq_wacr"] * liq[i]
        wacr[i] = np.clip(raw, sdf[i], msf[i])                                                                 # M-LIQ-02
        H["flag_corridor"][i] = ((raw < sdf[i]) | (raw > msf[i])).astype(float)

        # ============ 6. fuel pricing (OMCs/government see same-month import parity) ============
        H["crude_inr"][i] = (brent[i] + freight[i]) * inr[i] / 159
        parity = (brent[i] + crack[i] + freight[i]) * inr[i] / 159                                             # M-FUEL-01
        H["parity"][i] = parity
        vat, dealer, normal, lit = prm["vat_rate"], prm["dealer_margin"], prm["omc_normal_margin"], prm["litres_month"]
        lpg_cost = lpg_cost0 * (brent[i] / brent0) ** 0.8 * (inr[i] / inr0)
        lpg_loss = np.maximum(0.0, lpg_cost - prm["lpg_price"]) * prm["lpg_cyl_month"] / 1e5                   # M-FUEL-04
        H["lpg_loss"][i] = lpg_loss
        gf = policy_at(t, "gov_fuel")
        if gf == "adaptive_threshold":
            switched = H["cum_omc_loss"][i - 1] > prm["gov_loss_tolerance"]
            H["flag_policy_switch"][i] = switched.astype(float)
        else:
            switched = np.zeros(n, bool)
        r_prev, x_prev = retail[i - 1], excise[i - 1]
        full_price = (parity + normal + dealer + x_prev) * (1 + vat)
        new_r, new_x, comp_share = r_prev.copy(), x_prev.copy(), np.zeros(n)
        if gf == "full_passthrough":
            new_r = full_price
        elif gf == "freeze_budget_comp":
            comp_share[:] = 1.0
        elif gf == "partial_50" or gf == "adaptive_threshold":
            m = np.ones(n, bool) if gf == "partial_50" else switched
            new_r = np.where(m, r_prev + 0.5 * (full_price - r_prev), r_prev)
            comp_share = np.where(m & (gf == "partial_50"), 0.5, 0.0)
        elif gf == "excise_cut":
            marg_frozen = r_prev / (1 + vat) - dealer - x_prev - parity
            need = np.maximum(0.0, -marg_frozen)
            cut = np.minimum(need, x_prev)
            H["flag_excise_exhausted"][i] = (need > x_prev + 1e-9).astype(float)
            restore = np.where(marg_frozen > normal + 2.0, np.minimum(b["excise"] - x_prev, marg_frozen - normal - 2.0), 0.0)
            new_x = x_prev - cut + np.maximum(restore, 0.0)
        H["dec_gov_fuel"][i] = GOV_FUEL.index(gf)
        retail[i] = new_r; excise[i] = new_x
        margin = new_r / (1 + vat) - dealer - new_x - parity                                                   # M-FUEL-03
        H["omc_margin"][i] = margin
        omc_loss = np.maximum(0.0, -margin) * lit * LITRE_FACTOR
        H["omc_loss"][i] = omc_loss
        H["comp"][i] = comp_share * (omc_loss + lpg_loss)
        H["omc_burden"][i] = (normal - margin) * lit * LITRE_FACTOR + lpg_loss - H["comp"][i]
        H["cum_omc_loss"][i] = H["cum_omc_loss"][i - 1] + omc_loss + lpg_loss - H["comp"][i] - np.maximum(0, margin) * lit * LITRE_FACTOR

        # ============ 7. prices & expectations ============
        fuel_chg = 100 * np.log(retail[i] / retail[i - 1])
        H["energy_mm"][i] = prm["energy_auto_share"] * fuel_chg + (1 - prm["energy_auto_share"]) * ADMIN_ENERGY_TREND / 12   # M-PRC-01
        H["food_mm"][i] = prm["food_trend"] / 12 + food_shock[i] / 12 + prm["food_fuel"] * fuel_chg                          # M-PRC-02
        dep6 = dep[i - 6:i].mean(0)
        oil6 = (100 * np.diff(np.log(H["crude_inr"][i - 7:i]), axis=0)).mean(0)
        H["core_mm"][i] = prm["core_lambda"] * H["core_mm"][i - 1] + (1 - prm["core_lambda"]) * exp_infl[i - 1] / 12 \
            + prm["core_gap"] * H["gap"][i - 1] / 12 + prm["core_fx"] * dep6 + prm["core_oil"] * oil6                         # M-PRC-03
        for nm in ("food", "energy", "core"):
            H[nm + "_idx"][i] = H[nm + "_idx"][i - 1] * np.exp(H[nm + "_mm"][i] / 100)
            H[nm + "_yoy"][i] = 100 * (H[nm + "_idx"][i] / H[nm + "_idx"][i - 12] - 1)
        cpi_idx[i] = w_f * H["food_idx"][i] + w_e * H["energy_idx"][i] + w_c * H["core_idx"][i]                              # M-PRC-04
        H["cpi_yoy"][i] = 100 * (cpi_idx[i] / cpi_idx[i - 12] - 1)
        if spec.structure.get("expectations") == "anchored":
            theta = np.full(n, prm["exp_theta"] * 0.5); deanchor[i] = 0.0
        else:
            hi = (H["cpi_yoy"][i - 1] > 6) & (H["cpi_yoy"][i - 2] > 6) & (H["cpi_yoy"][i - 3] > 6)
            lo = (H["cpi_yoy"][i - 1] < 5.5) & (H["cpi_yoy"][i - 2] < 5.5) & (H["cpi_yoy"][i - 3] < 5.5)
            deanchor[i] = np.where(hi, 1.0, np.where(lo, 0.0, deanchor[i - 1]))
            theta = np.where(deanchor[i] == 1, prm["exp_theta_deanchor"], prm["exp_theta"])
        exp_infl[i] = exp_infl[i - 1] + theta * (H["cpi_yoy"][i - 1] - exp_infl[i - 1])                                    # M-PRC-05

        # ============ 8. output gap: exact linear decomposition by channel ============
        H["lend"][i] = wacr[i] + prm["lend_spread"]
        H["real_lend"][i] = H["lend"][i] - exp_infl[i]
        rr_dev = (wacr[i - 3] - exp_infl[i - 3]) - (wacr[P] - exp_infl[P]) if t >= 3 else np.zeros(n)
        ngdp_prev = H["ngdp"][i - 1]
        imp = {
            "init": 0.0,
            "rate": -prm["a_rate"] * rr_dev,                                                                       # M-REAL-01
            "fuel_hh": -prm["a_hh_fuel"] * prm["fuel_budget_share"] * fuel_chg,                                     # M-REAL-02
            "omc": -prm["a_omc"] * (H["omc_burden"][i] - burden0) / ngdp_prev * 100,                                # M-REAL-03
            "input": -prm["a_input"] * 100 * np.log(H["crude_inr"][i] / H["crude_inr"][i - 1]),                     # M-REAL-04
            "gdem": prm["a_gdem"] * gdem[i],                                                                        # M-REAL-05
            "risk": -prm["a_risk"] * (risk[i] - risk0),                                                             # M-REAL-06
            "stress": -prm["a_stress"] * H["stress"][i - 1],                                                        # M-REAL-07
            "food": -prm["a_food"] * (food_shock[i] - food0),                                                       # M-REAL-08
            "fiscal": -prm["a_fiscal"] * H["capex_cut"][i] / ngdp_prev * 100,                                       # M-REAL-09
            "phys": -prm["a_phys"] * shortfall[i],                                                                  # M-REAL-10
            "noise": prm["gap_sigma"] * sh["e_gap"][t],
        }
        g = np.zeros(n)
        for ch in GAP_CHANNELS:
            H["c_" + ch][i] = prm["gap_rho"] * H["c_" + ch][i - 1] + imp[ch]
            g += H["c_" + ch][i]
        H["gap"][i] = g
        act[i] = act[i - 1] + prm["pot_growth"] / 1200 + (H["gap"][i] - H["gap"][i - 1]) / 100                     # M-REAL-11
        if cm in QUARTER_END:
            H["gdp_yoy"][i] = 100 * (np.exp(act[i - 2:i + 1]).mean(0) / np.exp(act[i - 14:i - 11]).mean(0) - 1)

        # ============ 9. fiscal accounts (Rs lakh crore / month) ============
        H["ngdp"][i] = ngdp0m * np.exp(act[i] - act[P]) * cpi_idx[i] / 100
        ng = H["ngdp"][i]
        H["tax"][i] = prm["tax_ratio"] * ng * (1 + (prm["tax_buoy"] - 1) * H["gap"][i] / 100)
        H["excise_rev"][i] = excise[i] * lit * LITRE_FACTOR
        H["other_rec"][i] = or_ratio * ng
        H["fert"][i] = prm["fert_oil"] * (brent[i] - brent0) / 10
        H["interest_x"][i] = prm["fy_issuance"] / 12 * t * (g10[i - 1] - g10_0) / 100 / 12
        H["receipts"][i] = H["tax"][i] + H["excise_rev"][i] + H["other_rec"][i]
        H["expend"][i] = sp_ratio * ng + H["fert"][i] + H["interest_x"][i] + H["comp"][i] - H["capex_cut"][i]
        H["fd"][i] = H["expend"][i] - H["receipts"][i]                                                              # M-FIS-01
        H["debt"][i] = H["debt"][i - 1] + H["fd"][i]                                                                # M-FIS-03
        if new_fy:
            H["fy_cum_fd"][i] = H["fd"][i]; H["fy_cum_ngdp"][i] = ng
        else:
            H["fy_cum_fd"][i] = H["fy_cum_fd"][i - 1] + H["fd"][i]; H["fy_cum_ngdp"][i] = H["fy_cum_ngdp"][i - 1] + ng
        rem = months_left - 1
        H["fd_proj"][i] = 100 * (H["fy_cum_fd"][i] + H["fd"][i] * rem) / (H["fy_cum_ngdp"][i] + ng * rem)

        # ============ 10. 10Y yield ============
        fair = g10_0 + prm["g10_repo"] * (repo[i] - repo0) + prm["g10_us"] * (us10y[i] - us0) + prm["g10_fis"] * (H["fd_proj"][i - 1] - H["fd_target"][i - 1]) \
            + prm["g10_exp"] * (exp_infl[i] - exp0)
        g10[i] = g10[i - 1] + prm["g10_kappa"] * (fair - g10[i - 1]) + prm["g10_sigma"] * sh["e_g10"][t]             # M-BOND-01

        # ============ 11. credit & stress ============
        H["stress"][i] = prm["stress_rho"] * H["stress"][i - 1] + prm["stress_rate"] * (H["real_lend"][i] - real_lend0) \
            + prm["stress_gap"] * np.maximum(0.0, -H["gap"][i])                                                     # M-CRD-02
        cmm = prm["credit_trend"] / 12 + prm["credit_gap"] * (H["gap"][i] - gap0) / 12 - prm["credit_rate"] * (H["lend"][i] - lend0) / 12 \
            - prm["credit_stress"] * H["stress"][i] / 12
        H["credit_idx"][i] = H["credit_idx"][i - 1] * np.exp(cmm / 100)                                              # M-CRD-01
        H["credit_yoy"][i] = 100 * (H["credit_idx"][i] / H["credit_idx"][i - 12] - 1)

    meta = {"t0": base["t0_month"], "months": [month_label(t) for t in range(T + 1)], "burden0": burden0,
            "floor": floor, "or_ratio": or_ratio, "sp_ratio": sp_ratio}
    return Result(spec=spec, path_indices=list(path_indices), T=T, hist=H, params=prm, meta=meta)


def mpc_observe(H: dict, i: int):
    """Information set of the MPC at the START of month index i (PUBLISHED data only):
    CPI for month m is released mid m+1 -> usable from m+2 (rows <= i-2); quarterly GDP usable from quarter-end +3
    (rows <= i-3); expectations survey and market data from the previous month (rows <= i-1). Nothing at rows >= i."""
    obs_cpi = H["cpi_yoy"][i - 2].copy()
    obs_core = H["core_yoy"][i - 2].copy()
    obs_exp = H["exp_infl"][i - 1].copy()
    obs_gdp = _last_valid(H["gdp_yoy"][: i - 2])
    obs_dep3 = 100 * (np.log(H["inr"][i - 1]) - np.log(H["inr"][i - 4]))
    return obs_cpi, obs_core, obs_exp, obs_gdp, obs_dep3


def _last_valid(a):
    """Latest non-NaN row of a (k, n) array, per column."""
    out = np.full(a.shape[1], np.nan)
    for r in range(a.shape[0] - 1, -1, -1):
        m = np.isnan(out) & ~np.isnan(a[r])
        out[m] = a[r][m]
        if not np.isnan(out).any():
            break
    return out


def _active_override(overrides: dict, t: int, actor: str):
    """Branch overrides persist from their month onward (latest override at or before t wins)."""
    best = None
    for m in sorted(overrides):
        if m <= t and actor in overrides[m]:
            best = overrides[m][actor]
    return best
