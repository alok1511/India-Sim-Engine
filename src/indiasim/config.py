"""Loading, validating and hashing configuration (params, baseline, scenarios, mechanisms)."""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

import yaml

from . import ENGINE_VERSION

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
DATA = ROOT / "data"

POLICY_OPTIONS = {
    "gov_fuel": {
        "full_passthrough": "Full pass-through: retail moves so OMC margin returns to normal",
        "freeze_omc_absorb": "Freeze retail; OMCs absorb losses (status quo Oct 2026)",
        "freeze_budget_comp": "Freeze retail; Budget compensates OMC losses",
        "partial_50": "Pass through 50% of the gap; Budget compensates half the remaining loss",
        "excise_cut": "Cut excise to offset losses, then freeze (headroom ~Rs1/l after Mar-2026 cut)",
        "adaptive_threshold": "Freeze until cumulative OMC loss exceeds tolerance, then 50% pass-through",
    },
    "gov_fiscal": {
        "accommodate": "Let the deficit absorb oil costs",
        "hold_target": "Hold deficit target by cutting capex (half of projected overrun)",
    },
    "rbi_mpc": {
        "inflation_targeting": "Flexible inflation targeting on published headline/expectations/growth",
        "fx_defence": "Inflation targeting plus extra hikes when 3m depreciation exceeds a trigger",
        "look_through": "Look through first-round supply shocks; react to core and expectations",
        "hold": "No change (benchmark)",
    },
    "rbi_fx": {
        "heavy": "Absorb ~75% of FX pressure",
        "moderate": "Absorb ~50% of FX pressure",
        "light": "Absorb ~25% of FX pressure",
    },
    "rbi_steril": {
        "none": "No sterilisation",
        "half": "Offset half the liquidity drain",
        "full": "Offset all of the liquidity drain",
    },
}
STRUCTURE_OPTIONS = {
    "expectations": {"adaptive": "Adaptive with de-anchoring regime", "anchored": "Anchored (slow, no regime switch)"},
    "fx_regime": {"managed": "Managed float (policy intensity as chosen)", "flexible": "Flexible (intervention capped at 15%)"},
}
SHOCK_TYPES = {"oil_escalation", "oil_deescalation", "global_tightening", "food_supply"}


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_params() -> dict:
    return load_yaml(CONFIG / "params.yaml")


def load_baseline() -> dict:
    return load_yaml(DATA / "baseline_2026-10.yaml")


def load_mechanisms() -> dict:
    return load_yaml(CONFIG / "mechanisms.yaml")


def list_scenarios() -> list[str]:
    return sorted(p.stem for p in (CONFIG / "scenarios").glob("*.yaml"))


def load_scenario(sid: str) -> dict:
    return load_yaml(CONFIG / "scenarios" / f"{sid}.yaml")


@dataclass
class RunSpec:
    """Everything that determines a run. Two equal specs (same versions) reproduce identical results."""
    scenario: dict
    policies: dict
    structure: dict
    horizon: int = 24
    n_paths: int = 1
    seed: int = 20261025
    param_mode: str = "sampled"        # 'central' | 'sampled'  (outer-loop parameter uncertainty)
    shock_mode: str = "stochastic"     # 'stochastic' | 'deterministic' (within-path shocks)
    path_offset: int = 0               # path index of first path (for regenerating a single path)
    overrides: dict = field(default_factory=dict)  # {month:int -> {actor: option}} human/branch overrides
    param_overrides: dict = field(default_factory=dict)  # {name: value} fixed for all paths

    def validate(self) -> list[str]:
        errs = []
        if self.horizon not in range(6, 37):
            errs.append("horizon must be 6..36 months")
        for actor, opt in self.policies.items():
            if actor not in POLICY_OPTIONS or opt not in POLICY_OPTIONS[actor]:
                errs.append(f"unknown policy {actor}={opt}")
        for k in POLICY_OPTIONS:
            if k not in self.policies:
                errs.append(f"missing policy {k}")
        for k, v in self.structure.items():
            if k not in STRUCTURE_OPTIONS or v not in STRUCTURE_OPTIONS[k]:
                errs.append(f"unknown structure {k}={v}")
        for s in self.scenario.get("shocks", []):
            if s.get("type") not in SHOCK_TYPES:
                errs.append(f"unknown shock type {s.get('type')}")
            if not 1 <= int(s.get("start", 1)) <= self.horizon:
                errs.append(f"shock start {s.get('start')} outside horizon")
        for m, acts in self.overrides.items():
            for actor, opt in acts.items():
                if actor not in POLICY_OPTIONS or opt not in POLICY_OPTIONS[actor]:
                    errs.append(f"bad override month {m}: {actor}={opt}")
        if self.param_mode not in ("central", "sampled"):
            errs.append("param_mode must be central|sampled")
        if self.shock_mode not in ("stochastic", "deterministic"):
            errs.append("shock_mode must be stochastic|deterministic")
        if not 1 <= self.n_paths <= 20000:
            errs.append("n_paths must be 1..20000")
        return errs

    def to_dict(self) -> dict:
        d = asdict(self)
        d["overrides"] = {str(k): v for k, v in self.overrides.items()}
        return d

    @staticmethod
    def from_dict(d: dict) -> "RunSpec":
        d = copy.deepcopy(d)
        d["overrides"] = {int(k): v for k, v in d.get("overrides", {}).items()}
        return RunSpec(**d)


def spec_from_scenario(sid: str, **kw) -> RunSpec:
    sc = load_scenario(sid)
    pol = dict(sc["policies"])
    pol.update(kw.pop("policies", {}) or {})
    st = dict(sc["structure"])
    st.update(kw.pop("structure", {}) or {})
    return RunSpec(scenario=sc, policies=pol, structure=st, **kw)


def version_block() -> dict:
    p, m, b = load_params(), load_mechanisms(), load_baseline()
    return {"engine": ENGINE_VERSION, "params": p["version"], "mechanisms": m["version"], "baseline": b["snapshot_id"],
            "params_hash": stable_hash(p), "baseline_hash": stable_hash(b)}


def stable_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]


def spec_hash(spec: RunSpec) -> str:
    d = spec.to_dict()
    d["_versions"] = version_block()
    return stable_hash(d)
