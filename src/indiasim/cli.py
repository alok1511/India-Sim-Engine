"""Command-line interface. Also the stable interface a future agent team drives (JSON in, JSON/Markdown out).

  indiasim scenarios
  indiasim run --scenario oil_escalation --paths 1000 --policy gov_fuel=full_passthrough --out runs/x
  indiasim trace --scenario oil_escalation --path 7 [--branch 3:gov_fuel=partial_50] --out runs/x
  indiasim compare --scenario oil_escalation --bundle "status quo:" --bundle "pass-through:gov_fuel=full_passthrough"
  indiasim stress --scenario reference --cond "inr>105" --cond "cpi_yoy>6.5"
  indiasim situation --file situation.json --out runs/brief
  indiasim check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from .config import RunSpec, spec_from_scenario, list_scenarios, load_scenario, POLICY_OPTIONS, SHOCK_TYPES, STRUCTURE_OPTIONS, spec_hash
from .model import simulate
from .risk import DEFAULT_THRESHOLDS, Threshold, evaluate_threshold, representative_paths
from .analysis import branch, divergence_report, compare_strategies, reverse_stress
from .trace import build_trace, reconcile
from .checks import accounting_checks
from .export import results_summary, bands_csv, trace_markdown, assumptions_report, save_config, _clean


def _kv(items):
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _cond(s: str) -> Threshold:
    for op in (">", "<"):
        if op in s:
            v, lvl = s.split(op)
            return Threshold(f"C-{v}", v.strip(), op, float(lvl), "any", label=s)
    raise ValueError(f"bad condition {s}")


def _write(out: Path, name: str, text: str):
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_text(text, encoding="utf-8")
    return str(out / name)


def cmd_run(a):
    spec = spec_from_scenario(a.scenario, n_paths=a.paths, seed=a.seed, horizon=a.horizon, policies=_kv(a.policy), structure=_kv(a.structure))
    res = simulate(spec)
    summ = results_summary(res, DEFAULT_THRESHOLDS)
    files = []
    if a.out:
        out = Path(a.out)
        files.append(_write(out, "run_summary.json", json.dumps(summ, indent=1)))
        files.append(_write(out, "bands.csv", bands_csv(res)))
        files.append(_write(out, "config.json", save_config(spec)))
        files.append(_write(out, "assumptions_report.md", assumptions_report(spec)))
        if a.paths >= 20:
            for name, rp in representative_paths(res).items():
                one = simulate(RunSpec(**{**spec.__dict__, "n_paths": 1, "path_offset": rp["path_index"]}))
                ev = build_trace(one, 0, summ["identity"]["run_id"])
                tag = name.split(" ")[0]
                files.append(_write(out, f"trace_{tag}_p{rp['path_index']}.md", trace_markdown(ev, one, 0, f"{name} path", summ["identity"]["run_id"])))
                files.append(_write(out, f"trace_{tag}_p{rp['path_index']}.json", json.dumps(_clean(ev), indent=1)))
    print(json.dumps({"run_id": summ["identity"]["run_id"], "thresholds": [{"desc": t["description"], "freq": t["frequency"], "ci95": t["ci95"]}
                                                                           for t in summ["thresholds"]], "label": summ["interpretation"], "files": files}, indent=1))


def cmd_trace(a):
    spec = spec_from_scenario(a.scenario, n_paths=1, seed=a.seed, path_offset=a.path, policies=_kv(a.policy))
    res = simulate(spec)
    ev = build_trace(res, 0, spec_hash(spec))
    out = {"events": len(ev), "reconcile_mismatches": reconcile(ev, res, 0)}
    if a.branch:
        m, rest = a.branch.split(":", 1)
        o, alt = branch(spec, a.path, int(m), _kv(rest.split(",")))
        out["branch"] = _clean(divergence_report(o, alt))
    if a.out:
        _write(Path(a.out), f"trace_p{a.path}.md", trace_markdown(ev, res, 0))
        _write(Path(a.out), f"trace_p{a.path}.json", json.dumps(_clean(ev), indent=1))
    else:
        print(trace_markdown(ev, res, 0)[:4000])
    print(json.dumps(out, indent=1, default=str)[:6000])


def cmd_compare(a):
    spec = spec_from_scenario(a.scenario, n_paths=a.paths, seed=a.seed)
    bundles = {}
    for b in a.bundle:
        name, rest = b.split(":", 1)
        bundles[name] = _kv([x for x in rest.split(",") if x])
    cs = compare_strategies(spec, bundles)
    print(json.dumps(_clean({"note": cs["note"], "table": cs["table"]}), indent=1))


def cmd_stress(a):
    spec = spec_from_scenario(a.scenario, policies=_kv(a.policy))
    rs = reverse_stress(spec, [_cond(c) for c in a.cond], n_paths=a.paths)
    print(json.dumps(_clean({k: v for k, v in rs.items()}), indent=1)[:8000])


def validate_situation(d: dict) -> list[str]:
    errs = []
    for k in ("title", "as_of", "shocks"):
        if k not in d:
            errs.append(f"missing {k}")
    for s in d.get("shocks", []):
        if s.get("type") not in SHOCK_TYPES:
            errs.append(f"unknown shock type {s.get('type')}; allowed {sorted(SHOCK_TYPES)}")
    for actor, opt in (d.get("policies") or {}).items():
        if actor not in POLICY_OPTIONS or opt not in POLICY_OPTIONS[actor]:
            errs.append(f"bad policy {actor}={opt}")
    for k, v in (d.get("structure") or {}).items():
        if k not in STRUCTURE_OPTIONS or v not in STRUCTURE_OPTIONS[k]:
            errs.append(f"bad structure {k}={v}")
    return errs


def run_situation(d: dict, out: Path | None = None) -> dict:
    """Agent hook: a structured situation brief -> scenario run(s) -> machine-readable brief. The LLM never sets numbers
    for macro outcomes; it only selects shocks/policies/thresholds that the engine then computes."""
    errs = validate_situation(d)
    if errs:
        raise ValueError("; ".join(errs))
    base = load_scenario("reference")
    sc = {**base, "id": "situation", "name": d["title"], "description": d.get("narrative", ""), "shocks": d["shocks"]}
    spec = RunSpec(scenario=sc, policies={**base["policies"], **(d.get("policies") or {})}, structure={**base["structure"], **(d.get("structure") or {})},
                   horizon=int(d.get("horizon", 24)), n_paths=int(d.get("n_paths", 1000)), seed=int(d.get("seed", 20261025)))
    ths = [Threshold(**t) for t in d.get("thresholds", [])] or DEFAULT_THRESHOLDS
    res = simulate(spec)
    summ = results_summary(res, ths)
    alt = {}
    for name, pol in (d.get("compare_policies") or {}).items():
        alt[name] = pol
    comp = compare_strategies(spec, {"as specified": {}, **alt})["table"] if alt else []
    brief = {"situation": d, "summary": summ, "comparison": _clean(comp), "checks": accounting_checks(res)}
    if out:
        _write(out, "situation_result.json", json.dumps(_clean(brief), indent=1))
        _write(out, "assumptions_report.md", assumptions_report(spec))
    return brief


def cmd_situation(a):
    d = json.loads(Path(a.file).read_text())
    brief = run_situation(d, Path(a.out) if a.out else None)
    print(json.dumps({"run_id": brief["summary"]["identity"]["run_id"],
                      "thresholds": [(t["description"], round(t["frequency"], 3)) for t in brief["summary"]["thresholds"]],
                      "label": brief["summary"]["interpretation"]}, indent=1))


def cmd_check(a):
    ok = True
    for sid in list_scenarios():
        res = simulate(spec_from_scenario(sid, n_paths=200))
        bad = [c["check"] for c in accounting_checks(res) if not c["pass"]]
        r2 = simulate(spec_from_scenario(sid, n_paths=200))
        rep = all(np.array_equal(res.hist[v], r2.hist[v], equal_nan=True) for v in res.hist)
        print(f"{sid:20s} accounting: {'PASS' if not bad else 'FAIL ' + str(bad)} | reproducible: {rep}")
        ok &= (not bad) and rep
    sys.exit(0 if ok else 1)


def main(argv=None):
    p = argparse.ArgumentParser(prog="indiasim", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scenarios").set_defaults(fn=lambda a: print("\n".join(list_scenarios())))
    r = sub.add_parser("run"); r.add_argument("--scenario", default="oil_escalation"); r.add_argument("--paths", type=int, default=1000)
    r.add_argument("--seed", type=int, default=20261025); r.add_argument("--horizon", type=int, default=24)
    r.add_argument("--policy", action="append"); r.add_argument("--structure", action="append"); r.add_argument("--out"); r.set_defaults(fn=cmd_run)
    t = sub.add_parser("trace"); t.add_argument("--scenario", default="oil_escalation"); t.add_argument("--path", type=int, default=0)
    t.add_argument("--seed", type=int, default=20261025); t.add_argument("--policy", action="append"); t.add_argument("--branch"); t.add_argument("--out"); t.set_defaults(fn=cmd_trace)
    c = sub.add_parser("compare"); c.add_argument("--scenario", default="oil_escalation"); c.add_argument("--paths", type=int, default=500)
    c.add_argument("--seed", type=int, default=20261025); c.add_argument("--bundle", action="append", required=True); c.set_defaults(fn=cmd_compare)
    s = sub.add_parser("stress"); s.add_argument("--scenario", default="reference"); s.add_argument("--cond", action="append", required=True)
    s.add_argument("--paths", type=int, default=1); s.add_argument("--policy", action="append"); s.set_defaults(fn=cmd_stress)
    si = sub.add_parser("situation"); si.add_argument("--file", required=True); si.add_argument("--out"); si.set_defaults(fn=cmd_situation)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
