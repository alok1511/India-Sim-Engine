# Driving the simulator with an agent team (future design)

The engine is built so that agents **select** inputs and **read** outputs; they never invent macro numbers.
Everything quantitative comes from `simulate()` and is reproducible from the saved config.

## Stable interface
* `indiasim situation --file brief.json --out runs/x` - structured brief (schema: `examples/situation.schema.json`) -> runs
  + comparison + accounting checks -> `situation_result.json`, `assumptions_report.md`.
* `indiasim run | trace | compare | stress | check` - JSON to stdout; files with `--out`.
* Python: `indiasim.cli.run_situation(dict)`, `indiasim.analysis.branch / compare_strategies / reverse_stress`,
  `indiasim.trace.build_trace`.

## Proposed team (each role has one job and a hard boundary)
| Role | Input | Output | Must not |
|---|---|---|---|
| Situation analyst | news, data releases, your note | dated facts with sources; updates to signposts and baseline snapshot | set model parameters |
| Scenario designer | facts | 2-4 `situation.json` briefs (shock type, size, duration) + competing hypotheses | write outcome numbers |
| Simulation operator | briefs | engine runs, comparisons, reverse stress, traces (CLI only) | edit engine code during a run |
| Red team | results + assumptions register | premortem, strongest countercase, sensitivity asks, structure checks | soften the operator's numbers |
| Brief writer | all of the above | one-page brief: conclusion, who absorbs cost, signposts, what would change the view | add numbers not in run outputs |

Human gate: you approve the briefs before runs and the final note before use. Every number in the note must carry a
`run_id` that reproduces it.

## Guardrails already in the engine
* Frequencies are labelled conditional; single paths are labelled exploratory.
* Actors cannot see unpublished data (tested); scenario briefs are validated against allowed shock types and options.
* Overrides are logged in the config and reproduced on load.
