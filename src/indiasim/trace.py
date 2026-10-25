"""Readable scenario traces generated FROM THE RUN LOG of one path (never from endpoint charts).

Event types: shock, regime, publication, decision, state_change, constraint.
* state_change events fire when a variable has moved by more than a materiality threshold since it was
  last reported, so slow drifts are not lost and noise is not reported.
* parents are resolved through the mechanism graph: for an event on X, the latest events on X's
  source variables inside the link's lag window. Decisions take PUBLICATION events as information parents.
* quantitative contributions are attached only where an exact decomposition exists (linear identities,
  the linear output-gap system, two-factor price x volume midpoint split, base-weighted CPI shares).
  Everything else is labelled qualitative.
"""
from __future__ import annotations

import numpy as np

from .config import load_mechanisms, POLICY_OPTIONS
from .model import P, GAP_CHANNELS, GOV_FUEL, month_label, cal_month, QUARTER_END

VARS = {
    # var: (label, unit, threshold, mode) mode: abs | rel (fraction) | any
    "risk_off": ("Global risk-off index", "z-score", 0.5, "abs"),
    "us10y": ("US 10Y Treasury yield", "%", 0.2, "abs"),
    "gdem": ("World demand gap", "pp", 0.5, "abs"),
    "food_shock": ("Food supply shock", "pp annualised", 1.5, "abs"),
    "brent": ("Brent crude", "USD/bbl", 0.05, "rel"),
    "crude_bill": ("Crude import bill", "USD bn/month", 0.6, "abs"),
    "prod_exp": ("Petroleum product exports", "USD bn/month", 0.4, "abs"),
    "oil_net": ("Net oil balance", "USD bn/month", 0.6, "abs"),
    "remit": ("Remittances (net secondary income)", "USD bn/month", 0.25, "abs"),
    "nonoil_bal": ("Non-oil goods balance", "USD bn/month", 0.6, "abs"),
    "ca": ("Current account balance", "USD bn/month", 0.8, "abs"),
    "fpi": ("Portfolio flows (FPI)", "USD bn/month", 0.8, "abs"),
    "ka": ("Capital account", "USD bn/month", 0.8, "abs"),
    "pressure": ("FX pressure (excess USD demand)", "USD bn/month", 1.0, "abs"),
    "inr": ("INR per USD", "INR/USD", 0.0075, "rel"),
    "reserves": ("FX reserves", "USD bn", 6.0, "abs"),
    "liq": ("Banking liquidity", "Rs lakh crore", 0.3, "abs"),
    "wacr": ("Overnight rate (WACR)", "%", 0.15, "abs"),
    "parity": ("Fuel import-parity cost", "Rs/litre", 0.03, "rel"),
    "retail_fuel": ("Retail auto-fuel price (Delhi blend)", "Rs/litre", 0.01, "rel"),
    "omc_margin": ("OMC marketing margin", "Rs/litre", 2.5, "abs"),
    "cpi_yoy": ("Headline CPI inflation", "% y/y", 0.25, "abs"),
    "food_yoy": ("Food inflation", "% y/y", 0.5, "abs"),
    "energy_yoy": ("Energy inflation", "% y/y", 1.0, "abs"),
    "core_yoy": ("Core inflation", "% y/y", 0.25, "abs"),
    "exp_infl": ("Inflation expectations", "% (1y)", 0.12, "abs"),
    "gap": ("Output gap", "% of potential", 0.2, "abs"),
    "fd_proj": ("Projected fiscal deficit (current FY)", "% GDP", 0.06, "abs"),
    "g10": ("10Y G-sec yield", "%", 0.12, "abs"),
    "credit_yoy": ("Bank credit growth", "% y/y", 0.4, "abs"),
    "stress": ("Credit stress index", "index", 0.08, "abs"),
}
_V = list(VARS)
GROUP1 = _V[:_V.index("pressure") + 1]
GROUP2 = _V[_V.index("inr"):_V.index("parity") + 1]
GROUP3 = _V[_V.index("parity") + 1:]
SUPPORT = {"identity": "High (arithmetic)", "rule": "Medium (explicit rule; behaviour uncertain)",
           "external": "Medium (benchmarked to published estimates)", "judgmental": "Low-Medium (judgmental)",
           "illustrative": "Low (illustrative placeholder)"}
DECOMP = {"ca": ["oil_net", "nonoil_bal", "services", "remit", "prim_inc"],
          "oil_net": ["prod_exp", "crude_bill", "other_energy"], "ka": ["fdi", "fpi", "ecb_other", "resid_other"]}
SIGN = {"crude_bill": -1, "other_energy": -1}


def _fmt(v, unit):
    if unit.startswith("USD/bbl") or unit.startswith("Rs/"):
        return f"{v:,.1f}"
    if unit == "INR/USD":
        return f"{v:,.2f}"
    return f"{v:,.2f}"


class TraceBuilder:
    def __init__(self, res, j: int = 0, run_id: str = "run"):
        self.r, self.j, self.run_id = res, j, run_id
        self.H = {k: v[:, j] for k, v in res.hist.items()}
        self.prm = {k: float(v[j]) for k, v in res.params.items()}
        self.mech = {m["id"]: m for m in load_mechanisms()["links"] if m["implemented"]}
        self.by_dst = {}
        for m in self.mech.values():
            self.by_dst.setdefault(m["dst"], []).append(m)
        self.events, self.last_event = [], {}
        self.path = res.path_indices[j]
        self.seq = 0

    # ------------------------------------------------------------------ helpers
    def _id(self, t, kind, var):
        self.seq += 1
        return f"{self.run_id}:p{self.path}:t{t:02d}:{kind}:{var}:{self.seq}"

    def _parents_for(self, var, t):
        parents, mids = [], []
        for m in self.by_dst.get(var, []):
            mids.append(m["id"])
            lag = int(m.get("lag", 0))
            for s in m["src"]:
                ev = self.last_event.get(s)
                if ev and t - lag - 3 <= ev["t"] <= t:
                    parents.append(ev["id"])
        return sorted(set(parents)), mids

    def _add(self, ev):
        ev.setdefault("run_id", self.run_id); ev.setdefault("path", self.path)
        ev["month"] = month_label(ev["t"])
        self.events.append(ev)
        for v in ev.get("vars", []):
            self.last_event[v["var"]] = ev
        return ev

    def _mech_meta(self, mids):
        kinds, ev, counter, params = [], set(), [], set()
        for mid in mids:
            m = self.mech[mid]
            kinds.append(m["kind"]); ev.update(m.get("evidence", [])); params.update(m.get("params", []))
            if m.get("counter"):
                counter.append(m["counter"])
        weakest = sorted(kinds, key=lambda k: ["identity", "rule", "external", "judgmental", "illustrative"].index(k))[-1] if kinds else "judgmental"
        return SUPPORT[weakest], sorted(ev), counter, sorted(params)

    # ------------------------------------------------------------------ build
    def build(self):
        H, T = self.H, self.r.T
        sc = self.r.spec.scenario
        last_val = {v: H[v][P] for v in VARS}
        last_t = {v: 0 for v in VARS}
        shocks_by_t = {}
        for s in sc.get("shocks", []):
            shocks_by_t.setdefault(int(s["start"]), []).append(s)
        for t in range(1, T + 1):
            i = P + t
            # --- scenario shocks
            for s in shocks_by_t.get(t, []):
                self._shock_event(t, s)
            # --- regimes
            for var, label in (("disrupt", "Gulf supply-disruption regime"), ("esc", "Escalation layer (Hormuz)"),
                               ("deanchor", "Inflation-expectations de-anchoring regime")):
                if H[var][i] != H[var][i - 1]:
                    on = H[var][i] > H[var][i - 1]
                    parents = []
                    if var == "deanchor" and "cpi_yoy" in self.last_event:
                        parents = [self.last_event["cpi_yoy"]["id"]]
                    if var != "deanchor":
                        parents = [e["id"] for e in self.events if e["type"] == "shock"][-1:]
                    self._add({"id": self._id(t, "regime", var), "t": t, "type": "regime", "title": f"{label} {'starts' if on else 'ends'}",
                               "vars": [{"var": var, "before": float(H[var][i - 1]), "after": float(H[var][i]), "unit": "flag"}],
                               "mechanism": ["M-OIL-01"] if var != "deanchor" else ["M-PRC-05"], "parents": parents,
                               "calc": ("Markov regime: monthly end-hazard drawn per path (pre-drawn uniform)" if var != "deanchor"
                                        else "headline CPI >6% for 3 consecutive months -> faster expectation updating"),
                               "support": "Low-Medium (judgmental hazard)", "probability_note": "Regime timing is random across paths; this is one path.",
                               "decomposition": "qualitative"})
            # --- publications (information available to actors)
            self._publications(t)
            # --- decisions and state changes in the model's within-month order
            self._decisions(t, "start")
            for grp, after in ((GROUP1, "fx"), (GROUP2, "fuel"), (GROUP3, None)):
                for var in grp:
                    cur = H[var][i]
                    lab, unit, thr, mode = VARS[var]
                    prev = last_val[var]
                    moved = abs(cur - prev) > (thr * abs(prev) if mode == "rel" else thr)
                    if moved:
                        self._state_event(t, var, prev, cur, last_t[var])
                        last_val[var], last_t[var] = cur, t
                if after:
                    self._decisions(t, after)
            # --- constraints
            for flag, title, mid in (("flag_excise_exhausted", "Excise headroom exhausted: cannot offset OMC losses further", "M-FUEL-02"),
                                     ("flag_res_floor", "Reserves near adequacy floor: intervention scaled back", "M-FX-02"),
                                     ("flag_corridor", "Overnight rate pinned at corridor edge", "M-LIQ-02"),
                                     ("flag_policy_switch", "Adaptive fuel rule switches to 50% pass-through (loss tolerance exceeded)", "M-FUEL-02")):
                if H[flag][i] > 0 and H[flag][i - 1] == 0:
                    self._add({"id": self._id(t, "constraint", flag), "t": t, "type": "constraint", "title": title, "vars": [],
                               "mechanism": [mid], "parents": [self.events[-1]["id"]] if self.events else [],
                               "calc": "binding constraint in rule", "support": "Medium (explicit rule)", "decomposition": "qualitative"})
        return self.events

    def _shock_event(self, t, s):
        tp = s["type"]
        if tp == "oil_escalation":
            desc = (f"Scenario shock: Hormuz escalation. Anchor +USD{s['premium']:.0f}/bbl, freight +{s.get('freight_extra', 0):.0f}, "
                    f"cracks +{s.get('crack_extra', 0):.0f}, {s.get('shortfall_pct', 0):.0f}% physical shortfall for {s['forced_months']} months; "
                    f"then {100 * s['hazard_after']:.0f}%/month chance of ending. Type: SUPPLY disruption.")
        elif tp == "oil_deescalation":
            desc = "Scenario shock: ceasefire/de-escalation ends the disruption regime."
        elif tp == "global_tightening":
            desc = (f"Scenario shock: US10Y +{s.get('us10y', 0):.2f}pp, dollar +{s.get('dxy_pct', 0):.0f}%, risk-off +{s.get('risk', 0):.1f}sd, "
                    f"world demand gap {s.get('gdem', 0):+.1f}pp for {s.get('months', 9)} months.")
        else:
            desc = f"Scenario shock: food supply +{s.get('magnitude', 0):.1f}pp annualised for {s.get('months', 5)} months."
        self._add({"id": self._id(t, "shock", tp), "t": t, "type": "shock", "title": desc,
                   "vars": [{"var": "shock_" + tp, "before": None, "after": None, "unit": "scenario"}], "mechanism": [],
                   "parents": [], "shock_params": s, "calc": "imposed by scenario configuration (exogenous)",
                   "support": "n/a (assumption)", "probability_note": "Exploratory scenario: no probability is attached to its occurrence.",
                   "decomposition": "n/a"})

    def _publications(self, t):
        H, i = self.H, P + t
        # CPI for month t-1 is released mid-month t (available to decisions from t+1)
        if t >= 2:
            m = i - 1
            self._add({"id": self._id(t, "pub", "cpi"), "t": t, "type": "publication",
                       "title": f"CPI for {month_label(t - 1)} published: headline {H['cpi_yoy'][m]:.2f}%, food {H['food_yoy'][m]:.2f}%, core {H['core_yoy'][m]:.2f}%",
                       "vars": [{"var": "pub_cpi", "before": None, "after": float(H['cpi_yoy'][m]), "unit": "% y/y"}],
                       "mechanism": ["M-PUB-01"], "parents": [self.last_event["cpi_yoy"]["id"]] if "cpi_yoy" in self.last_event else [],
                       "calc": "occurrence month t-1; publication ~12th of month t; usable by MPC from month t+1",
                       "support": "High (calendar)", "decomposition": "n/a"})
            self.last_event["pub_cpi"] = self.events[-1]
        if cal_month(t - 2) in QUARTER_END and t >= 2:
            q = i - 2
            if not np.isnan(H["gdp_yoy"][q]):
                self._add({"id": self._id(t, "pub", "gdp"), "t": t, "type": "publication",
                           "title": f"GDP for quarter ending {month_label(t - 2)} published: {H['gdp_yoy'][q]:.2f}% y/y",
                           "vars": [{"var": "pub_gdp", "before": None, "after": float(H['gdp_yoy'][q]), "unit": "% y/y"}],
                           "mechanism": ["M-REAL-11"], "parents": [self.last_event["gap"]["id"]] if "gap" in self.last_event else [],
                           "calc": "3-month average activity vs year-ago quarter; released ~2 months after quarter end",
                           "support": "Medium (monthly activity proxy aggregated)", "decomposition": "n/a"})
                self.last_event["pub_gdp"] = self.events[-1]

    def _decisions(self, t, stage):
        H, i, spec = self.H, P + t, self.r.spec
        info = [self.last_event[k]["id"] for k in ("pub_cpi", "pub_gdp") if k in self.last_event]
        if stage == "start" and H["mpc_meeting"][i] > 0:
            d = H["dec_mpc_delta"][i]
            rule = spec.overrides and _ov(spec, t, "rbi_mpc") or spec.policies["rbi_mpc"]
            obs = {"CPI (latest published, % y/y)": round(H["obs_cpi"][i], 2), "Core CPI (latest published)": round(H["obs_core"][i], 2),
                   "Expectations (%)": round(H["obs_exp"][i], 2), "GDP (latest published, % y/y)": round(H["obs_gdp"][i], 2),
                   "3m INR depreciation (%)": round(H["obs_dep3"][i], 2)}
            self._add({"id": self._id(t, "decision", "mpc"), "t": t, "type": "decision", "actor": "RBI MPC",
                       "title": f"MPC {'hikes' if d > 0 else 'cuts' if d < 0 else 'holds'} repo {abs(d) * 100:.0f}bp to {H['repo'][i]:.2f}% (rule: {rule})",
                       "vars": [{"var": "repo", "before": float(H["repo"][i - 1]), "after": float(H["repo"][i]), "unit": "%"}],
                       "mechanism": ["M-MPC-01"], "parents": info, "observed": obs,
                       "choices": ["-50bp", "-25bp", "hold", "+25bp", "+50bp"], "chosen": f"{d * 100:+.0f}bp",
                       "constraints": "repo bounded 3-9%; max 50bp per meeting; uses only published data",
                       "rationale": f"Rule target {H['mpc_target'][i]:.2f}% vs current {H['repo'][i - 1]:.2f}%: move 25bp if gap >0.2pp, 50bp if >1.5pp.",
                       "expected": "Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.",
                       "calc": "explicit rule (M-MPC-01)", "support": SUPPORT["rule"], "decomposition": "n/a",
                       "probability_note": "Rule-based behaviour; not an estimate of how the real MPC will act."})
        if stage == "start":
            self._fiscal_decision(t)
            return
        if stage == "fx":
            self._fx_decision(t)
            return
        gf = GOV_FUEL[int(H["dec_gov_fuel"][i])]
        dr = H["retail_fuel"][i] - H["retail_fuel"][i - 1]
        dx = H["excise"][i] - H["excise"][i - 1]
        prev_gf = GOV_FUEL[int(H["dec_gov_fuel"][i - 1])] if t > 1 else None
        if t == 1 or gf != prev_gf or abs(dr) > 0.5 or abs(dx) > 0.05 or H["comp"][i] > 0 and H["comp"][i - 1] == 0:
            self._add({"id": self._id(t, "decision", "gov_fuel"), "t": t, "type": "decision", "actor": "Government / OMCs",
                       "title": f"Fuel pricing: {POLICY_OPTIONS['gov_fuel'][gf]}. Retail {dr:+.2f} Rs/l, excise {dx:+.2f} Rs/l, Budget compensation Rs{H['comp'][i] * 1e5:,.0f} crore",
                       "vars": [{"var": "retail_fuel", "before": float(H["retail_fuel"][i - 1]), "after": float(H["retail_fuel"][i]), "unit": "Rs/litre"}],
                       "mechanism": ["M-FUEL-02"], "parents": [self.last_event["parity"]["id"]] if "parity" in self.last_event else [],
                       "observed": {"Import parity (Rs/l)": round(H["parity"][i], 2), "OMC margin if frozen (Rs/l)":
                                    round(H["retail_fuel"][i - 1] / (1 + self.prm["vat_rate"]) - self.prm["dealer_margin"] - H["excise"][i - 1] - H["parity"][i], 2),
                                    "Cumulative net OMC loss (Rs lakh cr)": round(H["cum_omc_loss"][i - 1], 2)},
                       "choices": list(POLICY_OPTIONS["gov_fuel"]), "chosen": gf,
                       "constraints": "excise floor 0 (headroom ~Rs1/l blended after Mar-2026 cut); LPG frozen in all options",
                       "rationale": "Configured policy (or branch override); OMCs/government observe same-month import parity.",
                       "expected": {"full_passthrough": "Households bear cost via fuel CPI; OMC losses close; fiscal neutral.",
                                    "freeze_omc_absorb": "CPI insulated; OMC balance sheets absorb losses; PSU capex at risk.",
                                    "freeze_budget_comp": "CPI insulated; fiscal deficit absorbs; bond supply rises.",
                                    "partial_50": "Cost shared: half via prices, half via Budget.",
                                    "excise_cut": "Revenue forgone; limited by tiny remaining excise.",
                                    "adaptive_threshold": "Freeze until loss tolerance, then share via prices."}[gf],
                       "calc": "explicit rule (M-FUEL-02)", "support": SUPPORT["rule"], "decomposition": "n/a"})

    def _fx_decision(self, t):
        H, i = self.H, P + t
        if abs(H["interv"][i]) > 1.0:
            self._add({"id": self._id(t, "decision", "fx"), "t": t, "type": "decision", "actor": "RBI (FX)",
                       "title": f"RBI {'sells' if H['interv'][i] > 0 else 'buys'} USD {abs(H['interv'][i]):.1f}bn ({100 * H['dec_fx_phi'][i]:.0f}% of pressure)",
                       "vars": [{"var": "interv", "before": float(H["interv"][i - 1]), "after": float(H["interv"][i]), "unit": "USD bn"}],
                       "mechanism": ["M-FX-02", "M-LIQ-01"], "parents": [self.last_event["pressure"]["id"]] if "pressure" in self.last_event else [],
                       "observed": {"FX pressure (USD bn)": round(H["pressure"][i], 2), "Reserves prior (USD bn)": round(H["reserves"][i - 1], 1)},
                       "choices": ["heavy 75%", "moderate 50%", "light 25%"], "chosen": f"{100 * H['dec_fx_phi'][i]:.0f}%",
                       "constraints": f"scaled down near floor (~USD{float(np.atleast_1d(self.r.meta['floor'])[self.j]):.0f}bn); cannot sell below 95% of floor",
                       "rationale": "RBI observes same-month market pressure (high-frequency data).",
                       "expected": f"Drains Rs{abs(H['interv'][i]) * H['inr'][i] / 1000:.2f} lakh crore of liquidity; sterilised share {100 * H['steril'][i] / max(abs(H['interv'][i]) * H['inr'][i] / 1000, 1e-9):.0f}%.",
                       "calc": "interv = share x pressure", "support": SUPPORT["rule"], "decomposition": "n/a"})

    def _fiscal_decision(self, t):
        H, i = self.H, P + t
        if H["capex_cut"][i] > 0.005:
            self._add({"id": self._id(t, "decision", "fiscal"), "t": t, "type": "decision", "actor": "Government (fiscal)",
                       "title": f"Capex cut Rs{H['capex_cut'][i] * 1e5:,.0f} crore this month to defend the deficit target",
                       "vars": [{"var": "capex_cut", "before": float(H["capex_cut"][i - 1]), "after": float(H["capex_cut"][i]), "unit": "Rs lakh crore"}],
                       "mechanism": ["M-FIS-02"], "parents": [self.last_event["fd_proj"]["id"]] if "fd_proj" in self.last_event else [],
                       "observed": {"Projected FD last month (% GDP)": round(H["obs_fd_proj"][i], 2), "Target": H["fd_target"][i]},
                       "choices": ["accommodate", "hold_target"], "chosen": "hold_target", "constraints": "cut capped at 25% of monthly capex",
                       "rationale": "Closes half the projected overrun over remaining FY months.", "expected": "Lower deficit; demand falls (capex multiplier).",
                       "calc": "explicit rule (M-FIS-02)", "support": SUPPORT["rule"], "decomposition": "n/a"})

    def _state_event(self, t, var, prev, cur, t_prev):
        H, i, ip = self.H, P + t, P + t_prev
        lab, unit, _, _ = VARS[var]
        parents, mids = self._parents_for(var, t)
        support, evid, counter, params = self._mech_meta(mids) if mids else ("n/a", [], [], [])
        ev = {"id": self._id(t, "state", var), "t": t, "type": "state_change",
              "title": f"{lab} {'rises' if cur > prev else 'falls'} to {_fmt(cur, unit)} {unit} (from {_fmt(prev, unit)} in {month_label(t_prev)})",
              "vars": [{"var": var, "before": float(prev), "after": float(cur), "unit": unit, "since": month_label(t_prev)}],
              "mechanism": mids, "parents": parents, "support": support, "evidence": evid, "counterforces": counter, "params": params,
              "lag": max([int(self.mech[m].get("lag", 0)) for m in mids], default=0), "decomposition": "qualitative"}
        if not parents:
            ev["root_note"] = ("No reportable parent event within the lag window: the move comes from this path's random "
                               "innovations and/or persistence of earlier changes.")
        contrib = None
        if var == "gap":
            contrib = {ch: float(H["c_" + ch][i] - H["c_" + ch][ip]) for ch in GAP_CHANNELS}
            ev["decomposition"] = "exact (linear channel system)"
        elif var in DECOMP:
            contrib = {c: float(H[c][i] - H[c][ip]) * SIGN.get(c, 1) for c in DECOMP[var]}
            ev["decomposition"] = "exact (accounting identity; signs as effect on balance)"
        elif var == "crude_bill":
            p0, p1 = H["brent"][ip] + H["freight"][ip], H["brent"][i] + H["freight"][i]
            v0, v1 = H["crude_vol"][ip], H["crude_vol"][i]
            k = self.prm["bbl_per_t_crude"] / 1000
            contrib = {"price (Brent+freight)": float(k * (v0 + v1) / 2 * (p1 - p0)), "volume": float(k * (p0 + p1) / 2 * (v1 - v0))}
            ev["decomposition"] = "exact (two-factor midpoint split)"
            ev["calc"] = f"bill = {v1:.2f} MMT x {self.prm['bbl_per_t_crude']} bbl/t x USD{p1:.1f} / 1000 = USD{cur:.2f}bn (INR does not enter)"
        elif var == "cpi_yoy":
            w = {"food": self.prm["w_food"], "energy": self.prm["w_energy"], "core": self.prm["w_core"]}
            base = sum(w[k] * H[k + "_idx"][i - 12] for k in w)
            contrib = {k: float(w[k] * H[k + "_idx"][i - 12] / base * H[k + "_yoy"][i]) for k in w}
            ev["decomposition"] = "exact (base-weighted component contributions to the LEVEL of headline y/y)"
        elif var == "inr":
            dep_sum = H["dep"][ip + 1:i + 1]
            press = (H["pressure"][ip + 1:i + 1] - H["interv"][ip + 1:i + 1]) / self.prm["fx_depth"]
            dx = 0.3 * 100 * np.diff(H["dxy"][ip:i + 1])
            contrib = {"unabsorbed pressure": float(press.sum()), "dollar index": float(dx.sum()),
                       "noise": float(dep_sum.sum() - press.sum() - dx.sum())}
            ev["decomposition"] = "exact in log-% terms (sum of monthly depreciation drivers)"
        elif var == "reserves":
            contrib = {"intervention (BoP)": float(-H["interv"][ip + 1:i + 1].sum()), "valuation": float(H["valuation"][ip + 1:i + 1].sum())}
            ev["decomposition"] = "exact (stock-flow identity)"
        elif var == "omc_margin":
            ev["calc"] = (f"margin = {H['retail_fuel'][i]:.2f}/(1+{self.prm['vat_rate']:.3f}) - {self.prm['dealer_margin']:.1f} dealer - "
                          f"{H['excise'][i]:.2f} excise - {H['parity'][i]:.2f} parity = {cur:.2f} Rs/l")
            ev["decomposition"] = "exact (price build-up identity)"
        if contrib is not None:
            ev["contribution"] = {k: round(v, 3) for k, v in sorted(contrib.items(), key=lambda kv: -abs(kv[1]))}
        self._add(ev)
        ev["narrative"] = narrate(ev)


def _ov(spec, t, actor):
    best = None
    for m in sorted(spec.overrides):
        if m <= t and actor in spec.overrides[m]:
            best = spec.overrides[m][actor]
    return best


def narrate(ev) -> str:
    """Deterministic template narrative from the structured record."""
    s = f"{ev['month']}: {ev['title']}."
    if ev.get("contribution"):
        top = list(ev["contribution"].items())[:3]
        s += " Main drivers: " + ", ".join(f"{k} {v:+.2f}" for k, v in top) + f" [{ev['decomposition']}]."
    if ev.get("mechanism"):
        s += " Mechanism: " + ", ".join(ev["mechanism"]) + "."
    if ev.get("counterforces"):
        s += " Could be interrupted by: " + "; ".join(sorted(set(ev["counterforces"])))[:200] + "."
    return s


def build_trace(res, j=0, run_id="run"):
    tb = TraceBuilder(res, j, run_id)
    evs = tb.build()
    for e in evs:
        e.setdefault("narrative", narrate(e))
    return evs


def ancestors(events, eid, depth=6):
    """Causal chain (ancestors) of an event: list of (level, event)."""
    by_id = {e["id"]: e for e in events}
    out, frontier, seen = [], [(0, eid)], set()
    while frontier:
        lvl, cur = frontier.pop(0)
        if cur in seen or cur not in by_id or lvl > depth:
            continue
        seen.add(cur)
        out.append((lvl, by_id[cur]))
        for p in by_id[cur].get("parents", []):
            frontier.append((lvl + 1, p))
    return out


def reconcile(events, res, j=0) -> list[str]:
    """Every numeric claim in state/decision events must equal the run log. Returns list of mismatches."""
    bad = []
    for e in events:
        for v in e.get("vars", []):
            name = v["var"]
            if name in res.hist and v.get("after") is not None:
                actual = res.hist[name][P + e["t"], j]
                if not np.isclose(actual, v["after"], rtol=1e-9, atol=1e-9):
                    bad.append(f"{e['id']}: {name} {v['after']} != log {actual}")
        if e.get("decomposition", "").startswith("exact") and e.get("contribution") and e["type"] == "state_change":
            var = e["vars"][0]["var"]
            tot = sum(e["contribution"].values())
            if var in ("gap",) or var in DECOMP or var in ("crude_bill", "reserves"):
                target = e["vars"][0]["after"] - e["vars"][0]["before"]
                if not np.isclose(tot, target, atol=2e-3 * max(1, len(e["contribution"]))):
                    bad.append(f"{e['id']}: contributions {tot:.4f} != change {target:.4f}")
            elif var == "cpi_yoy":
                if not np.isclose(tot, e["vars"][0]["after"], atol=1e-2):
                    bad.append(f"{e['id']}: cpi contributions {tot:.4f} != level {e['vars'][0]['after']:.4f}")
    return bad
