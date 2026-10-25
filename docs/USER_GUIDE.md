# User guide: one complete experiment

**Question:** if the Gulf conflict escalates into a Hormuz disruption from November 2026, who absorbs the cost under
the current frozen-pump-price policy, and what changes if the government passes prices through or compensates OMCs?

## 1. Run
`streamlit run app/streamlit_app.py` -> sidebar: Scenario `oil_escalation` (default), 1,000 paths, Run.

## 2. Read the Overview (numbers below are from seed 20261025, 1,000 paths; they are conditional model frequencies)
| Metric | Reference path | Oil escalation |
|---|---|---|
| Peak Brent, median path peak (USD/bbl) | 125 | 163 |
| Peak INR/USD, median (P90) | 100.5 (106.6) | 104.5 (114.1) |
| Reserve low, median (P10), USD bn | 714 (671) | 674 (620) |
| Peak CPI, median (P90) | 5.6 (6.3) | 5.8 (6.9) |
| Weakest GDP quarter, median (P10) | 6.4 (5.8) | 5.6 (5.0) |
| Share of paths with CPI > 6% at any month | 19% | 38% |
| Share of paths with INR > 100 | 57% | 86% |

Why is CPI only modestly higher under escalation? Because pump prices are frozen: the first-round fuel effect lands on
OMC balance sheets (median net loss ~Rs4.5 lakh crore by Oct 2028), not on households.

## 3. Read one real path (Scenario playback)
Pick "central (P50 severity) - path 169". Step the timeline: shock (Nov) -> Brent -> crude bill (USD; INR does not enter)
-> product exports (offset) -> CA -> FX pressure -> RBI sells dollars (liquidity drain) -> import parity -> fuel decision
(freeze) -> OMC margin collapses -> output gap falls via physical shortfall, input costs and OMC capex. Open any event:
the record shows mechanism, parents, the calculation and an exact decomposition where one exists.

## 4. Change a decision and replay
Branch from Dec 2026: `gov_fuel` -> `full_passthrough`. History before December is identical; future shocks are the same
draws. On this path, CPI rises sharply, OMC losses close, and repo goes higher. The "who absorbs the cost" table shows the shift.

## 5. Compare strategies (common random numbers, 1,000 paths)
| Bundle | Peak CPI (median) | Weakest GDP qtr | OMC net loss (Rs lakh cr) | FY27 deficit (% GDP) | Peak 10Y |
|---|---|---|---|---|---|
| Status quo (freeze, OMCs absorb) | 5.8 | 5.6 | 4.5 | 4.33 | 8.35 |
| Full pass-through | 9.7 | 5.1 | 0.7 | 4.34 | 9.46 |
| Freeze + Budget compensates | 5.9 | 5.9 | -1.5 | 5.04 | 8.63 |
| 50% pass-through + half compensation | 9.1 | 5.0 | -0.4 | 4.45 | 9.60 |

Reading: there is no free option. Pass-through moves the cost to households and triggers more tightening; compensation
moves it to the deficit and bond yields. **Caution:** the model has no channel from higher yields or a wider deficit to
growth or sovereign risk, so the compensation route is flattered (premortem item 1).

## 6. How to interpret probabilities
* "38% of paths" = **conditional model frequency** under these assumptions. Not a forecast probability.
* The 95% interval shown is Monte Carlo sampling error only. Switching model structure (Risk lab -> "Run alternative
  structures") usually moves results more than that interval.
* A single path in playback is an **exploratory scenario** with no probability attached.

## 7. What would invalidate these conclusions
* The disruption ends fast (watch Brent < USD100 and tanker transits): escalation costs shrink, OMCs recoup.
* RBI steps back from heavy intervention: INR weaker, reserves stronger, CPI higher than shown.
* The deposit-window reversal accelerates (not modelled): INR and reserves worse than shown.
* Government changes pump prices or excise: re-run with the matching fuel option.
* Any parameter in the Key assumptions register proves materially wrong (check the sensitivity ranking first: fx_depth,
  fpi_risk and oil_anchor dominate INR outcomes).
