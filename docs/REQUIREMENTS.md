# Requirement ledger (status as of 2026-10-25)

Status: PASS = implemented and verified by the named check; PARTIAL = implemented with stated limits; NOT RUN = test defined but not executable here; DEFERRED = backlog.

| ID | Requirement (brief section) | Pri | Verification | Status |
|---|---|---|---|---|
| R-01 | Runs locally, opens immediately, no credentials (§2, AT-01) | P0 | `test_at01_launch_ui.py`; headless browser screenshots | PASS |
| R-02 | Python core, Streamlit+Plotly UI, YAML/CSV config, separated layers (§2) | P0 | code layout: model / actors in model rules / trace / risk / analysis / app | PASS |
| R-03 | No LLM key required; narratives from structured records (§2, §6) | P0 | `trace.narrate` deterministic templates | PASS |
| R-04 | Monthly steps, event decision points, native frequencies explicit (§2) | P0 | MODEL_SPEC §3; quarterly GDP aggregation; publication lags | PASS |
| R-05 | INR domestic / USD external, units explicit, FY Apr-Mar, IST calendar (§2) | P0 | AT-04 USD-vs-INR test; UNITS in UI | PASS |
| R-06 | Seven economic areas covered at stated aggregation (§3) | P0 | MODEL_SPEC §5; mechanisms.yaml | PARTIAL: employment = activity proxy; states, banks absent (visible gaps G-01..G-10) |
| R-07 | Variable and link dictionaries with full metadata (§4) | P0 | MODEL_SPEC §5; mechanisms.yaml; params.yaml | PASS |
| R-08 | Accounting checks with stated boundaries; closure explicit (§4) | P0 | `checks.py`; AT-04 | PASS |
| R-09 | Common-error guards (USD/INR, gross/net oil, CAD≠depreciation, shock type, pass-through vs tax vs subsidy vs margin, intervention vs liquidity, ordering) (§4) | P0 | AT-04, AT-05/06; FX closure; fuel identity | PASS |
| R-10 | Provenance for data; parameters labelled by status (§5) | P0 | EVIDENCE.csv (27 rows); params.yaml status; AT-15 | PASS |
| R-11 | Trace from run log with full event record fields (§6) | P0 | AT-08 reconcile; event schema in trace.py | PASS |
| R-12 | Occurrence vs publication vs awareness; no future info (§6, §8) | P0 | publication events; AT-07 | PASS (market anticipation NOT modelled - stated) |
| R-13 | Pause, step, inspect chain, branch, replay with fixed history and matched draws (§6) | P0 | Playback view; AT-09 | PASS |
| R-14 | Oil chain with offsets and alternative paths (§6) | P0 | AT-05/06; ceasefire scenario; remittance & product-export offsets | PASS |
| R-15 | Seeded MC; shocks vs parameters vs structure separated (§7) | P0 | AT-02, AT-11 | PASS |
| R-16 | Validated correlations, visible repair; t-tails justified (§7) | P1 | AT-11; CORR_REPORTS in Evidence tab | PASS |
| R-17 | Bands, endpoints, thresholds, first passage, duration, recovery with censoring, joint, ES, sensitivity, structure comparison (§7) | P0 | AT-10 fixture; Risk lab | PASS |
| R-18 | Labels: validated vs conditional vs exploratory; sampling error shown (§7) | P0 | AT-15; UI banners | PASS |
| R-19 | Representative paths are actual paths (§7) | P0 | AT-12 | PASS |
| R-20 | Mixture only with explicit weights (§7) | P1 | `risk.mixture`; UI sliders | PASS |
| R-21 | Actors: objectives, constraints, actions, info, cadence; govt fuel/tax and RBI policy/FX alternatives (§8) | P0 | POLICY_OPTIONS; decision records; AT-06 | PASS (objectives implicit in rules; no formal game theory - by design) |
| R-22 | Adjudication source labelled; human overrides logged and reproducible (§8) | P0 | `support` field; overrides in spec/config; AT-02 roundtrip | PASS |
| R-23 | Assumptions, ACH, signposts, premortem, reverse stress, after-action (§9) | P1 | Analyst tools tab; `reverse_stress`, `after_action` | PASS (ACH/signposts are dated manual inputs) |
| R-24 | Six connected views, left controls, scope on charts, stale marking (§10) | P0 | AT-01/13; screenshots | PASS |
| R-25 | Save/load/export with identity and versions (§10) | P0 | AT-02 roundtrip; Exports tab | PASS |
| R-26 | Durable state files (§12) | P1 | docs/*.md | PASS |
| R-27 | Acceptance tests 1-16 incl. edge cases (§13) | P0 | `pytest` 62 passed, 1 skipped | PASS except AT-16 NOT RUN |
| R-28 | Historical out-of-sample evaluation vs benchmark (§11E, AT-16) | P1 | requires real-time vintages | NOT RUN (B-01) |
| R-29 | Additional scenarios: global tightening, food stress (§11E) | P1 | scenario YAMLs; AT-04 grid | PASS |
| R-30 | Independent evaluator pass (§13) | P1 | docs/TEST_RESULTS.md | SELF-REVIEW ONLY (no independent reviewer used) |
| R-31 | Interface usable by a future agent team (user request) | P1 | `indiasim` CLI; `situation` JSON hook; AGENTS.md | PASS (agents themselves not built) |
