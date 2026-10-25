"""Save/load configurations; export results, traces and an assumptions/evidence report with run identity."""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone, timedelta

import numpy as np

from .config import RunSpec, spec_hash, version_block, load_params, load_mechanisms, POLICY_OPTIONS, DATA
from .model import P, month_label
from .risk import bands, evaluate_threshold, path_metrics, representative_paths, LABEL_FREQ

IST = timezone(timedelta(hours=5, minutes=30))
EXPORT_VARS = ["brent", "inr", "reserves", "ca", "pressure", "repo", "wacr", "g10", "cpi_yoy", "food_yoy", "core_yoy", "exp_infl",
               "gap", "gdp_yoy", "retail_fuel", "omc_margin", "cum_omc_loss", "fd_proj", "credit_yoy", "stress", "liq"]


def run_identity(spec: RunSpec) -> dict:
    return {"run_id": spec_hash(spec), "created_ist": datetime.now(IST).isoformat(timespec="seconds"), "versions": version_block(),
            "seed": spec.seed, "n_paths": spec.n_paths, "param_mode": spec.param_mode, "shock_mode": spec.shock_mode,
            "scenario": spec.scenario.get("id"), "policies": spec.policies, "structure": spec.structure, "overrides": spec.to_dict()["overrides"]}


def save_config(spec: RunSpec) -> str:
    return json.dumps({"identity": run_identity(spec), "spec": spec.to_dict()}, indent=2, default=str)


def load_config(text: str) -> tuple[RunSpec, list[str]]:
    d = json.loads(text)
    spec = RunSpec.from_dict(d["spec"])
    warnings = []
    saved = d.get("identity", {}).get("versions", {})
    now = version_block()
    for k in ("engine", "params", "mechanisms", "baseline", "params_hash", "baseline_hash"):
        if saved.get(k) != now.get(k):
            warnings.append(f"version mismatch {k}: saved {saved.get(k)} vs current {now.get(k)} - results may not reproduce exactly")
    return spec, warnings


def _clean(x):
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.ndarray):
        return [_clean(v) for v in x.tolist()]
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    return x


def results_summary(res, thresholds) -> dict:
    out = {"identity": run_identity(res.spec), "months": res.meta["months"], "interpretation": LABEL_FREQ, "bands": {}, "thresholds": []}
    for v in EXPORT_VARS:
        out["bands"][v] = {str(q): _clean(a) for q, a in bands(res, v).items()}
    for th in thresholds:
        e = evaluate_threshold(res, th)
        out["thresholds"].append(_clean({k: e[k] for k in ("description", "frequency", "ci95", "label", "summary", "n_paths")}))
    m = path_metrics(res)
    with np.errstate(all="ignore"):
        out["path_metric_quantiles"] = {k: _clean(np.nanpercentile(v, [5, 25, 50, 75, 95])) if np.isfinite(v).any() else None for k, v in m.items()}
    out["representative_paths"] = _clean(representative_paths(res)) if res.spec.n_paths >= 20 else {}
    return out


def bands_csv(res) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["run_id", spec_hash(res.spec), "label", LABEL_FREQ])
    w.writerow(["variable", "month", "p5", "p25", "p50", "p75", "p95"])
    for v in EXPORT_VARS:
        b = bands(res, v)
        for t in range(res.T + 1):
            w.writerow([v, month_label(t)] + [None if not np.isfinite(b[q][t]) else round(float(b[q][t]), 4) for q in (5, 25, 50, 75, 95)])
    return buf.getvalue()


def trace_markdown(events, res, j=0, title="Scenario trace", parent_run_id=None) -> str:
    idn = run_identity(res.spec)
    lines = [f"# {title}", "", f"Run `{parent_run_id or idn['run_id']}` (single-path regeneration `{idn['run_id']}`) | path {res.path_indices[j]} | scenario `{idn['scenario']}` | seed {idn['seed']} | "
             f"engine {idn['versions']['engine']} | params {idn['versions']['params']}", "",
             "> EXPLORATORY SCENARIO PATH generated from the run log. No probability is attached to this single path.", ""]
    cur = None
    for e in events:
        if e["month"] != cur:
            cur = e["month"]
            lines += ["", f"## {cur}", ""]
        lines.append(f"- **[{e['type']}]** {e.get('narrative') or e['title']}")
        if e["type"] == "decision":
            lines.append(f"  - Observed: {e.get('observed')} | Choices: {e.get('choices')} | Chosen: {e.get('chosen')} | Constraints: {e.get('constraints')}")
            lines.append(f"  - Expected response: {e.get('expected')}")
        if e.get("root_note"):
            lines.append(f"  - {e['root_note']}")
        lines.append(f"  - id `{e['id']}`; parents {len(e.get('parents', []))}; support: {e.get('support')}")
    return "\n".join(lines)


def assumptions_report(spec: RunSpec, extra_assumptions=None) -> str:
    idn = run_identity(spec)
    p = load_params()["params"]
    mech = load_mechanisms()["links"]
    L = ["# Assumptions and evidence report", "", f"Run identity: `{idn['run_id']}` | created {idn['created_ist']} IST", "",
         f"Versions: {idn['versions']}", "", f"Scenario: **{spec.scenario.get('name')}**", "", spec.scenario.get("description", "").strip(), "",
         "## Actor choices", ""]
    for a, o in spec.policies.items():
        L.append(f"- {a}: `{o}` - {POLICY_OPTIONS[a][o]}")
    L += ["", f"Structure: {spec.structure}", "", f"Overrides (branch/human): {idn['overrides'] or 'none'}", "",
          "## Interpretation", "", "- Percentages are CONDITIONAL MODEL FREQUENCIES under these assumptions, not validated forecast probabilities.",
          "- No parameter is estimated by this project. Status column shows the basis of each.", "",
          "## Parameters", "", "| name | value | range | status | unit | description |", "|---|---|---|---|---|---|"]
    for k in sorted(p):
        v = p[k]
        rng = f"{v.get('low', '')}-{v.get('high', '')}" if v.get("dist", "fixed") != "fixed" else "fixed"
        L.append(f"| {k} | {v['value']} | {rng} | {v['status']} | {v.get('unit', '')} | {v.get('desc', '')} |")
    L += ["", "## Mechanisms (implemented)", "", "| id | from -> to | kind | lag | description |", "|---|---|---|---|---|"]
    for m in mech:
        if m["implemented"]:
            L.append(f"| {m['id']} | {', '.join(m['src'])} -> {m['dst']} | {m['kind']} | {m['lag']} | {m['desc']} |")
    L += ["", "## Not implemented (visible gaps)", ""]
    for m in mech:
        if not m["implemented"]:
            L.append(f"- {m['id']}: {m['desc']}")
    L += ["", "## Evidence register", "", (DATA / "EVIDENCE.csv").read_text(encoding="utf-8").replace("\n", "  \n")[:20000]]
    if extra_assumptions:
        L += ["", "## Key assumptions register (analyst-edited)", ""] + [f"- {a}" for a in extra_assumptions]
    return "\n".join(L)
