# Test results (run 2026-10-25, Python 3.13, numpy 2.5, Streamlit 1.66, Linux)

Command: `python -m pytest -v` -> **62 passed, 1 skipped (AT-16 NOT RUN)** in ~30s. Plus `indiasim check` (all 6 scenarios: accounting PASS, reproducible True).

## Acceptance tests (brief section 13)

| AT | Requirement | Result | Evidence |
|---|---|---|---|
| 1 | Fresh launch, demo data, no credentials | PASS | AppTest launch; headless Chromium screenshots at 1440px and 430px |
| 2 | Same seed/config/version reproduces paths and trace IDs | PASS | bit-exact; path regenerated alone = same path in a 120-path batch |
| 3 | No-shock deterministic case follows specified baseline | PASS | independent re-implementation of oil rule and gap decay; stochastic variation tested separately |
| 4 | Accounting, units, signs, bounds; USD vs INR | PASS | 20 checks x 6 scenarios + 4 policy/structure combos; USD bill invariant to INR |
| 5 | Oil up -> gross USD crude spend up (volumes fixed); downstream conditional | PASS | pass-through vs freeze vs compensation produce different chains |
| 6 | Offsets / alternative choices alter chain without erasing costs | PASS | OMC losses rise when CPI is insulated; remittance offset switchable; ceasefire |
| 7 | No future / unpublished information | PASS | Dec-2026 food shock cannot move Dec or Jan MPC decisions; observation function ignores rows >= cutoff |
| 8 | Trace reconciles to run log; exact decompositions only where valid | PASS | 0 mismatches across 5 scenarios; parents precede children; qualitative labels where no decomposition |
| 9 | Branch keeps history, matched draws; unchanged replay = original | PASS | exogenous drivers bit-identical after branch |
| 10 | Thresholds, joint, durations, recovery vs hand computation; censoring | PASS | 4-path fixture computed by hand |
| 11 | Dependence valid; randomness/params/structure separated; convergence | PASS | PSD checks; repair visible; SE shrinks with n; split-half agreement |
| 12 | Bands vs representative paths; impossible states explicit | PASS | representative paths are members; extreme admissible case passes all bounds |
| 13 | Controls invalidate stale results; shared context | PASS | AppTest: changed control -> STALE banner listing the diff; rerun clears |
| 14 | Save/load/export retains config, versions, seed | PASS | roundtrip reproduces; version mismatch warns |
| 15 | No unsupported calibration/forecast/live-data claims | PASS | param status audit; UI/doc text scan |
| 16 | Historical evaluation without future information; benchmark | **NOT RUN** | no real-time data vintages assembled (backlog B-01) |

Edge cases (all PASS): zero-magnitude shocks reproduce reference exactly; persistent > brief escalation costs; simultaneous shocks worse than either alone; missing/invalid inputs rejected; infeasible excise cut flagged with losses still visible.

## Benchmark comparisons (in-sample plausibility, NOT validation)

| Moment | Model (central, deterministic) | Published | Verdict |
|---|---|---|---|
| CA change per +USD10/bbl | -USD1.30bn/month (-15.6bn/yr) | RBI MSM 17: ~-USD12.5bn/yr at 2018 volumes (E24) | consistent given higher 2026 volumes |
| Peak CPI per 10% oil, frozen pump prices | +0.17pp | RBI Bulletin 2025: ~0.20pp under managed prices (E25) | consistent |
| Peak CPI per 10% oil, full pass-through | +0.85pp | MSM 17: 0.49-1.06pp per USD10 at USD65 (~15%) (E24) | inside range when scaled |

## UI checks performed

* Streamlit AppTest: launch, every button clicked (replay, structures, comparison, failure-pathway search, mixture, run) with zero exceptions; all six scenarios run through playback with "all values match" reconciliation.
* Headless Chromium screenshots inspected at desktop (1440px) and narrow (430px): overview, causal map, playback, risk lab. Fixed: truncated metric values. Not inspected visually: strategy comparison and analyst tools tabs (functionally tested only).

## Defects found and fixed during verification

1. Trace crashed for non-oil scenarios (shock descriptions built eagerly) - fixed; covered by AT-08 parametrisation.
2. Path regenerated alone differed from batch at float level (BLAS matmul) - replaced with elementwise sums; now bit-exact.
3. t0 external accounts uninitialised (traces said "from 0.00") - fixed.
4. Mechanism names did not match engine names, so causal parents were missed - aligned; parents verified.
5. 10Y moved one-for-one with repo; MPC jumped 50bp too readily - recalibrated (judgmental).

## Evaluator pass (SELF-REVIEW - no independent reviewer was used)

Verdict: **CONDITIONAL PASS.** Implementation gates pass. Empirical forecasting validation is pending.

| Failed / partial requirement | Severity | Evidence | Smallest correction |
|---|---|---|---|
| R-28 / AT-16 historical evaluation | High for any predictive use | NOT RUN | Assemble 2022 oil-shock real-time vintages; run blind; compare with random-walk and RBI projections (B-01) |
| Fiscal route bias (no 10Y -> growth, no sovereign risk channel) | Medium | budget-compensation bundle shows the best growth outcome | Add 10Y/term-spread to the gap and a sovereign-spread rule (B-03) |
| R-06 coverage (employment, states, banks) | Medium | gaps G-01..G-10 visible | B-04, B-05 |
| Capital account plug; deposit-window reversal absent | Medium | KA-04 | Model the window explicitly (B-02) |
| Synthetic pre-sample histories | Medium for y/y readings in first 12 months | KA-10 | Load actual CPI/IIP/GDP history (B-06) |
| R-30 independent review | Low-Medium | self-review only | Independent red-team pass (B-08) |

Residual limitations: see docs/BACKLOG.md and the premortem register.

## Raw pytest output

```
tests/test_at01_launch_ui.py::test_fresh_launch_no_exception PASSED
tests/test_at01_launch_ui.py::test_changing_control_marks_results_stale_and_rerun_clears PASSED
tests/test_at01_launch_ui.py::test_strategy_button_produces_output PASSED
tests/test_at02_reproducibility.py::test_same_seed_identical PASSED
tests/test_at02_reproducibility.py::test_different_seed_differs PASSED
tests/test_at02_reproducibility.py::test_path_regenerates_identically_alone_or_in_batch PASSED
tests/test_at02_reproducibility.py::test_trace_ids_reproduce PASSED
tests/test_at02_reproducibility.py::test_save_load_roundtrip_reproduces PASSED
tests/test_at02_reproducibility.py::test_load_warns_on_version_mismatch PASSED
tests/test_at03_baseline.py::test_regime_and_oil_path_match_independent_calc PASSED
tests/test_at03_baseline.py::test_initial_gap_decays_geometrically_and_noise_zero PASSED
tests/test_at03_baseline.py::test_stochastic_variation_is_separate PASSED
tests/test_at04_accounting.py::test_accounting_all_scenarios[ceasefire] PASSED
tests/test_at04_accounting.py::test_accounting_all_scenarios[combined_stress] PASSED
tests/test_at04_accounting.py::test_accounting_all_scenarios[food_stress] PASSED
tests/test_at04_accounting.py::test_accounting_all_scenarios[global_tightening] PASSED
tests/test_at04_accounting.py::test_accounting_all_scenarios[oil_escalation] PASSED
tests/test_at04_accounting.py::test_accounting_all_scenarios[reference] PASSED
tests/test_at04_accounting.py::test_accounting_policy_structure_grid[full_passthrough-light-none-anchored-flexible] PASSED
tests/test_at04_accounting.py::test_accounting_policy_structure_grid[excise_cut-heavy-full-adaptive-managed] PASSED
tests/test_at04_accounting.py::test_accounting_policy_structure_grid[freeze_budget_comp-moderate-half-adaptive-flexible] PASSED
tests/test_at04_accounting.py::test_accounting_policy_structure_grid[adaptive_threshold-heavy-none-anchored-managed] PASSED
tests/test_at04_accounting.py::test_usd_bill_independent_of_exchange_rate PASSED
tests/test_at04_accounting.py::test_units_conversion_matches_ppac_july_2026 PASSED
tests/test_at04_accounting.py::test_ca_sign_convention PASSED
tests/test_at05_06_oil_channel.py::test_gross_usd_crude_spend_rises_with_price_volumes_fixed PASSED
tests/test_at05_06_oil_channel.py::test_downstream_depends_on_pricing_policy PASSED
tests/test_at05_06_oil_channel.py::test_remittance_offset_switchable PASSED
tests/test_at05_06_oil_channel.py::test_ca_sensitivity_benchmark_msm PASSED
tests/test_at05_06_oil_channel.py::test_full_passthrough_cpi_benchmark PASSED
tests/test_at05_06_oil_channel.py::test_ceasefire_reverses_oil_but_not_all_costs PASSED
tests/test_at07_information.py::test_mpc_blind_to_unpublished_shock_end_to_end PASSED
tests/test_at07_information.py::test_observation_function_ignores_rows_at_or_after_cutoff PASSED
tests/test_at07_information.py::test_trace_decisions_report_published_values PASSED
tests/test_at08_trace.py::test_trace_reconciles_and_is_well_formed[oil_escalation-3] PASSED
tests/test_at08_trace.py::test_trace_reconciles_and_is_well_formed[combined_stress-11] PASSED
tests/test_at08_trace.py::test_trace_reconciles_and_is_well_formed[food_stress-0] PASSED
tests/test_at08_trace.py::test_trace_reconciles_and_is_well_formed[ceasefire-5] PASSED
tests/test_at08_trace.py::test_trace_reconciles_and_is_well_formed[global_tightening-9] PASSED
tests/test_at08_trace.py::test_qualitative_label_where_no_exact_decomposition PASSED
tests/test_at09_branch.py::test_pre_branch_identical_and_draws_matched PASSED
tests/test_at09_branch.py::test_unchanged_policy_replay_reproduces_original PASSED
tests/test_at09_branch.py::test_override_persists_from_month_onward PASSED
tests/test_at10_risk_metrics.py::test_threshold_stats_match_hand_computation PASSED
tests/test_at10_risk_metrics.py::test_joint_same_month_vs_each_at_some_point PASSED
tests/test_at10_risk_metrics.py::test_wilson_and_es PASSED
tests/test_at11_12_uncertainty.py::test_correlation_matrices_valid_unrepaired PASSED
tests/test_at11_12_uncertainty.py::test_invalid_matrix_is_repaired_visibly PASSED
tests/test_at11_12_uncertainty.py::test_param_draws_once_per_path_and_separate_from_shocks PASSED
tests/test_at11_12_uncertainty.py::test_deterministic_shocks_with_sampled_params PASSED
tests/test_at11_12_uncertainty.py::test_structure_alternatives_change_results_with_same_draws PASSED
tests/test_at11_12_uncertainty.py::test_convergence_se_shrinks PASSED
tests/test_at11_12_uncertainty.py::test_representative_paths_are_actual_members PASSED
tests/test_at11_12_uncertainty.py::test_extreme_admissible_values_no_impossible_states PASSED
tests/test_at15_16_claims_history.py::test_no_parameter_claims_estimated_status PASSED
tests/test_at15_16_claims_history.py::test_ui_labels_frequencies_and_disclaims_validation PASSED
tests/test_at15_16_claims_history.py::test_docs_do_not_claim_live_or_validated PASSED
tests/test_at15_16_claims_history.py::test_historical_out_of_sample_evaluation SKIPPED [ 92%]
tests/test_edge_cases.py::test_zero_magnitude_shocks_equal_reference PASSED
tests/test_edge_cases.py::test_brief_vs_persistent_escalation PASSED
tests/test_edge_cases.py::test_simultaneous_worse_than_each_alone PASSED
tests/test_edge_cases.py::test_missing_and_invalid_inputs_rejected PASSED
tests/test_edge_cases.py::test_infeasible_excise_cut_is_flagged_not_faked PASSED
======================== 62 passed, 1 skipped in 29.67s ========================
```
