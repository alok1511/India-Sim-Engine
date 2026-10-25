"""AT-08 every displayed trace event reconciles to the run log; decompositions are exact where claimed."""
import numpy as np
import pytest

from indiasim.config import spec_from_scenario, load_mechanisms
from indiasim.model import simulate
from indiasim.trace import build_trace, reconcile


@pytest.mark.parametrize("sid,path", [("oil_escalation", 3), ("combined_stress", 11), ("food_stress", 0), ("ceasefire", 5), ("global_tightening", 9)])
def test_trace_reconciles_and_is_well_formed(sid, path):
    r = simulate(spec_from_scenario(sid, n_paths=1, path_offset=path))
    ev = build_trace(r, 0, "run")
    assert reconcile(ev, r, 0) == []
    ids = {e["id"] for e in ev}
    assert len(ids) == len(ev)
    mech = {m["id"] for m in load_mechanisms()["links"]}
    pos = {e["id"]: k for k, e in enumerate(ev)}
    for e in ev:
        for m in e.get("mechanism", []):
            assert m in mech, m
        for p in e.get("parents", []):
            assert p in ids and pos[p] < pos[e["id"]]          # parents exist and precede
        if e["type"] == "state_change":
            assert e["parents"] or e.get("root_note")          # orphan moves are labelled, not hidden
        assert e.get("narrative") or e["type"] in ("publication",)


def test_qualitative_label_where_no_exact_decomposition():
    r = simulate(spec_from_scenario("oil_escalation", n_paths=1))
    ev = build_trace(r, 0, "x")
    for e in ev:
        if e["type"] == "state_change" and e["vars"][0]["var"] in ("core_yoy", "fpi", "g10", "stress"):
            assert e["decomposition"] == "qualitative" and "contribution" not in e
