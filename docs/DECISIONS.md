# Decision record

| # | Decision | Alternatives | Rationale | Confidence | Invalidate if |
|---|---|---|---|---|---|
| D-01 | Build as a code repository (Python package + Streamlit app), not a chat artifact | Single HTML page; notebook | Needs versioned config, tests, saved runs, CLI for future agents; GitHub gives history and review | High | You only ever need a one-off visual |
| D-02 | Baseline = the CURRENT disruption regime (Brent ~USD117) resolving at random; oil case = escalation on top | Treat Oct-2026 as "normal" and shock from there | The economy is already in an oil shock; ignoring that would mis-state OMC losses, reserves and rates | High | Brent normalises before you use the model |
| D-03 | Vectorised engine over paths; trace regenerated from the same code for one path | Separate single-path engine with logging | One code path => trace and MC can never disagree; 2,000 paths in ~0.4s | High | Need per-event logging for every path |
| D-04 | All randomness pre-drawn per path from SeedSequence([seed, path]) | Global RNG stream | Bit-exact regeneration; matched draws for branches; batch-size invariance (BLAS matmul replaced to keep this exact) | High | — |
| D-05 | Gap impulses measured vs t0 conditions | Level effects vs neutral | Avoids double counting effects already in the starting gap | Medium | A well-identified starting gap becomes available |
| D-06 | FX closure via price-induced flows; residual capital as explicit plug | Fully modelled capital account | Data too thin to model every flow; plug is visible and testable | Medium | Better monthly BoP data |
| D-07 | Rule-based actors with menus; no game theory | Formal games with utilities | Payoffs/information not defensible; menus show trade-offs honestly | High | A specific two-player interaction with defensible payoffs |
| D-08 | Default RBI FX = heavy (75%) | moderate | Evidence of heavy defence near 97 (reserves -USD51bn in 4 weeks) | Medium | RBI steps back and INR moves freely |
| D-09 | MPC uses only published data; FX desk and OMCs see same-month market prices | Same info for all | Matches institutional reality; tested (AT-07) | High | — |
| D-10 | Deterministic mode ends regimes at median duration | Expected-value smoothing | Keeps nonlinear rules on a feasible path | Medium | — |
| D-11 | No sub-agents used for this build | Parallel research/review agents | Single coherent build; independent review is labelled as not done | — | You want a genuinely independent red-team review (backlog B-08) |
