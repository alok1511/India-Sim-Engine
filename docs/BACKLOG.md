# Backlog (prioritised)

## Implemented capability (v0.3.0)
Monthly engine; oil escalation, reference, ceasefire, global tightening, food stress, combined stress; six actor menus;
seeded Monte Carlo with separated uncertainty layers; risk lab; readable traces with branch/replay; strategy comparison;
analyst tools; CLI and situation hook; 62 tests.

## Implemented but UNCALIBRATED (use for exploration only)
FX depth, FPI sensitivities, residual capital, gap impulses, Phillips slope, expectations regime, credit/stress, 10Y premia,
oil regime hazards, crack/freight premia, CPI weights. All flagged judgmental/illustrative in params.yaml.

## Next (ordered by value for decisions)
| ID | Item | Why | Size |
|---|---|---|---|
| B-01 | Historical evaluation: 2022 oil shock with real-time vintages; blind run; compare with random walk and RBI projections | Only route to any claim of skill (AT-16) | L |
| B-02 | Model the RBI dollar-deposit window and its reversal as an explicit capital flow | Largest known unmodelled FX risk today (KA-04) | S |
| B-03 | Feed the 10Y yield/term spread into the gap; add a sovereign-spread rule linked to deficit and debt | Removes bias toward fiscal absorption | M |
| B-04 | Bank/NBFC/insurer balance-sheet block (MTM on G-secs, NIM, capital, credit supply) | Financial-stability feedback; relevant to insurance work | L |
| B-05 | States: VAT choices and state deficits | Fuel price and fiscal realism | M |
| B-06 | Load actual monthly histories (CPI components, IIP/PMI, INR, reserves) to remove synthetic base effects | Y/y readings in first year | S-M |
| B-07 | Re-estimate a few coefficients (ERPT, oil-to-core, FPI) on Indian data with documented windows | Moves parameters from judgmental to estimated | M |
| B-08 | Independent red-team review (separate agent or human) against REQUIREMENTS.md | Self-review limits | S |
| B-09 | Signposts from live sources (RBI DBIE, MoSPI, PPAC) with dated fetches | Turns snapshot into monitoring | M |
| B-10 | Agent team (see AGENTS.md): situation analyst -> scenario designer -> simulation operator -> red team -> brief writer | Your stated future use | M |
| B-11 | Gold imports, forward book, LPG price choices, sector heterogeneity, employment proxy | Coverage gaps G-01..G-10 | M each |
| B-12 | Bayesian updating of scenario weights from signposts (only with defensible likelihoods) | Living probability view | M |
