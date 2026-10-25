import copy
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indiasim.config import spec_from_scenario  # noqa: E402
from indiasim.model import simulate  # noqa: E402


def det(sid, **kw):
    """Deterministic central run: zero innovations, central parameters, regimes end at median duration."""
    return simulate(spec_from_scenario(sid, n_paths=1, param_mode="central", shock_mode="deterministic", **kw))


def mc(sid, n=300, **kw):
    return simulate(spec_from_scenario(sid, n_paths=n, **kw))


@pytest.fixture(scope="session")
def esc_mc():
    return mc("oil_escalation", 400)


@pytest.fixture(scope="session")
def ref_mc():
    return mc("reference", 400)
