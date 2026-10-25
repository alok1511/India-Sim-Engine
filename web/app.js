/* India Sim Engine - guided interface. Pure DOM, no framework. Numbers come only from engine.js. */
(function () {
  "use strict";
  const D = window.SIM_DATA, S = window.IndiaSim, P = S.P;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") el.className = v; else if (k === "html") el.innerHTML = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v); else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat()) if (kid !== null && kid !== undefined && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    return el;
  };

  // ------------------------------------------------------------------ plain language
  const SCEN = {
    reference: { name: "Nothing new", line: "Today's Gulf disruption fades at its own pace. The comparison point for everything else." },
    oil_escalation: { name: "Hormuz escalation", line: "Shipping through the Strait of Hormuz is disrupted from November. Oil jumps; some supply is lost." },
    ceasefire: { name: "Ceasefire", line: "The conflict ends in December. Oil prices fall back quickly." },
    global_tightening: { name: "World slows, US rates rise", line: "US interest rates and the dollar rise, investors turn nervous and world demand weakens." },
    food_stress: { name: "Monsoon fails in 2027", line: "A poor 2027 monsoon pushes food prices up from July 2027." },
    combined_stress: { name: "Escalation and world slowdown", line: "Hormuz escalation and a global slowdown at the same time." },
  };
  const SCEN_ORDER = ["reference", "oil_escalation", "ceasefire", "global_tightening", "food_stress", "combined_stress"];
  const POL = {
    gov_fuel: { q: "Petrol and diesel prices", opts: {
      freeze_omc_absorb: ["Keep frozen. Oil companies take the loss", "Today's policy"],
      full_passthrough: ["Pass the full cost on at the pump", ""],
      partial_50: ["Pass half on; the Budget covers half", ""],
      freeze_budget_comp: ["Keep frozen. The Budget pays oil companies", ""],
      excise_cut: ["Cut fuel tax to cushion it", "Little room left: tax was cut in March"],
      adaptive_threshold: ["Freeze until losses get too big, then pass half on", ""] } },
    rbi_mpc: { q: "RBI interest rates", opts: {
      inflation_targeting: ["Focus on inflation (the normal approach)", "Default"],
      fx_defence: ["Also raise rates to defend the rupee", ""],
      look_through: ["Look past fuel prices; watch core prices", ""],
      hold: ["Keep rates where they are", "For comparison"] } },
    rbi_fx: { q: "RBI selling dollars to steady the rupee", opts: {
      heavy: ["Heavily (about 3/4 of the pressure)", "Today's approach"],
      moderate: ["Moderately (about half)", ""],
      light: ["Lightly (about 1/4); let the rupee move", ""] } },
    gov_fiscal: { q: "Government budget", opts: {
      accommodate: ["Let the deficit absorb the cost", "Default"],
      hold_target: ["Hold the deficit target by cutting capital spending", ""] } },
    rbi_steril: { q: "When RBI sells dollars, cash leaves the banks. Put it back?", opts: {
      half: ["Put back half", "Default"], none: ["Don't put it back", ""], full: ["Put it all back", ""] } },
  };
  const STRUCT = {
    expectations: { q: "How people form inflation expectations", opts: { adaptive: "They can lose faith if inflation stays above 6%", anchored: "They stay anchored to RBI's target" } },
    fx_regime: { q: "How much RBI is willing to manage the rupee", opts: { managed: "Managed (as chosen above)", flexible: "Mostly free-floating (caps selling at 15%)" } },
  };
  const VARS = {
    brent: { label: "Oil price (Brent)", unit: "usd", fmt: v => `$${v.toFixed(0)}`, theme: "World & oil" },
    inr: { label: "Rupee per US dollar", unit: "inr", fmt: v => `₹${v.toFixed(1)}`, theme: "Rupee & dollars" },
    reserves: { label: "FX reserves", fmt: v => `$${v.toFixed(0)}bn`, theme: "Rupee & dollars" },
    cpi_yoy: { label: "Inflation (CPI)", fmt: v => `${v.toFixed(1)}%`, theme: "Prices" },
    core_yoy: { label: "Core inflation (excl. food & fuel)", fmt: v => `${v.toFixed(1)}%`, theme: "Prices" },
    food_yoy: { label: "Food inflation", fmt: v => `${v.toFixed(1)}%`, theme: "Prices" },
    gdp_yoy: { label: "GDP growth", fmt: v => `${v.toFixed(1)}%`, theme: "Growth & budget" },
    repo: { label: "RBI repo rate", fmt: v => `${v.toFixed(2)}%`, theme: "Banks & rates" },
    g10: { label: "10-year government bond yield", fmt: v => `${v.toFixed(2)}%`, theme: "Banks & rates" },
    retail_fuel: { label: "Pump price (petrol/diesel blend, Delhi)", fmt: v => `₹${v.toFixed(1)}/L`, theme: "Prices" },
    omc_margin: { label: "Oil companies' margin per litre", fmt: v => `₹${v.toFixed(1)}/L`, theme: "Prices" },
    cum_omc_loss: { label: "Oil companies' losses since Oct 2026", fmt: v => `₹${v.toFixed(2)} lakh cr`, theme: "Prices" },
    fd_proj: { label: "Central government deficit (this year)", fmt: v => `${v.toFixed(2)}% of GDP`, theme: "Growth & budget" },
    gap: { label: "Economy vs its normal pace", fmt: v => `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`, theme: "Growth & budget" },
  };
  const GAP_PLAIN = { init: "momentum from before", rate: "higher interest rates", fuel_hh: "fuel bills squeezing households", omc: "oil companies cutting investment",
    input: "costlier inputs for firms", gdem: "weaker world demand", risk: "global nervousness", stress: "borrower stress", food: "food prices squeezing rural incomes",
    fiscal: "government spending cuts", phys: "fuel shortages", noise: "other, random factors" };
  const CA_PLAIN = { oil_net: "net oil & gas trade", nonoil_bal: "other goods trade", services: "services exports (IT etc.)", remit: "remittances from abroad", prim_inc: "interest & dividends abroad" };

  // ------------------------------------------------------------------ state
  const DEFAULT = () => ({ sid: "oil_escalation", shocks: JSON.parse(JSON.stringify(D.scenarios)), policies: Object.assign({}, D.scenarios.oil_escalation.policies),
    structure: { expectations: "adaptive", fx_regime: "managed" }, n: 600, seed: 20261025, paramMode: "sampled", future: "typical", month: 1, cmpGroup: "gov_fuel" });
  let st = DEFAULT();
  try { const saved = JSON.parse(localStorage.getItem("indiasim-ui") || "null"); if (saved && saved.v === 2) st = Object.assign(st, saved.st); } catch (e) { /* storage unavailable */ }
  const save = () => { try { localStorage.setItem("indiasim-ui", JSON.stringify({ v: 2, st })); } catch (e) { /* ignore */ } };

  function spec(over = {}) {
    const sc = JSON.parse(JSON.stringify(st.shocks[over.sid || st.sid]));
    return Object.assign({ scenario: sc, policies: Object.assign({}, st.policies), structure: Object.assign({}, st.structure), horizon: 24, n_paths: st.n,
      seed: st.seed, param_mode: st.paramMode, shock_mode: "stochastic", path_offset: 0, overrides: {}, param_overrides: {} }, over.spec || {});
  }
  const cache = new Map();
  function run(sp) { const key = JSON.stringify(sp); if (!cache.has(key)) { if (cache.size > 30) cache.clear(); cache.set(key, S.simulate(D, sp)); } return cache.get(key); }

  // ------------------------------------------------------------------ formatting
  const f1 = v => (Number.isFinite(v) ? v.toFixed(1) : "–");
  const lakh = v => `${v < 0 ? "−" : ""}₹${Math.abs(v).toFixed(2)} lakh crore`;
  const lcr = (v, d = 1) => `${v < 0 ? "−" : ""}₹${Math.abs(v).toFixed(d)} L cr`;
  const crore = v => `₹${Math.round(v * 1e5).toLocaleString("en-IN")} crore`;
  const of100 = p => p >= 0.995 ? "every one of the" : p < 0.005 ? "none of the" : `${Math.round(p * 100)} in 100`;
  const ms = t => S.monthShort(t);
  const monthLong = t => { const [y, m] = S.monthLabel(t).split("-"); return `${["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][+m - 1]} ${y}`; };

  // ------------------------------------------------------------------ charts
  function niceTicks(lo, hi, n = 5) {
    const span = hi - lo || 1, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw))), norm = raw / mag;
    const step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag;
    const out = []; for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10)); return out;
  }
  function fanChart(box, o) {
    const W = 640, H = 240, L = 54, R = 14, T = 12, B = 30, T1 = o.months.length - 1;
    const xs = t => L + (W - L - R) * t / T1;
    const pts = [];
    const pushArr = a => a && a.forEach(v => Number.isFinite(v) && pts.push(v));
    if (o.bands) { pushArr(o.bands[5]); pushArr(o.bands[95]); } pushArr(o.median); pushArr(o.ref); pushArr(o.alt);
    if (Number.isFinite(o.t0)) pts.push(o.t0); (o.thr || []).forEach(th => pts.push(th.v));
    let lo = Math.min(...pts), hi = Math.max(...pts); const pad = (hi - lo) * 0.08 || 1; lo -= pad; hi += pad;
    const ys = v => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
    const ticks = niceTicks(lo, hi, 4).filter(v => v >= lo && v <= hi);
    const fin = (a, t) => a && Number.isFinite(a[t]);
    const line = a => { let d = "", on = false; for (let t = 0; t <= T1; t++) { if (!fin(a, t)) { if (!o.quarterly) on = false; continue; } d += `${on ? "L" : "M"}${xs(t).toFixed(1)},${ys(a[t]).toFixed(1)}`; on = true; } return d; };
    const area = (a, b) => { const idx = []; for (let t = 0; t <= T1; t++) if (fin(a, t) && fin(b, t)) idx.push(t); if (!idx.length) return "";
      return "M" + idx.map(t => `${xs(t).toFixed(1)},${ys(a[t]).toFixed(1)}`).join("L") + "L" + idx.slice().reverse().map(t => `${xs(t).toFixed(1)},${ys(b[t]).toFixed(1)}`).join("L") + "Z"; };
    let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${o.aria || ""}"><g class="grid">`;
    ticks.forEach(v => { s += `<line x1="${L}" x2="${W - R}" y1="${ys(v).toFixed(1)}" y2="${ys(v).toFixed(1)}"/>`; });
    s += `</g>`;
    ticks.forEach(v => { s += `<text x="${L - 6}" y="${(ys(v) + 4).toFixed(1)}" text-anchor="end">${o.tick ? o.tick(v) : v}</text>`; });
    for (let t = 0; t <= T1; t += 3) s += `<text x="${xs(t).toFixed(1)}" y="${H - 8}" text-anchor="middle">${o.months[t]}</text>`;
    (o.thr || []).forEach(th => { if (th.v >= lo && th.v <= hi) s += `<line class="thr" x1="${L}" x2="${W - R}" y1="${ys(th.v).toFixed(1)}" y2="${ys(th.v).toFixed(1)}"/><text class="thr-label" x="${W - R}" y="${(ys(th.v) - 4).toFixed(1)}" text-anchor="end">${th.label}</text>`; });
    if (o.bands) { s += `<path class="band-l" d="${area(o.bands[95], o.bands[5])}"/><path class="band-d" d="${area(o.bands[75], o.bands[25])}"/>`; }
    if (o.ref) s += `<path class="ref" d="${line(o.ref)}"/>`;
    s += `<path class="med ${o.cls || ""}" d="${line(o.median)}"/>`;
    if (o.quarterly) for (let t = 0; t <= T1; t++) if (fin(o.median, t)) s += `<circle class="dot" cx="${xs(t).toFixed(1)}" cy="${ys(o.median[t]).toFixed(1)}" r="3"/>`;
    if (o.alt) s += `<path class="alt" d="${line(o.alt)}"/>`;
    if (Number.isFinite(o.t0)) s += `<circle class="t0" cx="${xs(0)}" cy="${ys(o.t0).toFixed(1)}" r="5"/>`;
    if (o.marker !== undefined && o.marker !== null) s += `<line class="marker" x1="${xs(o.marker)}" x2="${xs(o.marker)}" y1="${T}" y2="${H - B}"/>`;
    s += `<line class="cursor" x1="0" x2="0" y1="${T}" y2="${H - B}" visibility="hidden"/></svg>`;
    box.innerHTML = s;
    const svg = box.querySelector("svg"), cur = svg.querySelector(".cursor");
    const tip = o.tipEl;
    const showAt = t => {
      if (!tip) return;
      const parts = [`<b>${o.months[t]}</b>`];
      if (fin(o.median, t)) parts.push(`${o.bands ? "typical" : "this future"} <b>${o.fmt(o.median[t])}</b>`);
      if (o.bands && fin(o.bands[25], t)) parts.push(`half of futures ${o.fmt(o.bands[25][t])}–${o.fmt(o.bands[75][t])}`, `9 in 10: ${o.fmt(o.bands[5][t])}–${o.fmt(o.bands[95][t])}`);
      if (fin(o.ref, t)) parts.push(`${o.refLabel || "nothing new"} ${o.fmt(o.ref[t])}`);
      if (fin(o.alt, t)) parts.push(`${o.altLabel || "your change"} <b>${o.fmt(o.alt[t])}</b>`);
      tip.innerHTML = parts.join(" · ");
    };
    svg.addEventListener("pointermove", e => {
      const r = svg.getBoundingClientRect(), x = (e.clientX - r.left) / r.width * W;
      let t = Math.round((x - L) / (W - L - R) * T1); t = Math.max(0, Math.min(T1, t));
      if (o.quarterly) { let best = t, bd = 99; for (let k = 0; k <= T1; k++) if (fin(o.median, k) && Math.abs(k - t) < bd) { bd = Math.abs(k - t); best = k; } t = best; }
      cur.setAttribute("x1", xs(t)); cur.setAttribute("x2", xs(t)); cur.setAttribute("visibility", "visible"); showAt(t);
    });
    svg.addEventListener("pointerleave", () => { cur.setAttribute("visibility", "hidden"); if (tip && o.defaultTip) tip.innerHTML = o.defaultTip; });
    if (tip && o.defaultTip) tip.innerHTML = o.defaultTip;
  }
  function series(res, v, j) { return Array.from({ length: res.T + 1 }, (_, t) => S.val(res, v, j, t)); }

  // ------------------------------------------------------------------ navigation
  const CHAPTERS = [["today", "Today"], ["whatif", "What if"], ["story", "One future"], ["choices", "Compare choices"], ["learn", "Learn"]];
  function go(id, push = true) {
    if (!CHAPTERS.some(c => c[0] === id)) id = "today";
    st.section = id; save();
    $$("nav.chapters a").forEach(a => a.setAttribute("aria-current", a.dataset.id === id ? "page" : "false"));
    $$("section.page").forEach(s => (s.hidden = s.id !== "p-" + id));
    $(".ribbon").hidden = id === "today" || id === "learn";
    if (push) { try { history.replaceState(null, "", "#" + id); } catch (e) { /* ignore */ } }
    window.scrollTo({ top: 0 });
    if (id === "whatif") ensureMain(); if (id === "story") ensureMain(() => renderStory()); if (id === "choices") renderChoices(); if (id === "learn") renderLearn();
  }
  function ribbon() {
    const p = st.policies;
    $(".ribbon .inner").innerHTML = "";
    $(".ribbon .inner").append(
      h("span", {}, "Situation: ", h("b", {}, SCEN[st.sid].name)), h("span", {}, "Pump prices: ", h("b", {}, POL.gov_fuel.opts[p.gov_fuel][0])),
      h("span", {}, "RBI: ", h("b", {}, POL.rbi_mpc.opts[p.rbi_mpc][0])), h("span", {}, h("b", {}, `${st.n}`), " simulated futures"),
      h("a", { href: "#whatif", class: "btn quiet", onclick: e => { e.preventDefault(); go("whatif"); } }, "Change"),
      h("span", { class: "busy", id: "busy" }));
  }

  // ------------------------------------------------------------------ TODAY
  function renderToday() {
    const b = D.baseline.values, ev = Object.fromEntries(D.evidence.map(e => [e.evidence_id, e]));
    const src = (id, label) => h("a", { href: ev[id] ? ev[id].url : "#", target: "_blank", rel: "noopener" }, label);
    const dials = [
      ["oil", "Oil price (Brent)", `$${b.brent.value}`, "/barrel", "Up from about $70 in March. Houthi attacks in Saudi Arabia pushed it to a six-month high on 23 Oct.", src("E15", "Rio Times, 23 Oct 2026")],
      ["", "Rupee", `₹${b.inr.value}`, "per $", "Close to its record low of ₹96.97 (May 2026). The RBI is selling dollars to slow the fall.", src("E11", "PTI, 7 Oct 2026")],
      ["", "RBI repo rate", `${b.repo.value.toFixed(2)}%`, "", "Raised by 0.25% on 7 October; stance changed to 'calibrated tightening'.", src("E01", "RBI policy, 7 Oct 2026")],
      ["", "Inflation (CPI)", `${b.cpi_yoy.value}%`, "Sep", "A 23-month high. Food inflation is 7.7%; onion prices doubled.", src("E13", "MoSPI, 12 Oct 2026")],
      ["", "FX reserves", `$${b.reserves.value}bn`, "", "Down about $51bn in four weeks as the RBI defended the rupee.", src("E10", "RBI weekly data, 2 Oct 2026")],
      ["", "Oil companies' loss", "₹8–9", "/litre", "Pump prices are frozen (Delhi petrol ₹102, diesel ₹95), so IOC, BPCL and HPCL absorb the gap.", src("E21", "ICRA, Sep 2026")],
    ];
    const steps = [
      ["Oil price rises", "A supply shock in the Gulf lifts the world oil price. India imports almost 90% of its crude."],
      ["Import bill grows (in dollars)", "India pays more dollars for the same barrels. Fuel exports earn a little more, which partly offsets this."],
      ["More dollars needed", "The current account deficit widens. If foreign investors are also pulling money out, demand for dollars exceeds supply."],
      ["Rupee falls, RBI steps in", "The RBI sells dollars from reserves to slow the fall. Selling dollars also pulls rupee cash out of banks."],
      ["Fuel costs more in rupees", "A weaker rupee makes every barrel even dearer in rupee terms."],
      ["Someone pays", "Either households pay at the pump, oil companies take losses, or the Budget pays. The cost does not disappear."],
      ["Prices, rates, growth", "Inflation, RBI rate decisions, bond yields and growth respond over the following months."],
    ];
    const pg = $("#p-today"); pg.innerHTML = "";
    pg.append(
      h("div", { class: "section-head" }, h("span", { class: "eyebrow" }, "Where India stands · snapshot of 25 October 2026"),
        h("h1", {}, "India is already living through an oil shock"),
        h("p", { class: "lead" }, "Oil is near $117, the rupee is close to its weakest ever, and the RBI has started raising rates again. Pump prices are frozen, so oil companies are quietly absorbing the cost. This tool lets you ask: what happens next, and who ends up paying?")),
      h("div", { class: "grid dials" }, dials.map(([cls, lab, val, unit, txt, s]) => h("div", { class: "card dial " + cls },
        h("span", { class: "label" }, lab), h("span", { class: "value" }, val, " ", h("small", {}, unit)), h("p", {}, txt), h("span", { class: "src" }, "Source: ", s)))),
      h("div", { class: "section-head" }, h("h2", {}, "How an oil shock travels through India"), h("p", { class: "muted" }, "Tap a step to read what happens there.")),
      h("div", { class: "flow", id: "flow" }, steps.map(([t, d], k) => h("button", { "aria-pressed": k === 0 ? "true" : "false", onclick: e => {
        $$("#flow button").forEach(x => x.setAttribute("aria-pressed", "false")); e.currentTarget.setAttribute("aria-pressed", "true"); $("#flow-detail").textContent = d; } }, h("b", {}, t)))),
      h("p", { class: "flow-detail", id: "flow-detail" }, steps[0][1]),
      h("div", { class: "section-head" }, h("h2", {}, "Three ways to explore")),
      h("div", { class: "grid g3" },
        tile("What if", "Pick a situation and decide how the government and RBI respond. See 600 possible futures at once.", "whatif"),
        tile("One future", "Walk through a single future month by month, read why each thing happened, and change a decision midway.", "story"),
        tile("Compare choices", "Same world, different decisions. See who pays under each fuel-price or RBI option.", "choices")),
      h("div", { class: "callout info" }, h("b", {}, "What this tool is, and isn't"),
        h("p", {}, "It is a transparent model of how shocks move through India's economy, started from real October 2026 data. It is not a forecast. When it says 'in 38 of 100 futures', that is how often something happens across the model's simulated futures, under the assumptions you chose. It has not been tested against history yet."),
        h("p", {}, h("a", { href: "#learn", onclick: e => { e.preventDefault(); go("learn"); } }, "Read how it works and its blind spots"))));
    function tile(t, d, id) { return h("a", { href: "#" + id, class: "card", style: "text-decoration:none;color:inherit;display:grid;gap:6px", onclick: e => { e.preventDefault(); go(id); } }, h("h3", {}, t), h("p", { class: "muted" }, d), h("span", { class: "btn quiet", style: "justify-self:start;padding-inline:0" }, "Open")); }
  }

  // ------------------------------------------------------------------ WHAT IF
  let main = null;
  function shockControls(box) {
    box.innerHTML = "";
    const sc = st.shocks[st.sid];
    const slider = (label, s, key, min, max, step, fmt, onchg) => {
      const id = `sl-${st.sid}-${key}`; const out = h("output", { for: id }, fmt(s[key]));
      const inp = h("input", { type: "range", id, min, max, step, value: s[key],
        oninput: e => { out.textContent = fmt(+e.target.value); }, onchange: e => { s[key] = +e.target.value; if (onchg) onchg(s); save(); recompute(); } });
      return h("div", { class: "slider" }, h("label", { for: id }, h("span", {}, label), out), inp);
    };
    if (!sc.shocks.length) { box.append(h("p", { class: "small muted" }, "No new shock. Only today's conditions and the model's own randomness move.")); return; }
    for (const s of sc.shocks) {
      if (s.type === "oil_escalation") box.append(
        slider("Extra oil price on top of today", s, "premium", 0, 80, 5, v => `+$${v}/barrel`),
        slider("Disruption lasts at least", s, "forced_months", 1, 12, 1, v => `${v} month${v > 1 ? "s" : ""}`),
        slider("After that, chance it ends each month", s, "hazard_after", 0.05, 0.6, 0.05, v => `${Math.round(v * 100)}%`),
        slider("Crude supply actually lost", s, "shortfall_pct", 0, 10, 0.5, v => `${v}%`));
      else if (s.type === "global_tightening") {
        s._base = s._base || { us10y: s.us10y, dxy_pct: s.dxy_pct, risk: s.risk, gdem: s.gdem }; s.sev = s.sev ?? 1;
        box.append(slider("How severe (1 = scenario default)", s, "sev", 0, 2, 0.25, v => `${v}×`, x => { for (const k of ["us10y", "dxy_pct", "risk", "gdem"]) x[k] = x._base[k] * x.sev; }),
          slider("How long it lasts", s, "months", 3, 18, 1, v => `${v} months`));
      } else if (s.type === "food_supply") box.append(
        slider("Food price shock", s, "magnitude", 0, 12, 0.5, v => `+${v} pts a year`),
        slider("Lasts", s, "months", 1, 12, 1, v => `${v} months`),
        slider("Starts", s, "start", 1, 24, 1, v => ms(v)));
      else if (s.type === "oil_deescalation") box.append(slider("Ceasefire month", s, "start", 1, 24, 1, v => ms(v)));
    }
  }
  function choiceGroup(actor, name) {
    const g = POL[actor];
    return h("fieldset", { class: "ctl-group", style: "border:0;padding:0;margin:0" }, h("legend", { class: "q" }, g.q),
      h("div", { class: "choice-list" }, Object.entries(g.opts).map(([k, [lab, note]]) => h("label", { class: "choice" },
        h("input", { type: "radio", name: name || actor, value: k, checked: st.policies[actor] === k, onchange: () => { st.policies[actor] = k; save(); ribbon(); recompute(); } }),
        h("div", {}, h("b", {}, lab), note ? h("span", {}, note) : null)))));
  }
  function renderControls() {
    const c = $("#controls"); c.innerHTML = "";
    c.append(
      h("div", { class: "ctl-group" }, h("div", { class: "q" }, "1. Pick a situation"),
        h("div", { class: "choice-list" }, SCEN_ORDER.map(id => h("label", { class: "choice" },
          h("input", { type: "radio", name: "scen", value: id, checked: st.sid === id, onchange: () => { st.sid = id; save(); ribbon(); shockControls($("#shockbox")); recompute(); } }),
          h("div", {}, h("b", {}, SCEN[id].name), h("span", {}, SCEN[id].line)))))),
      h("div", { class: "ctl-group" }, h("div", { class: "q" }, "2. How severe?"), h("div", { id: "shockbox", class: "ctl-group" })),
      h("div", { class: "ctl-group" }, h("div", { class: "q" }, "3. Who decides what?"), choiceGroup("gov_fuel"), choiceGroup("rbi_mpc"), choiceGroup("rbi_fx")),
      h("details", { class: "adv" }, h("summary", {}, "More options"),
        h("div", { class: "inner" }, choiceGroup("gov_fiscal"), choiceGroup("rbi_steril"),
          ...Object.entries(STRUCT).map(([k, g]) => h("label", { class: "field" }, h("b", {}, g.q),
            h("select", { id: "struct-" + k, onchange: e => { st.structure[k] = e.target.value; save(); recompute(); } },
              Object.entries(g.opts).map(([v, lab]) => h("option", { value: v, selected: st.structure[k] === v }, lab))))),
          h("label", { class: "field" }, h("b", {}, "Number of simulated futures"), h("select", { id: "nsel", onchange: e => { st.n = +e.target.value; save(); ribbon(); recompute(); } },
            [300, 600, 1000, 2000].map(v => h("option", { value: v, selected: st.n === v }, `${v}${v === 600 ? " (default)" : v === 2000 ? " (slower, ~2 s)" : ""}`)))),
          h("label", { class: "field" }, h("b", {}, "Uncertain model settings"), h("select", { id: "pmsel", onchange: e => { st.paramMode = e.target.value; save(); recompute(); } },
            h("option", { value: "sampled", selected: st.paramMode === "sampled" }, "Vary them across futures (recommended)"),
            h("option", { value: "central", selected: st.paramMode === "central" }, "Hold them at central values"))),
          h("label", { class: "field" }, h("b", {}, "Random seed (same seed = same futures)"), h("input", { id: "seed", type: "number", value: st.seed, onchange: e => { st.seed = +e.target.value || 1; save(); recompute(); }, style: "padding:8px;border-radius:8px;border:1px solid var(--line);background:var(--card)" })),
          h("button", { class: "btn", onclick: () => { st = DEFAULT(); st.section = "whatif"; save(); renderControls(); ribbon(); recompute(); } }, "Reset everything"))));
    shockControls($("#shockbox"));
  }
  let timer = null;
  function recompute() { clearTimeout(timer); $("#busy") && ($("#busy").textContent = "Updating…"); $("#results") && $("#results").classList.add("loading"); timer = setTimeout(() => { main = null; ensureMain(); }, 60); }
  function ensureMain(after) {
    if (main) { after && after(); return; }
    $("#busy") && ($("#busy").textContent = "Updating…");
    setTimeout(() => {
      const sp = spec(), res = run(sp), ref = st.sid === "reference" ? null : run(spec({ sid: "reference" }));
      main = { sp, res, ref, reps: S.representativePaths(res), metrics: S.pathMetrics(res), refMetrics: ref ? S.pathMetrics(ref) : null, burden: S.burden(res), refBurden: ref ? S.burden(ref) : null };
      renderResults(); $("#busy") && ($("#busy").textContent = ""); after && after();
    }, 20);
  }
  const THRESH = [
    { var: "cpi_yoy", op: ">", level: 6, kind: "any", observe: "monthly", label: "Inflation goes above 6% (the top of RBI's target band)" },
    { var: "cpi_yoy", op: ">", level: 6, kind: "duration", min_months: 3, observe: "monthly", label: "Inflation stays above 6% for 3 months or more" },
    { var: "inr", op: ">", level: 100, kind: "any", observe: "monthly", label: "Rupee weaker than ₹100 per dollar" },
    { var: "inr", op: ">", level: 105, kind: "any", observe: "monthly", label: "Rupee weaker than ₹105 per dollar" },
    { var: "reserves", op: "<", level: 650, kind: "any", observe: "monthly", label: "FX reserves fall below $650bn" },
    { var: "gdp_yoy", op: "<", level: 6, kind: "any", observe: "quarterly", label: "Growth slips below 6% in some quarter" },
    { var: "g10", op: ">", level: 8, kind: "any", observe: "monthly", label: "10-year bond yield above 8%" },
  ];
  const level = p => p < 0.15 ? ["low", "Unlikely here"] : p < 0.4 ? ["mid", "Plausible"] : ["high", "Common"];
  function inShort(m) {
    const { res, metrics: M, burden: B, refMetrics: RM } = m, n = res.n, med = a => S.median(a), p = (a, q) => S.pct(a, q);
    const cpi6 = S.evaluateThreshold(res, THRESH[0]);
    const out = [];
    out.push(`Oil peaks around <b>$${med(M.peak_brent).toFixed(0)}</b> in a typical future (between $${p(M.peak_brent, 10).toFixed(0)} and $${p(M.peak_brent, 90).toFixed(0)} in 8 of 10 futures).`);
    out.push(`The rupee's weakest point is about <b>₹${med(M.peak_inr).toFixed(1)}</b> per dollar in a typical future, and ₹${p(M.peak_inr, 90).toFixed(1)} in a bad one. The RBI spends about <b>$${B.reservesUsed.toFixed(0)}bn</b> of reserves.`);
    const pumpTxt = B.pumpPeak > 1 ? `pump prices rise up to ${B.pumpPeak.toFixed(0)}%` : "pump prices stay frozen";
    out.push(`Inflation goes above 6% in <b>${of100(cpi6.frequency)}</b> futures; a typical peak is ${med(M.peak_cpi).toFixed(1)}%. Here ${pumpTxt}, and oil companies end up ${B.omc >= 0 ? `losing about <b>${lakh(B.omc)}</b>` : `recovering about ${lakh(-B.omc)}`} by Oct 2028.`);
    if (Number.isFinite(med(M.min_gdp_yoy))) out.push(`Growth dips to about <b>${med(M.min_gdp_yoy).toFixed(1)}%</b> in the weakest quarter${RM ? ` (vs ${S.median(RM.min_gdp_yoy).toFixed(1)}% if nothing new happens)` : ""}. The RBI's repo rate peaks around ${med(M.peak_repo).toFixed(2)}%.`);
    out.push(`The central government deficit for 2026-27 ends near <b>${med(M.fd_fy27).toFixed(2)}% of GDP</b> (Budget target 4.3%).`);
    return out;
  }
  function renderResults() {
    const R = $("#results"); R.classList.remove("loading"); R.innerHTML = ""; R.classList.add("fade");
    const m = main, res = m.res;
    R.append(h("div", { class: "card inshort" }, h("span", { class: "eyebrow" }, `In short · ${SCEN[st.sid].name} · ${res.n} futures`),
      h("ul", {}, inShort(m).map(t => h("li", { html: t }))),
      h("p", { class: "small muted" }, "These are simulated futures under the assumptions you chose, not forecasts.")));
    const risk = h("div", { class: "card" }, h("h3", {}, "How often things cross a red line"),
      h("p", { class: "small muted", style: "margin:4px 0 12px" }, `Out of ${res.n} simulated futures${m.ref ? ", compared with 'nothing new'" : ""}.`));
    const list = h("div", { class: "risk-list" });
    for (const th of THRESH) {
      const e = S.evaluateThreshold(res, th), e0 = m.ref ? S.evaluateThreshold(m.ref, th) : null, [cls, word] = level(e.frequency);
      const delta = e0 ? Math.round((e.frequency - e0.frequency) * 100) : null;
      list.append(h("div", { class: "risk" }, h("span", { class: "what" }, th.label),
        h("span", { class: "count" }, `${Math.round(e.frequency * 100)} in 100 `, h("span", { class: "pill " + cls }, word)),
        h("div", { class: "bar" }, h("span", { style: `width:${(e.frequency * 100).toFixed(1)}%;background:var(--${cls === "low" ? "good" : cls === "mid" ? "warn" : "bad"})` })),
        h("span", { class: "note" }, (delta !== null ? `${delta > 0 ? "+" : ""}${delta} vs nothing new. ` : "") + (e.breached ? `Typically first happens around ${ms(Math.round(e.medianFirst))}.` : ""))));
    }
    risk.append(list); R.append(risk);
    R.append(h("div", { class: "legend" }, h("span", {}, h("i", { style: "background:var(--accent);height:3px" }), "typical future"),
      h("span", {}, h("i", { style: "background:var(--band-dark)" }), "half of futures"), h("span", {}, h("i", { style: "background:var(--band-light)" }), "9 in 10 futures"),
      m.ref ? h("span", {}, h("i", { style: "border-top:2px dashed var(--muted);height:0" }), "if nothing new happens") : null,
      h("span", {}, h("i", { style: "background:var(--oil);width:10px;height:10px;border-radius:50%" }), "today (Oct 2026)")));
    const charts = [
      ["brent", "Oil price", "US dollars per barrel", v => `$${v.toFixed(0)}`, [], "oil"],
      ["inr", "Rupee per US dollar", "Higher means a weaker rupee", v => `₹${v.toFixed(1)}`, [{ v: 100, label: "₹100" }]],
      ["cpi_yoy", "Inflation", "Consumer prices, % change over a year", v => `${v.toFixed(1)}%`, [{ v: 6, label: "6%: RBI's upper limit" }]],
      ["gdp_yoy", "GDP growth", "% over a year, quarterly", v => `${v.toFixed(1)}%`, [], "", true],
      ["repo", "RBI repo rate", "The RBI's policy interest rate, %", v => `${v.toFixed(2)}%`, []],
      ["reserves", "FX reserves", "US$ billion", v => `$${v.toFixed(0)}bn`, []],
      ["retail_fuel", "Pump price", "Rupees per litre, Delhi petrol/diesel blend", v => `₹${v.toFixed(1)}`, []],
      ["cum_omc_loss", "Oil companies' losses so far", "₹ lakh crore since Oct 2026 (net of any Budget support)", v => `₹${v.toFixed(2)}`, []],
    ];
    const grid = h("div", { class: "grid g2" });
    for (const [v, title, sub, fmt, thr, cls, q] of charts) {
      const box = h("div"), tip = h("div", { class: "tip" }), b = S.bands(res, v), refB = m.ref ? S.bands(m.ref, v) : null;
      let pk = 0; for (let t = 1; t <= res.T; t++) if (Number.isFinite(b[50][t]) && (v === "reserves" || v === "gdp_yoy" ? b[50][t] < b[50][pk] || !Number.isFinite(b[50][pk]) : b[50][t] > b[50][pk] || !Number.isFinite(b[50][pk]))) pk = t;
      const lo = v === "reserves" || v === "gdp_yoy";
      let tl = res.T; while (tl > 0 && !Number.isFinite(b[50][tl])) tl--;
      const read = Number.isFinite(b[50][pk]) ? `Typical future ${lo ? "bottoms" : "peaks"} at ${fmt(b[50][pk])} around ${ms(pk)}. Last reading ${fmt(b[50][tl])} (${ms(tl)}).` : "";
      grid.append(h("div", { class: "card chart-card" }, h("h3", {}, title), h("span", { class: "sub" }, sub), box, tip, h("p", { class: "read" }, read)));
      fanChart(box, { months: res.months.map((_, t) => ms(t)), bands: b, median: b[50], ref: refB ? refB[50] : null, t0: v === "gdp_yoy" ? NaN : S.val(res, v, 0, 0), fmt, tick: fmt, thr, cls, quarterly: !!q,
        tipEl: tip, defaultTip: "Hover or tap the chart to read a month.", aria: title });
    }
    R.append(grid);
    const B = m.burden, RB = m.refBurden;
    const row = (who, items) => h("div", { class: "row" }, h("span", { class: "who" }, who), h("div", { class: "what" }, items.map(([k, v]) => h("span", {}, k, " ", h("b", {}, v)))));
    R.append(h("div", { class: "card" }, h("h3", {}, "Who pays? (typical future, Nov 2026 to Oct 2028)"),
      h("p", { class: "small muted", style: "margin:4px 0 6px" }, "An oil shock is a loss for India. Your choices decide where it lands."),
      h("div", { class: "ledger" },
        row("Households", [["Pump price change at peak:", `${B.pumpPeak >= 0 ? "+" : ""}${B.pumpPeak.toFixed(0)}%`], ["Peak inflation:", `${B.peakCpi.toFixed(1)}%`]]),
        row("Oil companies", [["Losses by Oct 2028:", B.omc >= 0 ? lakh(B.omc) : `recover ${lakh(-B.omc)}`]]),
        row("Government", [["Extra oil-related cost:", lakh(B.fiscal)], ["2026-27 deficit:", `${B.fd27.toFixed(2)}% of GDP`]].concat(B.capex > 0.01 ? [["Capital spending cut:", lakh(B.capex)]] : [])),
        row("RBI", [["Reserves spent:", `$${B.reservesUsed.toFixed(0)}bn`], ["Rupee's worst fall:", `${B.rupee.toFixed(1)}%`]]),
        row("Economy", [["Weakest quarter's growth:", `${f1(B.minGdp)}%`]].concat(RB ? [["vs nothing new:", `${f1(RB.minGdp)}%`]] : [])),
        row("Borrowers", [["Repo peaks at:", `${B.peakRepo.toFixed(2)}%`], ["10-year yield peaks at:", `${B.peakG10.toFixed(2)}%`]]))));
    R.append(h("div", { class: "cta-row" }, h("a", { class: "btn primary", href: "#story", onclick: e => { e.preventDefault(); go("story"); } }, "Walk through one of these futures"),
      h("a", { class: "btn", href: "#choices", onclick: e => { e.preventDefault(); go("choices"); } }, "Compare decisions side by side")));
  }
  function renderWhatIf() {
    const pg = $("#p-whatif"); pg.innerHTML = "";
    pg.append(h("div", { class: "section-head" }, h("span", { class: "eyebrow" }, "What if"), h("h1", {}, "Pick a situation. Decide the response. See the futures."),
      h("p", { class: "lead" }, "Every change you make re-runs the model on hundreds of possible futures in your browser. Results update in about a second.")),
      h("div", { class: "whatif" }, h("aside", { class: "card controls", id: "controls", "aria-label": "Your choices" }), h("div", { id: "results", class: "grid loading", style: "gap:18px;min-height:400px" })));
    renderControls();
  }

  // ------------------------------------------------------------------ ONE FUTURE (story)
  const FUT = { calm: "Better than 9 in 10 futures", typical: "The middle of the pack", rough: "Worse than 9 in 10 futures", "very rough": "Worse than 49 in 50" };
  const STORY_VARS = {
    risk_off: [0.5, "abs"], us10y: [0.2, "abs"], brent: [0.05, "rel"], crude_bill: [0.6, "abs"], prod_exp: [0.4, "abs"], remit: [0.25, "abs"], ca: [0.8, "abs"],
    fpi: [0.8, "abs"], pressure: [1.0, "abs"], inr: [0.0075, "rel"], reserves: [6, "abs"], liq: [0.3, "abs"], parity: [0.03, "rel"], retail_fuel: [0.01, "rel"],
    omc_margin: [2.5, "abs"], cpi_yoy: [0.25, "abs"], food_yoy: [0.5, "abs"], core_yoy: [0.25, "abs"], exp_infl: [0.12, "abs"], gap: [0.2, "abs"],
    fd_proj: [0.06, "abs"], g10: [0.12, "abs"], credit_yoy: [0.4, "abs"], stress: [0.08, "abs"],
  };
  const THEME = { risk_off: "World & oil", us10y: "World & oil", brent: "World & oil", crude_bill: "Rupee & dollars", prod_exp: "Rupee & dollars", remit: "Rupee & dollars",
    ca: "Rupee & dollars", fpi: "Rupee & dollars", pressure: "Rupee & dollars", inr: "Rupee & dollars", reserves: "Rupee & dollars", liq: "Banks & rates",
    parity: "Fuel & prices", retail_fuel: "Fuel & prices", omc_margin: "Fuel & prices", cpi_yoy: "Fuel & prices", food_yoy: "Fuel & prices", core_yoy: "Fuel & prices",
    exp_infl: "Fuel & prices", gap: "Growth & budget", fd_proj: "Growth & budget", g10: "Banks & rates", credit_yoy: "Banks & rates", stress: "Banks & rates" };
  function sentence(v, prev, cur, tprev) {
    const up = cur > prev, since = tprev === 0 ? "in Oct 2026" : `in ${ms(tprev)}`;
    switch (v) {
      case "risk_off": return up ? "Global investors turn more nervous and pull back from riskier markets like India." : "Global investors calm down.";
      case "us10y": return `US 10-year interest rates ${up ? "rise" : "fall"} to ${cur.toFixed(2)}% (from ${prev.toFixed(2)}% ${since}).`;
      case "brent": return `Oil ${up ? "rises" : "falls"} to $${cur.toFixed(0)} a barrel (from $${prev.toFixed(0)} ${since}).`;
      case "crude_bill": return `India's crude import bill ${up ? "rises" : "falls"} to $${cur.toFixed(1)}bn a month (from $${prev.toFixed(1)}bn). This is in dollars; the rupee doesn't change it.`;
      case "prod_exp": return `India's fuel exports earn ${up ? "more" : "less"}: $${cur.toFixed(1)}bn a month. This ${up ? "partly offsets" : "adds to"} the import bill.`;
      case "remit": return `Money sent home by Indians abroad ${up ? "rises" : "falls"} to $${cur.toFixed(1)}bn a month${up ? " (higher oil lifts Gulf incomes, with a lag)" : ""}.`;
      case "ca": return cur < 0 ? `The current account deficit ${up ? "narrows" : "widens"} to $${(-cur).toFixed(1)}bn a month (more money going out than coming in).` : `The current account turns to a surplus of $${cur.toFixed(1)}bn a month.`;
      case "fpi": return cur < 0 ? `Foreign investors sell a net $${(-cur).toFixed(1)}bn of Indian shares and bonds this month.` : `Foreign investors buy a net $${cur.toFixed(1)}bn of Indian shares and bonds.`;
      case "pressure": return cur > 0 ? `India needs about $${cur.toFixed(1)}bn more dollars this month than flow in naturally.` : `More dollars flow in than India needs: about $${(-cur).toFixed(1)}bn spare.`;
      case "inr": return `The rupee ${up ? "weakens" : "strengthens"} to ₹${cur.toFixed(2)} per dollar (from ₹${prev.toFixed(2)} ${since}).`;
      case "reserves": return `FX reserves ${up ? "rise" : "fall"} to $${cur.toFixed(0)}bn (from $${prev.toFixed(0)}bn ${since}).`;
      case "liq": return `Spare cash in the banking system ${up ? "rises" : "falls"} to ${lakh(cur)}${cur < 0 ? " (a shortage)" : ""}.`;
      case "parity": return `A litre of petrol/diesel now costs ₹${cur.toFixed(1)} at world prices (from ₹${prev.toFixed(1)}). Oil price and the rupee both matter here.`;
      case "retail_fuel": return `Pump prices ${up ? "go up" : "come down"} to ₹${cur.toFixed(1)} a litre (from ₹${prev.toFixed(1)}).`;
      case "omc_margin": return cur < 0 ? `Oil companies now lose ₹${(-cur).toFixed(1)} on every litre they sell.` : `Oil companies earn ₹${cur.toFixed(1)} per litre, recovering earlier losses.`;
      case "cpi_yoy": return `Inflation ${up ? "rises" : "falls"} to ${cur.toFixed(1)}% (from ${prev.toFixed(1)}% ${since}).`;
      case "food_yoy": return `Food inflation ${up ? "rises" : "falls"} to ${cur.toFixed(1)}%.`;
      case "core_yoy": return `Core inflation (prices other than food and fuel) ${up ? "rises" : "falls"} to ${cur.toFixed(1)}%.`;
      case "exp_infl": return `People ${up ? "now expect higher" : "now expect lower"} inflation: ${cur.toFixed(1)}% for the year ahead.`;
      case "gap": return `The economy is running ${Math.abs(cur).toFixed(1)}% ${cur < 0 ? "below" : "above"} its normal pace (from ${prev >= 0 ? "+" : ""}${prev.toFixed(1)}%).`;
      case "fd_proj": return `This year's central government deficit is now heading for ${cur.toFixed(2)}% of GDP.`;
      case "g10": return `The 10-year government bond yield ${up ? "rises" : "falls"} to ${cur.toFixed(2)}%. Borrowing gets ${up ? "costlier" : "cheaper"} for government and companies.`;
      case "credit_yoy": return `Bank lending growth ${up ? "picks up" : "slows"} to ${cur.toFixed(1)}% a year.`;
      case "stress": return up ? "Borrowers find it harder to repay; banks become more cautious." : "Pressure on borrowers eases.";
    }
    return `${v} moves to ${cur}`;
  }
  const MECH = (() => { const by = {}; for (const m of D.mechanisms.links) if (m.implemented) (by[m.dst] = by[m.dst] || []).push(m); return by; })();
  function buildStory(Hp, prm, sp) {
    const T = sp.horizon, ev = [], last = {}, lastVal = {}, lastT = {};
    let seq = 0;
    const add = e => { e.id = ++seq; ev.push(e); (e.vars || []).forEach(v => (last[v] = e)); return e; };
    const parentsFor = (v, t) => { const out = new Set(); for (const m of MECH[v] || []) for (const s of m.src) { const e = last[s]; if (e && t - (+m.lag || 0) - 3 <= e.t && e.t <= t) out.add(e.id); } return [...out]; };
    for (const v of Object.keys(STORY_VARS)) { lastVal[v] = Hp[v][P]; lastT[v] = 0; }
    const byStart = {}; (sp.scenario.shocks || []).forEach(s => (byStart[s.start] = byStart[s.start] || []).push(s));
    const order1 = ["risk_off", "us10y", "brent", "crude_bill", "prod_exp", "remit", "ca", "fpi", "pressure"], order2 = ["inr", "reserves", "liq", "parity"],
      order3 = ["retail_fuel", "omc_margin", "cpi_yoy", "food_yoy", "core_yoy", "exp_infl", "gap", "fd_proj", "g10", "credit_yoy", "stress"];
    const state = (t, list) => { for (const v of list) { const i = P + t, cur = Hp[v][i], prev = lastVal[v], [thr, mode] = STORY_VARS[v];
      if (Math.abs(cur - prev) > (mode === "rel" ? thr * Math.abs(prev) : thr)) {
        const e = add({ t, type: "state", theme: THEME[v], vars: [v], text: sentence(v, prev, cur, lastT[v]), parents: parentsFor(v, t) });
        e.contrib = contrib(v, i, P + lastT[v]); lastVal[v] = cur; lastT[v] = t; } } };
    const contrib = (v, i, ip) => {
      if (v === "gap") return Object.fromEntries(S.GAP_CHANNELS.map(c => [GAP_PLAIN[c], Hp["c_" + c][i] - Hp["c_" + c][ip]]));
      if (v === "ca") return Object.fromEntries(Object.keys(CA_PLAIN).map(c => [CA_PLAIN[c], Hp[c][i] - Hp[c][ip]]));
      if (v === "cpi_yoy") { const w = { food: prm.w_food, fuel: prm.w_energy, "everything else (core)": prm.w_core }, k = { food: "food", fuel: "energy", "everything else (core)": "core" };
        const base = Object.keys(w).reduce((a, n) => a + w[n] * Hp[k[n] + "_idx"][i - 12], 0); return Object.fromEntries(Object.keys(w).map(n => [n, w[n] * Hp[k[n] + "_idx"][i - 12] / base * Hp[k[n] + "_yoy"][i]])); }
      return null;
    };
    for (let t = 1; t <= T; t++) {
      const i = P + t;
      for (const s of byStart[t] || []) add({ t, type: "shock", theme: "Situation", vars: ["shock_" + s.type], text: shockText(s), parents: [] });
      for (const [v, on, off] of [["disrupt", "A new Gulf supply disruption starts.", "The Gulf supply disruption ends. Oil traders quickly price out the risk."],
        ["esc", "The Hormuz escalation begins.", "The Hormuz escalation ends."], ["deanchor", "People start to lose faith that inflation will come down: expectations begin rising faster.", "Inflation expectations settle down again."]])
        if (Hp[v][i] !== Hp[v][i - 1]) add({ t, type: "regime", theme: v === "deanchor" ? "Fuel & prices" : "World & oil", vars: [v], text: Hp[v][i] > Hp[v][i - 1] ? on : off,
          parents: v === "deanchor" && last.cpi_yoy ? [last.cpi_yoy.id] : ev.filter(e => e.type === "shock").slice(-1).map(e => e.id) });
      if (Hp.mpc_meeting[i] > 0) {
        const d = Hp.dec_mpc_delta[i], rule = (sp.overrides && Object.keys(sp.overrides).map(Number).filter(m => m <= t).sort((a, b) => a - b).reduce((r, m) => sp.overrides[m].rbi_mpc || r, null)) || sp.policies.rbi_mpc;
        add({ t, type: "decision", theme: "RBI decision", vars: ["repo"], parents: [last.cpi_yoy, last.inr].filter(Boolean).map(e => e.id),
          text: `RBI's rate-setting committee ${d > 0 ? `raises the repo rate by ${(d).toFixed(2)}%` : d < 0 ? `cuts the repo rate by ${(-d).toFixed(2)}%` : "keeps the repo rate unchanged"} at ${Hp.repo[i].toFixed(2)}%.`,
          detail: `What it could see: inflation ${Hp.obs_cpi[i].toFixed(1)}% (the ${ms(t - 2)} figure; later months weren't published yet), growth ${f1(Hp.obs_gdp[i])}% (latest quarter), rupee ${Hp.obs_dep3[i] >= 0 ? "down" : "up"} ${Math.abs(Hp.obs_dep3[i]).toFixed(1)}% over three months. Approach: ${POL.rbi_mpc.opts[rule][0].toLowerCase()}.` });
      }
      if (Hp.capex_cut[i] > 0.005) add({ t, type: "decision", theme: "Government decision", vars: ["capex_cut"], parents: last.fd_proj ? [last.fd_proj.id] : [],
        text: `To hold its deficit target, the government cuts capital spending by ${crore(Hp.capex_cut[i])} this month.` });
      state(t, order1);
      if (Math.abs(Hp.interv[i]) > 3) add({ t, type: "decision", theme: "RBI decision", vars: ["interv"], parents: last.pressure ? [last.pressure.id] : [],
        text: Hp.interv[i] > 0 ? `The RBI sells $${Hp.interv[i].toFixed(1)}bn of reserves to slow the rupee's fall.` : `The RBI buys $${(-Hp.interv[i]).toFixed(1)}bn to rebuild reserves.`,
        detail: Hp.interv[i] > 0 ? `Selling dollars pulls ${lakh(Hp.interv[i] * Hp.inr[i] / 1000)} of cash out of banks; the RBI puts back ${lakh(Hp.steril[i])}.` : "" });
      state(t, order2);
      const gf = S.GOV_FUEL[Hp.dec_gov_fuel[i]], dr = Hp.retail_fuel[i] - Hp.retail_fuel[i - 1], dx = Hp.excise[i] - Hp.excise[i - 1];
      if (t === 1 || gf !== S.GOV_FUEL[Hp.dec_gov_fuel[i - 1]] || Math.abs(dr) > 0.5 || Math.abs(dx) > 0.05 || (Hp.comp[i] > 0 && Hp.comp[i - 1] === 0))
        add({ t, type: "decision", theme: "Government decision", vars: ["retail_fuel_dec"], parents: last.parity ? [last.parity.id] : [],
          text: `Fuel pricing: ${POL.gov_fuel.opts[gf][0].toLowerCase()}. ${Math.abs(dr) > 0.05 ? `Pump price ${dr > 0 ? "up" : "down"} ₹${Math.abs(dr).toFixed(1)}/L.` : "Pump price unchanged."}${Math.abs(dx) > 0.01 ? ` Fuel tax ${dx > 0 ? "raised" : "cut"} ₹${Math.abs(dx).toFixed(2)}/L.` : ""}${Hp.comp[i] > 0 ? ` The Budget pays oil companies ${crore(Hp.comp[i])}.` : ""}` });
      if (Hp.flag_excise_exhausted[i] && !Hp.flag_excise_exhausted[i - 1]) add({ t, type: "constraint", theme: "Limit reached", vars: [], parents: [], text: "The fuel tax can't be cut any further: it is already close to zero. Losses stay with oil companies." });
      if (Hp.flag_res_floor[i] && !Hp.flag_res_floor[i - 1]) add({ t, type: "constraint", theme: "Limit reached", vars: [], parents: [], text: "Reserves are getting close to the RBI's comfort floor, so it sells fewer dollars." });
      if (Hp.flag_policy_switch[i] && !Hp.flag_policy_switch[i - 1]) add({ t, type: "constraint", theme: "Government decision", vars: [], parents: [], text: "Oil company losses passed the government's tolerance: it starts passing half the cost on at the pump." });
      state(t, order3);
    }
    return ev;
  }
  function shockText(s) {
    if (s.type === "oil_escalation") return `Shock: Hormuz shipping is disrupted. Oil gets +$${s.premium}/barrel of extra risk premium, freight and refining margins jump, and ${s.shortfall_pct}% of crude supply is lost for ${s.forced_months} months.`;
    if (s.type === "oil_deescalation") return "Shock: a ceasefire is agreed and the Gulf disruption ends.";
    if (s.type === "global_tightening") return `Shock: US 10-year rates rise ${(s.us10y || 0).toFixed(2)}%, the dollar strengthens ${(s.dxy_pct || 0).toFixed(0)}%, and world demand weakens.`;
    return `Shock: the monsoon fails. Food prices start rising an extra ${s.magnitude} points a year for ${s.months} months.`;
  }
  let storyCache = null;
  function renderStory() {
    const pg = $("#p-story");
    const m = main, rp = m.reps[st.future] || m.reps.typical;
    const key = JSON.stringify([m.sp, rp.path]);
    if (!storyCache || storyCache.key !== key) {
      const one = S.onePath(D, m.sp, rp.path);
      storyCache = { key, one, H: one.paths[0], prm: one.params[0], events: buildStory(one.paths[0], one.params[0], m.sp), branch: null };
    }
    const sc = storyCache, H = sc.H, T = m.sp.horizon;
    st.month = Math.max(1, Math.min(T, st.month || 1));
    pg.innerHTML = "";
    pg.append(h("div", { class: "section-head" }, h("span", { class: "eyebrow" }, `One future · ${SCEN[st.sid].name}`), h("h1", {}, "Walk through one future, month by month"),
      h("p", { class: "lead" }, "Each option below is one complete simulated future picked from the set on the What if page. Step through the months to read what happened and why.")),
      h("div", { class: "futures" }, Object.entries(FUT).map(([k, d]) => h("button", { class: "future", "aria-pressed": st.future === k ? "true" : "false",
        onclick: () => { st.future = k; save(); renderStory(); } }, h("b", {}, k[0].toUpperCase() + k.slice(1)), h("span", {}, d)))));
    const tl = h("div", { class: "timeline", role: "tablist", "aria-label": "Months" });
    for (let t = 1; t <= T; t++) {
      const evs = sc.events.filter(e => e.t === t), dots = [];
      if (evs.some(e => e.type === "shock")) dots.push("shock"); if (evs.some(e => e.type === "decision" && e.vars[0] === "repo")) dots.push("decision"); if (evs.some(e => e.type === "regime")) dots.push("regime");
      tl.append(h("button", { class: "tl-m", role: "tab", "aria-current": t === st.month ? "true" : "false", onclick: () => { st.month = t; save(); renderStory(); } },
        h("span", {}, ms(t)), h("span", { class: "dots" }, dots.map(d => h("i", { class: d })))));
    }
    const nav = h("div", { class: "cta-row", style: "align-items:center" },
      h("button", { class: "btn", disabled: st.month <= 1, onclick: () => { st.month--; save(); renderStory(); } }, "Previous month"),
      h("button", { class: "btn primary", disabled: st.month >= T, onclick: () => { st.month++; save(); renderStory(); } }, "Next month"),
      h("span", { class: "legend" }, h("span", {}, h("i", { style: "background:var(--oil);width:8px;height:8px;border-radius:50%" }), "shock"),
        h("span", {}, h("i", { style: "background:var(--accent);width:8px;height:8px;border-radius:50%" }), "RBI rate decision"),
        h("span", {}, h("i", { style: "background:var(--bad);width:8px;height:8px;border-radius:50%" }), "turning point")));
    pg.append(h("div", { class: "card", style: "display:grid;gap:10px" }, tl, nav));
    const t = st.month, evs = sc.events.filter(e => e.t === t);
    const showAll = !!st.showAll;
    const shown = showAll ? evs : evs.filter(e => e.type !== "state" || ["brent", "inr", "reserves", "cpi_yoy", "retail_fuel", "omc_margin", "gap", "ca", "core_yoy", "fd_proj", "g10"].includes(e.vars[0]));
    const byId = Object.fromEntries(sc.events.map(e => [e.id, e]));
    const evBox = h("div", { class: "events" }, h("h2", {}, `What happened in ${monthLong(t)}`),
      shown.length ? shown.map(e => eventCard(e, byId)) : h("p", { class: "muted" }, "A quiet month: nothing moved past the reporting thresholds."),
      h("button", { class: "btn quiet", style: "justify-self:start", onclick: () => { st.showAll = !showAll; save(); renderStory(); } }, showAll ? "Show only the main events" : `Show all ${evs.length} events, including smaller moves`));
    const side = h("div", { class: "grid", style: "gap:14px" });
    const kv = h("div", { class: "kv" }), i = P + t;
    const rows = [["Oil price", "brent", v => `$${v.toFixed(0)}`, 1], ["Rupee per $", "inr", v => `₹${v.toFixed(1)}`, 1], ["Inflation", "cpi_yoy", v => `${v.toFixed(1)}%`, 1],
      ["Repo rate", "repo", v => `${v.toFixed(2)}%`, 1], ["FX reserves", "reserves", v => `$${v.toFixed(0)}bn`, -1], ["Pump price", "retail_fuel", v => `₹${v.toFixed(1)}`, 1],
      ["Oil co. losses so far", "cum_omc_loss", v => lcr(v, 2), 1], ["Economy vs normal", "gap", v => `${v >= 0 ? "+" : ""}${v.toFixed(1)}%`, -1], ["Deficit this year", "fd_proj", v => `${v.toFixed(2)}%`, 1]];
    for (const [lab, v, fmt, badDir] of rows) {
      const cur = H[v][i], base = H[v][P], d = cur - base, cls = Math.abs(d) < 1e-6 ? "flat" : (d * badDir > 0 ? "up" : "down");
      kv.append(h("span", { class: "k" }, lab), h("span", { class: "v" }, fmt(cur)), h("span", { class: "d " + cls }, Math.abs(d) < 1e-6 ? "same" : `${d > 0 ? "+" : "−"}${fmt(Math.abs(d)).replace(/^\+/, "")}`));
    }
    side.append(h("div", { class: "card" }, h("h3", {}, `Where things stand, ${ms(t)}`), h("p", { class: "small muted", style: "margin:2px 0 10px" }, "Change since October 2026. Red = worse for India, green = better."), kv));
    for (const [v, title, fmt, cls] of [["brent", "Oil price", x => `$${x.toFixed(0)}`, "oil"], ["inr", "Rupee per dollar", x => `₹${x.toFixed(1)}`, ""], ["cpi_yoy", "Inflation", x => `${x.toFixed(1)}%`, ""]]) {
      const box = h("div"), tip = h("div", { class: "tip" });
      side.append(h("div", { class: "card chart-card" }, h("h3", {}, title), box, tip));
      fanChart(box, { months: Array.from({ length: T + 1 }, (_, k) => ms(k)), median: Array.from(H[v].slice(P)), alt: sc.branch ? Array.from(sc.branch.H[v].slice(P)) : null, t0: H[v][P],
        fmt, tick: fmt, cls, marker: t, tipEl: tip, thr: v === "cpi_yoy" ? [{ v: 6, label: "6%" }] : [], defaultTip: sc.branch ? "Solid = this future; red dashed = with your change." : "Hover or tap to read a month." });
    }
    pg.append(h("div", { class: "story" }, evBox, side));
    pg.append(branchPanel(sc, m));
  }
  function eventCard(e, byId) {
    const cls = { shock: "t-shock", decision: "t-decision", regime: "t-regime", state: "t-state", constraint: "t-constraint" }[e.type] || "t-state";
    const card = h("div", { class: "event " + cls }, h("span", { class: "theme" }, e.theme), h("p", { class: "txt" }, e.text), e.detail ? h("p", { class: "small muted" }, e.detail) : null);
    if (e.contrib) {
      const entries = Object.entries(e.contrib).filter(([, v]) => Math.abs(v) > 0.005).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])).slice(0, 4);
      if (entries.length) {
        const mx = Math.max(...entries.map(x => Math.abs(x[1])));
        const title = e.vars[0] === "cpi_yoy" ? "What makes up inflation now (percentage points)" : e.vars[0] === "gap" ? "What moved the economy since last reported (points)" : "What moved it (US$ bn a month)";
        card.append(h("div", { class: "contrib" }, h("span", { class: "small muted" }, title), entries.map(([k, v]) => h("div", { class: "cb" }, h("span", {}, k), h("span", { class: "num", style: "text-align:right" }, `${v > 0 ? "+" : ""}${v.toFixed(2)}`),
          h("span", { class: "b" }, h("span", { style: `left:${v < 0 ? 50 - 50 * Math.abs(v) / mx : 50}%;width:${50 * Math.abs(v) / mx}%;background:${v < 0 ? "var(--bad)" : "var(--accent)"}` }))))));
      }
    }
    if (e.parents && e.parents.length) {
      const chain = h("div", { class: "chain", hidden: true });
      const seen = new Set(); let frontier = e.parents.slice(), depth = 0;
      while (frontier.length && depth < 3) { const nxt = []; for (const pid of frontier) { if (seen.has(pid) || !byId[pid]) continue; seen.add(pid); const p = byId[pid];
        chain.append(h("div", {}, h("span", {}, `${ms(p.t)}: ${p.text}`))); nxt.push(...(p.parents || [])); } frontier = nxt; depth++; }
      card.append(h("button", { class: "btn quiet why", "aria-expanded": "false", onclick: ev => { chain.hidden = !chain.hidden; ev.currentTarget.setAttribute("aria-expanded", String(!chain.hidden)); ev.currentTarget.textContent = chain.hidden ? "Why did this happen?" : "Hide the causes"; } }, "Why did this happen?"), chain);
    }
    return card;
  }
  function branchPanel(sc, m) {
    const box = h("div", { class: "card", style: "display:grid;gap:12px" }, h("h2", {}, "Change one decision from this month"),
      h("p", { class: "muted" }, `Everything before ${ms(st.month)} stays the same, and the world throws exactly the same events at India afterwards. Only the decision you change is different.`));
    const actorSel = h("select", { id: "br-actor" }, ["gov_fuel", "rbi_mpc", "rbi_fx"].map(a => h("option", { value: a, selected: (st.brActor || "gov_fuel") === a }, POL[a].q)));
    const optSel = h("select", { id: "br-opt" });
    const fill = () => { optSel.innerHTML = ""; const a = actorSel.value; Object.entries(POL[a].opts).filter(([k]) => k !== m.sp.policies[a]).forEach(([k, [lab]]) => optSel.append(h("option", { value: k }, lab))); };
    actorSel.addEventListener("change", () => { st.brActor = actorSel.value; fill(); }); fill();
    box.append(h("div", { class: "cta-row", style: "align-items:end" }, h("label", { class: "field" }, "Who", actorSel), h("label", { class: "field" }, "New choice", optSel),
      h("button", { class: "btn primary", onclick: () => {
        const ov = {}; ov[st.month] = { [actorSel.value]: optSel.value };
        const alt = S.onePath(D, m.sp, sc.one.pathIdx[0], ov);
        sc.branch = { H: alt.paths[0], res: alt, actor: actorSel.value, opt: optSel.value, month: st.month }; renderStory();
        setTimeout(() => $("#branch-out") && $("#branch-out").scrollIntoView({ behavior: "smooth", block: "start" }), 50);
      } }, "Replay with this change")));
    if (sc.branch) {
      const b0 = S.burdenPath(sc.one, 0), b1 = S.burdenPath(sc.branch.res, 0);
      const rows = [["Peak inflation", "peakCpi", v => `${v.toFixed(1)}%`, -1], ["Pump price at peak (vs Oct 2026)", "pumpPeak", v => `${v >= 0 ? "+" : ""}${v.toFixed(0)}%`, -1],
        ["Oil companies' losses by Oct 2028", "omc", v => lcr(v, 2), -1], ["Govt extra oil-related cost", "fiscal", v => lcr(v, 2), -1],
        ["2026-27 deficit", "fd27", v => `${v.toFixed(2)}%`, -1], ["Reserves spent", "reservesUsed", v => `$${v.toFixed(0)}bn`, -1], ["Rupee's worst fall", "rupee", v => `${v.toFixed(1)}%`, -1],
        ["Weakest growth quarter", "minGdp", v => `${f1(v)}%`, 1], ["Repo peak", "peakRepo", v => `${v.toFixed(2)}%`, -1]];
      const g = h("div", { class: "compare2" }, h("span", { class: "h" }, ""), h("span", { class: "h", style: "text-align:right" }, "Original"), h("span", { class: "h", style: "text-align:right" }, "With change"), h("span", { class: "h", style: "text-align:right" }, "Difference"));
      for (const [lab, k, fmt, good] of rows) { const a = b0[k], c = b1[k], d = c - a; const cls = Math.abs(d) < 1e-3 ? "flat" : (d * good > 0 ? "down" : "up");
        g.append(h("span", {}, lab), h("span", { class: "v" }, fmt(a)), h("span", { class: "v" }, fmt(c)), h("span", { class: "v " + cls }, Math.abs(d) < 1e-3 ? "same" : `${d > 0 ? "+" : "−"}${Math.abs(d).toFixed(2)}`)); }
      box.append(h("div", { id: "branch-out", class: "callout info" }, h("b", {}, `You changed: ${POL[sc.branch.actor].q} → "${POL[sc.branch.actor].opts[sc.branch.opt][0]}" from ${ms(sc.branch.month)}.`),
        h("p", {}, "Red dashed lines on the charts above show the changed future. Green differences are better for India, red are worse. Notice the cost usually moves to someone else rather than disappearing.")),
        h("div", { class: "table-wrap" }, g));
    }
    return box;
  }

  // ------------------------------------------------------------------ COMPARE CHOICES
  const GROUPS = { gov_fuel: "Petrol & diesel pricing", rbi_mpc: "RBI interest-rate approach", rbi_fx: "RBI dollar selling" };
  function renderChoices() {
    const pg = $("#p-choices"); pg.innerHTML = "";
    pg.append(h("div", { class: "section-head" }, h("span", { class: "eyebrow" }, `Compare choices · ${SCEN[st.sid].name}`),
      h("h1", {}, "Same world, different decisions"),
      h("p", { class: "lead" }, "Each option below faces exactly the same simulated futures, so every difference comes from the decision alone. No option is free: look at who carries the cost.")),
      h("div", { class: "seg", role: "group", "aria-label": "What to compare" }, Object.entries(GROUPS).map(([k, lab]) => h("button", { "aria-pressed": st.cmpGroup === k ? "true" : "false", onclick: () => { st.cmpGroup = k; save(); renderChoices(); } }, lab))));
    const out = h("div", { class: "grid loading", style: "gap:18px;min-height:300px" }); pg.append(out);
    setTimeout(() => {
      const actor = st.cmpGroup, sp = spec({ spec: { n_paths: 400 } });
      const bundles = Object.fromEntries(Object.keys(POL[actor].opts).map(k => [k, { [actor]: k }]));
      const cmp = S.compare(D, sp, bundles);
      out.classList.remove("loading"); out.innerHTML = "";
      const cols = [["Peak inflation", r => S.median(r.metrics.peak_cpi), v => `${v.toFixed(1)}%`, -1], ["Weakest growth quarter", r => S.median(r.metrics.min_gdp_yoy), v => `${v.toFixed(1)}%`, 1],
        ["Oil companies' losses", r => r.burden.omc, v => lcr(v), -1], ["2026-27 deficit", r => r.burden.fd27, v => `${v.toFixed(2)}%`, -1],
        ["Rupee's weakest", r => S.median(r.metrics.peak_inr), v => `₹${v.toFixed(1)}`, -1], ["Repo peak", r => S.median(r.metrics.peak_repo), v => `${v.toFixed(2)}%`, -1],
        ["10-year yield peak", r => S.median(r.metrics.peak_g10), v => `${v.toFixed(2)}%`, -1]];
      const names = Object.keys(cmp);
      const vals = cols.map(([, get]) => names.map(n => get(cmp[n])));
      const tbl = h("table", { class: "matrix" }, h("thead", {}, h("tr", {}, h("th", {}, "Option"), cols.map(c => h("th", { style: "text-align:right" }, c[0])))),
        h("tbody", {}, names.map((n, r) => h("tr", {}, h("td", {}, h("b", {}, POL[actor].opts[n][0]), n === sp.policies[actor] ? h("span", { class: "tag" }, "current") : null),
          cols.map(([, , fmt, good], c) => { const col = vals[c], x = col[r], best = good > 0 ? Math.max(...col) : Math.min(...col), worst = good > 0 ? Math.min(...col) : Math.max(...col);
            const cls = Math.abs(best - worst) < 1e-6 ? "" : Math.abs(x - best) < 1e-9 ? "rank-1" : Math.abs(x - worst) < 1e-9 ? "rank-3" : "";
            return h("td", { class: "n" }, h("span", { class: cls }, fmt(x))); })))));
      out.append(h("div", { class: "card" }, h("h3", {}, `${GROUPS[actor]}: typical outcomes`),
        h("p", { class: "small muted", style: "margin:4px 0 10px" }, `Medians across 400 futures. Green = best of these options on that measure, red = worst.`), h("div", { class: "table-wrap" }, tbl)));
      // scatter
      const box = h("div"), tip = h("div", { class: "tip" });
      out.append(h("div", { class: "card chart-card" }, h("h3", {}, "The trade-off: inflation against growth"),
        h("span", { class: "sub" }, "Each dot is an option (typical future). Lines show the range in 8 of 10 futures. Down-left is lower inflation; up is stronger growth."), box, tip));
      scatter(box, tip, names.map(n => ({ name: POL[actor].opts[n][0], x: S.median(cmp[n].metrics.peak_cpi), y: S.median(cmp[n].metrics.min_gdp_yoy),
        x0: S.pct(cmp[n].metrics.peak_cpi, 10), x1: S.pct(cmp[n].metrics.peak_cpi, 90), y0: S.pct(cmp[n].metrics.min_gdp_yoy, 10), y1: S.pct(cmp[n].metrics.min_gdp_yoy, 90), cur: n === sp.policies[actor] })));
      const ref = sp.policies[actor], take = [];
      for (const n of names) if (n !== ref) {
        const a = cmp[ref], b = cmp[n], dc = S.median(b.metrics.peak_cpi) - S.median(a.metrics.peak_cpi), dg = S.median(b.metrics.min_gdp_yoy) - S.median(a.metrics.min_gdp_yoy);
        take.push(`<b>${POL[actor].opts[n][0]}</b> vs current: peak inflation ${dc >= 0 ? "+" : ""}${dc.toFixed(1)} pts, weakest growth ${dg >= 0 ? "+" : ""}${dg.toFixed(1)} pts, oil company losses ${(b.burden.omc - a.burden.omc) >= 0 ? "+" : ""}${(b.burden.omc - a.burden.omc).toFixed(1)} lakh crore, deficit ${(b.burden.fd27 - a.burden.fd27) >= 0 ? "+" : ""}${(b.burden.fd27 - a.burden.fd27).toFixed(2)} pts.`);
      }
      out.append(h("div", { class: "card inshort" }, h("h3", {}, "Reading the differences"), h("ul", {}, take.map(t => h("li", { html: t })))));
      if (actor === "gov_fuel") out.append(h("div", { class: "callout" }, h("b", {}, "A blind spot to keep in mind"),
        h("p", {}, "Options where the Budget pays can look best for growth here. That is partly because the model has no channel from a bigger deficit or higher bond yields back to growth or India's credit rating. Treat that advantage as an upper bound.")));
      out.append(stressFinder(sp));
    }, 30);
  }
  function scatter(box, tip, pts) {
    const W = 640, H = 300, L = 54, R = 20, T = 30, B = 40;
    const xs = pts.flatMap(p => [p.x0, p.x1]), ys = pts.flatMap(p => [p.y0, p.y1]);
    let x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const px = (x1 - x0) * 0.1 || 0.5, py = (y1 - y0) * 0.1 || 0.5; x0 -= px; x1 += px; y0 -= py; y1 += py;
    const X = v => L + (W - L - R) * (v - x0) / (x1 - x0), Y = v => T + (H - T - B) * (1 - (v - y0) / (y1 - y0));
    let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Inflation versus growth by option"><g class="grid">`;
    niceTicks(y0, y1, 4).filter(v => v >= y0 && v <= y1).forEach(v => { s += `<line x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}"/>`; });
    s += `</g>`;
    niceTicks(y0, y1, 4).filter(v => v >= y0 && v <= y1).forEach(v => { s += `<text x="${L - 6}" y="${Y(v) + 4}" text-anchor="end">${v.toFixed(1)}%</text>`; });
    niceTicks(x0, x1, 5).filter(v => v >= x0 && v <= x1).forEach(v => { s += `<text x="${X(v)}" y="${H - 20}" text-anchor="middle">${v.toFixed(1)}%</text>`; });
    s += `<text x="${(L + W - R) / 2}" y="${H - 4}" text-anchor="middle">Peak inflation →</text><text x="${L}" y="${T - 14}">Weakest growth ↑</text>`;
    const placed = [];
    const lab = pts.map(p => { let x = X(p.x) + 11, y = Y(p.y) - 9; while (placed.some(q => Math.abs(q[0] - x) < 16 && Math.abs(q[1] - y) < 13)) x += 14; placed.push([x, y]); return [x, y]; });
    pts.forEach((p, k) => { s += `<g class="pt" data-k="${k}"><line x1="${X(p.x0)}" x2="${X(p.x1)}" y1="${Y(p.y)}" y2="${Y(p.y)}" stroke="var(--muted)" stroke-width="1.5"/>
      <line x1="${X(p.x)}" x2="${X(p.x)}" y1="${Y(p.y0)}" y2="${Y(p.y1)}" stroke="var(--muted)" stroke-width="1.5"/>
      <circle cx="${X(p.x)}" cy="${Y(p.y)}" r="${p.cur ? 9 : 7}" fill="${p.cur ? "var(--accent)" : "var(--card)"}" stroke="var(--accent)" stroke-width="2.5" style="cursor:pointer"/>
      <text x="${lab[k][0]}" y="${lab[k][1]}" style="fill:var(--ink)">${k + 1}</text></g>`; });
    s += `</svg>`; box.innerHTML = s;
    const key = h("ol", { class: "small", style: "margin:4px 0 0;padding-left:20px;display:grid;gap:2px" }, pts.map(p => h("li", {}, `${p.name}${p.cur ? " (current)" : ""}: inflation peak ${p.x.toFixed(1)}%, weakest growth ${p.y.toFixed(1)}%`)));
    box.append(key);
    tip.textContent = "Numbers next to dots match the list above.";
  }
  function stressFinder(sp) {
    const presets = {
      rupee_inflation: { label: "Rupee weaker than ₹105 AND inflation above 7%", c: [{ var: "inr", op: ">", level: 105, kind: "any", observe: "monthly" }, { var: "cpi_yoy", op: ">", level: 7, kind: "any", observe: "monthly" }] },
      reserves: { label: "FX reserves below $600bn", c: [{ var: "reserves", op: "<", level: 600, kind: "any", observe: "monthly" }] },
      growth: { label: "Growth below 5% in some quarter", c: [{ var: "gdp_yoy", op: "<", level: 5, kind: "any", observe: "quarterly" }] },
      yields: { label: "10-year yield above 8.5%", c: [{ var: "g10", op: ">", level: 8.5, kind: "any", observe: "monthly" }] },
    };
    const sel = h("select", { id: "stress-sel" }, Object.entries(presets).map(([k, v]) => h("option", { value: k }, v.label)));
    const res = h("div", { class: "grid", style: "gap:8px" });
    return h("div", { class: "card", style: "display:grid;gap:12px" }, h("h2", {}, "What would it take to break?"),
      h("p", { class: "muted" }, "Pick a red line. The model searches 90 combinations of oil shock, world slowdown and food shock, under three fuel-price policies, for the smallest combination that crosses it. These are ways things could break in the model, not how likely they are."),
      h("div", { class: "cta-row", style: "align-items:end" }, h("label", { class: "field" }, "Red line", sel), h("button", { class: "btn primary", onclick: e => {
        const btn = e.currentTarget; btn.disabled = true; res.innerHTML = "Searching…";
        setTimeout(() => {
          const r = S.reverseStress(D, sp, presets[sel.value].c, ["freeze_omc_absorb", "full_passthrough", "freeze_budget_comp"]);
          res.innerHTML = ""; btn.disabled = false;
          if (!r.found.length) { res.append(h("p", {}, `None of the ${r.tested} combinations crossed this line in the model's central path.`)); return; }
          const byPol = {}; r.found.forEach(f => (byPol[f.fuel] = byPol[f.fuel] || []).push(f));
          res.append(h("p", { class: "small muted" }, `${r.found.length} of ${r.tested} combinations cross it. The smallest ones, by fuel policy:`));
          for (const [pol, list] of Object.entries(byPol)) res.append(h("div", { class: "event t-constraint" }, h("span", { class: "theme" }, POL.gov_fuel.opts[pol][0]),
            h("p", {}, list.slice(0, 3).map(f => [f.oil ? `oil +$${f.oil} for ${f.months} month${f.months > 1 ? "s" : ""}` : "no new oil shock", f.glob ? `world slowdown ${f.glob}×` : null, f.food ? `food shock +${f.food} pts` : null].filter(Boolean).join(" + ")).join(";  or  "))));
          const none = ["freeze_omc_absorb", "full_passthrough", "freeze_budget_comp"].filter(p => !byPol[p]);
          if (none.length) res.append(h("p", { class: "small" }, `No combination breaks it under: ${none.map(p => POL.gov_fuel.opts[p][0].toLowerCase()).join("; ")}.`));
        }, 30); } }, "Find breaking points")), res);
  }

  // ------------------------------------------------------------------ LEARN
  function renderLearn() {
    const pg = $("#p-learn"); if (pg.dataset.done) return; pg.dataset.done = "1";
    const gl = [
      ["Current account deficit (CAD)", "When India pays the world more for goods, services, interest and transfers than it receives. It must be covered by foreign money coming in, or by the RBI using reserves.", "A bigger deficit only weakens the rupee if it isn't covered by inflows."],
      ["FX reserves", "The RBI's stock of dollars and other foreign assets. It sells them to slow a rupee fall.", "Each dollar sold also removes rupees from banks, so the RBI may put cash back ('sterilisation')."],
      ["Repo rate", "The interest rate at which the RBI lends to banks. It sets the tone for all borrowing costs.", "The MPC meets every two months and can only see data that has been published, usually 1 to 2 months old."],
      ["Inflation (CPI) and core inflation", "How much consumer prices rose over the last year. Core leaves out food and fuel to show underlying pressure.", "RBI targets 4%, with a tolerance band of 2% to 6%."],
      ["Oil marketing companies (OMCs)", "IOC, BPCL and HPCL, which sell petrol, diesel and cooking gas. With pump prices frozen, they lose money when costs rise.", "Their losses are a hidden cost of the shock: someone eventually pays."],
      ["Import parity", "What a litre of fuel costs India at world prices, in rupees. It rises with the oil price AND with a weaker rupee.", "This is compared with the pump price to find the oil companies' margin."],
      ["Output gap", "How far the economy is running above or below its normal, sustainable pace.", "Negative means slack: weaker hiring and investment."],
      ["10-year bond yield", "The interest rate the government pays to borrow for 10 years. It guides long-term loan rates.", "It rises with RBI rates, US rates, inflation expectations and bigger deficits."],
      ["Foreign portfolio investors (FPI)", "Foreign funds buying and selling Indian shares and bonds. They move fast when the world gets nervous.", "Outflows add to the dollars India needs."],
      ["'In 38 of 100 futures'", "How often something happens across the model's simulated futures, under the assumptions you chose.", "It is not a forecast probability. A different model or assumptions would give a different number."],
      ["Fan chart", "The middle line is a typical future. The dark band holds half the futures, the light band 9 in 10.", "The middle line is month-by-month, so it is not itself one single future. Use 'One future' for that."],
      ["Lakh crore", "₹1 lakh crore = ₹1,00,000 crore = ₹1 trillion, roughly $10bn at today's rupee.", "India's GDP this year is about ₹393 lakh crore."],
    ];
    const sg = D.signposts.items;
    const statusOf = s => s.snapshot === null || s.level === null ? ["info", "Check manually"] : ((s.op === ">" ? s.snapshot > s.level : s.snapshot < s.level) ? ["high", "Crossed"] : ["low", "Not yet"]);
    const ach = D.ach;
    const score = { CC: "Strongly fits", C: "Fits", N: "Neutral", I: "Doesn't fit", II: "Strongly against" };
    pg.innerHTML = "";
    pg.append(
      h("div", { class: "section-head" }, h("span", { class: "eyebrow" }, "Learn"), h("h1", {}, "How to read it, and where it can be wrong")),
      h("div", { class: "toc" }, [["l-read", "Reading the charts"], ["l-gloss", "Plain-English terms"], ["l-watch", "What to watch"], ["l-assume", "Big assumptions"], ["l-oil", "Why is oil at $117?"], ["l-blind", "Blind spots"], ["l-src", "Sources"], ["l-hood", "Under the hood"]]
        .map(([id, lab]) => h("a", { class: "btn", href: "#learn", onclick: e => { e.preventDefault(); document.getElementById(id).scrollIntoView({ behavior: "smooth" }); } }, lab))),
      h("div", { id: "l-read", class: "card prose" }, h("h2", {}, "Reading the charts"),
        h("p", {}, "Each chart shows hundreds of futures at once. The solid line is a typical future month by month. The dark band holds half of the futures and the light band 9 in 10. The grey dashed line is the 'nothing new' situation, so the gap between the lines is the effect of the shock you chose. The orange dot is today's real value."),
        h("p", {}, "Wide bands mean the model is unsure. Bands only show randomness inside this model; if the model's assumptions are wrong, reality can land outside them.")),
      h("div", { id: "l-gloss", class: "section-head" }, h("h2", {}, "Plain-English terms")),
      h("div", { class: "gloss" }, gl.map(([t, a, b]) => h("div", { class: "card" }, h("h3", {}, t), h("p", {}, a), h("p", { class: "small muted" }, b)))),
      h("div", { id: "l-watch", class: "card", style: "display:grid;gap:10px" }, h("h2", {}, "What to watch"),
        h("p", { class: "muted" }, `Signals that would tell you which future is unfolding. Values are a dated snapshot from ${D.signposts.snapshot_date}, not live data.`),
        h("div", { class: "table-wrap" }, h("table", { class: "matrix" }, h("thead", {}, h("tr", {}, ["Signal", "Snapshot", "Red line", "Status", "Points to", "Could mislead because"].map(x => h("th", {}, x)))),
          h("tbody", {}, sg.map(s => { const [c, w] = statusOf(s); return h("tr", {}, h("td", {}, s.indicator), h("td", { class: "n" }, s.snapshot ?? "–"), h("td", { class: "n" }, s.level === null ? "–" : `${s.op} ${s.level}`),
            h("td", {}, h("span", { class: "pill " + c }, w)), h("td", {}, (s.scenarios || []).map(x => SCEN[x] ? SCEN[x].name : x).join(", ")), h("td", { class: "small" }, s.false_positive)); }))))),
      h("div", { id: "l-assume", class: "card", style: "display:grid;gap:10px" }, h("h2", {}, "Big assumptions"),
        h("p", { class: "muted" }, "If one of these is wrong, the results move. 'How sure' is the model builder's judgement."),
        ...D.assumptions.items.map(a => h("div", { class: "event t-state" }, h("span", { class: "theme" }, `Matters: ${({ H: "a lot", M: "somewhat", L: "a little" })[a.importance]} · How sure: `, h("span", { class: "pill " + ({ H: "high", M: "mid", L: "low" })[a.uncertainty] }, ({ H: "not very", M: "fairly", L: "quite" })[a.uncertainty])),
          h("p", { class: "txt" }, a.assumption), h("p", { class: "small muted" }, "If wrong: " + a.if_false)))),
      h("div", { id: "l-oil", class: "card", style: "display:grid;gap:10px" }, h("h2", {}, "Why is oil at $117? Four explanations"),
        h("p", { class: "muted" }, "Testing evidence against each explanation. The useful evidence is the kind that fits one explanation but not the others. This is a thinking aid; it does not produce probabilities."),
        h("div", { class: "table-wrap" }, h("table", { class: "matrix" }, h("thead", {}, h("tr", {}, h("th", {}, "Evidence"), Object.values(ach.hypotheses).map(x => h("th", {}, x.name)))),
          h("tbody", {}, ach.evidence.map(e => h("tr", {}, h("td", {}, e.item), Object.keys(ach.hypotheses).map(k => h("td", { class: "small" }, h("span", { class: "pill " + ({ CC: "low", C: "low", N: "info", I: "high", II: "high" })[e[k]] }, score[e[k]]))))))))),
      h("div", { id: "l-blind", class: "card prose" }, h("h2", {}, "Blind spots"), h("ul", { style: "margin:0;padding-left:20px;display:grid;gap:6px" }, D.premortem.model_weaknesses.map(w => h("li", {}, w))),
        h("p", {}, h("b", {}, "Strongest case against the gloomy futures: "), D.premortem.strongest_countercase[0])),
      h("div", { id: "l-src", class: "card", style: "display:grid;gap:8px" }, h("h2", {}, "Sources"), h("p", { class: "muted small" }, "Every starting number comes from a dated source. Model settings are judgement, not estimates."),
        h("ul", { style: "margin:0;padding-left:20px;display:grid;gap:4px" }, D.evidence.filter(e => e.url && e.url.startsWith("http")).map(e => h("li", { class: "small" }, h("a", { href: e.url, target: "_blank", rel: "noopener" }, e.publisher), ` · ${e.item} · ${e.publication_date}`)))),
      h("div", { id: "l-hood", class: "card prose" }, h("h2", {}, "Under the hood"),
        h("p", {}, `This page runs the same engine as the Python model in the India-Sim-Engine repository (engine ${D.engine_version}, parameters ${D.versions.params}). Given identical inputs, the two agree on every number to about one part in a billion; this is checked automatically. The only difference is the random-number stream, which gives statistically equivalent futures.`),
        h("p", {}, "Starting state: 25 October 2026. Horizon: November 2026 to October 2028, monthly. GDP is quarterly. Fiscal years run April to March."),
        h("p", {}, "Not done yet: testing the model against a past episode (such as the 2022 oil shock). Until then, use it to explore and reason, not to predict."),
        h("p", {}, h("a", { href: "https://github.com/alok1511/India-Sim-Engine", target: "_blank", rel: "noopener" }, "github.com/alok1511/India-Sim-Engine"))));
  }

  // ------------------------------------------------------------------ boot
  function boot() {
    $("nav.chapters").append(...CHAPTERS.map(([id, lab]) => h("a", { href: "#" + id, "data-id": id, onclick: e => { e.preventDefault(); go(id); } }, lab)));
    renderToday(); renderWhatIf(); ribbon();
    const start = (location.hash || "").slice(1) || st.section || "today";
    go(start, false);
    if (start !== "whatif") ensureMain();
  }
  boot();
})();
