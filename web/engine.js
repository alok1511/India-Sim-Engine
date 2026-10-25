/* India-Sim-Engine: browser/Node port of src/indiasim/model.py (engine 0.3.0).
 * Same equations, same within-month order, same constants. Parity with Python is tested on injected
 * parameters and random draws (tests/test_js_parity.py). Only the random-number generator differs:
 * the browser draws its own streams (statistically equivalent, not bit-identical to numpy).
 * Pure functions, no DOM. Works as window.IndiaSim or require('./engine.js').
 */
(function (root) {
  "use strict";
  const P = 24;
  const MPC_MONTHS = new Set([12, 2, 4, 6, 8, 10]);
  const QUARTER_END = new Set([3, 6, 9, 12]);
  const GAP_CHANNELS = ["init", "rate", "fuel_hh", "omc", "input", "gdem", "risk", "stress", "food", "fiscal", "phys", "noise"];
  const GOV_FUEL = ["full_passthrough", "freeze_omc_absorb", "freeze_budget_comp", "partial_50", "excise_cut", "adaptive_threshold"];
  const GOV_FIS = ["accommodate", "hold_target"];
  const FX_OPTS = { heavy: 0.75, moderate: 0.5, light: 0.25 };
  const STERIL = { none: 0.0, half: 0.5, full: 1.0 };
  const ADMIN_ENERGY_TREND = 3.0, US_INFL = 2.5, LITRE_FACTOR = 1e-3;
  const SHOCK_KEYS = ["z_oil", "z_us", "z_dxy", "z_risk", "z_gdem", "chi2", "u_reg", "u_esc", "e_fx", "e_gap", "e_g10", "e_food"];

  // ------------------------------------------------------------------ calendar
  function monthLabel(t) { const k = 2026 * 12 + 9 + t; return `${Math.floor(k / 12)}-${String((k % 12) + 1).padStart(2, "0")}`; }
  function calMonth(t) { return ((2026 * 12 + 9 + t) % 12 + 12) % 12 + 1; }
  function fiscalYear(t) { const k = 2026 * 12 + 9 + t, y = Math.floor(k / 12), m = (k % 12) + 1; return "FY" + String(m >= 4 ? y + 1 : y).slice(-2); }
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function monthShort(t) { const k = 2026 * 12 + 9 + t; return `${MONTHS[k % 12]} '${String(Math.floor(k / 12)).slice(-2)}`; }

  // ------------------------------------------------------------------ random numbers (browser streams)
  function splitmix32(a) { return function () { a |= 0; a = (a + 0x9e3779b9) | 0; let t = a ^ (a >>> 16); t = Math.imul(t, 0x21f0aaad); t ^= t >>> 15; t = Math.imul(t, 0x735a2d97); return ((t ^= t >>> 15) >>> 0); }; }
  function makeRng(seed, path, stream) {
    const sm = splitmix32((seed * 2654435761) ^ (path * 40503) ^ (stream * 97));
    let s0 = sm(), s1 = sm(), s2 = sm(), s3 = sm();
    function next() { // xoshiro128**
      const r = Math.imul(rotl(Math.imul(s1, 5), 7), 9) >>> 0; const t = s1 << 9;
      s2 ^= s0; s3 ^= s1; s1 ^= s2; s0 ^= s3; s2 ^= t; s3 = rotl(s3, 11); return r;
    }
    function rotl(x, k) { return (x << k) | (x >>> (32 - k)); }
    const uni = () => (next() + 0.5) / 4294967296; // (0,1)
    let spare = null;
    const norm = () => { if (spare !== null) { const v = spare; spare = null; return v; } const u = uni(), v = uni(); const r = Math.sqrt(-2 * Math.log(u)); spare = r * Math.sin(2 * Math.PI * v); return r * Math.cos(2 * Math.PI * v); };
    return { uni, norm };
  }
  function drawShocks(seed, path, T, df) {
    const rng = makeRng(seed, path, 1), sh = {};
    for (const k of SHOCK_KEYS) sh[k] = new Float64Array(T + 1);
    for (let t = 0; t <= T; t++) { sh.z_oil[t] = rng.norm(); sh.z_us[t] = rng.norm(); sh.z_dxy[t] = rng.norm(); sh.z_risk[t] = rng.norm(); sh.z_gdem[t] = rng.norm(); }
    for (let t = 0; t <= T; t++) { let c = 0; for (let k = 0; k < df; k++) { const z = rng.norm(); c += z * z; } sh.chi2[t] = c; }
    for (const k of ["u_reg", "u_esc"]) for (let t = 0; t <= T; t++) sh[k][t] = rng.uni();
    for (const k of ["e_fx", "e_gap", "e_g10", "e_food"]) for (let t = 0; t <= T; t++) sh[k][t] = rng.norm();
    return sh;
  }
  function sampleParams(D, seed, path, mode, overrides) {
    const cfg = D.params.params, names = Object.keys(cfg).sort(), prm = {};
    for (const nm of names) prm[nm] = +cfg[nm].value;
    if (mode === "sampled") {
      const rng = makeRng(seed, path, 0);
      for (const nm of names) {
        const p = cfg[nm], d = p.dist || "fixed";
        if (d === "uniform") prm[nm] = p.low + rng.uni() * (p.high - p.low);
        else if (d === "triangular") { const a = p.low, c = p.value, b = p.high, u = rng.uni(), F = (c - a) / (b - a);
          prm[nm] = u < F ? a + Math.sqrt(u * (b - a) * (c - a)) : b - Math.sqrt((1 - u) * (b - a) * (b - c)); }
      }
    }
    for (const k in (overrides || {})) prm[k] = +overrides[k];
    return prm;
  }

  // ------------------------------------------------------------------ scenario offsets
  function offsetPath(T, start, months, mag, decay = 0.8) {
    const off = new Float64Array(T + 1);
    for (let t = 1; t <= T; t++) {
      if (start <= t && t < start + months) off[t] = mag;
      else if (t >= start + months) off[t] = mag * Math.pow(decay, t - (start + months) + 1);
    }
    return off;
  }
  function scenarioPaths(scenario, T) {
    const z = () => new Float64Array(T + 1);
    const sp = { off_us: z(), off_dxy: z(), off_risk: z(), off_gdem: z(), off_food: z(), esc: null, deesc: null };
    const add = (a, b) => { for (let t = 0; t <= T; t++) a[t] += b[t]; };
    for (const s of scenario.shocks || []) {
      const st = +s.start;
      if (s.type === "global_tightening") {
        const m = +(s.months ?? 9);
        add(sp.off_us, offsetPath(T, st, m, s.us10y ?? 0)); add(sp.off_dxy, offsetPath(T, st, m, (s.dxy_pct ?? 0) / 100));
        add(sp.off_risk, offsetPath(T, st, m, s.risk ?? 0)); add(sp.off_gdem, offsetPath(T, st, m, s.gdem ?? 0));
      } else if (s.type === "food_supply") add(sp.off_food, offsetPath(T, st, +(s.months ?? 5), s.magnitude ?? 0, 0.6));
      else if (s.type === "oil_escalation") {
        sp.esc = Object.assign({}, s);
        for (let t = 0; t <= T; t++) sp.off_risk[t] += t >= st ? (s.risk_impulse ?? 0) * Math.pow(0.8, t - st) : 0;
      } else if (s.type === "oil_deescalation") sp.deesc = st;
    }
    return sp;
  }
  const medianDuration = h => (h > 0 && h < 1) ? Math.max(1, Math.ceil(Math.log(0.5) / Math.log(1 - h))) : 1e6;
  function policyAt(spec, t, actor) {
    let best = null;
    const ov = spec.overrides || {};
    for (const m of Object.keys(ov).map(Number).sort((a, b) => a - b)) if (m <= t && ov[m][actor]) best = ov[m][actor];
    return best || spec.policies[actor];
  }

  // ------------------------------------------------------------------ one path
  function simulatePath(D, spec, prm, sh) {
    const b = {}; for (const [k, v] of Object.entries(D.baseline.values)) b[k] = +v.value;
    const central = {}; for (const [k, v] of Object.entries(D.params.params)) central[k] = +v.value;
    const T = spec.horizon, L = P + T + 1, det = spec.shock_mode === "deterministic";
    if (det) { sh = {}; for (const k of SHOCK_KEYS) sh[k] = new Float64Array(T + 1).fill(k === "chi2" ? central.oil_t_df - 2 : (k === "u_reg" || k === "u_esc") ? 1 : 0); }
    const scp = scenarioPaths(spec.scenario, T);
    const H = {};
    const nw = (name, fill = 0) => (H[name] = new Float64Array(L).fill(fill));
    const brent = nw("brent", b.brent), bh = D.baseline.brent_history;
    bh.forEach((v, k) => { brent[P - bh.length + 1 + k] = v; });
    for (let i = 0; i < P - bh.length + 1; i++) brent[i] = bh[0];
    const disrupt = nw("disrupt", b.disrupt), esc = nw("esc"), shortfall = nw("shortfall");
    const crack = nw("crack", prm.crack_base + prm.crack_disrupt * b.disrupt);
    const freight = nw("freight", prm.freight_base + prm.freight_disrupt * b.disrupt);
    const us10y = nw("us10y", b.us10y), dxy = nw("dxy"), risk = nw("risk_off", b.risk_off), gdem = nw("gdem"), food_shock = nw("food_shock", b.food_shock);
    const inr = nw("inr", b.inr), dep = nw("dep"), reserves = nw("reserves", b.reserves);
    const repo = nw("repo", b.repo), sdf = nw("sdf", b.repo - 0.25), msf = nw("msf", b.repo + 0.25);
    const liq = nw("liq", b.liq), wacr = nw("wacr", Math.min(Math.max(b.repo - prm.liq_wacr * b.liq, b.repo - 0.25), b.repo + 0.25));
    const g10 = nw("g10", b.g10), exp_infl = nw("exp_infl", b.exp_infl), deanchor = nw("deanchor");
    const retail = nw("retail_fuel", b.retail_fuel), excise = nw("excise", b.excise);
    ["crude_vol", "crude_bill", "prod_exp", "other_energy", "oil_net", "nonoil_bal", "services", "remit", "prim_inc", "ca", "fdi", "fpi", "ecb_other",
      "resid_other", "ka", "pressure", "interv", "fx_adjust", "valuation", "steril", "parity", "crude_inr", "omc_margin", "omc_loss", "lpg_loss", "comp",
      "omc_burden", "cum_omc_loss", "food_mm", "energy_mm", "core_mm", "gap", "act", "gdp_yoy", "credit_idx", "credit_yoy", "stress", "ngdp", "tax",
      "excise_rev", "other_rec", "fert", "interest_x", "capex_cut", "receipts", "expend", "fd", "debt", "fy_cum_fd", "fy_cum_ngdp", "fd_proj", "fd_target",
      "lend", "real_lend", "dec_gov_fuel", "dec_gov_fis", "dec_mpc_delta", "dec_fx_phi", "mpc_meeting", "mpc_target", "obs_cpi", "obs_core", "obs_exp",
      "obs_gdp", "obs_dep3", "obs_fd_proj", "flag_excise_exhausted", "flag_res_floor", "flag_corridor", "flag_policy_switch", "cpi_yoy", "food_yoy",
      "energy_yoy", "core_yoy"].forEach(n => nw(n));
    for (const ch of GAP_CHANNELS) nw("c_" + ch);
    H.gdp_yoy.fill(NaN);
    for (const [nm, yy] of [["food_idx", b.food_yoy], ["energy_idx", b.energy_yoy], ["core_idx", b.core_yoy]]) {
      const a = nw(nm);
      for (let i = 0; i < L; i++) a[i] = 100.0 * Math.pow(1 + yy / 100, (i - P) / 12);
      const mm = H[nm.replace("_idx", "_mm")];
      for (let i = 0; i <= P; i++) mm[i] = 100 * Math.log(1 + yy / 100) / 12;
    }
    const wf = prm.w_food, we = prm.w_energy, wc = prm.w_core;
    const cpi_idx = nw("cpi_idx");
    for (let i = 0; i < L; i++) cpi_idx[i] = wf * H.food_idx[i] + we * H.energy_idx[i] + wc * H.core_idx[i];
    for (const nm of ["cpi", "food", "energy", "core"]) { const src = nm === "cpi" ? cpi_idx : H[nm + "_idx"]; for (let i = 12; i < L; i++) H[nm + "_yoy"][i] = 100 * (src[i] / src[i - 12] - 1); }
    const act = H.act;
    for (let i = 0; i < L; i++) act[i] = (i - P) * Math.log(1.075) / 12;
    const qmean = (i) => (Math.exp(act[i - 2]) + Math.exp(act[i - 1]) + Math.exp(act[i])) / 3 / ((Math.exp(act[i - 14]) + Math.exp(act[i - 13]) + Math.exp(act[i - 12])) / 3);
    for (let i = 0; i <= P; i++) if (QUARTER_END.has(calMonth(i - P)) && i >= 14) H.gdp_yoy[i] = 100 * (qmean(i) - 1);
    H.gap.fill(b.gap); for (let i = 0; i <= P; i++) H.c_init[i] = b.gap;
    for (let i = 0; i < L; i++) { H.credit_idx[i] = Math.pow(1 + b.credit_yoy / 100, (i - P) / 12); H.credit_yoy[i] = b.credit_yoy; }
    const ngdp0m = b.ngdp_annual / 12;
    for (let i = 0; i < L; i++) H.ngdp[i] = ngdp0m * Math.exp(act[i] - act[P]) * cpi_idx[i] / 100;
    const sp_ratio = 53.5 / b.ngdp_annual;
    const exc_rev0 = b.excise * prm.litres_month * LITRE_FACTOR;
    const or_ratio = sp_ratio - b.fd_target / 100 - prm.tax_ratio - exc_rev0 / ngdp0m;
    for (let i = 0; i <= P; i++) H.fd[i] = b.fd_target / 100 * H.ngdp[i];
    H.fd_target.fill(b.fd_target); for (let i = 0; i <= P; i++) H.fd_proj[i] = b.fd_target;
    let s1 = 0, s2 = 0; for (let i = P - 6; i <= P; i++) { s1 += H.fd[i]; s2 += H.ngdp[i]; }
    H.fy_cum_fd[P] = s1; H.fy_cum_ngdp[P] = s2;
    H.debt.fill(b.debt_ratio / 100 * b.ngdp_annual);
    for (let i = 0; i <= P; i++) { H.crude_inr[i] = (brent[i] + freight[i]) * b.inr / 159; H.parity[i] = (brent[i] + crack[i] + freight[i]) * b.inr / 159; }
    const marg0 = retail[P] / (1 + prm.vat_rate) - prm.dealer_margin - excise[P] - H.parity[P];
    const lpg_cost0 = prm.lpg_price + b.lpg_loss_cyl;
    for (let i = 0; i <= P; i++) {
      H.omc_margin[i] = marg0; H.lpg_loss[i] = prm.lpg_cyl_month * b.lpg_loss_cyl / 1e5;
      H.omc_loss[i] = Math.max(0, -marg0) * prm.litres_month * LITRE_FACTOR;
    }
    const burden0 = (prm.omc_normal_margin - marg0) * prm.litres_month * LITRE_FACTOR + H.lpg_loss[P];
    for (let i = 0; i <= P; i++) H.omc_burden[i] = burden0;
    H.lend.fill(wacr[P] + prm.lend_spread); H.real_lend.fill(H.lend[P] - b.exp_infl);
    const us0 = b.us10y, g10_0 = b.g10, exp0 = b.exp_infl, brent0 = b.brent, inr0 = b.inr, repo0 = b.repo;
    const spread0 = g10_0 - us0, gap0 = b.gap, lend0 = H.lend[P], real_lend0 = H.real_lend[P];
    const remit_ref = brent[P - 6], risk0 = b.risk_off, food0 = b.food_shock;
    const floor = prm.res_floor_months * prm.imports_month;
    for (let i = 0; i <= P; i++) {
      H.crude_vol[i] = prm.crude_vol0;
      H.crude_bill[i] = prm.crude_vol0 * prm.bbl_per_t_crude * (brent[i] + freight[i]) / 1000;
      H.prod_exp[i] = prm.prod_vol0 * prm.bbl_per_t_prod * (brent[i] + crack[i]) / 1000;
      H.other_energy[i] = prm.other_energy0 * ((1 - prm.other_energy_oilshare) + prm.other_energy_oilshare * brent[i] / b.brent);
      H.oil_net[i] = H.prod_exp[i] - H.crude_bill[i] - H.other_energy[i];
      H.nonoil_bal[i] = prm.nonoil_bal0; H.services[i] = prm.services0; H.remit[i] = prm.remit0; H.prim_inc[i] = prm.prim0;
      H.ca[i] = H.oil_net[i] + H.nonoil_bal[i] + H.services[i] + H.remit[i] + H.prim_inc[i];
      H.fdi[i] = prm.fdi0; H.fpi[i] = prm.fpi_base - prm.fpi_risk * b.risk_off; H.ecb_other[i] = prm.ecb_other0; H.resid_other[i] = prm.resid_other0;
      H.ka[i] = H.fdi[i] + H.fpi[i] + H.ecb_other[i] + H.resid_other[i];
      H.pressure[i] = -(H.ca[i] + H.ka[i]); H.interv[i] = 0.5 * H.pressure[i]; H.dec_fx_phi[i] = 0.5; H.fx_adjust[i] = H.pressure[i] - H.interv[i];
    }
    const escCfg = scp.esc, h_base = prm.baseline_hazard, deesc = scp.deesc;
    const detBaseEnd = det ? medianDuration(central.baseline_hazard) : null;
    const detEscEnd = (det && escCfg) ? escCfg.start + escCfg.forced_months + medianDuration(escCfg.hazard_after) - 1 : null;
    const Lc = D.chol.calm, Ls = D.chol.stress;
    const lastValidGdp = (upto) => { for (let r = upto - 1; r >= 0; r--) if (!Number.isNaN(H.gdp_yoy[r])) return H.gdp_yoy[r]; return NaN; };

    for (let t = 1; t <= T; t++) {
      const i = P + t, cm = calMonth(t);
      // 0. decisions on published information
      const rule = policyAt(spec, t, "rbi_mpc"), meeting = MPC_MONTHS.has(cm);
      const obs_cpi = H.cpi_yoy[i - 2], obs_core = H.core_yoy[i - 2], obs_exp = exp_infl[i - 1];
      const obs_gdp = lastValidGdp(i - 2), obs_dep3 = 100 * (Math.log(inr[i - 1]) - Math.log(inr[i - 4]));
      const gap_obs = obs_gdp - 7.0;
      const it = prm.r_neutral + 4 + prm.mpc_infl_coef * (0.5 * obs_cpi + 0.5 * obs_exp - 4) + prm.mpc_gap_coef * gap_obs;
      let target;
      if (rule === "inflation_targeting") target = it;
      else if (rule === "fx_defence") target = it + (obs_dep3 > prm.mpc_fx_trigger ? 0.5 : 0.0);
      else if (rule === "look_through") target = prm.r_neutral + 4 + prm.mpc_infl_coef * (0.5 * obs_core + 0.5 * obs_exp - 4) + 0.3 * gap_obs;
      else target = repo[i - 1];
      const diff = target - repo[i - 1];
      let step = diff > 1.5 ? 0.5 : diff > 0.2 ? 0.25 : diff < -1.5 ? -0.5 : diff < -0.2 ? -0.25 : 0.0;
      if (!meeting || rule === "hold") step = 0;
      repo[i] = Math.min(Math.max(repo[i - 1] + step, 3.0), 9.0);
      sdf[i] = repo[i] - 0.25; msf[i] = repo[i] + 0.25;
      H.dec_mpc_delta[i] = repo[i] - repo[i - 1]; H.mpc_meeting[i] = meeting ? 1 : 0; H.mpc_target[i] = target;
      H.obs_cpi[i] = obs_cpi; H.obs_core[i] = obs_core; H.obs_exp[i] = obs_exp; H.obs_gdp[i] = obs_gdp; H.obs_dep3[i] = obs_dep3;
      const fis = policyAt(spec, t, "gov_fiscal");
      H.dec_gov_fis[i] = GOV_FIS.indexOf(fis);
      const fd_tgt = fiscalYear(t) === "FY27" ? b.fd_target : prm.fd_target_fy28;
      H.fd_target[i] = fd_tgt;
      const new_fy = cm === 4, months_left = (((3 - cm) % 12) + 12) % 12 + 1;
      const obs_proj = H.fd_proj[i - 1]; H.obs_fd_proj[i] = obs_proj;
      if (fis === "hold_target" && !new_fy) {
        const fy_ngdp_proj = H.fy_cum_ngdp[i - 1] + H.ngdp[i - 1] * months_left;
        const overrun = Math.max(0.0, (obs_proj - fd_tgt - 0.1) / 100 * fy_ngdp_proj);
        H.capex_cut[i] = Math.min(0.25 * prm.capex_month, prm.fis_capex_cut * overrun / months_left);
      } else H.capex_cut[i] = 0.0;

      // 1. regimes & global drivers
      const prev_d = disrupt[i - 1], prev_e = esc[i - 1];
      let d_now;
      if (det) d_now = prev_d === 1 ? (t >= detBaseEnd ? 0 : 1) : 0;
      else d_now = prev_d === 1 ? (sh.u_reg[t] >= h_base ? 1 : 0) : (sh.u_reg[t] < prm.onset_hazard ? 1 : 0);
      if (deesc !== null && t >= deesc) d_now = t === deesc ? 0 : d_now;
      let e_now = 0;
      if (escCfg) {
        const s0 = +escCfg.start, fm = +escCfg.forced_months;
        if (s0 <= t && t < s0 + fm) e_now = 1;
        else if (t >= s0 + fm) e_now = det ? (t <= detEscEnd ? 1 : 0) : (prev_e === 1 ? (sh.u_esc[t] >= escCfg.hazard_after ? 1 : 0) : 0);
        if (deesc !== null && t >= deesc) e_now = 0;
        d_now = Math.max(d_now, e_now);
        shortfall[i] = (s0 <= t && t < s0 + fm) ? (escCfg.shortfall_pct ?? 0) : 0;
      }
      disrupt[i] = d_now; esc[i] = e_now;
      const stressReg = d_now + e_now > 0, Lm = stressReg ? Ls : Lc;
      const z = [sh.z_oil[t], sh.z_us[t], sh.z_dxy[t], sh.z_risk[t], sh.z_gdem[t]];
      const eps = [0, 1, 2, 3, 4].map(k => { let s = 0; for (let m = 0; m < 5; m++) s = s + Lm[k][m] * z[m]; return s; });
      const t_scale = Math.sqrt((central.oil_t_df - 2.0) / Math.max(sh.chi2[t], 1e-9));
      const e_oil = eps[0] * t_scale;
      const off_r_now = risk0 * d_now + scp.off_risk[t], off_r_prev = risk0 * prev_d + scp.off_risk[t - 1];
      risk[i] = off_r_now + prm.risk_rho * (risk[i - 1] - off_r_prev) + prm.risk_sigma * eps[3];
      gdem[i] = scp.off_gdem[t] + prm.gdem_rho * (gdem[i - 1] - scp.off_gdem[t - 1]) + prm.gdem_sigma * eps[4];
      us10y[i] = scp.off_us[t] + prm.us_anchor + (1 - prm.us_kappa) * (us10y[i - 1] - prm.us_anchor - scp.off_us[t - 1]) + prm.us_sigma * eps[1];
      dxy[i] = dxy[i - 1] + (scp.off_dxy[t] - scp.off_dxy[t - 1]) + central.dxy_sigma * eps[2];
      food_shock[i] = scp.off_food[t] + prm.food_rho * (food_shock[i - 1] - scp.off_food[t - 1]) + prm.food_sigma * sh.e_food[t];
      const esc_prem = escCfg ? escCfg.premium : 0.0;
      const anchor = prm.oil_anchor + prm.oil_disrupt_prem * d_now + esc_prem * e_now + prm.oil_gdem_beta * gdem[i];
      const kap = (d_now !== prev_d || e_now !== prev_e) ? 0.6 : prm.oil_kappa;
      const sig = stressReg ? prm.oil_sigma_stress : prm.oil_sigma;
      const lb = Math.log(brent[i - 1]);
      brent[i] = Math.exp(lb + kap * (Math.log(Math.max(anchor, 20.0)) - lb) + sig * e_oil);
      crack[i] = prm.crack_base + prm.crack_disrupt * d_now + (escCfg ? (escCfg.crack_extra ?? 0) : 0) * e_now;
      freight[i] = prm.freight_base + prm.freight_disrupt * d_now + (escCfg ? (escCfg.freight_extra ?? 0) : 0) * e_now;

      // 2. external accounts
      H.crude_vol[i] = prm.crude_vol0 * (1 + prm.vol_elast_act * (H.gap[i - 1] - gap0) / 100) * Math.pow(brent[i] / brent0, prm.vol_elast_price) * (1 - shortfall[i] / 100);
      H.crude_bill[i] = H.crude_vol[i] * prm.bbl_per_t_crude * (brent[i] + freight[i]) / 1000;
      H.prod_exp[i] = prm.prod_vol0 * prm.bbl_per_t_prod * (brent[i] + crack[i]) / 1000;
      H.other_energy[i] = prm.other_energy0 * ((1 - prm.other_energy_oilshare) + prm.other_energy_oilshare * brent[i] / brent0);
      H.oil_net[i] = H.prod_exp[i] - H.crude_bill[i] - H.other_energy[i];
      const rel_p = 100 * Math.log(cpi_idx[i - 1] / 100) - US_INFL * (t - 1) / 12;
      let ml = 0; for (let r = i - 6; r < i; r++) ml += Math.log(inr[r]);
      const real_dep6 = 100 * (ml / 6 - Math.log(inr0)) - rel_p;
      H.nonoil_bal[i] = prm.nonoil_bal0 + prm.nonoil_gdem * gdem[i] + prm.nonoil_fx * real_dep6 - prm.nonoil_gap * (H.gap[i - 1] - gap0);
      H.services[i] = prm.services0 + prm.services_gdem * gdem[i];
      H.remit[i] = prm.remit0 * (1 + prm.remit_oil * (brent[i - 6] / remit_ref - 1));
      H.prim_inc[i] = prm.prim0 - prm.prim_us * (us10y[i] - us0);
      H.ca[i] = H.oil_net[i] + H.nonoil_bal[i] + H.services[i] + H.remit[i] + H.prim_inc[i];
      // 3. capital account
      const expdep = (dep[i - 3] + dep[i - 2] + dep[i - 1]) / 3;
      H.fdi[i] = prm.fdi0;
      H.fpi[i] = prm.fpi_base + prm.fpi_spread * ((g10[i - 1] - us10y[i - 1]) - spread0) - prm.fpi_risk * risk[i] - prm.fpi_dep * expdep + prm.fpi_gap * (H.gap[i - 1] - gap0);
      H.ecb_other[i] = prm.ecb_other0 - prm.ecb_us * (us10y[i] - us0);
      H.resid_other[i] = prm.resid_other0;
      H.ka[i] = H.fdi[i] + H.fpi[i] + H.ecb_other[i] + H.resid_other[i];
      // 4. FX market
      const pressure = -(H.ca[i] + H.ka[i]); H.pressure[i] = pressure;
      let phi = FX_OPTS[policyAt(spec, t, "rbi_fx")];
      if (spec.structure.fx_regime === "flexible") phi = Math.min(phi, 0.15);
      const near = Math.min(Math.max((reserves[i - 1] - floor) / (0.15 * floor), 0.1), 1.0);
      H.flag_res_floor[i] = near < 1.0 ? 1 : 0;
      const phi_eff = pressure > 0 ? phi * near : 0.7;
      let interv = phi_eff * pressure;
      interv = Math.min(interv, Math.max(reserves[i - 1] - 0.95 * floor, 0.0));
      H.interv[i] = interv; H.dec_fx_phi[i] = phi_eff;
      const resid = pressure - interv;
      dep[i] = resid / prm.fx_depth + 0.3 * 100 * (dxy[i] - dxy[i - 1]) + prm.fx_sigma * sh.e_fx[t];
      inr[i] = inr[i - 1] * Math.exp(dep[i] / 100);
      H.valuation[i] = -prm.res_nonusd_share * reserves[i - 1] * (dxy[i] - dxy[i - 1]);
      reserves[i] = reserves[i - 1] - interv + H.valuation[i];
      H.fx_adjust[i] = resid;
      // 5. liquidity
      const st_frac = STERIL[policyAt(spec, t, "rbi_steril")];
      const drain = interv * inr[i] / 1000.0;
      H.steril[i] = st_frac * drain;
      liq[i] = liq[i - 1] - drain + H.steril[i];
      const raw = repo[i] - prm.liq_wacr * liq[i];
      wacr[i] = Math.min(Math.max(raw, sdf[i]), msf[i]);
      H.flag_corridor[i] = (raw < sdf[i] || raw > msf[i]) ? 1 : 0;
      // 6. fuel pricing
      H.crude_inr[i] = (brent[i] + freight[i]) * inr[i] / 159;
      const parity = (brent[i] + crack[i] + freight[i]) * inr[i] / 159; H.parity[i] = parity;
      const vat = prm.vat_rate, dealer = prm.dealer_margin, normal = prm.omc_normal_margin, lit = prm.litres_month;
      const lpg_cost = lpg_cost0 * Math.pow(brent[i] / brent0, 0.8) * (inr[i] / inr0);
      const lpg_loss = Math.max(0.0, lpg_cost - prm.lpg_price) * prm.lpg_cyl_month / 1e5; H.lpg_loss[i] = lpg_loss;
      const gf = policyAt(spec, t, "gov_fuel");
      let switched = false;
      if (gf === "adaptive_threshold") { switched = H.cum_omc_loss[i - 1] > prm.gov_loss_tolerance; H.flag_policy_switch[i] = switched ? 1 : 0; }
      const r_prev = retail[i - 1], x_prev = excise[i - 1];
      const full_price = (parity + normal + dealer + x_prev) * (1 + vat);
      let new_r = r_prev, new_x = x_prev, comp_share = 0;
      if (gf === "full_passthrough") new_r = full_price;
      else if (gf === "freeze_budget_comp") comp_share = 1.0;
      else if (gf === "partial_50" || gf === "adaptive_threshold") {
        const m = gf === "partial_50" ? true : switched;
        new_r = m ? r_prev + 0.5 * (full_price - r_prev) : r_prev;
        comp_share = (m && gf === "partial_50") ? 0.5 : 0.0;
      } else if (gf === "excise_cut") {
        const marg_frozen = r_prev / (1 + vat) - dealer - x_prev - parity;
        const need = Math.max(0.0, -marg_frozen), cut = Math.min(need, x_prev);
        H.flag_excise_exhausted[i] = need > x_prev + 1e-9 ? 1 : 0;
        const restore = marg_frozen > normal + 2.0 ? Math.min(b.excise - x_prev, marg_frozen - normal - 2.0) : 0.0;
        new_x = x_prev - cut + Math.max(restore, 0.0);
      }
      H.dec_gov_fuel[i] = GOV_FUEL.indexOf(gf);
      retail[i] = new_r; excise[i] = new_x;
      const margin = new_r / (1 + vat) - dealer - new_x - parity; H.omc_margin[i] = margin;
      const omc_loss = Math.max(0.0, -margin) * lit * LITRE_FACTOR; H.omc_loss[i] = omc_loss;
      H.comp[i] = comp_share * (omc_loss + lpg_loss);
      H.omc_burden[i] = (normal - margin) * lit * LITRE_FACTOR + lpg_loss - H.comp[i];
      H.cum_omc_loss[i] = H.cum_omc_loss[i - 1] + omc_loss + lpg_loss - H.comp[i] - Math.max(0, margin) * lit * LITRE_FACTOR;
      // 7. prices & expectations
      const fuel_chg = 100 * Math.log(retail[i] / retail[i - 1]);
      H.energy_mm[i] = prm.energy_auto_share * fuel_chg + (1 - prm.energy_auto_share) * ADMIN_ENERGY_TREND / 12;
      H.food_mm[i] = prm.food_trend / 12 + food_shock[i] / 12 + prm.food_fuel * fuel_chg;
      let d6 = 0; for (let r = i - 6; r < i; r++) d6 += dep[r];
      let o6 = 0; for (let r = i - 6; r < i; r++) o6 += 100 * (Math.log(H.crude_inr[r]) - Math.log(H.crude_inr[r - 1]));
      H.core_mm[i] = prm.core_lambda * H.core_mm[i - 1] + (1 - prm.core_lambda) * exp_infl[i - 1] / 12 + prm.core_gap * H.gap[i - 1] / 12 + prm.core_fx * (d6 / 6) + prm.core_oil * (o6 / 6);
      for (const nm of ["food", "energy", "core"]) {
        H[nm + "_idx"][i] = H[nm + "_idx"][i - 1] * Math.exp(H[nm + "_mm"][i] / 100);
        H[nm + "_yoy"][i] = 100 * (H[nm + "_idx"][i] / H[nm + "_idx"][i - 12] - 1);
      }
      cpi_idx[i] = wf * H.food_idx[i] + we * H.energy_idx[i] + wc * H.core_idx[i];
      H.cpi_yoy[i] = 100 * (cpi_idx[i] / cpi_idx[i - 12] - 1);
      let theta;
      if (spec.structure.expectations === "anchored") { theta = prm.exp_theta * 0.5; deanchor[i] = 0; }
      else {
        const c = H.cpi_yoy;
        const hi = c[i - 1] > 6 && c[i - 2] > 6 && c[i - 3] > 6, lo = c[i - 1] < 5.5 && c[i - 2] < 5.5 && c[i - 3] < 5.5;
        deanchor[i] = hi ? 1 : lo ? 0 : deanchor[i - 1];
        theta = deanchor[i] === 1 ? prm.exp_theta_deanchor : prm.exp_theta;
      }
      exp_infl[i] = exp_infl[i - 1] + theta * (H.cpi_yoy[i - 1] - exp_infl[i - 1]);
      // 8. output gap
      H.lend[i] = wacr[i] + prm.lend_spread; H.real_lend[i] = H.lend[i] - exp_infl[i];
      const rr_dev = t >= 3 ? (wacr[i - 3] - exp_infl[i - 3]) - (wacr[P] - exp_infl[P]) : 0;
      const ngdp_prev = H.ngdp[i - 1];
      const imp = {
        init: 0.0, rate: -prm.a_rate * rr_dev, fuel_hh: -prm.a_hh_fuel * prm.fuel_budget_share * fuel_chg,
        omc: -prm.a_omc * (H.omc_burden[i] - burden0) / ngdp_prev * 100,
        input: -prm.a_input * 100 * Math.log(H.crude_inr[i] / H.crude_inr[i - 1]),
        gdem: prm.a_gdem * gdem[i], risk: -prm.a_risk * (risk[i] - risk0), stress: -prm.a_stress * H.stress[i - 1],
        food: -prm.a_food * (food_shock[i] - food0), fiscal: -prm.a_fiscal * H.capex_cut[i] / ngdp_prev * 100,
        phys: -prm.a_phys * shortfall[i], noise: prm.gap_sigma * sh.e_gap[t],
      };
      let g = 0;
      for (const ch of GAP_CHANNELS) { H["c_" + ch][i] = prm.gap_rho * H["c_" + ch][i - 1] + imp[ch]; g += H["c_" + ch][i]; }
      H.gap[i] = g;
      act[i] = act[i - 1] + prm.pot_growth / 1200 + (H.gap[i] - H.gap[i - 1]) / 100;
      if (QUARTER_END.has(cm)) H.gdp_yoy[i] = 100 * (qmean(i) - 1);
      // 9. fiscal
      H.ngdp[i] = ngdp0m * Math.exp(act[i] - act[P]) * cpi_idx[i] / 100;
      const ng = H.ngdp[i];
      H.tax[i] = prm.tax_ratio * ng * (1 + (prm.tax_buoy - 1) * H.gap[i] / 100);
      H.excise_rev[i] = excise[i] * lit * LITRE_FACTOR;
      H.other_rec[i] = or_ratio * ng;
      H.fert[i] = prm.fert_oil * (brent[i] - brent0) / 10;
      H.interest_x[i] = prm.fy_issuance / 12 * t * (g10[i - 1] - g10_0) / 100 / 12;
      H.receipts[i] = H.tax[i] + H.excise_rev[i] + H.other_rec[i];
      H.expend[i] = sp_ratio * ng + H.fert[i] + H.interest_x[i] + H.comp[i] - H.capex_cut[i];
      H.fd[i] = H.expend[i] - H.receipts[i];
      H.debt[i] = H.debt[i - 1] + H.fd[i];
      if (new_fy) { H.fy_cum_fd[i] = H.fd[i]; H.fy_cum_ngdp[i] = ng; }
      else { H.fy_cum_fd[i] = H.fy_cum_fd[i - 1] + H.fd[i]; H.fy_cum_ngdp[i] = H.fy_cum_ngdp[i - 1] + ng; }
      const rem = months_left - 1;
      H.fd_proj[i] = 100 * (H.fy_cum_fd[i] + H.fd[i] * rem) / (H.fy_cum_ngdp[i] + ng * rem);
      // 10. 10Y
      const fair = g10_0 + prm.g10_repo * (repo[i] - repo0) + prm.g10_us * (us10y[i] - us0) + prm.g10_fis * (H.fd_proj[i - 1] - H.fd_target[i - 1]) + prm.g10_exp * (exp_infl[i] - exp0);
      g10[i] = g10[i - 1] + prm.g10_kappa * (fair - g10[i - 1]) + prm.g10_sigma * sh.e_g10[t];
      // 11. credit & stress
      H.stress[i] = prm.stress_rho * H.stress[i - 1] + prm.stress_rate * (H.real_lend[i] - real_lend0) + prm.stress_gap * Math.max(0.0, -H.gap[i]);
      const cmm = prm.credit_trend / 12 + prm.credit_gap * (H.gap[i] - gap0) / 12 - prm.credit_rate * (H.lend[i] - lend0) / 12 - prm.credit_stress * H.stress[i] / 12;
      H.credit_idx[i] = H.credit_idx[i - 1] * Math.exp(cmm / 100);
      H.credit_yoy[i] = 100 * (H.credit_idx[i] / H.credit_idx[i - 12] - 1);
    }
    H._meta = { burden0, floor };
    return H;
  }

  // ------------------------------------------------------------------ many paths
  const KEEP = ["brent", "inr", "reserves", "repo", "g10", "cpi_yoy", "core_yoy", "food_yoy", "gdp_yoy", "gap", "retail_fuel", "omc_margin",
    "cum_omc_loss", "fd_proj", "ca", "pressure", "interv", "credit_yoy", "exp_infl", "disrupt", "esc", "comp", "fert", "interest_x", "excise_rev",
    "excise", "capex_cut", "wacr", "liq", "parity"];
  function simulate(D, spec, opts = {}) {
    const n = spec.shock_mode === "deterministic" && spec.param_mode === "central" ? 1 : spec.n_paths;
    const off = spec.path_offset || 0, df = +D.params.params.oil_t_df.value;
    const keep = opts.full ? null : (opts.keep || KEEP);
    const paths = [], params = [], idx = [];
    for (let j = 0; j < n; j++) {
      const pi = off + j;
      const prm = opts.prm ? opts.prm[j] : sampleParams(D, spec.seed, pi, spec.param_mode, spec.param_overrides);
      const sh = opts.shocks ? opts.shocks[j] : drawShocks(spec.seed, pi, spec.horizon, df);
      const H = simulatePath(D, spec, prm, sh);
      if (keep) { const k2 = {}; for (const v of keep) k2[v] = H[v]; k2._meta = H._meta; paths.push(k2); } else paths.push(H);
      params.push(prm); idx.push(pi);
    }
    return { spec, T: spec.horizon, n, paths, params, pathIdx: idx, months: Array.from({ length: spec.horizon + 1 }, (_, t) => monthLabel(t)) };
  }
  // value of var at month t (0..T) for path j
  const val = (res, v, j, t) => res.paths[j][v][P + t];

  // ------------------------------------------------------------------ risk statistics
  function quantile(sorted, q) { if (!sorted.length) return NaN; const h = (sorted.length - 1) * q / 100, lo = Math.floor(h), hi = Math.ceil(h); return sorted[lo] + (sorted[hi] - sorted[lo]) * (h - lo); }
  function bands(res, v, qs = [5, 25, 50, 75, 95]) {
    const out = {}; qs.forEach(q => (out[q] = new Array(res.T + 1)));
    for (let t = 0; t <= res.T; t++) {
      const xs = []; for (let j = 0; j < res.n; j++) { const x = val(res, v, j, t); if (!Number.isNaN(x)) xs.push(x); }
      xs.sort((a, b) => a - b); qs.forEach(q => (out[q][t] = xs.length ? quantile(xs, q) : NaN));
    }
    return out;
  }
  function wilson(k, n, z = 1.96) { if (!n) return [NaN, NaN]; const p = k / n, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [Math.max(0, c - h), Math.min(1, c + h)]; }
  function maxRun(b) { let best = 0, cur = 0; for (const x of b) { cur = x ? cur + 1 : 0; best = Math.max(best, cur); } return best; }
  function evaluateThreshold(res, th) {
    const months = []; for (let t = 1; t <= res.T; t++) {
      if (th.observe === "quarterly" && !QUARTER_END.has(calMonth(t))) continue;
      if (th.observe === "fy_end" && calMonth(t) !== 3) continue;
      months.push(t);
    }
    const hits = [], first = [], dur = [], rec = [], cens = [];
    for (let j = 0; j < res.n; j++) {
      const B = months.map(t => { const x = val(res, th.var, j, t); return !Number.isNaN(x) && (th.op === ">" ? x > th.level : x < th.level); });
      const any = B.some(Boolean);
      hits.push(th.kind === "endpoint" ? B[B.length - 1] : th.kind === "duration" ? maxRun(B) >= (th.min_months || 3) : any);
      const f = B.indexOf(true); first.push(f >= 0 ? months[f] : NaN); dur.push(maxRun(B));
      if (any) {
        const k = th.observe === "monthly" || !th.observe ? (th.recover_months || 3) : 1; let found = false;
        for (let s = f + 1; s <= B.length - k; s++) if (!B.slice(s, s + k).some(Boolean)) { rec.push(months[s + k - 1] - months[f]); found = true; break; }
        if (!found) { rec.push(NaN); cens.push(j); }
      }
    }
    const k = hits.filter(Boolean).length;
    const ft = first.filter(x => !Number.isNaN(x)).sort((a, b) => a - b);
    return { frequency: k / res.n, hits: k, n: res.n, ci95: wilson(k, res.n), hit: hits, first, maxDuration: dur,
      medianFirst: ft.length ? quantile(ft, 50) : NaN, breached: first.filter(x => !Number.isNaN(x)).length, notRecovered: cens.length };
  }
  function pathMetrics(res) {
    const m = { peak_cpi: [], peak_inr: [], min_reserves: [], min_gdp_yoy: [], min_gap: [], peak_repo: [], peak_g10: [], cum_omc_loss: [], fd_fy27: [], peak_brent: [], end_cpi: [], end_inr: [] };
    const fyEnd = (() => { for (let t = 1; t <= res.T; t++) if (fiscalYear(t) === "FY27" && calMonth(t) === 3) return t; return null; })();
    for (let j = 0; j < res.n; j++) {
      const s = (v, f) => { let r = f === "max" ? -Infinity : Infinity, ok = false; for (let t = 1; t <= res.T; t++) { const x = val(res, v, j, t); if (!Number.isNaN(x)) { ok = true; r = f === "max" ? Math.max(r, x) : Math.min(r, x); } } return ok ? r : NaN; };
      m.peak_cpi.push(s("cpi_yoy", "max")); m.peak_inr.push(s("inr", "max")); m.min_reserves.push(s("reserves", "min")); m.min_gdp_yoy.push(s("gdp_yoy", "min"));
      m.min_gap.push(s("gap", "min")); m.peak_repo.push(s("repo", "max")); m.peak_g10.push(s("g10", "max")); m.peak_brent.push(s("brent", "max"));
      m.cum_omc_loss.push(val(res, "cum_omc_loss", j, res.T)); m.fd_fy27.push(fyEnd ? val(res, "fd_proj", j, fyEnd) : NaN);
      m.end_cpi.push(val(res, "cpi_yoy", j, res.T)); m.end_inr.push(val(res, "inr", j, res.T));
    }
    return m;
  }
  const ADVERSE = { peak_cpi: 1, peak_inr: 1, min_reserves: -1, min_gdp_yoy: -1, min_gap: -1, peak_g10: 1 };
  function representativePaths(res) {
    const m = pathMetrics(res), n = res.n, s = new Array(n).fill(0), cnt = new Array(n).fill(0);
    for (const [k, sign] of Object.entries(ADVERSE)) {
      const x = m[k], good = x.filter(v => !Number.isNaN(v)); if (!good.length) continue;
      const mu = good.reduce((a, b) => a + b, 0) / good.length, sd = Math.sqrt(good.reduce((a, b) => a + (b - mu) ** 2, 0) / good.length) || 1;
      for (let j = 0; j < n; j++) if (!Number.isNaN(x[j])) { s[j] += sign * (x[j] - mu) / sd; cnt[j]++; }
    }
    const sev = s.map((v, j) => cnt[j] ? v / cnt[j] : 0), srt = [...sev].sort((a, b) => a - b), out = {};
    for (const [name, q] of [["calm", 10], ["typical", 50], ["rough", 90], ["very rough", 98]]) {
      const target = quantile(srt, q); let best = 0, bd = Infinity;
      sev.forEach((v, j) => { const d = Math.abs(v - target); if (d < bd) { bd = d; best = j; } });
      out[name] = { j: best, path: res.pathIdx[best], severity: sev[best], pct: q };
    }
    return out;
  }
  const median = a => { const x = a.filter(v => !Number.isNaN(v)).sort((p, q) => p - q); return quantile(x, 50); };
  const pct = (a, q) => { const x = a.filter(v => !Number.isNaN(v)).sort((p, r) => p - r); return quantile(x, q); };

  // ------------------------------------------------------------------ who pays
  function burdenPath(res, j) {
    const T = res.T, H = res.paths[j], prm = res.params[j];
    let fiscal = 0, capex = 0;
    for (let t = 1; t <= T; t++) { const i = P + t; fiscal += H.comp[i] + H.fert[i] + H.interest_x[i] - (H.excise_rev[i] - H.excise[P] * prm.litres_month * 1e-3) - H.capex_cut[i]; capex += H.capex_cut[i]; }
    let minRes = Infinity, peakInr = -Infinity, peakCpi = -Infinity, gapLoss = 0, minG = Infinity, pr = -Infinity, pg = -Infinity;
    for (let t = 1; t <= T; t++) { const i = P + t; minRes = Math.min(minRes, H.reserves[i]); peakInr = Math.max(peakInr, H.inr[i]); peakCpi = Math.max(peakCpi, H.cpi_yoy[i]);
      gapLoss += Math.min(H.gap[i], 0); if (!Number.isNaN(H.gdp_yoy[i])) minG = Math.min(minG, H.gdp_yoy[i]); pr = Math.max(pr, H.repo[i]); pg = Math.max(pg, H.g10[i]); }
    return {
      pump: 100 * (H.retail_fuel[P + T] / H.retail_fuel[P] - 1), pumpPeak: 100 * (Math.max(...Array.from(H.retail_fuel.slice(P + 1))) / H.retail_fuel[P] - 1),
      peakCpi, omc: H.cum_omc_loss[P + T], fiscal, capex, fd27: T >= 5 ? H.fd_proj[P + 5] : NaN, reservesUsed: H.reserves[P] - minRes,
      rupee: 100 * (peakInr / H.inr[P] - 1), gapLoss, minGdp: minG === Infinity ? NaN : minG, peakRepo: pr, peakG10: pg,
    };
  }
  function burden(res) {
    const all = []; for (let j = 0; j < res.n; j++) all.push(burdenPath(res, j));
    const out = {}; for (const k of Object.keys(all[0])) out[k] = median(all.map(a => a[k]));
    return out;
  }

  // ------------------------------------------------------------------ branch & compare & stress
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function onePath(D, spec, pathIndex, overrides) {
    const s = clone(spec); s.n_paths = 1; s.path_offset = pathIndex; if (overrides) s.overrides = overrides;
    return simulate(D, s, { full: true });
  }
  function compare(D, spec, bundles) {
    const out = {};
    for (const [name, pol] of Object.entries(bundles)) { const s = clone(spec); s.policies = Object.assign({}, spec.policies, pol); const r = simulate(D, s); out[name] = { res: r, metrics: pathMetrics(r), burden: burden(r) }; }
    return out;
  }
  function stressScenario(base, g) {
    const sc = clone(base); sc.shocks = (sc.shocks || []).filter(x => !["oil_escalation", "global_tightening", "food_supply"].includes(x.type));
    if (g.oil > 0) sc.shocks.push({ type: "oil_escalation", start: 1, premium: g.oil, forced_months: g.months, hazard_after: 0.2, shortfall_pct: 3 * g.oil / 40, freight_extra: 6 * g.oil / 40, crack_extra: 8 * g.oil / 40, risk_impulse: g.oil / 40 });
    if (g.glob > 0) sc.shocks.push({ type: "global_tightening", start: 1, months: 9, us10y: 0.5 * g.glob, dxy_pct: 3 * g.glob, risk: g.glob, gdem: -g.glob });
    if (g.food > 0) sc.shocks.push({ type: "food_supply", start: 3, months: 5, magnitude: g.food });
    return sc;
  }
  function reverseStress(D, spec, conds, policies) {
    const found = []; let tested = 0;
    for (const oil of [0, 20, 40, 60]) for (const months of [1, 3, 6]) for (const glob of [0, 1, 2]) for (const food of [0, 4, 8]) {
      if (oil === 0 && months !== 1) continue;
      for (const fuel of policies || [spec.policies.gov_fuel]) {
        const s = clone(spec); s.scenario = stressScenario(spec.scenario, { oil, months, glob, food }); s.policies.gov_fuel = fuel;
        s.n_paths = 1; s.param_mode = "central"; s.shock_mode = "deterministic"; s.path_offset = 0;
        const r = simulate(D, s); tested++;
        if (conds.every(c => evaluateThreshold(r, c).frequency === 1)) found.push({ oil, months, glob, food, fuel, size: +(oil / 40 + glob / 1.5 + food / 6 + (oil ? months / 3 : 0) * 0.25).toFixed(2) });
      }
    }
    found.sort((a, b) => a.size - b.size);
    return { found, tested };
  }

  root.IndiaSim = { P, simulate, simulatePath, sampleParams, drawShocks, scenarioPaths, bands, evaluateThreshold, pathMetrics, representativePaths,
    burden, burdenPath, onePath, compare, reverseStress, wilson, median, pct, monthLabel, monthShort, calMonth, fiscalYear, GAP_CHANNELS, GOV_FUEL, val };
  if (typeof module !== "undefined") module.exports = root.IndiaSim;
})(typeof window !== "undefined" ? window : globalThis);
