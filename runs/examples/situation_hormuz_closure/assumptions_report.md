# Assumptions and evidence report

Run identity: `b4ed8c36e704` | created 2026-10-25T13:57:54+05:30 IST

Versions: {'engine': '0.3.0', 'params': 'params-0.3.0', 'mechanisms': 'mech-0.3.0', 'baseline': 'IN-2026-10', 'params_hash': '8afe57371205', 'baseline_hash': '39b51f689e36'}

Scenario: **Hormuz closure for 4 months with a weaker global economy**

Analyst brief: Houthi strikes widen to tanker traffic; Hormuz transits fall sharply from November. US data soften. Question: which risks for India cross critical thresholds, and does a 50% pump-price pass-through change the picture?

## Actor choices

- gov_fuel: `freeze_omc_absorb` - Freeze retail; OMCs absorb losses (status quo Oct 2026)
- gov_fiscal: `accommodate` - Let the deficit absorb oil costs
- rbi_mpc: `inflation_targeting` - Flexible inflation targeting on published headline/expectations/growth
- rbi_fx: `heavy` - Absorb ~75% of FX pressure
- rbi_steril: `half` - Offset half the liquidity drain

Structure: {'expectations': 'adaptive', 'fx_regime': 'managed'}

Overrides (branch/human): none

## Interpretation

- Percentages are CONDITIONAL MODEL FREQUENCIES under these assumptions, not validated forecast probabilities.
- No parameter is estimated by this project. Status column shows the basis of each.

## Parameters

| name | value | range | status | unit | description |
|---|---|---|---|---|---|
| a_fiscal | 0.3 | 0.15-0.45 | judgmental | per % monthly GDP capex change | Capex multiplier impulse |
| a_food | 0.015 | fixed | judgmental | per pp food shock | Rural real-income squeeze |
| a_gdem | 0.05 | fixed | judgmental | per pp gdem | External demand |
| a_hh_fuel | 0.5 | 0.3-0.8 | judgmental | per pp fuel real-income loss | Household real-income squeeze from fuel prices |
| a_input | 0.008 | 0.004-0.012 | judgmental | per 1% landed crude Rs cost change | Firms' input-cost squeeze |
| a_omc | 0.05 | fixed | judgmental | per % monthly GDP OMC loss | OMC loss -> capex deferral |
| a_phys | 0.15 | fixed | judgmental | per % crude physical shortfall | Supply rationing hit |
| a_rate | 0.04 | 0.02-0.06 | judgmental | per pp real rate gap (3m lag) | Interest-rate channel |
| a_risk | 0.03 | fixed | judgmental | per z risk-off | Confidence / financial conditions |
| a_stress | 0.03 | fixed | judgmental | per stress unit | Credit supply |
| baseline_hazard | 0.12 | 0.06-0.25 | judgmental | prob per month | Monthly probability the baseline disruption regime ends |
| bbl_per_t_crude | 7.33 | fixed | external | bbl/tonne | Standard conversion |
| bbl_per_t_prod | 7.6 | fixed | illustrative | bbl/tonne | Lighter product conversion |
| capex_month | 1.02 | fixed | derived | Rs lakh crore/month | Central capex 12.2/12 (cap on cuts = 25%) |
| core_fx | 0.08 | 0.04-0.12 | external | per 1% (6m avg) depreciation | ERPT to core (implies ~0.2 long-run on core) |
| core_gap | 0.15 | 0.08-0.25 | judgmental | pp annual per 1% gap | Phillips-curve slope |
| core_lambda | 0.6 | fixed | judgmental | persistence | Core m/m inflation persistence |
| core_oil | 0.007 | 0.003-0.012 | external | per 1% landed crude Rs cost (6m avg) | Indirect oil cost pass-through to core; benchmarked to E24/E25 |
| crack_base | 18.0 | fixed | illustrative | USD/bbl | Auto-fuel crack over Brent, no disruption |
| crack_disrupt | 4.0 | 2.0-10.0 | illustrative | USD/bbl | Extra crack in disruption regime (calibrated so t0 OMC margin = -8.5) |
| credit_gap | 0.6 | fixed | judgmental | pp annual per 1% gap | Credit demand vs activity |
| credit_rate | 1.0 | fixed | judgmental | pp annual per pp lending rate change | Credit vs price of credit |
| credit_stress | 1.5 | fixed | judgmental | pp annual per stress unit | Bank supply tightening |
| credit_trend | 11.0 | fixed | illustrative | % y/y | Trend credit growth |
| crude_vol0 | 21.4 | fixed | external | MMT/month | Crude import volume (Jul 2026 PPAC provisional) |
| dealer_margin | 3.8 | fixed | illustrative | Rs/litre | Dealer commission |
| dxy_sigma | 0.018 | fixed | external | log sd per month | Dollar index monthly sd |
| ecb_other0 | 3.7 | fixed | external | USD bn/month | ECB + other investment |
| ecb_us | 0.6 | fixed | judgmental | USD bn per pp US10Y | ECB borrowing deterred by US yields |
| energy_auto_share | 0.6 | fixed | illustrative | share | Petrol/diesel share of energy component; rest administered (LPG/electricity) |
| exp_theta | 0.05 | fixed | judgmental | per month | Adaptive expectations speed (anchored) |
| exp_theta_deanchor | 0.15 | fixed | judgmental | per month | Speed after de-anchoring (headline >6 for 3 months) |
| fd_target_fy28 | 4.1 | fixed | illustrative | % GDP | Assumed FY28 deficit target (not announced) |
| fdi0 | 2.0 | fixed | external | USD bn/month | Net FDI |
| fert_oil | 0.01 | fixed | illustrative | Rs lakh crore/month per USD10 Brent above t0 | LNG-linked fertiliser subsidy sensitivity |
| fis_capex_cut | 0.5 | fixed | judgmental | share | Share of projected overrun closed by capex cuts under 'hold target' |
| food_fuel | 0.06 | 0.03-0.1 | judgmental | pp m/m per 1% retail fuel change | Transport-cost pass-through to food |
| food_rho | 0.7 | 0.55-0.85 | judgmental | AR(1) | Food supply shock persistence |
| food_sigma | 1.5 | fixed | judgmental | pp annualised per month | Food shock innovation sd |
| food_trend | 4.5 | fixed | judgmental | % annual | Food inflation trend |
| fpi_base | -1.7 | fixed | illustrative | USD bn/month | FPI intercept (calibrated so t0 FPI = -3.2 at central fpi_risk) |
| fpi_dep | 0.8 | 0.2-1.5 | judgmental | USD bn per %/month expected depreciation | Momentum / expectations channel |
| fpi_gap | 0.5 | fixed | judgmental | USD bn per 1% gap | Growth attracts flows |
| fpi_risk | 1.5 | 0.8-2.5 | judgmental | USD bn per z risk-off | Risk-appetite sensitivity |
| fpi_spread | 1.2 | 0.5-2.0 | judgmental | USD bn per pp (India10Y-US10Y) | Yield-spread sensitivity |
| freight_base | 1.5 | fixed | illustrative | USD/bbl | Freight+insurance on landed crude |
| freight_disrupt | 1.5 | 0.5-3.0 | illustrative | USD/bbl | War-risk premium in disruption regime |
| fuel_budget_share | 0.06 | fixed | illustrative | share | Household fuel budget share |
| fx_depth | 3.0 | 1.5-6.0 | illustrative | USD bn per 1% move | Unabsorbed pressure needed to move INR 1% |
| fx_sigma | 0.8 | fixed | judgmental | % per month | Idiosyncratic INR noise |
| fy_issuance | 15.0 | fixed | illustrative | Rs lakh crore/yr | Gross borrowing repricing base |
| g10_exp | 0.4 | fixed | judgmental | pp per pp expectations | Inflation-expectations premium |
| g10_fis | 0.25 | fixed | judgmental | pp per pp GDP FD slippage | Supply/credibility premium |
| g10_kappa | 0.3 | fixed | judgmental | per month | 10Y adjustment speed |
| g10_repo | 0.6 | 0.4-0.8 | judgmental | pp per pp repo | 10Y pass-through of policy-rate changes (term structure) |
| g10_sigma | 0.06 | fixed | judgmental | pp per month | 10Y noise |
| g10_us | 0.25 | 0.1-0.4 | judgmental | pp per pp US10Y | US yield spillover |
| gap_rho | 0.88 | 0.82-0.92 | judgmental | AR(1) monthly | Output-gap persistence (QPM-type) |
| gap_sigma | 0.12 | fixed | judgmental | pp per month | Demand noise |
| gdem_rho | 0.9 | fixed | judgmental | AR(1) | Global demand gap persistence |
| gdem_sigma | 0.3 | fixed | judgmental | pp per month | Global demand gap innovation sd |
| gov_loss_tolerance | 1.0 | 0.5-1.5 | judgmental | Rs lakh crore cumulative | Adaptive rule: OMC loss tolerated before pass-through |
| imports_month | 66.8 | fixed | derived | USD bn/month | Import cover base (734/11 months) |
| lend_spread | 3.5 | fixed | illustrative | pp | Lending rate over WACR |
| liq_wacr | 0.12 | fixed | illustrative | pp per Rs lakh crore deficit | WACR sensitivity to liquidity (bounded by corridor) |
| litres_month | 13.5 | fixed | illustrative | bn litres/month | Petrol+diesel consumption |
| lpg_cyl_month | 20.0 | fixed | illustrative | crore cylinders/month | Domestic LPG refills |
| lpg_price | 853.0 | fixed | illustrative | Rs/cylinder | Domestic LPG retail (unverified) |
| mpc_fx_trigger | 2.0 | 1.5-3.0 | judgmental | % 3m depreciation | FX-defence rule trigger |
| mpc_gap_coef | 0.5 | fixed | judgmental | pp per pp growth gap | MPC reaction to growth gap |
| mpc_infl_coef | 1.0 | 0.7-1.5 | judgmental | pp per pp inflation gap | MPC reaction to inflation gap |
| nonoil_bal0 | -14.5 | fixed | illustrative | USD bn/month | Non-oil merchandise balance (residual from Q1 BoP) |
| nonoil_fx | 0.12 | 0.05-0.2 | judgmental | USD bn per 1% real depreciation (6m avg, lagged) | Non-oil balance response to real INR |
| nonoil_gap | 0.6 | fixed | judgmental | USD bn per 1% gap | Import demand from domestic activity |
| nonoil_gdem | 0.8 | 0.4-1.2 | judgmental | USD bn per pp gdem | Export response to world demand |
| oil_anchor | 82.0 | 70.0-92.0 | judgmental | USD/bbl | Brent anchor when no disruption regime |
| oil_disrupt_prem | 35.0 | 20.0-45.0 | judgmental | USD/bbl | Anchor premium while baseline disruption regime persists (t0 implies ~35) |
| oil_gdem_beta | 3.0 | 1.5-5.0 | judgmental | USD/bbl per pp gdem | Demand-driven oil anchor shift |
| oil_kappa | 0.15 | 0.08-0.25 | judgmental | per month | Brent mean reversion toward regime anchor (half-life ~4 months) |
| oil_sigma | 0.075 | 0.06-0.1 | external | log sd per month | Brent monthly volatility (calm); ~historical 7-10% |
| oil_sigma_stress | 0.11 | 0.08-0.14 | judgmental | log sd per month | Brent volatility in disruption regime |
| oil_t_df | 5 | fixed | judgmental | dof | Student-t tails on oil innovation (unit variance scaled) |
| omc_normal_margin | 2.0 | fixed | illustrative | Rs/litre | Margin OMCs target under full pass-through |
| onset_hazard | 0.01 | fixed | judgmental | prob per month | Probability a new disruption regime starts once ended |
| other_energy0 | 2.9 | fixed | illustrative | USD bn/month | LNG + LPG/product imports at t0 |
| other_energy_oilshare | 0.6 | fixed | illustrative | share | Share of other energy imports indexed to Brent |
| pot_growth | 6.5 | 6.0-7.0 | judgmental | % annual | Potential growth |
| prim0 | -3.5 | fixed | external | USD bn/month | Net primary income |
| prim_us | 0.15 | fixed | judgmental | USD bn per pp US10Y | Higher global yields raise income outgo |
| prod_vol0 | 5.5 | fixed | external | MMT/month | Petroleum product exports |
| r_neutral | 1.4 | 0.9-1.9 | judgmental | % real | Neutral real policy rate (range informed by RBI research, not verified here) |
| remit0 | 13.6 | fixed | external | USD bn/month | Net secondary income |
| remit_oil | 0.15 | 0.0-0.3 | judgmental | elasticity to Brent, 6m lag | Gulf income offset: higher oil raises remittances with lag |
| res_floor_months | 8.0 | 7.0-9.0 | judgmental | months of imports | Reserve level below which RBI scales back intervention |
| res_nonusd_share | 0.25 | fixed | judgmental | share | Non-USD reserve share for valuation effects |
| resid_other0 | -3.8 | fixed | illustrative | USD bn/month | Residual capital incl. errors & omissions (explicit plug to Q1 BoP) |
| risk_rho | 0.8 | fixed | judgmental | AR(1) | Risk-off persistence |
| risk_sigma | 0.45 | fixed | judgmental | z per month | Risk-off innovation sd |
| services0 | 17.2 | fixed | external | USD bn/month | Net services |
| services_gdem | 0.25 | fixed | judgmental | USD bn per pp gdem | Services exports vs world demand |
| stress_gap | 0.05 | fixed | judgmental | per 1% negative gap | Cash-flow stress |
| stress_rate | 0.04 | fixed | judgmental | per pp real lending rate above t0 | Debt-service stress |
| stress_rho | 0.92 | fixed | judgmental | AR(1) | Credit-stress persistence |
| tax_buoy | 1.1 | fixed | judgmental | elasticity | Tax buoyancy |
| tax_ratio | 0.073 | fixed | derived | share of nominal GDP | Net tax / NGDP (28.7/393) |
| us_anchor | 4.6 | 4.0-5.2 | judgmental | % | US10Y long-run anchor |
| us_kappa | 0.05 | fixed | judgmental | per month | US10Y mean reversion |
| us_sigma | 0.15 | fixed | external | pp per month | US10Y monthly sd (historical order of magnitude) |
| vat_rate | 0.177 | fixed | illustrative | share | Blended Delhi VAT (ad valorem) |
| vol_elast_act | 1.0 | fixed | judgmental | elasticity | Crude volume vs activity gap |
| vol_elast_price | -0.02 | -0.06-0.0 | judgmental | elasticity | Short-run price elasticity of crude import volume |
| w_core | 0.55 | fixed | illustrative | weight | CPI core |
| w_energy | 0.08 | fixed | illustrative | weight | CPI energy incl. petrol/diesel/LPG |
| w_food | 0.37 | fixed | illustrative | weight | CPI food weight (base-2024 weights not verified) |

## Mechanisms (implemented)

| id | from -> to | kind | lag | description |
|---|---|---|---|---|
| M-OIL-01 | disrupt, esc, shock_oil_escalation, shock_oil_deescalation -> brent | judgmental | 0 | Supply-disruption regime raises the Brent anchor; Brent mean-reverts toward it (faster in a regime-change month). |
| M-OIL-02 | gdem -> brent | judgmental | 0 | Demand-driven oil move: weaker world demand lowers the anchor. |
| M-OIL-03 | disrupt, esc -> crack | illustrative | 0 | Disruption widens product cracks and war-risk freight. |
| M-OIL-04 | esc -> shortfall | illustrative | 0 | Escalation scenario imposes a physical crude shortfall during its forced window. |
| M-GLB-01 | shock_global_tightening, shock_oil_escalation, disrupt, esc -> risk_off | judgmental | 0 | Risk-off: elevated while a disruption regime lasts; scenario impulses add to it; AR(1) with correlated innovations. |
| M-GLB-02 | shock_global_tightening -> us10y | judgmental | 0 | US10Y mean-reverts to an anchor; scenario offsets shift it. |
| M-GLB-03 | shock_global_tightening -> gdem | judgmental | 0 | World demand gap AR(1) with scenario offsets. |
| M-GLB-04 | shock_food_supply -> food_shock | judgmental | 0 | Food supply shock AR(1); starts from the Sep-2026 food spike and decays. |
| M-EXT-01 | brent, freight, crude_vol -> crude_bill | identity | 0 | USD crude import bill = volume x bbl/tonne x (Brent + freight). Independent of INR. |
| M-EXT-02 | brent, crack -> prod_exp | identity | 0 | Product exports rise with Brent and cracks: an offset to gross crude cost. |
| M-EXT-03 | brent -> other_energy | illustrative | 0 | LNG/LPG/product imports partly oil-indexed. |
| M-EXT-04 | crude_bill, prod_exp, other_energy -> oil_net | identity | 0 | Net oil balance = product exports - crude imports - other energy imports. |
| M-EXT-05 | gdem, inr, gap -> nonoil_bal | judgmental | 1 | Non-oil goods balance improves with world demand and (lagged) real depreciation; worsens with domestic activity. |
| M-EXT-06 | gdem -> services | judgmental | 0 | Services exports track world demand. |
| M-EXT-07 | brent -> remit | judgmental | 6 | OFFSET: higher oil raises Gulf incomes and remittances with a ~6-month lag. Weakened if the conflict disrupts Gulf economies. |
| M-EXT-08 | us10y -> prim_inc | judgmental | 0 | Higher global yields raise income outgo. |
| M-EXT-09 | oil_net, nonoil_bal, services, remit, prim_inc -> ca | identity | 0 | Current account = oil net + non-oil goods + services + secondary income + primary income. |
| M-CAP-01 | g10, us10y, risk_off, inr, gap, gdem -> fpi | judgmental | 1 | Portfolio flows respond to the yield spread, risk appetite, recent depreciation (momentum) and growth. |
| M-CAP-02 | us10y -> ecb_other | judgmental | 0 | External borrowing deterred by higher US yields. |
| M-CAP-03 | fpi, ecb_other -> ka | identity | 0 | Capital account = FDI + FPI + ECB/other + residual (explicit plug incl. errors & omissions). |
| M-FX-01 | ca, ka -> pressure | identity | 0 | Ex-ante FX pressure = -(CA + KA). A larger CAD is pressure only if not financed. |
| M-FX-02 | pressure, reserves -> interv | rule | 0 | RBI absorbs a share of pressure (intensity choice), scaled down near the reserve floor. |
| M-FX-03 | pressure, interv, dxy -> inr | illustrative | 0 | Unabsorbed pressure moves INR by 1% per fx_depth USD bn, plus dollar-index pass-through and noise. |
| M-FX-04 | interv, dxy -> reserves | identity | 0 | Reserves change = -intervention (BoP) + valuation effect from the dollar. |
| M-FX-05 | pressure, interv -> fx_adjust | identity | 0 | BoP closure: price-induced balancing flows equal unabsorbed pressure so CA + KA + adjustment = change in reserves. |
| M-LIQ-01 | interv -> liq | identity | 0 | Dollar sales drain rupee liquidity one-for-one; sterilisation (OMO/VRR/swaps) offsets a chosen share. |
| M-LIQ-02 | liq, repo -> wacr | rule | 0 | Overnight rate (WACR) moves within the SDF-MSF corridor with liquidity. |
| M-FUEL-01 | brent, crack, freight, inr -> parity | identity | 0 | Import-parity cost of auto fuel (Rs/litre) = (Brent + crack + freight) x INR / 159. |
| M-FUEL-02 | parity -> retail_fuel | rule | 0 | Government/OMC pricing choice sets the retail price, excise and any budget compensation. |
| M-FUEL-03 | retail_fuel, excise, parity -> omc_margin | identity | 0 | OMC margin = retail/(1+VAT) - dealer margin - excise - parity cost; losses = shortfall x volume. |
| M-FUEL-04 | brent, inr -> lpg_loss | illustrative | 0 | LPG under-recovery at a frozen cylinder price. |
| M-PRC-01 | retail_fuel -> energy_yoy | identity | 0 | Energy CPI moves with retail auto-fuel prices (share) plus administered items trend. |
| M-PRC-02 | food_shock, retail_fuel -> food_yoy | judgmental | 0 | Food inflation = trend + supply shock + transport-cost pass-through. |
| M-PRC-03 | exp_infl, gap, inr, parity -> core_yoy | external | 1 | Core inflation: persistence + expectations + Phillips slope + ERPT + indirect oil costs. |
| M-PRC-04 | food_yoy, energy_yoy, core_yoy -> cpi_yoy | identity | 0 | Headline CPI = weighted components (weights approximate). |
| M-PRC-05 | cpi_yoy -> exp_infl | judgmental | 1 | Adaptive expectations; speed jumps if headline >6% for 3 months (de-anchoring regime) under the 'adaptive' structure. |
| M-MPC-01 | cpi_yoy, gdp_yoy, exp_infl, inr -> repo | rule | 2 | MPC decides at bi-monthly meetings using only PUBLISHED data (CPI with 2-month availability lag, GDP quarterly +2 months). |
| M-FIS-01 | brent, omc_margin, excise, gap -> fd_proj | identity | 0 | Fiscal deficit = expenditure (base + fertiliser + interest + OMC compensation - capex cuts) - receipts (tax + fuel excise + other). |
| M-FIS-02 | fd_proj -> capex_cut | rule | 1 | Under 'hold target', projected overrun is half-closed by capex cuts (capped at 25% of monthly capex). |
| M-FIS-03 | fd_proj -> debt | identity | 0 | Debt stock accumulates the deficit (no valuation, no states). |
| M-BOND-01 | repo, us10y, fd_proj, exp_infl -> g10 | judgmental | 0 | 10Y yield adjusts toward repo + term premium + US spillover + fiscal + expectations premia. |
| M-REAL-01 | wacr, exp_infl -> gap | judgmental | 3 | Higher real rates (vs t0) lower the output gap after ~3 months. |
| M-REAL-02 | retail_fuel -> gap | judgmental | 0 | Retail fuel increases squeeze household real income (one-off impulse that decays). |
| M-REAL-03 | omc_margin, lpg_loss -> gap | judgmental | 0 | Uncompensated OMC losses (vs t0) defer PSU capex. |
| M-REAL-04 | parity -> gap | judgmental | 0 | Firms' input-cost squeeze from landed crude in rupees. |
| M-REAL-05 | gdem -> gap | judgmental | 0 | External demand. |
| M-REAL-06 | risk_off -> gap | judgmental | 0 | Confidence / financial conditions. |
| M-REAL-07 | stress -> gap | judgmental | 0 | Credit supply tightening. |
| M-REAL-08 | food_shock -> gap | judgmental | 0 | Rural real-income squeeze from food prices. |
| M-REAL-09 | capex_cut -> gap | judgmental | 0 | Capex cuts lower demand (multiplier ~2.5 at central values). |
| M-REAL-10 | shortfall -> gap | judgmental | 0 | Physical fuel rationing. |
| M-REAL-11 | gap -> gdp_yoy | identity | 0 | Monthly activity index = potential x (1+gap); quarterly GDP y/y = 3-month average vs year-ago (explicit aggregation). |
| M-CRD-01 | wacr, gap, stress -> credit_yoy | judgmental | 0 | Credit growth vs lending rate, activity and bank stress. |
| M-CRD-02 | wacr, exp_infl, gap -> stress | judgmental | 0 | Debt-service stress rises with real lending rates and negative gaps (nonlinear: only negative gap). |
| M-PUB-01 | cpi_yoy, gdp_yoy -> published | rule | 2 | Publication calendar: CPI usable by decisions from month m+2; quarterly GDP from quarter-end +3; market data from m+1. |

## Not implemented (visible gaps)

- G-01: Employment / labour market: only an activity proxy exists.
- G-02: State VAT choices and state fiscal positions.
- G-03: China trade diversion, tariffs, supply chains.
- G-04: Bank MTM losses, NIM, capital; insurance and NBFC balance sheets.
- G-05: Sector heterogeneity and equity markets.
- G-06: Monsoon -> agricultural output (only via prices).
- G-07: Strategic OPEC+/SPR responses (only via hazard rates).
- G-08: Gold imports response to INR and uncertainty.
- G-09: RBI forward book / NDF market; only spot intervention modelled.
- G-10: Wage indexation and firm expectations.

## Evidence register

evidence_id,item,value,unit,observation_period,publisher,source_title,url,publication_date,retrieval_date,kind,frequency,used_for,limitations  
E01,Repo rate after 63rd MPC,5.50,% p.a.,2026-10-07,SCC Online (reporting RBI MPS),RBI hikes repo rate to 5.50%; shifts policy stance to calibrated tightening,https://www.scconline.com/blog/post/2026/10/09/rbi-hikes-repo-rate-to-5-50-percent-october-2026/,2026-10-09,2026-10-25,reported actual,event,baseline repo; SDF 5.25; MSF 5.75; stance,secondary report of RBI statement; primary RBI MPS not opened  
E02,RBI CPI projection FY27 / Q3 / Q4,5.2 / 6.0 / 5.7,% y/y,FY2026-27,SCC Online (reporting RBI MPS),same as E01,https://www.scconline.com/blog/post/2026/10/09/rbi-hikes-repo-rate-to-5-50-percent-october-2026/,2026-10-09,2026-10-25,official forecast,quarterly,benchmark only (not a model input),official forecast not an actual  
E03,RBI GDP projection FY27 / Q3 / Q4,7.1 / 6.9 / 6.8,% y/y,FY2026-27,SCC Online (reporting RBI MPS),same as E01,https://www.scconline.com/blog/post/2026/10/09/rbi-hikes-repo-rate-to-5-50-percent-october-2026/,2026-10-09,2026-10-25,official forecast,quarterly,benchmark only,official forecast  
E04,Current account deficit Q1 FY27,-4.2 (0.5% GDP),USD bn per quarter,2026-04 to 2026-06,Reserve Bank of India,Developments in India's Balance of Payments during Q1 2026-27,https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63493,2026-09-01,2026-10-25,reported actual (preliminary),quarterly,calibrating CA components (monthly = quarter/3),preliminary; no seasonality adjustment in model  
E05,Merchandise trade deficit Q1 FY27,-86.1,USD bn per quarter,2026-04 to 2026-06,Reserve Bank of India,same as E04,https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63493,2026-09-01,2026-10-25,reported actual (preliminary),quarterly,non-oil balance derived as residual,oil split not in release  
E06,Net services receipts Q1 FY27,51.6,USD bn per quarter,2026-04 to 2026-06,Reserve Bank of India,same as E04,https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63493,2026-09-01,2026-10-25,reported actual (preliminary),quarterly,services baseline 17.2/month,  
E07,Net secondary income (mainly remittances) Q1 FY27,40.8,USD bn per quarter,2026-04 to 2026-06,Reserve Bank of India,same as E04,https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63493,2026-09-01,2026-10-25,reported actual (preliminary),quarterly,remittance baseline 13.6/month,gross personal transfers 42.9  
E08,Net primary income Q1 FY27,-10.5,USD bn per quarter,2026-04 to 2026-06,Reserve Bank of India,same as E04,https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63493,2026-09-01,2026-10-25,reported actual (preliminary),quarterly,primary income baseline -3.5/month,  
E09,Capital flows Q1 FY27: FDI 6.1 / FPI -9.6 / ECB 3.3 / other investment 7.7 / reserves -8.1,see value,USD bn per quarter,2026-04 to 2026-06,Reserve Bank of India,same as E04,https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=63493,2026-09-01,2026-10-25,reported actual (preliminary),quarterly,capital account baseline; residual other capital is an explicit plug,banking capital and E&O not separately read  
E10,Forex reserves week ended 2 Oct 2026,734.6,USD bn,2026-10-02,Trading Economics / Business Today (citing RBI WSS),India's FX Reserves Fall for Fourth Week,https://tradingeconomics.com/india/foreign-exchange-reserves/news/590126,2026-10,2026-10-25,reported actual,weekly,reserves starting stock,secondary; ~USD 51bn fall from 4 Sep peak includes valuation  
E11,INR/USD close 7 Oct 2026,96.78,INR per USD,2026-10-07,The Pioneer (PTI),Rupee slumps 43 paise to close at 96.78 against US dollar,https://dailypioneer.com/news/slug-lite/rupee-slumps-43-paise-to-close-at-96-78-against-us-dollar?year=2026,2026-10-08,2026-10-25,reported actual (provisional),daily,INR starting level (97.0 used for late Oct),late-October close not verified; record low 96.97 in May 2026 per Business Today  
E12,FPI equity outflows 2026 YTD,~-30,USD bn,2026-01 to 2026-10,Business Today,Rupee near record low: why RBI's multiple defences are losing effectiveness,https://www.businesstoday.in/latest/economy/story/rupee-near-record-low-why-rbis-multiple-defences-are-losing-effectiveness-560381-2026-10-08,2026-10-08,2026-10-25,reported estimate,annual-to-date,FPI baseline outflow ~-3/month,secondary  
E13,CPI headline / food Sep 2026 (base 2024),5.54 / 7.74,% y/y,2026-09,Business Today (citing MoSPI),India's retail inflation rises to 5.54% in September; food inflation hits 7.74%,https://www.businesstoday.in/latest/economy/story/indias-retail-inflation-rises-to-5-54-in-september-food-inflation-hits-7-74-561057-2026-10-12,2026-10-12,2026-10-25,reported actual,monthly,starting CPI components,MoSPI PDF blocked by robots; core not reported; base-2024 weights not verified  
E14,Real GDP growth Q1 FY27,7.8,% y/y,2026-04 to 2026-06,News On AIR (citing MoSPI/NSO),India's real GDP growth rate rises to 7.8% in Q1 FY2026-27,https://newsonair.gov.in/indias-real-gdp-growth-rate-rises-to-7-8-in-first-quarter-of-fy-2026-27/,2026-08-31,2026-10-25,reported actual (first estimate),quarterly,starting output gap judgement (+0.3%),gap is model judgement not data  
E15,Brent settle 23 Oct 2026,116.72,USD/bbl,2026-10-23,Rio Times / CNBC headline,Brent crude settles at US$116.72; six-month high on Houthi attacks in Saudi Arabia,https://www.riotimesonline.com/oil-markets-latam-friday-october-23-2026,2026-10-23,2026-10-25,reported market price,daily,starting Brent,CNBC page not retrievable; value consistent across 3 headlines  
E16,2026 oil market chronology (Iran war; Hormuz; peak $126 intraday 30 Apr),see value,USD/bbl,2026-03 to 2026-06,Wikipedia,2026-2028 world oil market chronology,https://en.wikipedia.org/wiki/2026%E2%80%932028_world_oil_market_chronology,n/a,2026-10-25,secondary compilation,daily,approximate Brent pre-history (Apr-Jun),tertiary source; Jul-Oct not covered  
E17,India 10Y G-sec yield,7.46,%,2026-10-23,Trading Economics,India 10Y Yield news stream,https://tradingeconomics.com/india/government-bond-yield/news/587153,2026-10-23,2026-10-25,reported market price,daily,starting 10Y yield,secondary  
E18,US 10Y Treasury yield,~5.2,%,2026-09-28,Trading Economics,India 10Y Yield Hits Near 2-Year High,https://tradingeconomics.com/india/government-bond-yield/news/587153,2026-09-28,2026-10-25,reported market price,daily,starting US10Y,one month stale; not verified for late Oct  
E19,Crude imports July 2026 (PPAC provisional): 21.4 MMT / USD 13.7bn; product exports 5.5 MMT / USD 5.0bn; LNG USD 1.2bn; net oil & gas USD 11.2bn; import dependency 88.5%,see value,MMT; USD bn per month,2026-07,Angel One (citing Business Standard / PPAC),India's crude import bill climbs 41% to $13.7 billion in July 2026,https://www.angelone.in/news/economy/india-s-crude-import-bill-climbs-41-to-13-7-billion-in-july-2026-amid-higher-oil-prices,2026-08-20,2026-10-25,reported actual (provisional),monthly,crude/product volumes; bbl conversion check,PPAC primary not opened  
E20,Excise cut on petrol and diesel 27 Mar 2026: Rs10/l; petrol Rs13->3; diesel ->0,see value,Rs/litre,2026-03-27,Vision IAS,India cuts excise duty on petrol and diesel,https://visionias.in/blog/current-affairs/india-cuts-excise-duty-on-petrol-and-diesel-what-it-means-for-fuel-prices,2026-03,2026-10-25,reported policy,event,excise headroom constraint (near-exhausted),secondary  
E21,OMC marketing losses: petrol -8/l; diesel -9/l; LPG ~-300/cylinder; ~Rs 5.3bn/day; Indian basket 117.4 on 21 Sep 2026,see value,Rs/litre,2026-09,Construction World (citing ICRA),OMCs face Rs 5.3 bn daily loss as fuel prices stay unchanged,https://www.constructionworld.in/policy-updates-and-economic-news/omcs-face-rs.-5.3-bn-daily-loss-as-fuel-prices-stay-unchanged/97761,2026-09-26,2026-10-25,researcher estimate (ICRA),monthly,calibrates starting OMC margin (-8.5/l) and LPG loss,estimate; cost structure approximated  
E22,Retail fuel Delhi 17 Oct 2026: petrol 102.12; diesel 95.20 (Mumbai 111.21 / 97.83),see value,Rs/litre,2026-10-17,The Hans India,Petrol and diesel prices today ... 17 October 2026,https://www.thehansindia.com/business/market-compass/petrol-and-diesel-prices-today-in-hyderabad-delhi-chennai-and-mumbai-on-17-october-2026-1133197,2026-10-17,2026-10-25,reported price,daily,starting representative retail price (Delhi blend),VAT rates approximated  
E23,Union Budget FY27: fiscal deficit 4.3% GDP; total expenditure Rs53.5 lakh cr; net tax Rs28.7 lakh cr; debt/GDP 55.6%,see value,% GDP; Rs lakh crore,FY2026-27 BE,Scroll.in,Budget 2026: Fiscal deficit estimated to be 4.3% of GDP in 2026-27,https://scroll.in/latest/1090412/scroll_in,2026-02-01,2026-10-25,official budget estimate,annual,fiscal baseline run-rate,nominal GDP BE not read; Rs393 lakh cr is an approximation  
E24,Oil shock effects at USD10/bbl: CPI +49 to 106 bp (pass-through dependent); CAD +USD12.5bn (~0.43% GDP); fiscal up to 0.43% GDP at zero pass-through,see value,bp; USD bn; % GDP,2014-2018 data,RBI Mint Street Memo 17 (Ghosh & Tomar),The Impact of Crude Price Shock on India's CAD Inflation and Fiscal Deficit,https://rbi.org.in/Scripts/MSM_Mintstreetmemos17.aspx,2019-01-04,2026-10-25,researcher estimate,n/a,validation benchmarks for oil channel (tests),2019 vintage; volumes and tax structure since changed  
E25,Oil-inflation pass-through: 10% oil -> ~20bp headline (contemporaneous; managed pump prices); QPM2.0 peak ~30bp incl FX; core response stronger than headline,see value,bp,2009Q3-2024Q3,RBI Bulletin (Kundu Tewari Bhattacharyya),Revisiting the Oil Price and Inflation Nexus in India,https://www.rbi.org.in/Scripts/BS_ViewBulletin.aspx?Id=23516,2025-07-23,2026-10-25,researcher estimate,quarterly,validation benchmark under managed pricing (tests),reflects managed-price regime; not transferable to full pass-through  
E26,Methodology: structured analytic techniques (key assumptions; ACH; indicators; premortem/red team),n/a,n/a,n/a,CIA Center for the Study of Intelligence,A Tradecraft Primer (2009),https://www.cia.gov/resources/csi/static/Tradecraft-Primer-apr09.pdf,2009-03,not opened this session,method reference,n/a,design of analyst tools,not opened in this session; cited from brief  
E27,Methodology: wargaming adjudication and red teaming,n/a,n/a,n/a,UK Ministry of Defence,Defence Wargaming Handbook,https://www.gov.uk/government/publications/defence-wargaming-handbook,n/a,not opened this session,method reference,n/a,adjudication labelling design,not opened in this session; cited from brief  
