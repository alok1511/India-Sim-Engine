// Reads a parity case (spec, injected params/shocks) from argv[2], runs the JS engine, writes full histories to argv[3].
const fs = require("fs");
const S = require("../web/engine.js");
const D = JSON.parse(fs.readFileSync(__dirname + "/../web/data.json", "utf8"));
const c = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = [];
for (let j = 0; j < c.params.length; j++) {
  const sh = {}; for (const k in c.shocks[j]) sh[k] = Float64Array.from(c.shocks[j][k]);
  const H = S.simulatePath(D, c.spec, c.params[j], sh);
  const o = {}; for (const k in H) if (k !== "_meta") o[k] = Array.from(H[k], x => (Number.isNaN(x) ? null : x));
  out.push(o);
}
fs.writeFileSync(process.argv[3], JSON.stringify(out));
