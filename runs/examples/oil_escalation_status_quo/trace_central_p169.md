# central (P50 severity) path

Run `7d5d0c2ca78b` | path 169 | scenario `oil_escalation` | seed 20261025 | engine 0.3.0 | params params-0.3.0

> EXPLORATORY SCENARIO PATH generated from the run log. No probability is attached to this single path.


## 2026-11

- **[shock]** 2026-11: Scenario shock: Hormuz escalation. Anchor +USD40/bbl, freight +6, cracks +8, 3% physical shortfall for 3 months; then 20%/month chance of ending. Type: SUPPLY disruption..
  - id `2313560ef632:p169:t01:shock:oil_escalation:1`; parents 0; support: n/a (assumption)
- **[regime]** 2026-11: Escalation layer (Hormuz) starts. Mechanism: M-OIL-01.
  - id `2313560ef632:p169:t01:regime:esc:2`; parents 1; support: Low-Medium (judgmental hazard)
- **[state_change]** 2026-11: Brent crude rises to 136.2 USD/bbl (from 116.7 in 2026-10). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - id `2313560ef632:p169:t01:state:brent:3`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2026-11: Crude import bill rises to 21.93 USD bn/month (from 18.69 in 2026-10). Main drivers: price (Brent+freight) +3.94, volume -0.70 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t01:state:crude_bill:4`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-11: Petroleum product exports rises to 7.06 USD bn/month (from 5.91 in 2026-10). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t01:state:prod_exp:5`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-11: Net oil balance falls to -18.06 USD bn/month (from -15.68 in 2026-10). Main drivers: crude_bill -3.24, prod_exp +1.15, other_energy -0.29 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t01:state:oil_net:6`; parents 2; support: High (arithmetic)
- **[state_change]** 2026-11: Current account balance falls to -5.71 USD bn/month (from -2.88 in 2026-10). Main drivers: oil_net -2.38, nonoil_bal -0.32, services -0.11 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t01:state:ca:7`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-11: Portfolio flows (FPI) falls to -3.68 USD bn/month (from -2.52 in 2026-10). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t01:state:fpi:8`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2026-11: Capital account falls to -1.79 USD bn/month (from -0.62 in 2026-10). Main drivers: fpi -1.16, ecb_other -0.01, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t01:state:ka:9`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-11: FX pressure (excess USD demand) rises to 7.49 USD bn/month (from 3.50 in 2026-10). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t01:state:pressure:10`; parents 2; support: High (arithmetic)
- **[decision]** 2026-11: RBI sells USD 5.6bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(7.49), 'Reserves prior (USD bn)': np.float64(734.6)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.56 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t01:decision:fx:11`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2026-11: INR per USD rises to 99.39 INR/USD (from 97.00 in 2026-10). Main drivers: unabsorbed pressure +1.07, dollar index +0.69, noise +0.67 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t01:state:inr:12`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2026-11: FX reserves falls to 724.73 USD bn (from 734.60 in 2026-10). Main drivers: intervention (BoP) -5.62, valuation -4.25 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t01:state:reserves:13`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-11: Fuel import-parity cost rises to 110.9 Rs/litre (from 87.7 in 2026-10). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t01:state:parity:14`; parents 2; support: High (arithmetic)
- **[decision]** 2026-11: Fuel pricing: Freeze retail; OMCs absorb losses (status quo Oct 2026). Retail +0.00 Rs/l, excise +0.00 Rs/l, Budget compensation Rs0 crore. Mechanism: M-FUEL-02.
  - Observed: {'Import parity (Rs/l)': np.float64(110.87), 'OMC margin if frozen (Rs/l)': np.float64(-32.78), 'Cumulative net OMC loss (Rs lakh cr)': np.float64(0.0)} | Choices: ['full_passthrough', 'freeze_omc_absorb', 'freeze_budget_comp', 'partial_50', 'excise_cut', 'adaptive_threshold'] | Chosen: freeze_omc_absorb | Constraints: excise floor 0 (headroom ~Rs1/l blended after Mar-2026 cut); LPG frozen in all options
  - Expected response: CPI insulated; OMC balance sheets absorb losses; PSU capex at risk.
  - id `2313560ef632:p169:t01:decision:gov_fuel:15`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2026-11: OMC marketing margin falls to -32.8 Rs/litre (from -9.7 in 2026-10). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t01:state:omc_margin:16`; parents 2; support: High (arithmetic)
- **[state_change]** 2026-11: Output gap falls to -0.61 % of potential (from 0.30 in 2026-10). Main drivers: phys -0.45, input -0.23, noise -0.06 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t01:state:gap:17`; parents 3; support: Low-Medium (judgmental)

## 2026-12

- **[publication]** 2026-12: CPI for 2026-11 published: headline 5.52%, food 7.73%, core 4.47%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t02:pub:cpi:18`; parents 0; support: High (calendar)
- **[decision]** 2026-12: MPC hikes repo 25bp to 5.75% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(5.51), 'Core CPI (latest published)': np.float64(4.43), 'Expectations (%)': np.float64(5.03), 'GDP (latest published, % y/y)': np.float64(7.5), '3m INR depreciation (%)': np.float64(2.43)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t02:decision:mpc:19`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2026-12: Brent crude rises to 151.2 USD/bbl (from 136.2 in 2026-11). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - id `2313560ef632:p169:t02:state:brent:20`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2026-12: Crude import bill rises to 23.91 USD bn/month (from 21.93 in 2026-11). Main drivers: price (Brent+freight) +2.25, volume -0.27 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t02:state:crude_bill:21`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-12: Petroleum product exports rises to 7.69 USD bn/month (from 7.06 in 2026-11). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t02:state:prod_exp:22`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-12: Net oil balance falls to -19.64 USD bn/month (from -18.06 in 2026-11). Main drivers: crude_bill -1.98, prod_exp +0.63, other_energy -0.22 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t02:state:oil_net:23`; parents 2; support: High (arithmetic)
- **[state_change]** 2026-12: Current account balance falls to -7.23 USD bn/month (from -5.71 in 2026-11). Main drivers: oil_net -1.58, nonoil_bal +0.26, remit -0.12 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t02:state:ca:24`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-12: Portfolio flows (FPI) falls to -5.42 USD bn/month (from -3.68 in 2026-11). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t02:state:fpi:25`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2026-12: Capital account falls to -3.49 USD bn/month (from -1.79 in 2026-11). Main drivers: fpi -1.75, ecb_other +0.04, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t02:state:ka:26`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-12: FX pressure (excess USD demand) rises to 10.72 USD bn/month (from 7.49 in 2026-11). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t02:state:pressure:27`; parents 2; support: High (arithmetic)
- **[decision]** 2026-12: RBI sells USD 8.0bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(10.72), 'Reserves prior (USD bn)': np.float64(724.7)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.82 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t02:decision:fx:28`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2026-12: INR per USD rises to 101.47 INR/USD (from 99.39 in 2026-11). Main drivers: unabsorbed pressure +1.53, dollar index +0.76, noise -0.21 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t02:state:inr:29`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2026-12: FX reserves falls to 712.11 USD bn (from 724.73 in 2026-11). Main drivers: intervention (BoP) -8.04, valuation -4.58 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t02:state:reserves:30`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-12: Banking liquidity falls to 0.31 Rs lakh crore (from 1.00 in 2026-10). Mechanism: M-LIQ-01.
  - id `2313560ef632:p169:t02:state:liq:31`; parents 1; support: High (arithmetic)
- **[state_change]** 2026-12: Overnight rate (WACR) rises to 5.71 % (from 5.38 in 2026-10). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t02:state:wacr:32`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2026-12: Fuel import-parity cost rises to 122.7 Rs/litre (from 110.9 in 2026-11). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t02:state:parity:33`; parents 2; support: High (arithmetic)
- **[state_change]** 2026-12: OMC marketing margin falls to -44.7 Rs/litre (from -32.8 in 2026-11). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t02:state:omc_margin:34`; parents 2; support: High (arithmetic)
- **[state_change]** 2026-12: Output gap falls to -1.19 % of potential (from -0.61 in 2026-11). Main drivers: phys -0.38, input -0.09, omc -0.07 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t02:state:gap:35`; parents 4; support: Low-Medium (judgmental)
- **[state_change]** 2026-12: Credit stress index rises to 0.10 index (from 0.00 in 2026-10). Mechanism: M-CRD-02.
  - id `2313560ef632:p169:t02:state:stress:36`; parents 2; support: Low-Medium (judgmental)

## 2027-01

- **[publication]** 2027-01: CPI for 2026-12 published: headline 5.48%, food 7.44%, core 4.60%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t03:pub:cpi:37`; parents 0; support: High (calendar)
- **[decision]** 2027-01: RBI sells USD 8.1bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(10.78), 'Reserves prior (USD bn)': np.float64(712.1)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.81 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t03:decision:fx:38`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-01: INR per USD falls to 100.53 INR/USD (from 101.47 in 2026-12). Main drivers: noise -2.16, unabsorbed pressure +1.54, dollar index -0.30 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t03:state:inr:39`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-01: FX reserves falls to 705.80 USD bn (from 712.11 in 2026-12). Main drivers: intervention (BoP) -8.09, valuation +1.78 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t03:state:reserves:40`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-01: Banking liquidity falls to -0.09 Rs lakh crore (from 0.31 in 2026-12). Mechanism: M-LIQ-01.
  - id `2313560ef632:p169:t03:state:liq:41`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-01: Food inflation falls to 7.24 % y/y (from 7.74 in 2026-10). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - id `2313560ef632:p169:t03:state:food_yoy:42`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2027-01: Core inflation rises to 4.87 % y/y (from 4.43 in 2026-10). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t03:state:core_yoy:43`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2027-01: Output gap falls to -1.53 % of potential (from -1.19 in 2026-12). Main drivers: phys -0.31, omc -0.06, input +0.05 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t03:state:gap:44`; parents 5; support: Low-Medium (judgmental)
- **[state_change]** 2027-01: 10Y G-sec yield rises to 7.62 % (from 7.46 in 2026-10). Mechanism: M-BOND-01. Could be interrupted by: Issuance cuts; RBI OMO purchases.
  - id `2313560ef632:p169:t03:state:g10:45`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2027-01: Credit stress index rises to 0.18 index (from 0.10 in 2026-12). Mechanism: M-CRD-02.
  - id `2313560ef632:p169:t03:state:stress:46`; parents 2; support: Low-Medium (judgmental)

## 2027-02

- **[publication]** 2027-02: CPI for 2027-01 published: headline 5.54%, food 7.24%, core 4.87%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t04:pub:cpi:47`; parents 0; support: High (calendar)
- **[publication]** 2027-02: GDP for quarter ending 2026-12 published: 6.57% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t04:pub:gdp:48`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[decision]** 2027-02: MPC hikes repo 25bp to 6.00% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(5.48), 'Core CPI (latest published)': np.float64(4.6), 'Expectations (%)': np.float64(5.07), 'GDP (latest published, % y/y)': np.float64(7.5), '3m INR depreciation (%)': np.float64(3.58)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t04:decision:mpc:49`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-02: Crude import bill rises to 25.01 USD bn/month (from 23.91 in 2026-12). Main drivers: price (Brent+freight) +0.60, volume +0.50 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t04:state:crude_bill:50`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-02: Net oil balance falls to -20.63 USD bn/month (from -19.64 in 2026-12). Main drivers: crude_bill -1.10, prod_exp +0.17, other_energy -0.06 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t04:state:oil_net:51`; parents 2; support: High (arithmetic)
- **[decision]** 2027-02: RBI sells USD 8.0bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(10.61), 'Reserves prior (USD bn)': np.float64(705.8)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.81 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t04:decision:fx:52`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-02: INR per USD rises to 102.30 INR/USD (from 100.53 in 2027-01). Main drivers: unabsorbed pressure +1.51, noise +0.12, dollar index +0.10 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t04:state:inr:53`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-02: FX reserves falls to 697.23 USD bn (from 705.80 in 2027-01). Main drivers: intervention (BoP) -7.96, valuation -0.62 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t04:state:reserves:54`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-02: Banking liquidity falls to -0.50 Rs lakh crore (from -0.09 in 2027-01). Mechanism: M-LIQ-01.
  - id `2313560ef632:p169:t04:state:liq:55`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-02: Overnight rate (WACR) rises to 6.06 % (from 5.71 in 2026-12). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t04:state:wacr:56`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-02: OMC marketing margin falls to -48.2 Rs/litre (from -44.7 in 2026-12). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t04:state:omc_margin:57`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-02: Core inflation rises to 5.21 % y/y (from 4.87 in 2027-01). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t04:state:core_yoy:58`; parents 3; support: Medium (benchmarked to published estimates)

## 2027-03

- **[publication]** 2027-03: CPI for 2027-02 published: headline 5.57%, food 6.83%, core 5.21%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t05:pub:cpi:59`; parents 0; support: High (calendar)
- **[state_change]** 2027-03: Brent crude rises to 165.6 USD/bbl (from 151.2 in 2026-12). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t05:state:brent:60`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-03: Crude import bill rises to 26.60 USD bn/month (from 25.01 in 2027-02). Main drivers: price (Brent+freight) +1.59, volume +0.00 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t05:state:crude_bill:61`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-03: Petroleum product exports rises to 8.29 USD bn/month (from 7.69 in 2026-12). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t05:state:prod_exp:62`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-03: Net oil balance falls to -21.94 USD bn/month (from -20.63 in 2027-02). Main drivers: crude_bill -1.59, prod_exp +0.43, other_energy -0.15 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t05:state:oil_net:63`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-03: Current account balance falls to -8.99 USD bn/month (from -7.23 in 2026-12). Main drivers: oil_net -2.30, nonoil_bal +0.41, remit +0.15 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t05:state:ca:64`; parents 1; support: High (arithmetic)
- **[decision]** 2027-03: RBI sells USD 8.8bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(11.71), 'Reserves prior (USD bn)': np.float64(697.2)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.91 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t05:decision:fx:65`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-03: INR per USD rises to 103.48 INR/USD (from 102.30 in 2027-02). Main drivers: unabsorbed pressure +1.67, noise -0.30, dollar index -0.21 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t05:state:inr:66`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-03: FX reserves falls to 689.69 USD bn (from 697.23 in 2027-02). Main drivers: intervention (BoP) -8.78, valuation +1.24 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t05:state:reserves:67`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-03: Banking liquidity falls to -0.95 Rs lakh crore (from -0.50 in 2027-02). Mechanism: M-LIQ-01.
  - id `2313560ef632:p169:t05:state:liq:68`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-03: Fuel import-parity cost rises to 134.5 Rs/litre (from 122.7 in 2026-12). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t05:state:parity:69`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-03: OMC marketing margin falls to -56.4 Rs/litre (from -48.2 in 2027-02). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t05:state:omc_margin:70`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-03: Food inflation falls to 6.43 % y/y (from 7.24 in 2027-01). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t05:state:food_yoy:71`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-03: Core inflation rises to 5.61 % y/y (from 5.21 in 2027-02). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t05:state:core_yoy:72`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2027-03: Bank credit growth falls to 10.51 % y/y (from 11.00 in 2026-10). Mechanism: M-CRD-01.
  - id `2313560ef632:p169:t05:state:credit_yoy:73`; parents 3; support: Low-Medium (judgmental)
- **[state_change]** 2027-03: Credit stress index rises to 0.34 index (from 0.18 in 2027-01). Mechanism: M-CRD-02.
  - id `2313560ef632:p169:t05:state:stress:74`; parents 2; support: Low-Medium (judgmental)

## 2027-04

- **[regime]** 2027-04: Gulf supply-disruption regime ends. Mechanism: M-OIL-01.
  - id `2313560ef632:p169:t06:regime:disrupt:75`; parents 1; support: Low-Medium (judgmental hazard)
- **[regime]** 2027-04: Escalation layer (Hormuz) ends. Mechanism: M-OIL-01.
  - id `2313560ef632:p169:t06:regime:esc:76`; parents 1; support: Low-Medium (judgmental hazard)
- **[publication]** 2027-04: CPI for 2027-03 published: headline 5.64%, food 6.43%, core 5.61%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t06:pub:cpi:77`; parents 0; support: High (calendar)
- **[decision]** 2027-04: MPC hikes repo 25bp to 6.25% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(5.57), 'Core CPI (latest published)': np.float64(5.21), 'Expectations (%)': np.float64(5.12), 'GDP (latest published, % y/y)': np.float64(6.57), '3m INR depreciation (%)': np.float64(1.97)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t06:decision:mpc:78`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-04: Brent crude falls to 94.0 USD/bbl (from 165.6 in 2027-03). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - id `2313560ef632:p169:t06:state:brent:79`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2027-04: Crude import bill falls to 14.79 USD bn/month (from 26.60 in 2027-03). Main drivers: price (Brent+freight) -12.09, volume +0.28 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t06:state:crude_bill:80`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-04: Petroleum product exports falls to 4.68 USD bn/month (from 8.29 in 2027-03). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t06:state:prod_exp:81`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-04: Net oil balance rises to -12.67 USD bn/month (from -21.94 in 2027-03). Main drivers: crude_bill +11.81, prod_exp -3.60, other_energy +1.07 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t06:state:oil_net:82`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-04: Current account balance rises to -0.03 USD bn/month (from -8.99 in 2027-03). Main drivers: oil_net +9.27, nonoil_bal -0.25, services -0.13 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t06:state:ca:83`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-04: Portfolio flows (FPI) rises to -3.78 USD bn/month (from -5.42 in 2026-12). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t06:state:fpi:84`; parents 3; support: Low-Medium (judgmental)
- **[state_change]** 2027-04: Capital account rises to -1.68 USD bn/month (from -3.49 in 2026-12). Main drivers: fpi +1.64, ecb_other +0.17, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t06:state:ka:85`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-04: FX pressure (excess USD demand) falls to 1.71 USD bn/month (from 10.72 in 2026-12). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t06:state:pressure:86`; parents 2; support: High (arithmetic)
- **[decision]** 2027-04: RBI sells USD 1.3bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(1.71), 'Reserves prior (USD bn)': np.float64(689.7)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.13 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t06:decision:fx:87`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-04: Overnight rate (WACR) rises to 6.37 % (from 6.06 in 2027-02). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t06:state:wacr:88`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-04: Fuel import-parity cost falls to 73.7 Rs/litre (from 134.5 in 2027-03). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t06:state:parity:89`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-04: OMC marketing margin rises to 4.3 Rs/litre (from -56.4 in 2027-03). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t06:state:omc_margin:90`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-04: Core inflation rises to 6.06 % y/y (from 5.61 in 2027-03). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t06:state:core_yoy:91`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2027-04: Inflation expectations rises to 5.14 % (1y) (from 5.00 in 2026-10). Mechanism: M-PRC-05. Could be interrupted by: Credible RBI action.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t06:state:exp_infl:92`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-04: Output gap rises to -0.53 % of potential (from -1.53 in 2027-01). Main drivers: input +0.67, phys +0.48, food +0.15 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t06:state:gap:93`; parents 5; support: Low-Medium (judgmental)

## 2027-05

- **[publication]** 2027-05: CPI for 2027-04 published: headline 5.72%, food 6.01%, core 6.06%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t07:pub:cpi:94`; parents 0; support: High (calendar)
- **[publication]** 2027-05: GDP for quarter ending 2027-03 published: 5.31% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t07:pub:gdp:95`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[state_change]** 2027-05: Brent crude falls to 86.9 USD/bbl (from 94.0 in 2027-04). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - id `2313560ef632:p169:t07:state:brent:96`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2027-05: Crude import bill falls to 13.85 USD bn/month (from 14.79 in 2027-04). Main drivers: price (Brent+freight) -1.11, volume +0.17 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t07:state:crude_bill:97`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-05: Net oil balance rises to -11.93 USD bn/month (from -12.67 in 2027-04). Main drivers: crude_bill +0.93, prod_exp -0.30, other_energy +0.11 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t07:state:oil_net:98`; parents 2; support: High (arithmetic)
- **[decision]** 2027-05: RBI sells USD 1.1bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(1.42), 'Reserves prior (USD bn)': np.float64(690.4)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.11 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t07:decision:fx:99`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-05: Fuel import-parity cost falls to 69.6 Rs/litre (from 73.7 in 2027-04). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t07:state:parity:100`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-05: OMC marketing margin rises to 8.5 Rs/litre (from 4.3 in 2027-04). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t07:state:omc_margin:101`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-05: Food inflation falls to 5.29 % y/y (from 6.43 in 2027-03). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t07:state:food_yoy:102`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-05: Energy inflation falls to 1.95 % y/y (from 3.00 in 2026-10). Mechanism: M-PRC-01.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t07:state:energy_yoy:103`; parents 0; support: High (arithmetic)
- **[state_change]** 2027-05: Core inflation rises to 6.44 % y/y (from 6.06 in 2027-04). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t07:state:core_yoy:104`; parents 4; support: Medium (benchmarked to published estimates)
- **[state_change]** 2027-05: Output gap rises to -0.28 % of potential (from -0.53 in 2027-04). Main drivers: phys +0.11, food +0.09, omc +0.08 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t07:state:gap:105`; parents 5; support: Low-Medium (judgmental)
- **[state_change]** 2027-05: Projected fiscal deficit (current FY) falls to 4.22 % GDP (from 4.30 in 2026-10). Mechanism: M-FIS-01.
  - id `2313560ef632:p169:t07:state:fd_proj:106`; parents 3; support: High (arithmetic)

## 2027-06

- **[publication]** 2027-06: CPI for 2027-05 published: headline 5.65%, food 5.29%, core 6.44%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t08:pub:cpi:107`; parents 0; support: High (calendar)
- **[decision]** 2027-06: MPC cuts repo 25bp to 6.00% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(5.72), 'Core CPI (latest published)': np.float64(6.06), 'Expectations (%)': np.float64(5.17), 'GDP (latest published, % y/y)': np.float64(5.31), '3m INR depreciation (%)': np.float64(1.68)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: -25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t08:decision:mpc:108`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-06: Petroleum product exports falls to 4.24 USD bn/month (from 4.68 in 2027-04). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t08:state:prod_exp:109`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-06: Remittances (net secondary income) rises to 13.90 USD bn/month (from 13.60 in 2026-10). Mechanism: M-EXT-07. Could be interrupted by: Gulf activity disruption, expat departures.
  - id `2313560ef632:p169:t08:state:remit:110`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2027-06: Non-oil goods balance falls to -15.25 USD bn/month (from -14.50 in 2026-10). Mechanism: M-EXT-05. Could be interrupted by: Gold imports surge in uncertainty (not modelled).
  - id `2313560ef632:p169:t08:state:nonoil_bal:111`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2027-06: Portfolio flows (FPI) rises to -2.74 USD bn/month (from -3.78 in 2027-04). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t08:state:fpi:112`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2027-06: Capital account rises to -0.55 USD bn/month (from -1.68 in 2027-04). Main drivers: fpi +1.04, ecb_other +0.08, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t08:state:ka:113`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-06: FX pressure (excess USD demand) falls to 0.12 USD bn/month (from 1.71 in 2027-04). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t08:state:pressure:114`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-06: INR per USD rises to 104.62 INR/USD (from 103.48 in 2027-03). Main drivers: dollar index +1.30, noise -0.67, unabsorbed pressure +0.46 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t08:state:inr:115`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-06: FX reserves falls to 679.84 USD bn (from 689.69 in 2027-03). Main drivers: valuation -7.42, intervention (BoP) -2.43 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t08:state:reserves:116`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-06: Overnight rate (WACR) falls to 6.13 % (from 6.37 in 2027-04). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t08:state:wacr:117`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-06: Food inflation falls to 4.67 % y/y (from 5.29 in 2027-05). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t08:state:food_yoy:118`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-06: Core inflation rises to 6.70 % y/y (from 6.44 in 2027-05). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t08:state:core_yoy:119`; parents 4; support: Medium (benchmarked to published estimates)

## 2027-07

- **[publication]** 2027-07: CPI for 2027-06 published: headline 5.56%, food 4.67%, core 6.70%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t09:pub:cpi:120`; parents 0; support: High (calendar)
- **[state_change]** 2027-07: Portfolio flows (FPI) rises to -1.84 USD bn/month (from -2.74 in 2027-06). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t09:state:fpi:121`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2027-07: Capital account rises to 0.38 USD bn/month (from -0.55 in 2027-06). Main drivers: fpi +0.90, ecb_other +0.04, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t09:state:ka:122`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-07: INR per USD falls to 103.26 INR/USD (from 104.62 in 2027-06). Main drivers: noise -0.90, dollar index -0.31, unabsorbed pressure -0.10 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t09:state:inr:123`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-07: Food inflation falls to 3.90 % y/y (from 4.67 in 2027-06). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t09:state:food_yoy:124`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-07: Output gap rises to -0.02 % of potential (from -0.28 in 2027-05). Main drivers: phys +0.17, food +0.13, omc +0.13 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t09:state:gap:125`; parents 4; support: Low-Medium (judgmental)
- **[state_change]** 2027-07: Bank credit growth falls to 10.07 % y/y (from 10.51 in 2027-03). Mechanism: M-CRD-01.
  - id `2313560ef632:p169:t09:state:credit_yoy:126`; parents 2; support: Low-Medium (judgmental)

## 2027-08

- **[publication]** 2027-08: CPI for 2027-07 published: headline 5.34%, food 3.90%, core 6.84%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t10:pub:cpi:127`; parents 0; support: High (calendar)
- **[publication]** 2027-08: GDP for quarter ending 2027-06 published: 6.32% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t10:pub:gdp:128`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[decision]** 2027-08: MPC cuts repo 25bp to 5.75% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(5.56), 'Core CPI (latest published)': np.float64(6.7), 'Expectations (%)': np.float64(5.22), 'GDP (latest published, % y/y)': np.float64(5.31), '3m INR depreciation (%)': np.float64(-0.07)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: -25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t10:decision:mpc:129`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-08: FX pressure (excess USD demand) falls to -1.14 USD bn/month (from 0.12 in 2027-06). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t10:state:pressure:130`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-08: INR per USD rises to 104.21 INR/USD (from 103.26 in 2027-07). Main drivers: noise +0.60, dollar index +0.51, unabsorbed pressure -0.20 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t10:state:inr:131`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-08: Overnight rate (WACR) falls to 5.87 % (from 6.13 in 2027-06). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t10:state:wacr:132`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-08: Fuel import-parity cost falls to 67.3 Rs/litre (from 69.6 in 2027-05). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t10:state:parity:133`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-08: Headline CPI inflation falls to 5.19 % y/y (from 5.51 in 2026-10). Main drivers: core +3.81, food +1.26, energy +0.12 [exact (base-weighted component contributions to the LEVEL of headline y/y)]. Mechanism: M-PRC-04.
  - id `2313560ef632:p169:t10:state:cpi_yoy:134`; parents 3; support: High (arithmetic)

## 2027-09

- **[publication]** 2027-09: CPI for 2027-08 published: headline 5.19%, food 3.42%, core 6.91%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t11:pub:cpi:135`; parents 1; support: High (calendar)
- **[state_change]** 2027-09: Fuel import-parity cost rises to 71.3 Rs/litre (from 67.3 in 2027-08). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t11:state:parity:136`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-09: Food inflation falls to 2.99 % y/y (from 3.90 in 2027-07). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t11:state:food_yoy:137`; parents 0; support: Low-Medium (judgmental)

## 2027-10

- **[publication]** 2027-10: CPI for 2027-09 published: headline 5.02%, food 2.99%, core 6.91%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t12:pub:cpi:138`; parents 1; support: High (calendar)
- **[decision]** 2027-10: MPC hikes repo 25bp to 6.00% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(5.19), 'Core CPI (latest published)': np.float64(6.91), 'Expectations (%)': np.float64(5.22), 'GDP (latest published, % y/y)': np.float64(6.32), '3m INR depreciation (%)': np.float64(-0.08)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t12:decision:mpc:139`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-10: Remittances (net secondary income) falls to 13.50 USD bn/month (from 13.90 in 2027-06). Mechanism: M-EXT-07. Could be interrupted by: Gulf activity disruption, expat departures.
  - id `2313560ef632:p169:t12:state:remit:140`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2027-10: FX pressure (excess USD demand) rises to 0.45 USD bn/month (from -1.14 in 2027-08). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t12:state:pressure:141`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-10: FX reserves falls to 673.72 USD bn (from 679.84 in 2027-06). Main drivers: valuation -7.28, intervention (BoP) +1.17 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t12:state:reserves:142`; parents 0; support: High (arithmetic)
- **[state_change]** 2027-10: Overnight rate (WACR) rises to 6.12 % (from 5.87 in 2027-08). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t12:state:wacr:143`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-10: Headline CPI inflation falls to 4.94 % y/y (from 5.19 in 2027-08). Main drivers: core +3.77, food +1.07, energy +0.10 [exact (base-weighted component contributions to the LEVEL of headline y/y)]. Mechanism: M-PRC-04.
  - id `2313560ef632:p169:t12:state:cpi_yoy:144`; parents 1; support: High (arithmetic)

## 2027-11

- **[publication]** 2027-11: CPI for 2027-10 published: headline 4.94%, food 2.89%, core 6.86%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t13:pub:cpi:145`; parents 1; support: High (calendar)
- **[publication]** 2027-11: GDP for quarter ending 2027-09 published: 6.33% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t13:pub:gdp:146`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[state_change]** 2027-11: Brent crude falls to 80.8 USD/bbl (from 86.9 in 2027-05). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t13:state:brent:147`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2027-11: Crude import bill falls to 12.98 USD bn/month (from 13.85 in 2027-05). Main drivers: price (Brent+freight) -0.95, volume +0.08 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t13:state:crude_bill:148`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-11: Net oil balance rises to -11.22 USD bn/month (from -11.93 in 2027-05). Main drivers: crude_bill +0.87, prod_exp -0.25, other_energy +0.09 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t13:state:oil_net:149`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-11: FX pressure (excess USD demand) falls to -1.54 USD bn/month (from 0.45 in 2027-10). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t13:state:pressure:150`; parents 0; support: High (arithmetic)
- **[decision]** 2027-11: RBI buys USD 1.1bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-1.54), 'Reserves prior (USD bn)': np.float64(673.7)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.11 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t13:decision:fx:151`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-11: INR per USD falls to 103.05 INR/USD (from 104.21 in 2027-08). Main drivers: dollar index -0.79, unabsorbed pressure -0.27, noise -0.07 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t13:state:inr:152`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-11: FX reserves rises to 685.29 USD bn (from 673.72 in 2027-10). Main drivers: valuation +10.49, intervention (BoP) +1.08 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t13:state:reserves:153`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-11: Fuel import-parity cost falls to 65.0 Rs/litre (from 71.3 in 2027-09). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t13:state:parity:154`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-11: OMC marketing margin rises to 13.1 Rs/litre (from 8.5 in 2027-05). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t13:state:omc_margin:155`; parents 1; support: High (arithmetic)

## 2027-12

- **[publication]** 2027-12: CPI for 2027-11 published: headline 4.93%, food 2.92%, core 6.82%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t14:pub:cpi:156`; parents 1; support: High (calendar)
- **[decision]** 2027-12: MPC holds repo 0bp to 6.00% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(4.94), 'Core CPI (latest published)': np.float64(6.86), 'Expectations (%)': np.float64(5.2), 'GDP (latest published, % y/y)': np.float64(6.33), '3m INR depreciation (%)': np.float64(-1.12)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +0bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t14:decision:mpc:157`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-12: Current account balance rises to 1.29 USD bn/month (from -0.03 in 2027-04). Main drivers: oil_net +1.69, nonoil_bal -0.31, remit -0.23 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t14:state:ca:158`; parents 2; support: High (arithmetic)
- **[state_change]** 2027-12: Portfolio flows (FPI) rises to -0.29 USD bn/month (from -1.84 in 2027-07). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t14:state:fpi:159`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2027-12: Capital account rises to 1.76 USD bn/month (from 0.38 in 2027-07). Main drivers: fpi +1.55, ecb_other -0.18, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t14:state:ka:160`; parents 1; support: High (arithmetic)
- **[state_change]** 2027-12: FX pressure (excess USD demand) falls to -3.04 USD bn/month (from -1.54 in 2027-11). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t14:state:pressure:161`; parents 2; support: High (arithmetic)
- **[decision]** 2027-12: RBI buys USD 2.1bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-3.04), 'Reserves prior (USD bn)': np.float64(685.3)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.22 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t14:decision:fx:162`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2027-12: INR per USD falls to 102.19 INR/USD (from 103.05 in 2027-11). Main drivers: unabsorbed pressure -0.52, dollar index -0.28, noise -0.03 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t14:state:inr:163`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2027-12: Output gap rises to 0.31 % of potential (from -0.02 in 2027-07). Main drivers: phys +0.23, omc +0.17, noise +0.14 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t14:state:gap:164`; parents 3; support: Low-Medium (judgmental)

## 2028-01

- **[publication]** 2028-01: CPI for 2027-12 published: headline 4.86%, food 2.94%, core 6.68%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t15:pub:cpi:165`; parents 1; support: High (calendar)
- **[state_change]** 2028-01: Brent crude rises to 94.4 USD/bbl (from 80.8 in 2027-11). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t15:state:brent:166`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2028-01: Crude import bill rises to 15.12 USD bn/month (from 12.98 in 2027-11). Main drivers: price (Brent+freight) +2.13, volume +0.01 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t15:state:crude_bill:167`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-01: Petroleum product exports rises to 4.70 USD bn/month (from 4.24 in 2027-06). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t15:state:prod_exp:168`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-01: Net oil balance falls to -12.99 USD bn/month (from -11.22 in 2027-11). Main drivers: crude_bill -2.14, prod_exp +0.56, other_energy -0.20 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t15:state:oil_net:169`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-01: Non-oil goods balance rises to -14.37 USD bn/month (from -15.25 in 2027-06). Mechanism: M-EXT-05. Could be interrupted by: Gold imports surge in uncertainty (not modelled).
  - id `2313560ef632:p169:t15:state:nonoil_bal:170`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2028-01: Current account balance falls to -0.23 USD bn/month (from 1.29 in 2027-12). Main drivers: oil_net -2.02, nonoil_bal +0.33, services +0.17 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t15:state:ca:171`; parents 3; support: High (arithmetic)
- **[decision]** 2028-01: RBI buys USD 1.5bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-2.17), 'Reserves prior (USD bn)': np.float64(689.0)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.15 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t15:decision:fx:172`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-01: INR per USD falls to 100.77 INR/USD (from 102.19 in 2027-12). Main drivers: dollar index -1.09, unabsorbed pressure -0.37, noise +0.06 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t15:state:inr:173`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2028-01: FX reserves rises to 696.79 USD bn (from 685.29 in 2027-11). Main drivers: valuation +7.84, intervention (BoP) +3.65 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t15:state:reserves:174`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-01: Fuel import-parity cost rises to 72.2 Rs/litre (from 65.0 in 2027-11). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t15:state:parity:175`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-01: OMC marketing margin falls to 5.9 Rs/litre (from 13.1 in 2027-11). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t15:state:omc_margin:176`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-01: Core inflation falls to 6.39 % y/y (from 6.70 in 2027-06). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t15:state:core_yoy:177`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2028-01: Output gap falls to 0.04 % of potential (from 0.31 in 2027-12). Main drivers: input -0.21, noise -0.11, food -0.07 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t15:state:gap:178`; parents 3; support: Low-Medium (judgmental)

## 2028-02

- **[publication]** 2028-02: CPI for 2028-01 published: headline 4.82%, food 3.25%, core 6.39%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t16:pub:cpi:179`; parents 1; support: High (calendar)
- **[publication]** 2028-02: GDP for quarter ending 2027-12 published: 7.21% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t16:pub:gdp:180`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[decision]** 2028-02: MPC holds repo 0bp to 6.00% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(4.86), 'Core CPI (latest published)': np.float64(6.68), 'Expectations (%)': np.float64(5.17), 'GDP (latest published, % y/y)': np.float64(6.33), '3m INR depreciation (%)': np.float64(-3.12)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +0bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t16:decision:mpc:181`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-02: Portfolio flows (FPI) rises to 0.77 USD bn/month (from -0.29 in 2027-12). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t16:state:fpi:182`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2028-02: Capital account rises to 2.65 USD bn/month (from 1.76 in 2027-12). Main drivers: fpi +1.05, ecb_other -0.16, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t16:state:ka:183`; parents 1; support: High (arithmetic)
- **[decision]** 2028-02: RBI buys USD 2.1bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-3.0), 'Reserves prior (USD bn)': np.float64(696.8)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.21 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t16:decision:fx:184`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-02: Food inflation rises to 3.69 % y/y (from 2.99 in 2027-09). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t16:state:food_yoy:185`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2028-02: Core inflation falls to 6.04 % y/y (from 6.39 in 2028-01). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t16:state:core_yoy:186`; parents 3; support: Medium (benchmarked to published estimates)

## 2028-03

- **[publication]** 2028-03: CPI for 2028-02 published: headline 4.79%, food 3.69%, core 6.04%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t17:pub:cpi:187`; parents 1; support: High (calendar)
- **[state_change]** 2028-03: Portfolio flows (FPI) falls to -0.08 USD bn/month (from 0.77 in 2028-02). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t17:state:fpi:188`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2028-03: FX pressure (excess USD demand) rises to -1.90 USD bn/month (from -3.04 in 2027-12). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t17:state:pressure:189`; parents 2; support: High (arithmetic)
- **[decision]** 2028-03: RBI buys USD 1.3bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-1.9), 'Reserves prior (USD bn)': np.float64(697.6)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.13 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t17:decision:fx:190`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-03: Banking liquidity rises to -0.61 Rs lakh crore (from -0.95 in 2027-03). Mechanism: M-LIQ-01.
  - id `2313560ef632:p169:t17:state:liq:191`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-03: Core inflation falls to 5.61 % y/y (from 6.04 in 2028-02). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t17:state:core_yoy:192`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2028-03: Output gap rises to 0.24 % of potential (from 0.04 in 2028-01). Main drivers: gdem +0.12, noise +0.10, food -0.08 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t17:state:gap:193`; parents 3; support: Low-Medium (judgmental)

## 2028-04

- **[publication]** 2028-04: CPI for 2028-03 published: headline 4.70%, food 4.07%, core 5.61%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t18:pub:cpi:194`; parents 1; support: High (calendar)
- **[decision]** 2028-04: MPC hikes repo 25bp to 6.25% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(4.79), 'Core CPI (latest published)': np.float64(6.04), 'Expectations (%)': np.float64(5.13), 'GDP (latest published, % y/y)': np.float64(7.21), '3m INR depreciation (%)': np.float64(-1.35)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t18:decision:mpc:195`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[decision]** 2028-04: RBI buys USD 1.4bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-1.96), 'Reserves prior (USD bn)': np.float64(700.0)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.14 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t18:decision:fx:196`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-04: INR per USD falls to 99.64 INR/USD (from 100.77 in 2028-01). Main drivers: unabsorbed pressure -1.17, noise +0.56, dollar index -0.51 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t18:state:inr:197`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2028-04: FX reserves rises to 704.54 USD bn (from 696.79 in 2028-01). Main drivers: intervention (BoP) +4.80, valuation +2.95 [exact (stock-flow identity)]. Mechanism: M-FX-04.
  - id `2313560ef632:p169:t18:state:reserves:198`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-04: Overnight rate (WACR) rises to 6.31 % (from 6.12 in 2027-10). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t18:state:wacr:199`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-04: Headline CPI inflation falls to 4.55 % y/y (from 4.94 in 2027-10). Main drivers: core +2.84, food +1.62, energy +0.09 [exact (base-weighted component contributions to the LEVEL of headline y/y)]. Mechanism: M-PRC-04.
  - id `2313560ef632:p169:t18:state:cpi_yoy:200`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-04: Food inflation rises to 4.40 % y/y (from 3.69 in 2028-02). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t18:state:food_yoy:201`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2028-04: Core inflation falls to 5.13 % y/y (from 5.61 in 2028-03). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t18:state:core_yoy:202`; parents 3; support: Medium (benchmarked to published estimates)

## 2028-05

- **[publication]** 2028-05: CPI for 2028-04 published: headline 4.55%, food 4.40%, core 5.13%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t19:pub:cpi:203`; parents 1; support: High (calendar)
- **[publication]** 2028-05: GDP for quarter ending 2028-03 published: 8.31% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t19:pub:gdp:204`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[decision]** 2028-05: RBI buys USD 1.4bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-1.96), 'Reserves prior (USD bn)': np.float64(704.5)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.14 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t19:decision:fx:205`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-05: Food inflation rises to 5.06 % y/y (from 4.40 in 2028-04). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t19:state:food_yoy:206`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2028-05: Core inflation falls to 4.69 % y/y (from 5.13 in 2028-04). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t19:state:core_yoy:207`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2028-05: 10Y G-sec yield rises to 7.78 % (from 7.62 in 2027-01). Mechanism: M-BOND-01. Could be interrupted by: Issuance cuts; RBI OMO purchases.
  - id `2313560ef632:p169:t19:state:g10:208`; parents 1; support: Low-Medium (judgmental)

## 2028-06

- **[publication]** 2028-06: CPI for 2028-05 published: headline 4.56%, food 5.06%, core 4.69%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t20:pub:cpi:209`; parents 1; support: High (calendar)
- **[decision]** 2028-06: MPC hikes repo 25bp to 6.50% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(4.55), 'Core CPI (latest published)': np.float64(5.13), 'Expectations (%)': np.float64(5.08), 'GDP (latest published, % y/y)': np.float64(8.31), '3m INR depreciation (%)': np.float64(-1.27)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t20:decision:mpc:210`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-06: Crude import bill rises to 15.83 USD bn/month (from 15.12 in 2028-01). Main drivers: price (Brent+freight) +0.71, volume -0.01 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t20:state:crude_bill:211`; parents 0; support: High (arithmetic)
- **[state_change]** 2028-06: Non-oil goods balance falls to -15.02 USD bn/month (from -14.37 in 2028-01). Mechanism: M-EXT-05. Could be interrupted by: Gold imports surge in uncertainty (not modelled).
  - id `2313560ef632:p169:t20:state:nonoil_bal:212`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2028-06: Current account balance falls to -1.62 USD bn/month (from -0.23 in 2028-01). Main drivers: nonoil_bal -0.65, oil_net -0.59, services -0.12 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t20:state:ca:213`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-06: FX pressure (excess USD demand) rises to -0.30 USD bn/month (from -1.90 in 2028-03). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t20:state:pressure:214`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-06: Overnight rate (WACR) rises to 6.56 % (from 6.31 in 2028-04). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t20:state:wacr:215`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-06: Fuel import-parity cost rises to 74.6 Rs/litre (from 72.2 in 2028-01). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t20:state:parity:216`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-06: Core inflation falls to 4.39 % y/y (from 4.69 in 2028-05). Mechanism: M-PRC-03. Could be interrupted by: Weak demand; margin compression.
  - id `2313560ef632:p169:t20:state:core_yoy:217`; parents 3; support: Medium (benchmarked to published estimates)
- **[state_change]** 2028-06: 10Y G-sec yield rises to 7.93 % (from 7.78 in 2028-05). Mechanism: M-BOND-01. Could be interrupted by: Issuance cuts; RBI OMO purchases.
  - id `2313560ef632:p169:t20:state:g10:218`; parents 1; support: Low-Medium (judgmental)

## 2028-07

- **[publication]** 2028-07: CPI for 2028-06 published: headline 4.54%, food 5.47%, core 4.39%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t21:pub:cpi:219`; parents 1; support: High (calendar)
- **[state_change]** 2028-07: Capital account falls to 1.32 USD bn/month (from 2.65 in 2028-02). Main drivers: fpi -1.62, ecb_other +0.29, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t21:state:ka:220`; parents 0; support: High (arithmetic)
- **[state_change]** 2028-07: INR per USD rises to 101.82 INR/USD (from 99.64 in 2028-04). Main drivers: noise +2.49, unabsorbed pressure -0.36, dollar index +0.03 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t21:state:inr:221`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2028-07: OMC marketing margin falls to 3.1 Rs/litre (from 5.9 in 2028-01). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t21:state:omc_margin:222`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-07: Food inflation rises to 6.02 % y/y (from 5.06 in 2028-05). Mechanism: M-PRC-02. Could be interrupted by: Imports, stock releases.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t21:state:food_yoy:223`; parents 0; support: Low-Medium (judgmental)

## 2028-08

- **[publication]** 2028-08: CPI for 2028-07 published: headline 4.66%, food 6.02%, core 4.25%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t22:pub:cpi:224`; parents 1; support: High (calendar)
- **[publication]** 2028-08: GDP for quarter ending 2028-06 published: 7.22% y/y. Mechanism: M-REAL-11.
  - id `2313560ef632:p169:t22:pub:gdp:225`; parents 1; support: Medium (monthly activity proxy aggregated)
- **[decision]** 2028-08: MPC holds repo 0bp to 6.50% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(4.54), 'Core CPI (latest published)': np.float64(4.39), 'Expectations (%)': np.float64(5.03), 'GDP (latest published, % y/y)': np.float64(8.31), '3m INR depreciation (%)': np.float64(2.16)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: +0bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t22:decision:mpc:226`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-08: Brent crude rises to 102.0 USD/bbl (from 94.4 in 2028-01). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t22:state:brent:227`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2028-08: Net oil balance falls to -13.98 USD bn/month (from -12.99 in 2028-01). Main drivers: crude_bill -1.19, prod_exp +0.32, other_energy -0.11 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t22:state:oil_net:228`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-08: Portfolio flows (FPI) falls to -1.66 USD bn/month (from -0.08 in 2028-03). Mechanism: M-CAP-01. Could be interrupted by: Index inclusion flows; valuation-driven buying.
  - id `2313560ef632:p169:t22:state:fpi:229`; parents 2; support: Low-Medium (judgmental)
- **[state_change]** 2028-08: FX pressure (excess USD demand) rises to 1.74 USD bn/month (from -0.30 in 2028-06). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t22:state:pressure:230`; parents 2; support: High (arithmetic)
- **[decision]** 2028-08: RBI sells USD 1.3bn (75% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(1.74), 'Reserves prior (USD bn)': np.float64(705.8)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 75% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.13 lakh crore of liquidity; sterilised share 50%.
  - id `2313560ef632:p169:t22:decision:fx:231`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-08: Fuel import-parity cost rises to 78.0 Rs/litre (from 74.6 in 2028-06). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t22:state:parity:232`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-08: OMC marketing margin falls to 0.1 Rs/litre (from 3.1 in 2028-07). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t22:state:omc_margin:233`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-08: Inflation expectations falls to 5.01 % (1y) (from 5.14 in 2027-04). Mechanism: M-PRC-05. Could be interrupted by: Credible RBI action.
  - id `2313560ef632:p169:t22:state:exp_infl:234`; parents 1; support: Low-Medium (judgmental)
- **[state_change]** 2028-08: Projected fiscal deficit (current FY) rises to 4.29 % GDP (from 4.22 in 2027-05). Mechanism: M-FIS-01.
  - id `2313560ef632:p169:t22:state:fd_proj:235`; parents 2; support: High (arithmetic)

## 2028-09

- **[publication]** 2028-09: CPI for 2028-08 published: headline 4.68%, food 6.13%, core 4.23%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t23:pub:cpi:236`; parents 1; support: High (calendar)
- **[state_change]** 2028-09: Brent crude falls to 57.8 USD/bbl (from 102.0 in 2028-08). Mechanism: M-OIL-01, M-OIL-02. Could be interrupted by: SPR releases, OPEC+ spare capacity, demand destruction; Supply cuts in response to weak demand.
  - No reportable parent event within the lag window: the move comes from this path's random innovations and/or persistence of earlier changes.
  - id `2313560ef632:p169:t23:state:brent:237`; parents 0; support: Low-Medium (judgmental)
- **[state_change]** 2028-09: Crude import bill falls to 9.49 USD bn/month (from 15.83 in 2028-06). Main drivers: price (Brent+freight) -6.52, volume +0.17 [exact (two-factor midpoint split)]. Mechanism: M-EXT-01. Could be interrupted by: Volume response; discounted Russian barrels (not modelled).
  - id `2313560ef632:p169:t23:state:crude_bill:238`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-09: Petroleum product exports falls to 3.17 USD bn/month (from 4.70 in 2028-01). Mechanism: M-EXT-02. Could be interrupted by: Export curbs / windfall taxes.
  - id `2313560ef632:p169:t23:state:prod_exp:239`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-09: Net oil balance rises to -8.34 USD bn/month (from -13.98 in 2028-08). Main drivers: crude_bill +6.82, prod_exp -1.84, other_energy +0.66 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-04.
  - id `2313560ef632:p169:t23:state:oil_net:240`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-09: Current account balance rises to 3.44 USD bn/month (from -1.62 in 2028-06). Main drivers: oil_net +5.24, nonoil_bal -0.25, remit +0.13 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-EXT-09.
  - id `2313560ef632:p169:t23:state:ca:241`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-09: Capital account falls to 0.26 USD bn/month (from 1.32 in 2028-07). Main drivers: fpi -1.08, ecb_other +0.01, fdi +0.00 [exact (accounting identity; signs as effect on balance)]. Mechanism: M-CAP-03.
  - id `2313560ef632:p169:t23:state:ka:242`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-09: FX pressure (excess USD demand) falls to -3.70 USD bn/month (from 1.74 in 2028-08). Mechanism: M-FX-01. Could be interrupted by: Capital inflows.
  - id `2313560ef632:p169:t23:state:pressure:243`; parents 2; support: High (arithmetic)
- **[decision]** 2028-09: RBI buys USD 2.6bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-3.7), 'Reserves prior (USD bn)': np.float64(707.2)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.27 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t23:decision:fx:244`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-09: INR per USD rises to 102.66 INR/USD (from 101.82 in 2028-07). Main drivers: dollar index +0.81, noise +0.39, unabsorbed pressure -0.39 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t23:state:inr:245`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2028-09: Fuel import-parity cost falls to 49.9 Rs/litre (from 78.0 in 2028-08). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t23:state:parity:246`; parents 2; support: High (arithmetic)
- **[state_change]** 2028-09: OMC marketing margin rises to 28.2 Rs/litre (from 0.1 in 2028-08). Mechanism: M-FUEL-03.
  - id `2313560ef632:p169:t23:state:omc_margin:247`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-09: Output gap rises to 0.87 % of potential (from 0.24 in 2028-03). Main drivers: input +0.55, noise +0.10, rate -0.08 [exact (linear channel system)]. Mechanism: M-REAL-01, M-REAL-02, M-REAL-03, M-REAL-04, M-REAL-05, M-REAL-06, M-REAL-07, M-REAL-08, M-REAL-09, M-REAL-10. Could be interrupted by: Budget compensation; Transfers.
  - id `2313560ef632:p169:t23:state:gap:248`; parents 4; support: Low-Medium (judgmental)
- **[state_change]** 2028-09: Projected fiscal deficit (current FY) falls to 4.22 % GDP (from 4.29 in 2028-08). Mechanism: M-FIS-01.
  - id `2313560ef632:p169:t23:state:fd_proj:249`; parents 3; support: High (arithmetic)

## 2028-10

- **[publication]** 2028-10: CPI for 2028-09 published: headline 4.80%, food 6.31%, core 4.32%. Mechanism: M-PUB-01.
  - id `2313560ef632:p169:t24:pub:cpi:250`; parents 1; support: High (calendar)
- **[decision]** 2028-10: MPC cuts repo 25bp to 6.25% (rule: inflation_targeting). Mechanism: M-MPC-01.
  - Observed: {'CPI (latest published, % y/y)': np.float64(4.68), 'Core CPI (latest published)': np.float64(4.23), 'Expectations (%)': np.float64(4.99), 'GDP (latest published, % y/y)': np.float64(7.22), '3m INR depreciation (%)': np.float64(2.47)} | Choices: ['-50bp', '-25bp', 'hold', '+25bp', '+50bp'] | Chosen: -25bp | Constraints: repo bounded 3-9%; max 50bp per meeting; uses only published data
  - Expected response: Higher real rates cool demand after ~3 months and widen the yield spread (supports FPI); costs: credit growth, stress.
  - id `2313560ef632:p169:t24:decision:mpc:251`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-10: Non-oil goods balance falls to -15.71 USD bn/month (from -15.02 in 2028-06). Mechanism: M-EXT-05. Could be interrupted by: Gold imports surge in uncertainty (not modelled).
  - id `2313560ef632:p169:t24:state:nonoil_bal:252`; parents 2; support: Low-Medium (judgmental)
- **[decision]** 2028-10: RBI buys USD 2.4bn (70% of pressure). Mechanism: M-FX-02, M-LIQ-01.
  - Observed: {'FX pressure (USD bn)': np.float64(-3.46), 'Reserves prior (USD bn)': np.float64(702.3)} | Choices: ['heavy 75%', 'moderate 50%', 'light 25%'] | Chosen: 70% | Constraints: scaled down near floor (~USD500bn); cannot sell below 95% of floor
  - Expected response: Drains Rs0.25 lakh crore of liquidity; sterilised share -50%.
  - id `2313560ef632:p169:t24:decision:fx:253`; parents 1; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-10: INR per USD falls to 101.50 INR/USD (from 102.66 in 2028-09). Main drivers: noise -1.10, unabsorbed pressure -0.59, dollar index +0.56 [exact in log-% terms (sum of monthly depreciation drivers)]. Mechanism: M-FX-03. Could be interrupted by: Exporter conversion, forward-book use.
  - id `2313560ef632:p169:t24:state:inr:254`; parents 2; support: Low (illustrative placeholder)
- **[state_change]** 2028-10: Banking liquidity rises to -0.28 Rs lakh crore (from -0.61 in 2028-03). Mechanism: M-LIQ-01.
  - id `2313560ef632:p169:t24:state:liq:255`; parents 1; support: High (arithmetic)
- **[state_change]** 2028-10: Overnight rate (WACR) falls to 6.28 % (from 6.56 in 2028-06). Mechanism: M-LIQ-02.
  - id `2313560ef632:p169:t24:state:wacr:256`; parents 2; support: Medium (explicit rule; behaviour uncertain)
- **[state_change]** 2028-10: Fuel import-parity cost falls to 47.7 Rs/litre (from 49.9 in 2028-09). Mechanism: M-FUEL-01.
  - id `2313560ef632:p169:t24:state:parity:257`; parents 2; support: High (arithmetic)