"""AT-10 threshold, joint, duration and recovery statistics vs independent hand computation on a small fixture.
Censored non-recoveries are counted explicitly."""
import numpy as np

from indiasim.model import P
from indiasim.risk import Threshold, evaluate_threshold, joint_frequency, wilson, expected_shortfall


class Fake:
    def __init__(self, series: dict):
        n, T1 = next(iter(series.values())).shape
        self.T = T1 - 1
        self.hist = {k: np.vstack([np.full((P, n), np.nan), v.T]) for k, v in series.items()}
        self.path_indices = list(range(n))

    def panel(self, v):
        return self.hist[v][P:, :].T


# months 0..8 (t0 + 8 months); level 6
CPI = np.array([
    [5, 5, 5, 5, 5, 5, 5, 5, 5],      # never breaches
    [5, 7, 7, 5, 5, 5, 5, 5, 5],      # breach m1-2, recovers (3 safe months) -> recovery time 4-1 = 3? see below
    [5, 5, 5, 7, 7, 7, 7, 7, 7],      # breach from m3 to end: not recovered (censored); endpoint breach
    [5, 7, 5, 7, 5, 5, 5, 5, 7],      # intermittent; recovers after m3; endpoint breach
], float)
INR = np.array([[90] * 9, [101] + [90] * 8, [90, 90, 90, 101, 90, 90, 90, 90, 90], [90] * 9], float)


def test_threshold_stats_match_hand_computation():
    f = Fake({"cpi_yoy": CPI, "inr": INR})
    any_ = evaluate_threshold(f, Threshold("a", "cpi_yoy", ">", 6, "any"))
    assert any_["frequency"] == 0.75
    assert list(any_["first_passage"][1:]) == [1, 3, 1] and np.isnan(any_["first_passage"][0])
    assert list(any_["max_duration"]) == [0, 2, 6, 1]
    assert list(any_["months_beyond"]) == [0, 2, 6, 3]
    # recovery: first index s after first breach f with 3 consecutive safe months; time = month(s+2) - month(f)
    # path1: f=m1, safe run m3,m4,m5 -> 5-1 = 4 ; path2: never -> censored ; path3: f=m1, safe m4,m5,m6 -> 6-1 = 5
    assert any_["recovery_time"][1] == 4 and any_["recovery_time"][3] == 5
    assert bool(any_["censored"][2]) and not any_["censored"][1]
    assert any_["summary"]["n_not_recovered_by_horizon"] == 1
    end = evaluate_threshold(f, Threshold("e", "cpi_yoy", ">", 6, "endpoint"))
    assert end["frequency"] == 0.5
    dur = evaluate_threshold(f, Threshold("d", "cpi_yoy", ">", 6, "duration", min_months=2))
    assert dur["frequency"] == 0.5


def test_joint_same_month_vs_each_at_some_point():
    f = Fake({"cpi_yoy": CPI, "inr": INR})
    a, b = Threshold("a", "cpi_yoy", ">", 6, "any"), Threshold("b", "inr", ">", 100, "any")
    same = joint_frequency(f, [a, b], same_month=True)
    each = joint_frequency(f, [a, b], same_month=False)
    # path2: CPI>6 m3 and INR>100 m3 -> same month; path1: INR breach at m0 (excluded: t0 is observed, not simulated)
    assert same["frequency"] == 0.25
    assert each["frequency"] == 0.25


def test_wilson_and_es():
    lo, hi = wilson(50, 100)
    assert abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3
    x = np.arange(100.0)
    assert expected_shortfall(x, 0.1, "low") == 4.5 and expected_shortfall(x, 0.1, "high") == 94.5
