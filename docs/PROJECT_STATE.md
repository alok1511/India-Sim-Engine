# Project state

**Objective:** transparent, interactive India macro scenario and strategic-risk simulator with honest uncertainty and a
complete readable oil-shock case (brief: attachment of 2026-10-25).

**Phase:** E complete for v0.3.0 (implementation gates pass; empirical validation pending).

**Verified:** 62 tests pass, 1 not run (historical evaluation); accounting checks pass on all scenarios; UI launched and
inspected headlessly; trace reconciliation exact on all scenarios.

**Blockers:** none for exploratory use. Predictive use is blocked on B-01 (historical evaluation with vintages).

**Exact next action:** B-02 (model the RBI dollar-deposit window reversal), then B-03 (yield/sovereign-risk feedback),
then B-01.

**Data vintage:** baseline snapshot as of 2026-10-25 (data/baseline_2026-10.yaml). Refresh before each use: Brent, INR,
reserves, CPI, repo, 10Y, OMC margins, retail fuel prices.
