"""AT-02 same seed/config/version reproduces paths and trace identities; AT-14 save/load retains reproducibility."""
import copy

import numpy as np

from conftest import mc
from indiasim.config import spec_from_scenario
from indiasim.model import simulate
from indiasim.trace import build_trace
from indiasim.export import save_config, load_config


def test_same_seed_identical():
    a, b = mc("oil_escalation", 200), mc("oil_escalation", 200)
    for v in a.hist:
        assert np.array_equal(a.hist[v], b.hist[v], equal_nan=True), v


def test_different_seed_differs():
    a = mc("oil_escalation", 50)
    b = simulate(spec_from_scenario("oil_escalation", n_paths=50, seed=7))
    assert not np.allclose(a.hist["brent"], b.hist["brent"])


def test_path_regenerates_identically_alone_or_in_batch():
    batch = mc("oil_escalation", 120)
    one = simulate(spec_from_scenario("oil_escalation", n_paths=1, path_offset=77))
    for v in ("brent", "inr", "cpi_yoy", "gap", "repo", "reserves"):
        assert np.array_equal(batch.hist[v][:, 77], one.hist[v][:, 0], equal_nan=True), v


def test_trace_ids_reproduce():
    s = spec_from_scenario("oil_escalation", n_paths=1, path_offset=5)
    e1 = build_trace(simulate(s), 0, "r"); e2 = build_trace(simulate(s), 0, "r")
    assert [e["id"] for e in e1] == [e["id"] for e in e2]
    assert len({e["id"] for e in e1}) == len(e1)


def test_save_load_roundtrip_reproduces():
    s = spec_from_scenario("combined_stress", n_paths=60, seed=11, policies={"gov_fuel": "partial_50"})
    s.overrides = {4: {"rbi_fx": "light"}}
    text = save_config(s)
    s2, warns = load_config(text)
    assert not warns
    a, b = simulate(s), simulate(s2)
    assert np.array_equal(a.hist["inr"], b.hist["inr"])


def test_load_warns_on_version_mismatch():
    import json
    s = spec_from_scenario("reference")
    d = json.loads(save_config(s)); d["identity"]["versions"]["params"] = "params-0.0.1"
    _, warns = load_config(json.dumps(d))
    assert any("params" in w for w in warns)
