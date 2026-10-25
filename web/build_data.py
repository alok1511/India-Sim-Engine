"""Export the model's configuration to JSON for the browser engine (single source of truth = config/ and data/)."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import yaml  # noqa: E402
from indiasim import ENGINE_VERSION  # noqa: E402
from indiasim.config import load_params, load_baseline, load_mechanisms, list_scenarios, load_scenario, POLICY_OPTIONS, version_block  # noqa: E402
from indiasim.randomness import CHOL  # noqa: E402


def build():
    an = ROOT / "config" / "analysis"
    data = {
        "engine_version": ENGINE_VERSION,
        "versions": version_block(),
        "params": load_params(),
        "baseline": load_baseline(),
        "scenarios": {s: load_scenario(s) for s in list_scenarios()},
        "mechanisms": load_mechanisms(),
        "policy_options": POLICY_OPTIONS,
        "chol": {k: v.tolist() for k, v in CHOL.items()},
        "evidence": list(csv.DictReader(open(ROOT / "data" / "EVIDENCE.csv", encoding="utf-8"))),
        "assumptions": yaml.safe_load(open(an / "assumptions.yaml")),
        "ach": yaml.safe_load(open(an / "ach.yaml")),
        "signposts": yaml.safe_load(open(an / "signposts.yaml")),
        "premortem": yaml.safe_load(open(an / "premortem.yaml")),
    }
    out = ROOT / "web" / "data.json"
    out.write_text(json.dumps(data, default=str), encoding="utf-8")
    return out


if __name__ == "__main__":
    p = build()
    print(p, p.stat().st_size, "bytes")
