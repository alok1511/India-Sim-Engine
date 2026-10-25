# Model specification (engine 0.3.0, params-0.3.0, mech-0.3.0)

## 1. What the model is (and is not)

A **monthly, semi-structural, actor-explicit scenario engine** for India with the rest of the world represented only through the channels that hit India (oil, US rates, the dollar, risk appetite, world demand, food supply). It combines:

| Method | Used for | Why this method |
|---|---|---|
| Accounting identities | Current account, capital account, BoP closure, reserves stock-flow, liquidity, fuel price build-up, fiscal deficit and debt, CPI aggregation | These must hold exactly; they are where common errors (USD vs INR, gross vs net oil) happen |
| Semi-structural equations (QPM-style) | Output gap, core inflation, expectations, 10Y yield, credit | Transparent, small, auditable; signs and lags are defensible even when coefficients are judgmental |
| Regime-switching stochastic drivers | Oil disruption regime, escalation layer, correlated global innovations, fat oil tails | Supply disruptions start and end abruptly; oil returns are heavy-tailed |
| Explicit actor rules | RBI MPC, RBI FX & sterilisation, Government fuel pricing, Government fiscal rule | Lets you switch responses and read who absorbs the cost |
| Behavioural equations | Households (fuel real income), firms (input costs, capex), banks (stress, credit), FPIs | Private responses enter as rules, not as LLM judgement |

It is **not** a DSGE model, a full national-accounts system, a forecasting model, or a global model. It has **not** been estimated or validated out of sample.

## 2. Closure and boundaries (stated, not hidden)

* **External closure:** ex-ante FX pressure `= -(CA + KA)`. RBI sells a policy-chosen share. Unabsorbed pressure moves INR (`fx_depth`), and ex-post price-induced flows (`fx_adjust`) close the BoP so that `CA + KA + fx_adjust = ΔReserves(BoP) = -intervention`. `fx_adjust` is a **model closure**, not an observed BoP line.
* **Residual capital** (incl. errors & omissions) is an explicit constant plug calibrated to Q1 FY27 (E09). The RBI dollar-deposit window reversal is **not modelled** (KA-04).
* **Fiscal:** central government only, BE run-rate at t0 conditions plus explicit deviations (OMC compensation, fertiliser, interest, fuel excise, capex cuts, buoyancy). Apr–Oct 2026 assumed on BE pace. States, PSU balance sheets and off-budget items are outside the boundary.
* **National accounts:** no expenditure-side GDP identity. Demand channels are *contributions to the output gap* (exactly decomposable), not consumption/investment levels.
* **Monetary:** policy corridor SDF = repo − 25bp, MSF = repo + 25bp; WACR moves inside it with liquidity. Bank, NBFC and insurer balance sheets are absent.

## 3. Frequencies and aggregation

* State transitions are **monthly**. t0 = October 2026; t = 1 is November 2026. Horizon 12 or 24 months (configurable 6–36).
* **GDP is quarterly**: the monthly activity index `A_t = potential × (1 + gap)` is averaged over the quarter and compared with the year-ago quarter. It is published two months after quarter end. No interpolation of GDP back to months.
* **CPI is monthly** (index, y/y). Released mid-month m+1, usable by decisions from m+2.
* **Markets** (INR, yields, Brent) are monthly averages/levels; actors observe the previous month (MPC) or same-month real-time prices (FX intervention, OMC pricing) — granted explicitly.
* **Pre-sample (24 months)** is SYNTHETIC except Brent (approximate, partly sourced). Y/y CPI and GDP over the first 12 months therefore carry artificial base effects (KA-10).

## 4. Within-month ordering

0. Start-of-month decisions on published information: MPC (meeting months Dec, Feb, Apr, Jun, Aug, Oct); fiscal rule (uses own accounts to t−1).
1. Regimes and global drivers (Markov regimes from pre-drawn uniforms; correlated innovations via regime-specific Cholesky; Student-t oil tails).
2. External accounts in USD (INR and activity of t−1: invoicing lag).
3. Capital account (yield spread and depreciation momentum of t−1; risk-off of t).
4. FX market: pressure → intervention (reserve-floor scaled) → INR → reserves.
5. Liquidity drain/sterilisation → WACR in the corridor.
6. Fuel pricing decision with same-month import parity → OMC margin, losses, compensation.
7. Prices: energy (retail fuel), food (shock + transport), core (persistence, expectations, gap, ERPT, indirect oil) → headline → expectations (with de-anchoring regime).
8. Output gap = Σ channel contributions (exact linear system, each channel decays at ρ).
9. Fiscal accounts. 10. 10Y yield. 11. Credit and stress. 12. Activity index and quarterly GDP.

Feedback is resolved **through time** (lags), not by simultaneous solution. Example: rupee depreciation in month t affects non-oil trade from t+1 and core inflation through a 6-month average.

## 5. Variable dictionary (core state)

| Variable | Definition | Unit | Freq | Role | t0 value (source) | Update rule | Bounds / missing data |
|---|---|---|---|---|---|---|---|
| brent | Brent crude | USD/bbl | M | external driver | 116.7 (E15, 23 Oct 2026) | log mean reversion to regime anchor + t-innovation; κ=0.6 in regime-change month (M-OIL-01/02) | >0 by construction (log); bound checked |
| disrupt / esc | Disruption regime / escalation layer | flag | M | regime | 1 / 0 (assumed) | Markov with hazard; escalation forced window | — |
| crack, freight | Auto-fuel crack; landed freight | USD/bbl | M | driver | 22, 3 (illustrative, calibrated to E21) | regime-dependent constants (M-OIL-03) | — |
| us10y | US 10Y | % | M | driver | 5.2 (E18, stale) | AR to anchor + scenario offset (M-GLB-02) | — |
| dxy | Dollar index | log, t0=0 | M | driver | 0 | random walk + offset | — |
| risk_off | Global risk-off | z | M | driver | 1.0 (assumed) | AR(1), elevated with regime (M-GLB-01) | — |
| gdem | World demand gap | pp | M | driver | 0 | AR(1) + offset (M-GLB-03) | — |
| food_shock | Food supply shock | pp annualised | M | driver | 3.2 (derived E13) | AR(1) + offset (M-GLB-04) | — |
| crude_bill | Crude import bill | USD bn/month | M | derived | 18.8 | vol × 7.33 × (Brent+freight)/1000 (M-EXT-01) | INR never enters |
| prod_exp | Product exports | USD bn/month | M | derived (offset) | 5.8 | 5.5 MMT × 7.6 × (Brent+crack)/1000 | — |
| oil_net | Net oil & gas balance | USD bn/month | M | derived | −15.9 | identity (M-EXT-04) | — |
| nonoil_bal | Non-oil goods balance | USD bn/month | M | derived | −14.5 (derived E05) | gdem, lagged real INR, gap (M-EXT-05) | — |
| services, remit, prim_inc | CA components | USD bn/month | M | derived | 17.2, 13.6, −3.5 (E06–E08) | M-EXT-06..08 | Q1 averages; no seasonality |
| ca | Current account | USD bn/month | M | derived | −3.1 | identity (M-EXT-09) | — |
| fpi, ka | Portfolio flows; capital account | USD bn/month | M | derived | −3.2; −1.3 | M-CAP-01..03 | residual plug explicit |
| pressure, interv | FX pressure; RBI net sales | USD bn/month | M | derived; policy | 4.4; — | identity; rule (M-FX-01/02) | sales stop at 95% of floor |
| inr | INR per USD | INR | M | derived | 97.0 (E11) | unabsorbed pressure / depth + 0.3×Δdxy + noise (M-FX-03) | >0 |
| reserves | FX reserves | USD bn | M | stock | 734.6 (E10) | −interv + valuation (M-FX-04) | ≥0 checked |
| liq, wacr | Banking liquidity; overnight rate | Rs lakh cr; % | M | derived | 1.0 (assumed); 5.38 | stock-flow; corridor-bounded rule | corridor binding flagged |
| repo | Policy repo | % | event (bi-monthly) | policy | 5.50 (E01) | MPC rule on published data, 25/50bp steps | 3–9% |
| g10 | 10Y G-sec | % | M | derived | 7.46 (E17) | partial adjustment to repo×0.6 + US + fiscal + expectations premia | — |
| parity | Auto-fuel import parity | Rs/litre | M | derived | 86.4 | (Brent+crack+freight)×INR/159 | — |
| retail_fuel, excise | Retail price (Delhi blend); central excise | Rs/litre | M | policy | 97.62 (E22); 1.05 (E20) | Govt fuel rule (M-FUEL-02) | excise ≥ 0 (infeasible cuts flagged) |
| omc_margin | OMC marketing margin | Rs/litre | M | derived | −8.4 (E21: −8/−9) | identity (M-FUEL-03) | — |
| cum_omc_loss | Net uncompensated OMC losses since t0 | Rs lakh cr | M | stock | 0 | Σ losses − compensation − recoupment | — |
| food/energy/core/cpi index & y/y | CPI | index, % y/y | M | derived | 5.54 headline, 7.74 food (E13) | M-PRC-01..04; weights 0.37/0.08/0.55 (unverified) | — |
| exp_infl | Effective 1y expectations | % | M | derived | 5.0 (assumed) | adaptive; de-anchoring regime (M-PRC-05) | — |
| gap, c_* | Output gap and channel contributions | % of potential | M | derived | +0.3 (assumed, E14) | Σ channels, each c=ρc+impulse (M-REAL-01..10) | exact decomposition |
| gdp_yoy | Real GDP growth | % y/y | **Q** | derived | Q1 FY27 7.8 (E14) | quarterly aggregation (M-REAL-11) | NaN in non-quarter months |
| fd_proj | Projected FY central deficit | % GDP | M | derived | 4.3 (E23) | run-rate projection of FY flows | — |
| credit_yoy, stress | Credit growth; stress index | % y/y; index | M | derived | 11.0; 0 (assumed) | M-CRD-01/02 | stress nonlinear (only negative gap) |

## 6. Key equations (monthly; full code in `src/indiasim/model.py`)

```
Oil:      ln B_t = ln B_{t-1} + κ_t [ln(a + p·D_t + e·E_t + β·gdem_t) − ln B_{t-1}] + σ(D,E)·ε_oil,t,  ε_oil ~ t5 (unit var)
USD bill: crude_bill_t = V_t · 7.33 · (B_t + f_t)/1000,   V_t = V0 (1+gap_{t-1}/100)(B_t/B0)^η (1 − shortfall_t)
FX:       P_t = −(CA_t + KA_t);  I_t = φ·s(R_{t-1})·P_t;  Δln INR_t·100 = (P_t − I_t)/depth + 0.3·Δdxy_t·100 + σ_fx ε
Liquidity: L_t = L_{t-1} − I_t·INR_t/1000 + θ_ster·I_t·INR_t/1000;  WACR = clip(repo − k·L_t, SDF, MSF)
Fuel:     retail = (margin + parity + excise + dealer)(1+VAT)   [identity; the policy rule chooses retail/excise]
Core:     π^c_t(m/m) = λπ^c_{t-1} + (1−λ)E_{t-1}/12 + κ·gap_{t-1}/12 + γ_fx·avg6(dep) + γ_oil·avg6(Δln crude_INR)
Gap:      gap_t = Σ_k c_{k,t},  c_{k,t} = ρ c_{k,t-1} + impulse_{k,t}   (impulses measured vs t0 conditions)
MPC:      i* = r* + 4 + c_π(½CPI_obs + ½E_obs − 4) + c_y(GDP_obs − 7);  step 25bp if |i*−i|>0.2, 50bp if >1.5
```

**Impulses are measured relative to t0 conditions** (t0 conditions are assumed already embedded in the starting gap and its decay). This avoids spurious drift from level effects that were already present before October 2026.

## 7. Uncertainty layers (kept separate)

1. **Within-path shocks** (inner): correlated driver innovations (calm vs stress correlation regimes, validated PSD), Student-t oil tails, regime timing via pre-drawn uniforms, FX/gap/yield/food noise. Drawn once per path from `SeedSequence([seed, path])`.
2. **Parameter uncertainty** (outer): 36 of 114 parameters with uniform/triangular ranges, drawn ONCE per path (structural meaning), separate child stream. Switch: `param_mode = central | sampled`.
3. **Model structure / actor behaviour**: expectations `adaptive | anchored`, FX regime `managed | flexible`, and the actor-choice menus. Compared as conditional results; never averaged unless explicit weights are supplied (`risk.mixture`).

Behavioural variation inside a rule (e.g. MPC inflation coefficient 0.7–1.5) is a sampled parameter, labelled "actor behaviour" in params.yaml.

## 8. Calibration status

No parameter is estimated in this project. Of 114 parameters: 70 judgmental, 28 illustrative, 13 external (benchmarked to a source), 3 derived. 55 causal links are implemented; 10 conceptual gaps are shown but not executed. Two **benchmark checks** (not calibrations) agree with published ranges: +USD10/bbl → CA −USD15.6bn/yr (MSM 17: USD12.5bn at 2018 volumes); frozen pump prices → +0.17pp CPI per 10% oil (RBI Bulletin 2025: ~0.20pp under managed prices). Agreement on two moments is not validation.
