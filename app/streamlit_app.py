"""India Economic Scenario & Strategic Risk Simulator - local Streamlit interface.

Run:  streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from indiasim import ENGINE_VERSION  # noqa: E402
from indiasim.config import (RunSpec, list_scenarios, load_scenario, load_params, load_mechanisms, load_baseline, POLICY_OPTIONS,  # noqa: E402
                             STRUCTURE_OPTIONS, spec_hash, CONFIG, DATA)
from indiasim.model import simulate, P, month_label, GAP_CHANNELS  # noqa: E402
from indiasim.risk import (DEFAULT_THRESHOLDS, Threshold, evaluate_threshold, joint_frequency, bands, path_metrics,  # noqa: E402
                           representative_paths, expected_shortfall, convergence, sensitivity_rank, mixture, LABEL_FREQ, LABEL_EXPL)
from indiasim.trace import build_trace, ancestors, reconcile, VARS as TRACE_VARS  # noqa: E402
from indiasim.analysis import branch, divergence_report, compare_strategies, reverse_stress, after_action, burden_table  # noqa: E402
from indiasim.checks import accounting_checks  # noqa: E402
from indiasim.randomness import CORR_REPORTS  # noqa: E402
from indiasim.export import save_config, load_config, results_summary, bands_csv, trace_markdown, assumptions_report, _clean  # noqa: E402
from indiasim.insights import overview_takeaways, compare_takeaways  # noqa: E402

st.set_page_config(page_title="India Scenario & Risk Simulator", layout="wide", page_icon=":material/monitoring:")


def _st_version():
    try:
        return tuple(int(x) for x in st.__version__.split(".")[:2])
    except Exception:  # noqa: BLE001
        return (0, 0)


# Streamlit >= 1.50 uses width="stretch"; older releases only understand use_container_width=True.
WIDE = {"width": "stretch"} if _st_version() >= (1, 50) else {"use_container_width": True}

C = {"blue": "#0072B2", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "verm": "#D55E00", "purple": "#CC79A7", "grey": "#7F7F7F", "black": "#222"}
UNITS = {"brent": "USD/bbl", "inr": "INR per USD", "reserves": "USD bn", "repo": "%", "cpi_yoy": "% y/y", "core_yoy": "% y/y", "food_yoy": "% y/y",
         "gdp_yoy": "% y/y (quarterly)", "gap": "% of potential", "fd_proj": "% of GDP (FY projection)", "g10": "%", "retail_fuel": "Rs/litre",
         "omc_margin": "Rs/litre", "ca": "USD bn/month", "pressure": "USD bn/month", "exp_infl": "%", "credit_yoy": "% y/y", "cum_omc_loss": "Rs lakh crore",
         "wacr": "%", "liq": "Rs lakh crore", "stress": "index"}
LABELS = {"brent": "Brent crude", "inr": "Rupee (INR per USD, up = weaker)", "reserves": "FX reserves", "repo": "Repo rate", "cpi_yoy": "Headline CPI",
          "core_yoy": "Core CPI", "food_yoy": "Food CPI", "gdp_yoy": "Real GDP growth", "gap": "Output gap", "fd_proj": "Central fiscal deficit (projected FY)",
          "g10": "10Y G-sec yield", "retail_fuel": "Retail auto fuel (Delhi blend)", "omc_margin": "OMC marketing margin", "ca": "Current account",
          "pressure": "FX pressure", "exp_infl": "Inflation expectations", "credit_yoy": "Bank credit growth", "cum_omc_loss": "Cumulative OMC net loss",
          "wacr": "Overnight rate (WACR)", "liq": "Banking liquidity", "stress": "Credit stress"}
GLOSSARY = {
    "CAD (current account deficit)": "When India pays the world more for goods, services, income and transfers than it receives. Financed by capital inflows or by running down reserves. A larger CAD is pressure on the rupee only if it is not financed.",
    "FX pressure": "Net demand for dollars at the current exchange rate = -(current account + capital account). The RBI absorbs part by selling dollars; the rest moves the rupee.",
    "Repo rate": "The RBI's policy rate. The overnight market rate (WACR) moves within the SDF-MSF corridor around it.",
    "OMC": "Oil marketing companies (IOC, BPCL, HPCL). With pump prices frozen, they lose money when import costs rise ('under-recovery').",
    "Import parity": "What a litre of fuel costs India at international prices in rupees: (Brent + product crack + freight) x INR / 159 litres per barrel.",
    "Output gap": "How far activity is above (+) or below (-) its sustainable level, in %. Negative = slack.",
    "Conditional model frequency": "The share of simulated paths in which something happens under the chosen assumptions. NOT a forecast probability.",
    "FPI": "Foreign portfolio investors: flows into Indian shares and bonds. Fast-moving and sensitive to risk appetite and yield spreads.",
}
BUNDLES = {
    "Status quo (freeze, OMCs absorb)": {},
    "Full pass-through": {"gov_fuel": "full_passthrough"},
    "Freeze + Budget compensates": {"gov_fuel": "freeze_budget_comp"},
    "50% pass-through + half compensation": {"gov_fuel": "partial_50"},
    "Excise cut (limited headroom)": {"gov_fuel": "excise_cut"},
    "Adaptive (freeze until loss tolerance)": {"gov_fuel": "adaptive_threshold"},
    "Status quo + hold deficit target": {"gov_fiscal": "hold_target"},
    "Status quo + RBI FX defence rule": {"rbi_mpc": "fx_defence"},
    "Status quo + RBI looks through supply shock": {"rbi_mpc": "look_through"},
    "Status quo + light FX intervention": {"rbi_fx": "light"},
}


# ------------------------------------------------------------------ cached runs
@st.cache_data(show_spinner=False, max_entries=24)
def run_cached(spec_json: str):
    spec = RunSpec.from_dict(json.loads(spec_json))
    return simulate(spec)


def spec_json(spec: RunSpec) -> str:
    return json.dumps(spec.to_dict(), sort_keys=True, default=str)


def run(spec):
    return run_cached(spec_json(spec))


# ------------------------------------------------------------------ sidebar: global controls
def sidebar() -> RunSpec:
    sb = st.sidebar
    base = load_baseline()
    sb.markdown(f"### Scope\n**Baseline snapshot:** {base['as_of']} (t0 = Oct 2026)  \n"
                "**Data status:** dated, partially sourced snapshot; not live. Parameters are judgmental/illustrative, not estimated.")
    sids = list_scenarios()
    sid = sb.selectbox("Scenario", sids, index=sids.index("oil_escalation"), key="sid")
    sc = copy.deepcopy(load_scenario(sid))
    sb.caption(sc["description"].strip())
    horizon = sb.radio("Horizon (months)", [12, 24], index=1, horizontal=True, key="horizon")
    with sb.expander("Shock settings (fixed by intervention)", expanded=True):
        for k, s in enumerate(sc["shocks"]):
            tp = s["type"]
            if tp == "oil_escalation":
                s["premium"] = st.slider("Oil escalation premium (USD/bbl on anchor)", 0.0, 80.0, float(s["premium"]), 5.0, key=f"prem{k}")
                s["forced_months"] = st.slider("Forced duration (months)", 1, 12, int(s["forced_months"]), key=f"fm{k}")
                s["hazard_after"] = st.slider("Monthly chance escalation ends afterwards", 0.05, 0.6, float(s["hazard_after"]), 0.05, key=f"ha{k}")
                s["shortfall_pct"] = st.slider("Physical crude shortfall during forced window (%)", 0.0, 10.0, float(s["shortfall_pct"]), 0.5, key=f"sf{k}")
                s["start"] = st.slider("Start month (1 = Nov 2026)", 1, horizon, int(s["start"]), key=f"st{k}")
            elif tp == "global_tightening":
                mult = st.slider("Global tightening severity (x scenario default)", 0.0, 2.0, 1.0, 0.25, key=f"gt{k}")
                for f in ("us10y", "dxy_pct", "risk", "gdem"):
                    s[f] = s[f] * mult
                s["months"] = st.slider("Tightening persists (months)", 3, 18, int(s["months"]), key=f"gm{k}")
            elif tp == "food_supply":
                s["magnitude"] = st.slider("Food shock (pp annualised)", 0.0, 12.0, float(s["magnitude"]), 0.5, key=f"fs{k}")
                s["months"] = st.slider("Food shock months", 1, 12, int(s["months"]), key=f"fmo{k}")
                s["start"] = st.slider("Food shock start month", 1, horizon, min(int(s["start"]), horizon), key=f"fst{k}")
            elif tp == "oil_deescalation":
                s["start"] = st.slider("Ceasefire month", 1, horizon, int(s["start"]), key=f"de{k}")
        if not sc["shocks"]:
            st.caption("Reference path: no imposed shock. Only the endogenous model and random regime timing move.")
        sc["shocks"] = [s for s in sc["shocks"] if int(s.get("start", 1)) <= horizon]
    with sb.expander("Actor responses", expanded=True):
        pol = {}
        names = {"gov_fuel": "Govt / OMC fuel pricing", "gov_fiscal": "Govt fiscal stance", "rbi_mpc": "RBI monetary policy rule",
                 "rbi_fx": "RBI FX intervention", "rbi_steril": "RBI sterilisation"}
        for actor, opts in POLICY_OPTIONS.items():
            keys = list(opts)
            pol[actor] = st.selectbox(names[actor], keys, index=keys.index(sc["policies"][actor]), format_func=lambda o, a=actor: f"{o}: {POLICY_OPTIONS[a][o]}",
                                      key=f"pol_{actor}")
    with sb.expander("Model structure / regime"):
        stc = {}
        for k, opts in STRUCTURE_OPTIONS.items():
            keys = list(opts)
            stc[k] = st.selectbox(k, keys, index=keys.index(sc["structure"][k]), format_func=lambda o, d=opts: f"{o}: {d[o]}", key=f"st_{k}")
    with sb.expander("Uncertainty", expanded=True):
        pm = st.radio("Parameter uncertainty", ["sampled", "central"], horizontal=True, key="pm",
                      help="sampled: each path draws uncertain parameters once (outer loop). central: all paths use central values.")
        sm = st.radio("Shocks", ["stochastic", "deterministic"], horizontal=True, key="sm",
                      help="deterministic: zero innovations; regimes end at their median duration. One path is enough.")
        n = st.select_slider("Paths", [1, 100, 250, 500, 1000, 2000, 4000], value=1000 if sm == "stochastic" else 1, key="npaths",
                             help="Preview = 250. Runtime ~0.2s per 1,000 paths. More paths narrow sampling error, not model uncertainty.")
        seed = int(st.number_input("Seed", value=20261025, step=1, key="seed"))
    spec = RunSpec(scenario=sc, policies=pol, structure=stc, horizon=int(horizon), n_paths=int(n), seed=seed, param_mode=pm, shock_mode=sm)
    errs = spec.validate()
    if errs:
        sb.error("; ".join(errs))
    run_btn = sb.button("Run simulation", type="primary", **WIDE)
    with sb.expander("Save / load configuration"):
        st.download_button("Download config JSON", save_config(spec), file_name=f"config_{spec_hash(spec)}.json", mime="application/json")
        up = st.file_uploader("Load config JSON", type="json")
        if up is not None:
            lspec, warns = load_config(up.read().decode())
            for w in warns:
                st.warning(w)
            st.session_state["loaded_spec"] = lspec
            st.info("Loaded. It runs as-is (sidebar widgets are not changed); press 'Run loaded config'.")
        if "loaded_spec" in st.session_state and st.button("Run loaded config"):
            st.session_state["result_spec"] = st.session_state["loaded_spec"]
    if run_btn and not errs:
        st.session_state["result_spec"] = spec
    return spec


def spec_diff(a: RunSpec, b: RunSpec) -> list[str]:
    da, db = a.to_dict(), b.to_dict()
    out = []
    for k in ("horizon", "n_paths", "seed", "param_mode", "shock_mode"):
        if da[k] != db[k]:
            out.append(f"{k}: {db[k]} -> {da[k]}")
    for grp in ("policies", "structure"):
        for k in da[grp]:
            if da[grp][k] != db[grp].get(k):
                out.append(f"{k}: {db[grp].get(k)} -> {da[grp][k]}")
    if da["scenario"] != db["scenario"]:
        out.append(f"scenario/shock settings: {db['scenario'].get('id')} -> {da['scenario'].get('id')} (or shock sliders changed)")
    return out


def scope_line(spec: RunSpec) -> str:
    p = spec.policies
    return (f"{spec.scenario.get('id')} | fuel={p['gov_fuel']} fiscal={p['gov_fiscal']} mpc={p['rbi_mpc']} fx={p['rbi_fx']} | "
            f"{spec.structure['expectations']}/{spec.structure['fx_regime']} | n={spec.n_paths} {spec.param_mode}/{spec.shock_mode} seed={spec.seed} | run {spec_hash(spec)}")


# ------------------------------------------------------------------ charts
def fan(res, var, title=None, reps=None, height=300, extra=None):
    b = bands(res, var)
    x = res.meta["months"]
    fig = go.Figure()
    quarterly = var == "gdp_yoy"
    mode = "lines+markers" if quarterly else "lines"
    if res.spec.n_paths > 1:
        for lo, hi, op, nm in ((5, 95, 0.18, "P5-P95"), (25, 75, 0.35, "P25-P75")):
            xs, ylo, yhi = x, b[lo], b[hi]
            if quarterly:
                m = np.isfinite(b[50]); xs = list(np.array(x)[m]); ylo, yhi = b[lo][m], b[hi][m]
            fig.add_trace(go.Scatter(x=list(xs) + list(xs)[::-1], y=list(yhi) + list(ylo)[::-1], fill="toself", fillcolor=f"rgba(0,114,178,{op})",
                                     line=dict(width=0), name=f"model band {nm}", hoverinfo="skip"))
    ym = b[50]
    xs = x
    if quarterly:
        m = np.isfinite(ym); xs = list(np.array(x)[m]); ym = ym[m]
    fig.add_trace(go.Scatter(x=xs, y=ym, mode=mode, line=dict(color=C["blue"], width=2),
                             name="median of paths (marginal)" if res.spec.n_paths > 1 else "simulated path"))
    if reps:
        for (nm, rp), col in zip(reps.items(), [C["green"], C["black"], C["verm"], C["purple"]]):
            y = res.hist[var][P:, rp["j"]]
            xx = x
            if quarterly:
                mm = np.isfinite(y); xx = list(np.array(x)[mm]); y = y[mm]
            fig.add_trace(go.Scatter(x=xx, y=y, mode=mode, line=dict(color=col, width=1, dash="dot"), name=f"path {rp['path_index']} ({nm.split(' ')[0]})"))
    if extra:
        for nm, (xx, yy, col) in extra.items():
            fig.add_trace(go.Scatter(x=xx, y=yy, mode=mode, line=dict(color=col, width=2, dash="dash"), name=nm))
    if var != "gdp_yoy":
        fig.add_trace(go.Scatter(x=[x[0]], y=[res.hist[var][P, 0]], mode="markers", marker=dict(symbol="diamond", size=11, color=C["orange"], line=dict(color="black", width=1)),
                                 name="observed t0 snapshot (Oct 2026)"))
    fig.update_layout(title=dict(text=f"{title or LABELS.get(var, var)} <span style='font-size:11px;color:#777'>[{UNITS.get(var, '')}]</span>", font=dict(size=14)),
                      height=height, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
                      yaxis_title=UNITS.get(var, ""), hovermode="x unified", template="plotly_white")
    return fig


def show_fig(fig, spec, key=None):
    st.plotly_chart(fig, **WIDE, key=key)
    st.caption(f"Scope: {scope_line(spec)}")


def hist_fig(x, title, unit, color=C["blue"], vline=None):
    fig = go.Figure(go.Histogram(x=x[np.isfinite(x)], nbinsx=40, marker_color=color))
    if vline is not None:
        fig.add_vline(x=vline, line_dash="dash", line_color=C["verm"])
    fig.update_layout(title=title, height=260, margin=dict(l=10, r=10, t=40, b=10), xaxis_title=unit, yaxis_title="paths", template="plotly_white")
    return fig


# ------------------------------------------------------------------ views
def view_overview(res):
    spec = res.spec
    st.subheader("Overview")
    st.info(f"**How to read the numbers.** Bands and percentages are {LABEL_FREQ.lower()}. No result here is a validated forecast. "
            "Medians of individual months are not a single feasible path: use Scenario playback for real paths.")
    m = path_metrics(res)
    cols = st.columns(6)
    cards = [("Peak CPI, %", "peak_cpi", 1, 90), ("Peak INR/USD", "peak_inr", 1, 90), ("Reserve low, USD bn", "min_reserves", 0, 10),
             ("Weakest GDP qtr, %", "min_gdp_yoy", 1, 10), ("Peak repo, %", "peak_repo", 2, 90), ("FY27 deficit, % GDP", "fd_fy27", 2, 90)]
    for c, (lab, k, dp, q) in zip(cols, cards):
        x = m[k]
        if np.isfinite(x).any():
            c.metric(lab, f"{np.nanmedian(x):.{dp}f}", help=f"median across paths; {'P90' if q == 90 else 'P10'} adverse = {np.nanpercentile(x, q):.2f}")
            c.caption(f"adverse P{q}: {np.nanpercentile(x, q):.2f}")
    reps = representative_paths(res) if spec.n_paths >= 20 else None
    show_reps = st.toggle("Overlay actual representative paths (benign / central / adverse / tail)", value=False)
    vars_ = ["brent", "inr", "cpi_yoy", "gdp_yoy", "reserves", "repo", "retail_fuel", "omc_margin", "fd_proj"]
    for row in range(0, len(vars_), 3):
        cs = st.columns(3)
        for c, v in zip(cs, vars_[row:row + 3]):
            with c:
                show_fig(fan(res, v, reps=reps if show_reps else None), spec, key=f"ov_{v}")
    st.markdown("#### Takeaways (generated from this run)")
    for t in overview_takeaways(res):
        st.markdown(f"- {t}")
    st.markdown("#### Threshold events")
    rows = []
    for th in DEFAULT_THRESHOLDS:
        e = evaluate_threshold(res, th)
        rows.append({"event": th.describe(), "frequency": e["frequency"], "95% sampling CI": f"{e['ci95'][0]:.3f}-{e['ci95'][1]:.3f}",
                     "median first month": month_label(int(e["summary"]["median_first_passage_month"])) if np.isfinite(e["summary"]["median_first_passage_month"]) else "-",
                     "not recovered by horizon (share of breaches)": e["summary"]["share_not_recovered_given_breach"], "label": "conditional model frequency"})
    st.dataframe(pd.DataFrame(rows), **WIDE, hide_index=True,
                 column_config={"frequency": st.column_config.ProgressColumn(format="%.3f", min_value=0, max_value=1)})
    with st.expander("Plain-language definitions"):
        for k, v in GLOSSARY.items():
            st.markdown(f"**{k}.** {v}")


def view_causal_map():
    st.subheader("Causal map")
    st.caption("Solid = implemented and executed by the engine. Dashed grey = conceptual gap (NOT implemented). Colour = evidence basis. "
               "Right-to-left links are lagged feedbacks resolved through time, not simultaneous arrows.")
    mech = load_mechanisms()["links"]
    cols = {0: ["shock_oil_escalation", "shock_oil_deescalation", "shock_global_tightening", "shock_food_supply", "disrupt", "esc"],
            1: ["brent", "crack", "shortfall", "us10y", "dxy", "risk_off", "gdem", "food_shock"],
            2: ["crude_vol", "crude_bill", "prod_exp", "other_energy", "oil_net", "nonoil_bal", "services", "remit", "prim_inc", "ca", "fpi", "ecb_other", "ka"],
            3: ["pressure", "interv", "fx_adjust", "inr", "reserves", "liq", "wacr", "repo", "g10"],
            4: ["parity", "retail_fuel", "omc_margin", "lpg_loss", "energy_yoy", "food_yoy", "core_yoy", "cpi_yoy", "exp_infl", "published"],
            5: ["gap", "gdp_yoy", "credit_yoy", "stress", "fd_proj", "capex_cut", "debt", "employment", "state_finances", "china_trade",
                "bank_balance_sheets", "sectors_equity", "agri_output", "opec_spr", "gold_imports", "forward_book", "wages"]}
    pos = {}
    for c, nodes in cols.items():
        for k, nd in enumerate(nodes):
            pos[nd] = (c * 2.0, -k * 1.0 - (c % 2) * 0.5)
    for m in mech:
        for nd in m["src"] + [m["dst"]]:
            pos.setdefault(nd, (11.0, -len(pos) * 0.3))
    kind_col = {"identity": C["green"], "rule": C["blue"], "external": C["purple"], "judgmental": C["orange"], "illustrative": C["verm"], "gap": "#BBBBBB"}
    fig = go.Figure()
    for m in mech:
        for s in m["src"]:
            (x0, y0), (x1, y1) = pos[s], pos[m["dst"]]
            back = x1 < x0
            fig.add_trace(go.Scatter(x=[x0, (x0 + x1) / 2, x1], y=[y0, (y0 + y1) / 2 + (0.6 if back else 0), y1], mode="lines",
                                     line=dict(color=kind_col.get(m["kind"], C["grey"]), width=1.3 if m["implemented"] else 1,
                                               dash="solid" if m["implemented"] else "dash", shape="spline"),
                                     hoverinfo="text", text=f"{m['id']} ({m['kind']}, lag {m['lag']}): {m['desc']}", showlegend=False))
    implemented_nodes = {n for m in mech if m["implemented"] for n in m["src"] + [m["dst"]]}
    xs, ys, tx, colr = [], [], [], []
    for nd, (x, y) in pos.items():
        xs.append(x); ys.append(y); tx.append(nd); colr.append(C["black"] if nd in implemented_nodes else "#BBBBBB")
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+text", text=tx, textposition="middle right", textfont=dict(size=10, color=colr),
                             marker=dict(size=9, color=colr), hoverinfo="text", showlegend=False))
    for k, col in kind_col.items():
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=col, dash="dash" if k == "gap" else "solid"), name=k))
    for c, lab in enumerate(["Shocks & regimes", "Global drivers", "External accounts", "FX, money, rates", "Fuel & prices", "Real, credit, fiscal"]):
        fig.add_annotation(x=c * 2.0, y=1.2, text=f"<b>{lab}</b>", showarrow=False, font=dict(size=11))
    fig.update_layout(height=820, xaxis=dict(visible=False, range=[-0.5, 12.5]), yaxis=dict(visible=False), template="plotly_white",
                      margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=1.04))
    st.plotly_chart(fig, **WIDE)
    ids = [f"{m['id']}: {', '.join(m['src'])} -> {m['dst']}" for m in mech]
    pick = st.selectbox("Drill into a link", ids)
    m = mech[ids.index(pick)]
    pc = load_params()["params"]
    ev = pd.read_csv(DATA / "EVIDENCE.csv")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"**{m['id']}** - {'IMPLEMENTED' if m['implemented'] else 'NOT IMPLEMENTED (gap)'} - kind: `{m['kind']}`, lag {m['lag']} months")
        st.write(m["desc"])
        st.markdown(f"**Counterforces:** {m.get('counter') or '-'}  \n**Would be invalidated if:** {m.get('invalid') or '-'}")
    with c2:
        if m.get("params"):
            st.dataframe(pd.DataFrame([{"param": p_, "value": pc[p_]["value"], "range": f"{pc[p_].get('low', '')}-{pc[p_].get('high', '')}",
                                        "status": pc[p_]["status"], "unit": pc[p_].get("unit")} for p_ in m["params"] if p_ in pc]), hide_index=True, **WIDE)
        if m.get("evidence"):
            st.dataframe(ev[ev.evidence_id.isin(m["evidence"])][["evidence_id", "item", "value", "publisher", "url", "publication_date", "kind"]],
                         hide_index=True, **WIDE, column_config={"url": st.column_config.LinkColumn()})


def view_playback(res):
    spec = res.spec
    st.subheader("Scenario playback")
    st.caption(f"{LABEL_EXPL}. The narrative is generated from this path's run log. Pre-branch history stays fixed when you replay.")
    reps = representative_paths(res) if spec.n_paths >= 20 else {}
    opts = {f"{k} - path {v['path_index']}": v["path_index"] for k, v in reps.items()}
    opts["choose a path index"] = None
    c1, c2 = st.columns([2, 1])
    choice = c1.selectbox("Path", list(opts), index=1 if len(opts) > 2 else 0)
    pidx = opts[choice]
    if pidx is None:
        pidx = int(c2.number_input("Path index", 0, spec.path_offset + spec.n_paths - 1, 0))
    one_spec = copy.deepcopy(spec); one_spec.n_paths, one_spec.path_offset = 1, int(pidx)
    one = run(one_spec)
    rid = spec_hash(spec)
    events = build_trace(one, 0, rid)
    bad = reconcile(events, one, 0)
    st.caption(f"{len(events)} events | reconciliation with run log: {'all values match' if not bad else str(bad[:3])}")
    month = st.slider("Timeline (pause and step through)", 1, one.T, min(6, one.T), format="%d", key="tl")
    st.caption(f"Showing events up to **{month_label(month)}**")
    types = st.multiselect("Event types", ["shock", "regime", "decision", "state_change", "publication", "constraint"],
                           default=["shock", "regime", "decision", "state_change", "constraint"])
    left, right = st.columns([3, 2])
    with left:
        shown = [e for e in events if e["t"] <= month and e["type"] in types]
        cur = None
        for e in shown[-80:]:
            if e["month"] != cur:
                cur = e["month"]
                st.markdown(f"##### {cur}")
            icon = {"shock": ":material/bolt:", "regime": ":material/swap_horiz:", "decision": ":material/gavel:", "publication": ":material/newspaper:",
                    "constraint": ":material/block:", "state_change": ":material/trending_flat:"}[e["type"]]
            with st.expander(f"{icon} {e['title'][:150]}"):
                st.write(e.get("narrative", ""))
                rec = {k: v for k, v in e.items() if k not in ("narrative",)}
                st.json(_clean(rec), expanded=False)
    with right:
        sel_vars = st.multiselect("Path series", list(LABELS), default=["brent", "inr", "cpi_yoy", "gap"], key="pbvars")
        for v in sel_vars:
            fig = fan(one, v, height=210)
            fig.add_vline(x=month_label(month), line_dash="dot", line_color=C["verm"])
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, **WIDE, key=f"pb_{v}")
        st.markdown("**Causal chain inspector**")
        cand = [e for e in events if e["t"] <= month and e["type"] in ("state_change", "decision", "constraint", "regime")]
        if cand:
            labels = [f"{e['month']} | {e['title'][:80]}" for e in cand]
            k = st.selectbox("Event", range(len(cand)), index=len(cand) - 1, format_func=lambda i: labels[i])
            for lvl, a in ancestors(events, cand[k]["id"]):
                st.markdown(f"{'&nbsp;' * 6 * lvl}{'↳ ' if lvl else ''}**{a['month']}** {a['title'][:110]}  \n{'&nbsp;' * 6 * lvl}"
                            f"<span style='color:#777;font-size:12px'>{', '.join(a.get('mechanism', [])) or a['type']} | support: {a.get('support')}</span>",
                            unsafe_allow_html=True)
    st.divider()
    st.markdown("#### Branch and replay")
    st.caption("Change an actor decision from a month onward. All future shocks are the SAME random draws (matched), so differences come from the decision.")
    b1, b2, b3 = st.columns(3)
    bm = b1.slider("Branch from month", 1, one.T, min(2, one.T), key="bm")
    actor = b2.selectbox("Actor", list(POLICY_OPTIONS), key="ba")
    cur_opt = spec.policies[actor]
    alt_opts = [o for o in POLICY_OPTIONS[actor] if o != cur_opt]
    opt = b3.selectbox("Alternative choice", alt_opts, format_func=lambda o: f"{o}: {POLICY_OPTIONS[actor][o]}", key="bo")
    if st.button("Replay this path with the alternative", type="primary"):
        o, alt = branch(spec, int(pidx), int(bm), {actor: opt})
        st.session_state["branch"] = (o, alt, actor, cur_opt, opt, int(bm), int(pidx))
    if "branch" in st.session_state:
        o, alt, actor_, cur_, opt_, bm_, pid_ = st.session_state["branch"]
        if pid_ != int(pidx):
            st.caption("Branch shown below belongs to another path; rerun the branch for this path.")
        d = divergence_report(o, alt)
        st.markdown(f"**What changed:** {actor_} `{cur_}` -> `{opt_}` from {month_label(bm_)} on path {pid_}. "
                    f"First divergence: **{d['first_divergence']}**. Pre-branch history identical: **{d['pre_branch_history_identical']}**. {d['matched_draws_note']}")
        cs = st.columns(4)
        for c, v in zip(cs, ["retail_fuel", "cpi_yoy", "inr", "gap"]):
            with c:
                f = fan(o, v, height=230, extra={"branch": (o.meta["months"], alt.hist[v][P:, 0], C["verm"])})
                f.update_layout(showlegend=False)
                st.plotly_chart(f, **WIDE, key=f"br_{v}")
        bt = pd.DataFrame({"original": d["burden_original"], "branch": d["burden_branch"]})
        bt["difference"] = bt["branch"] - bt["original"]
        st.markdown("**Who absorbs the cost (this path)**")
        st.dataframe(bt.round(2), **WIDE)
        st.caption("What could interrupt the branch: actor reversal, regime change in oil, or assumptions in the register (Analyst tools). "
                   "Evidence that would support it: watch the signposts linked to this scenario.")


def view_risk(res):
    spec = res.spec
    st.subheader("Risk lab")
    st.info(f"{LABEL_FREQ}. Intervals are Monte Carlo SAMPLING intervals only; they do not include model or parameter-structure uncertainty.")
    if spec.n_paths < 100:
        st.warning("Run at least 100 stochastic paths for risk metrics.")
        return
    df = pd.DataFrame([{**{k: v for k, v in th.__dict__.items()}} for th in DEFAULT_THRESHOLDS])
    st.markdown("**Threshold definitions** (edit, add rows; var must be a model variable; kind: any | endpoint | duration; observe: monthly | quarterly | fy_end)")
    ed = st.data_editor(df, num_rows="dynamic", **WIDE, key="th_ed")
    ths = []
    for _, r in ed.iterrows():
        try:
            if r["var"] in res.hist:
                ths.append(Threshold(**{k: (int(r[k]) if k in ("min_months", "recover_months") else r[k]) for k in df.columns}))
        except Exception as ex:  # noqa: BLE001
            st.warning(f"Skipped row: {ex}")
    rows, evs = [], {}
    for th in ths:
        e = evaluate_threshold(res, th); evs[th.id] = e
        s = e["summary"]
        rows.append({"id": th.id, "event": th.describe(), "frequency": e["frequency"], "CI95": f"{e['ci95'][0]:.3f}-{e['ci95'][1]:.3f}",
                     "breached paths": s["n_breached"], "recovered": s["n_recovered"], "not recovered (censored)": s["n_not_recovered_by_horizon"],
                     "median months to recover": s["median_recovery_months_among_recovered"], "mean months beyond (if breached)": s["mean_months_beyond_given_breach"]})
    st.dataframe(pd.DataFrame(rows), **WIDE, hide_index=True)
    if ths:
        c1, c2 = st.columns(2)
        pick = c1.selectbox("Threshold for timing charts", [t.id for t in ths])
        e = evs[pick]
        with c1:
            st.plotly_chart(hist_fig(e["first_passage"], f"First passage month index ({pick})", "months after Oct 2026"), **WIDE)
        with c2:
            st.plotly_chart(hist_fig(e["max_duration"], f"Longest consecutive breach ({pick})", "months", C["verm"]), **WIDE)
        jsel = st.multiselect("Joint stress: all of these in the SAME month (monthly variables)", [t.id for t in ths if t.observe == "monthly"],
                              default=[t.id for t in ths if t.observe == "monthly"][:2])
        if len(jsel) >= 2:
            j = joint_frequency(res, [t for t in ths if t.id in jsel])
            st.markdown(f"**Joint:** {j['description']}: **{j['frequency']:.3f}** (CI {j['ci95'][0]:.3f}-{j['ci95'][1]:.3f}) - {j['label']}")
    st.markdown("#### Distributions and tail severity")
    m = path_metrics(res)
    c1, c2, c3 = st.columns(3)
    metric = c1.selectbox("Path metric", list(m), index=list(m).index("min_gdp_yoy"))
    alpha = c2.slider("Tail share for expected shortfall", 0.01, 0.25, 0.10, 0.01)
    adverse = "low" if metric.startswith("min") else "high"
    es = expected_shortfall(m[metric], alpha, adverse)
    c3.metric(f"Expected shortfall ({int(alpha * 100)}% worst paths)", f"{es:.2f}", help="Mean of the worst tail of path outcomes; conditional on the model")
    st.plotly_chart(hist_fig(m[metric], f"Distribution of {metric} across paths", metric), **WIDE)
    st.markdown("#### Sampling convergence")
    if ths:
        st.dataframe(pd.DataFrame(convergence(res, ths[0])).astype({"n": str}), hide_index=True, **WIDE)
        st.caption("Estimates should stabilise as n grows and the two halves should agree within ~2 standard errors. A narrow MC error says nothing about whether assumptions are right.")
    st.markdown("#### Sensitivity: which uncertain parameters drive this metric?")
    if spec.param_mode == "sampled":
        sr = pd.DataFrame(sensitivity_rank(res, metric, 12))
        if not sr.empty:
            f = go.Figure(go.Bar(x=sr["spearman"], y=sr["param"], orientation="h", marker_color=[C["verm"] if v > 0 else C["blue"] for v in sr["spearman"]]))
            f.update_layout(height=340, template="plotly_white", margin=dict(l=10, r=10, t=20, b=10), xaxis_title="Spearman rank correlation with " + metric)
            st.plotly_chart(f, **WIDE)
    else:
        st.caption("Switch parameter uncertainty to 'sampled' to see sensitivity rankings.")
    st.markdown("#### Model-structure comparison (same seeds)")
    if st.button("Run alternative structures"):
        rows = []
        for e_ in ("adaptive", "anchored"):
            for f_ in ("managed", "flexible"):
                s2 = copy.deepcopy(spec); s2.structure = {"expectations": e_, "fx_regime": f_}
                r2 = run(s2)
                mm = path_metrics(r2)
                rows.append({"expectations": e_, "fx_regime": f_, "CPI>6% any": evaluate_threshold(r2, DEFAULT_THRESHOLDS[0])["frequency"],
                             "INR>100 any": evaluate_threshold(r2, DEFAULT_THRESHOLDS[2])["frequency"], "median peak CPI": np.nanmedian(mm["peak_cpi"]),
                             "median peak INR": np.nanmedian(mm["peak_inr"]), "median reserve trough": np.nanmedian(mm["min_reserves"])})
        st.dataframe(pd.DataFrame(rows).round(3), hide_index=True, **WIDE)
        st.caption("Differences across structures are model uncertainty. They are typically larger than Monte Carlo sampling error.")
    with st.expander("Judgment-weighted mixture across scenarios (optional)"):
        st.caption("Only with explicit weights you set. Equal weights are NOT neutral evidence.")
        sids = st.multiselect("Scenarios", list_scenarios(), default=["reference", "oil_escalation", "ceasefire"])
        ws = {s_: st.slider(f"weight: {s_}", 0.0, 1.0, round(1 / max(len(sids), 1), 2), 0.05, key=f"w_{s_}") for s_ in sids}
        if sids and st.button("Compute mixture") and sum(ws.values()) > 0:
            rs = {}
            for s_ in sids:
                sc = load_scenario(s_)
                s2 = copy.deepcopy(spec); s2.scenario = sc
                rs[s_] = run(s2)
            mx = mixture(rs, ws, ths[0] if ths else DEFAULT_THRESHOLDS[0])
            st.write(mx)
            st.caption("Sensitivity: vary the weights and watch the aggregate; parts are shown so the weights can be challenged.")


def view_strategy(res):
    spec = res.spec
    st.subheader("Strategy comparison")
    st.caption("Each bundle runs with identical shocks and parameter draws (common random numbers). The table shows trade-offs; no universal 'best' policy is computed.")
    picks = st.multiselect("Policy bundles (first = reference)", list(BUNDLES), default=list(BUNDLES)[:4])
    n = st.select_slider("Paths per bundle", [100, 250, 500, 1000], value=250)
    if st.button("Run comparison", type="primary") and picks:
        base = copy.deepcopy(spec); base.n_paths = n
        if base.shock_mode == "deterministic":
            base.n_paths = 1
        st.session_state["cmp"] = (compare_strategies(base, {k: BUNDLES[k] for k in picks}), spec_hash(base))
    if "cmp" in st.session_state:
        cs, h = st.session_state["cmp"]
        st.caption(f"Comparison context: base run {h}; bundles differ ONLY in: " + "; ".join(f"{k} -> {BUNDLES.get(k) or 'base policies'}" for k in cs["results"]))
        tbl = pd.DataFrame([{k: v for k, v in r.items() if k != "burden"} for r in cs["table"]]).set_index("bundle")
        show = [c for c in tbl.columns if "(median)" in c or "paired" in c]
        st.dataframe(tbl[show].T.round(2), **WIDE)
        for t in compare_takeaways(cs):
            st.markdown(f"- {t}")
        st.markdown("**Who absorbs the cost** (medians across paths)")
        st.dataframe(pd.DataFrame({r["bundle"]: r["burden"] for r in cs["table"]}).round(2), **WIDE)
        f = go.Figure()
        for (name, mtr), col in zip(cs["metrics"].items(), [C["blue"], C["orange"], C["green"], C["verm"], C["purple"], C["sky"], C["black"], C["grey"]] * 2):
            x, y = mtr["peak_cpi"], mtr["min_gdp_yoy"]
            f.add_trace(go.Scatter(x=[np.nanmedian(x)], y=[np.nanmedian(y)], mode="markers+text", text=[name], textposition="top center",
                                   marker=dict(size=12, color=col), name=name,
                                   error_x=dict(type="data", symmetric=False, array=[np.nanpercentile(x, 90) - np.nanmedian(x)], arrayminus=[np.nanmedian(x) - np.nanpercentile(x, 10)]),
                                   error_y=dict(type="data", symmetric=False, array=[np.nanpercentile(y, 90) - np.nanmedian(y)], arrayminus=[np.nanmedian(y) - np.nanpercentile(y, 10)])))
        f.update_layout(height=430, template="plotly_white", xaxis_title="Peak headline CPI (% y/y) - lower is better",
                        yaxis_title="Weakest quarterly GDP growth (% y/y) - higher is better", showlegend=False, title="Trade-off: inflation vs growth (median, P10-P90 bars)")
        st.plotly_chart(f, **WIDE)
        st.caption(f"Scope: {scope_line(spec)}")


def view_tools(res):
    spec = res.spec
    st.subheader("Analyst tools")
    t1, t2, t3, t4, t5, t6 = st.tabs(["Key assumptions", "Competing hypotheses", "Signposts", "Premortem / red team", "Reverse stress test", "After-action review"])
    with t1:
        ka = yaml.safe_load((CONFIG / "analysis" / "assumptions.yaml").read_text())["items"]
        st.data_editor(pd.DataFrame(ka), num_rows="dynamic", **WIDE, key="ka_ed")
        st.caption("test_param links an assumption to the sensitivity ranking in the Risk lab. Edits live in this session; export via the Evidence tab report.")
    with t2:
        ach = yaml.safe_load((CONFIG / "analysis" / "ach.yaml").read_text())
        st.markdown(f"**Question:** {ach['question']}")
        hs = ach["hypotheses"]
        st.write({k: f"{v['name']} (scenario: {v['scenario']})" for k, v in hs.items()})
        df = pd.DataFrame(ach["evidence"])
        ed = st.data_editor(df, num_rows="dynamic", **WIDE, key="ach_ed")
        score = {"CC": 2, "C": 1, "N": 0, "I": -1, "II": -2}
        inc = {h: int(sum(1 for v in ed[h] if v in ("I", "II")) + sum(1 for v in ed[h] if v == "II")) for h in hs}
        diag = ed[list(hs)].apply(lambda r: float(np.std([score.get(x, 0) for x in r])), axis=1)
        st.markdown("**Inconsistency count** (weighted; II counts double). Lower = harder to reject. NOT a probability.")
        st.write(inc)
        st.markdown("**Diagnostic value of each evidence item** (spread of scores across hypotheses; 0 = does not discriminate)")
        st.dataframe(pd.DataFrame({"evidence": ed["item"], "diagnosticity": diag.round(2)}), hide_index=True, **WIDE)
        st.caption("Focus on disconfirming evidence. Related items (e.g. the same attack reported twice) should not be double counted.")
    with t3:
        sg = yaml.safe_load((CONFIG / "analysis" / "signposts.yaml").read_text())
        st.warning(f"Dated snapshot entered manually on {sg['snapshot_date']} - NOT live status. Edit 'snapshot' to update.")
        df = pd.DataFrame(sg["items"])
        ed = st.data_editor(df, **WIDE, key="sig_ed")

        def status(r):
            try:
                if r["snapshot"] is None or r["level"] is None or pd.isna(r["snapshot"]) or pd.isna(r["level"]):
                    return "manual check"
                hit = float(r["snapshot"]) > float(r["level"]) if r["op"] == ">" else float(r["snapshot"]) < float(r["level"])
                return "TRIGGERED (snapshot)" if hit else "not triggered (snapshot)"
            except Exception:  # noqa: BLE001
                return "manual check"
        st.dataframe(pd.DataFrame({"indicator": ed["indicator"], "status": ed.apply(status, axis=1), "scenarios": ed["scenarios"]}), hide_index=True, **WIDE)
    with t4:
        pm = yaml.safe_load((CONFIG / "analysis" / "premortem.yaml").read_text())
        for k in ("prompts", "model_weaknesses", "strongest_countercase", "missing_actors"):
            st.markdown(f"**{k.replace('_', ' ').capitalize()}**")
            for x in pm[k]:
                st.markdown(f"- {x}")
        st.text_area("Your premortem notes (session only; include in exported report)", key="pm_notes", height=120)
    with t5:
        st.caption("Search shock combinations for which ALL conditions occur. Output = discovered failure pathways, NOT their likelihood.")
        c1, c2, c3 = st.columns(3)
        v1 = c1.selectbox("Condition 1 variable", ["inr", "cpi_yoy", "reserves", "g10", "fd_proj", "gap"], index=0)
        o1 = c1.selectbox("op1", [">", "<"], index=0); l1 = c1.number_input("level 1", value=105.0)
        v2 = c2.selectbox("Condition 2 variable", ["cpi_yoy", "inr", "reserves", "g10", "fd_proj", "gap"], index=0)
        o2 = c2.selectbox("op2", [">", "<"], index=0); l2 = c2.number_input("level 2", value=7.0)
        with_pol = c3.checkbox("Also search fuel-pricing responses", value=True)
        nrs = c3.select_slider("Mode", [1, 50, 100], value=1, help="1 = deterministic central path; >1 = path frequency >= 0.5")
        if st.button("Search failure pathways"):
            pg = {"gov_fuel": ["freeze_omc_absorb", "full_passthrough", "freeze_budget_comp"]} if with_pol else None
            rs = reverse_stress(spec, [Threshold("c1", v1, o1, l1, "any"), Threshold("c2", v2, o2, l2, "any")], n_paths=nrs, policy_grid=pg)
            st.markdown(f"Tested {rs['tested']} combinations ({rs['mode']}). Conditions: {rs['conditions']}. **{rs['label']}**")
            st.dataframe(pd.DataFrame(rs["pathways"]).head(40), **WIDE, hide_index=True)
    with t6:
        st.caption("State what a policy was meant to achieve; compare with simulated outcomes for the CURRENT run.")
        c1, c2 = st.columns(2)
        cpi_goal = c1.number_input("Intent: peak CPI below", value=6.0)
        gdp_goal = c2.number_input("Intent: weakest GDP quarter above", value=6.0)
        aa = after_action(res, {"peak_cpi": ("<", cpi_goal), "min_gdp_yoy": (">", gdp_goal)})
        st.dataframe(pd.DataFrame(aa["intent_vs_outcome"]).round(3), hide_index=True, **WIDE)
        st.markdown("**Trade-offs (median across paths)**")
        st.dataframe(pd.Series(aa["trade_offs"]).round(2).rename("value"), **WIDE)
        st.markdown("**Follow-up questions**")
        for q in aa["follow_up"]:
            st.markdown(f"- {q}")


def view_evidence(res):
    spec = res.spec
    st.subheader("Evidence & methodology")
    st.error("Validation status: NO validated forecasting skill. Implementation and accounting checks pass; parameters are judgmental or illustrative; "
             "no out-of-sample evaluation has been performed. Use for structured exploration, not prediction.")
    t1, t2, t3, t4, t5, t6 = st.tabs(["Parameters", "Evidence register", "Mechanisms & gaps", "Checks (this run)", "Tests & limits", "Exports"])
    with t1:
        pc = load_params()["params"]
        st.dataframe(pd.DataFrame([{"name": k, **{f: v.get(f) for f in ("value", "low", "high", "dist", "status", "unit", "desc", "evidence")}} for k, v in pc.items()]),
                     **WIDE, hide_index=True)
    with t2:
        ev = pd.read_csv(DATA / "EVIDENCE.csv")
        st.dataframe(ev, **WIDE, hide_index=True, column_config={"url": st.column_config.LinkColumn()})
        b = load_baseline()
        st.markdown("**Starting state (t0 snapshot)**")
        st.dataframe(pd.DataFrame([{"var": k, **v} for k, v in b["values"].items()]), **WIDE, hide_index=True)
    with t3:
        mech = load_mechanisms()["links"]
        st.dataframe(pd.DataFrame([{"id": m["id"], "implemented": m["implemented"], "from": ", ".join(m["src"]), "to": m["dst"], "kind": m["kind"], "lag": m["lag"],
                                    "description": m["desc"], "counterforces": m.get("counter"), "invalidation": m.get("invalid")} for m in mech]),
                     **WIDE, hide_index=True)
    with t4:
        ch = accounting_checks(res)
        st.dataframe(pd.DataFrame(ch), **WIDE, hide_index=True)
        st.markdown("**Correlation matrices (driver innovations)**")
        st.write(CORR_REPORTS)
    with t5:
        for fn in ("TEST_RESULTS.md", "MODEL_SPEC.md"):
            p_ = ROOT / "docs" / fn
            if p_.exists():
                with st.expander(fn):
                    st.markdown(p_.read_text())
    with t6:
        rid = spec_hash(spec)
        st.download_button("Configuration (JSON)", save_config(spec), file_name=f"config_{rid}.json")
        if spec.n_paths >= 1:
            st.download_button("Results summary (JSON)", json.dumps(results_summary(res, DEFAULT_THRESHOLDS), indent=1), file_name=f"results_{rid}.json")
            st.download_button("Percentile bands (CSV)", bands_csv(res), file_name=f"bands_{rid}.csv")
        extra = [st.session_state.get("pm_notes", "")] if st.session_state.get("pm_notes") else None
        st.download_button("Assumptions & evidence report (Markdown)", assumptions_report(spec, extra), file_name=f"assumptions_{rid}.md")
        reps = representative_paths(res) if spec.n_paths >= 20 else {"single path": {"path_index": spec.path_offset}}
        name = st.selectbox("Trace to export", list(reps))
        one_spec = copy.deepcopy(spec); one_spec.n_paths, one_spec.path_offset = 1, int(reps[name]["path_index"])
        one = run(one_spec)
        evs = build_trace(one, 0, rid)
        st.download_button("Selected trace (Markdown)", trace_markdown(evs, one, 0, f"{name} path", rid), file_name=f"trace_{rid}_p{one_spec.path_offset}.md")
        st.download_button("Selected trace (JSON)", json.dumps(_clean(evs), indent=1), file_name=f"trace_{rid}_p{one_spec.path_offset}.json")


# ------------------------------------------------------------------ main
def main():
    st.title("India Economic Scenario & Strategic Risk Simulator")
    st.caption(f"Engine {ENGINE_VERSION} | illustrative, transparent, unvalidated | INR for domestic values, USD for external; months in Asia/Kolkata calendar; fiscal years Apr-Mar")
    spec = sidebar()
    if "result_spec" not in st.session_state:
        st.session_state["result_spec"] = spec   # demo opens immediately with default settings
    rspec = st.session_state["result_spec"]
    with st.spinner("Simulating..."):
        res = run(rspec)
    diff = spec_diff(spec, rspec)
    if diff:
        st.warning("**Results are STALE** - the sidebar differs from the settings that produced them: " + "; ".join(diff) + ". Press **Run simulation**.")
    st.caption(f"Showing results for: {scope_line(rspec)}")
    tabs = st.tabs(["Overview", "Causal map", "Scenario playback", "Risk lab", "Strategy comparison", "Analyst tools", "Evidence & methodology"])
    with tabs[0]:
        view_overview(res)
    with tabs[1]:
        view_causal_map()
    with tabs[2]:
        view_playback(res)
    with tabs[3]:
        view_risk(res)
    with tabs[4]:
        view_strategy(res)
    with tabs[5]:
        view_tools(res)
    with tabs[6]:
        view_evidence(res)


main()
