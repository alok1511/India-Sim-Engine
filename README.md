# indiasim — India Economic Scenario & Strategic Risk Simulator

A transparent, interactive simulation engine for exploring how shocks and policy decisions propagate through India's
economy: introduce a shock, explore paths, read a path's causal sequence, inspect actor decisions, change a decision,
replay, and compare.

> **Status: illustrative and unvalidated.** Implementation and accounting checks pass (62 tests). Parameters are
> judgmental or illustrative; no out-of-sample evaluation has been run. Percentages are *conditional model frequencies*,
> not forecast probabilities. The starting state is a dated snapshot (2026-10-25), not live data.

## Quick start (about 2 minutes, no API keys, no accounts)

```bash
git clone <your-repo-url> indiasim && cd indiasim
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
streamlit run app/streamlit_app.py                        # opens http://localhost:8501
```

Command line (also the interface for a future agent team):

```bash
indiasim check                                            # accounting + reproducibility on all scenarios
indiasim run --scenario oil_escalation --paths 1000 --out runs/oil
indiasim trace --scenario oil_escalation --path 169 --branch 2:gov_fuel=full_passthrough
indiasim compare --scenario oil_escalation --bundle "status quo:" --bundle "pass-through:gov_fuel=full_passthrough"
indiasim stress --scenario reference --cond "inr>105" --cond "cpi_yoy>6.5"
indiasim situation --file examples/situation_hormuz_closure.json --out runs/hormuz
python -m pytest                                          # 62 passed, 1 skipped (historical evaluation not run)
```

## What is inside

| Path | Contents |
|---|---|
| `src/indiasim/model.py` | Monthly engine (vectorised over paths), actor rules, mechanism IDs on every equation |
| `src/indiasim/trace.py` | Event traces built from the run log; causal parents; exact decompositions where valid |
| `src/indiasim/risk.py` | Thresholds, first passage, duration, recovery (censoring), joint stress, ES, convergence, sensitivity, mixtures |
| `src/indiasim/analysis.py` | Branch/replay with matched draws, strategy comparison, cost absorption, reverse stress, after-action |
| `src/indiasim/checks.py` | Accounting, unit and bound checks with stated boundaries |
| `app/streamlit_app.py` | Seven views: Overview, Causal map, Playback, Risk lab, Strategy comparison, Analyst tools, Evidence |
| `config/` | Parameters (status-labelled), mechanisms (55 implemented + 10 visible gaps), 6 scenarios, analyst registers |
| `data/` | Baseline snapshot (2026-10-25) and `EVIDENCE.csv` (27 dated sources) |
| `docs/` | MODEL_SPEC, REQUIREMENTS, DECISIONS, TEST_RESULTS, USER_GUIDE, BACKLOG, PROJECT_STATE |
| `AGENTS.md`, `examples/` | Agent-team design and the situation-brief JSON schema |
| `runs/examples/` | Saved example runs with traces and assumptions reports |

## Scenarios
`reference` (current Gulf-disruption regime resolving at random) · `oil_escalation` (Hormuz) · `ceasefire` ·
`global_tightening` · `food_stress` · `combined_stress`. Actor menus: fuel pricing (6), fiscal stance (2), MPC rule (4),
FX intervention (3), sterilisation (3). Structures: expectations adaptive/anchored, FX managed/flexible.

## Refresh the snapshot before use
Edit `data/baseline_2026-10.yaml` (Brent, INR, reserves, CPI, repo, 10Y, OMC margins, retail fuel) and add a row to
`data/EVIDENCE.csv` for each changed value. Versions and hashes are written into every export so old runs stay traceable.

## Read before relying on results
`docs/TEST_RESULTS.md` (self-review verdict: conditional pass), `config/analysis/premortem.yaml` (known biases, incl.
the model flattering fiscal absorption), `docs/BACKLOG.md`.
