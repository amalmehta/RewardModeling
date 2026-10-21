/* Reward Shapes site. All data is precomputed in data.js; every interaction is a pure
   re-render from memory, so nothing waits on the network. */
(() => {
  "use strict";
  const D = window.RS_DATA;
  const $ = (s) => document.querySelector(s);
  const SHAPES = D.shapes;
  const NAMES = { sparse: "Sparse goal", dense: "Dense distance", shaped: "Potential-shaped",
                  multi: "Two goals", lava: "Goal + lava" };
  const DASH = { sparse: "", multi: "6 3", shaped: "8 3 2 3", dense: "2 3", lava: "5 2 1 2" };
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const color = (sh) => css(`--c-${sh}`);
  const fmt = (x, d = 3) => (x == null || Number.isNaN(x) ? "–" : (+x).toFixed(d));
  const ARROWS = ["↑", "↓", "←", "→"];
  const state = { shape: "sparse", fb: "prefs", ni: 4, view: "map_canon", rcfb: "prefs", ooshape: "sparse" };
  try { Object.assign(state, JSON.parse(localStorage.getItem("rs-state") || "{}")); } catch (e) {}
  const save = () => { try { localStorage.setItem("rs-state", JSON.stringify(state)); } catch (e) {} };

  /* ---------- abstract (numbers come from the data, never typed) ---------- */
  function abstract() {
    const ns = D.n_star.prefs, nd = D.n_star.demos, h2 = D.H2.by.all;
    const n = (x) => (x == null ? "more than 1000" : x);
    $("#abstract").innerHTML =
      `We take five reward shapes in one 8×8 gridworld (sparse goal, dense distance, potential-shaped, two goals, goal + lava) ` +
      `and recover each from synthetic pairwise preferences (Bradley–Terry) or demonstrations (MaxEnt IRL). ` +
      `Getting a policy within 5% of optimal took ${n(ns.sparse)} preference pairs for the sparse goal, ${n(ns.dense)} for dense, ` +
      `${n(ns.shaped)} for shaped, ${n(ns.multi)} for two goals and ${n(ns.lava)} for lava ` +
      `(demonstrations: ${n(nd.sparse)}, ${n(nd.dense)}, ${n(nd.shaped)}, ${n(nd.multi)}, ${n(nd.lava)}). ` +
      `Across all runs, the EPIC distance correlates with regret at ρ = ${fmt(h2.epic, 2)}, against ρ = ${fmt(h2.pearson, 2)} ` +
      `for raw reward correlation. Labelers and parameters are simulated; see “What is invented here”.`;
  }

  /* ---------- explorer ---------- */
  function heat(v) {
    const lo = css("--heat-lo").split(","), mid = css("--heat-mid").split(","), hi = css("--heat-hi").split(",");
    const t = Math.max(-1, Math.min(1, v));
    const [a, b, u] = t < 0 ? [mid, lo, -t] : [mid, hi, t];
    return `rgb(${a.map((x, i) => Math.round(+x + (b[i] - x) * u)).join(",")})`;
  }
  function buildGrid(el) {
    const frag = document.createDocumentFragment();
    for (let s = 0; s < 64; s++) {
      const c = document.createElement("div");
      c.className = "cell"; c.dataset.s = s;
      c.innerHTML = `<span class="mark"></span><span class="arr"></span>`;
      frag.appendChild(c);
    }
    el.appendChild(frag);
  }
  const L = D.layout, idx = (rc) => rc[0] * L.size + rc[1];
  const marks = {};
  marks[idx(L.goal)] = "●";
  function paintGrid(el, map, policy, shape) {
    const m = Math.max(1e-9, ...map.map(Math.abs));
    const lava = new Set(shape === "lava" ? L.lava.map(idx) : []);
    const second = shape === "multi" ? idx(L.second_goal) : -1;
    el.querySelectorAll(".cell").forEach((c, s) => {
      c.style.backgroundColor = heat(map[s] / m);
      c.dataset.v = map[s];
      const p = policy[s], best = Math.max(...p);
      const arr = c.lastChild;
      arr.textContent = best - Math.min(...p) < 1e-6 ? "·" : ARROWS[p.indexOf(best)];
      c.firstChild.textContent = marks[s] || (s === second ? "○" : lava.has(s) ? "◆" : "");
    });
  }
  function renderExplorer() {
    const n = D.n_grid[state.ni];
    $("#n-out").textContent = n;
    $("#n-in").value = state.ni;
    const t = D.truth[state.shape];
    const ex = D.examples[`${state.shape}|${state.fb}|${n}`];
    paintGrid($("#g-true"), t[state.view], t.policy, state.shape);
    paintGrid($("#g-learned"), ex[state.view], ex.policy, state.shape);
    const cur = D.curves[state.fb];
    const pick = (metric) => cur[metric][state.shape][state.ni];
    $("#ex-stats").innerHTML = [
      ["Normalized regret", ex.regret, pick("regret"), 3],
      ["EPIC distance", ex.epic, pick("epic"), 2],
      ["Raw Pearson distance", ex.pearson, pick("pearson"), 2],
    ].map(([k, v, agg, d]) => `<div class="stat"><span>${k}</span><b>${fmt(v, d)}</b>` +
      `<span>10-seed mean ${fmt(agg.mean, d)} [${fmt(agg.lo, d)}, ${fmt(agg.hi, d)}]</span></div>`).join("");
    syncRadios();
  }

  /* ---------- radios / chips ---------- */
  function chips(el, key, onChange) {
    el.innerHTML = SHAPES.map((sh) => `<button class="chip" role="radio" data-v="${sh}" aria-checked="false">` +
      `<i style="background:var(--c-${sh})"></i>${NAMES[sh]}</button>`).join("");
    bindRadio(el, key, onChange);
  }
  function bindRadio(el, key, onChange) {
    el.addEventListener("click", (e) => {
      const b = e.target.closest("[data-v]");
      if (!b) return;
      state[key] = b.dataset.v; save(); onChange();
    });
    el.dataset.key = key;
  }
  function syncRadios() {
    document.querySelectorAll("[data-key]").forEach((el) => {
      el.querySelectorAll("[data-v]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.v === state[el.dataset.key])));
    });
  }

  /* ---------- line chart (SVG, crosshair tooltip) ---------- */
  const tip = $("#tip");
  function lineChart(el, opt) {
    const W = el.clientWidth || 440, H = opt.height || 240, M = { l: 44, r: opt.labels ? 92 : 14, t: 24, b: 34 };
    const xs = opt.series[0].points.map((p) => p.x);
    const all = opt.series.flatMap((s) => s.points.flatMap((p) => [p.lo ?? p.y, p.hi ?? p.y]));
    const y0 = opt.ymin ?? Math.min(0, ...all), y1 = opt.ymax ?? Math.max(...all) * 1.05;
    const lx = (x) => (opt.xlog ? Math.log10(x) : x);
    const x0 = lx(Math.min(...xs)), x1 = lx(Math.max(...xs));
    const X = (x) => M.l + ((lx(x) - x0) / (x1 - x0 || 1)) * (W - M.l - M.r);
    const Y = (y) => H - M.b - ((y - y0) / (y1 - y0 || 1)) * (H - M.t - M.b);
    const path = (pts, k) => pts.map((p, i) => `${i ? "L" : "M"}${X(p.x).toFixed(1)},${Y(p[k]).toFixed(1)}`).join("");
    const yt = ticks(y0, y1, 4);
    const xt = opt.xticks || xs;
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${opt.title}"><text class="title" x="${M.l}" y="14">${opt.title}</text><g class="ax">`;
    yt.forEach((v) => { s += `<line class="gridl" x1="${M.l}" x2="${W - M.r}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${M.l - 6}" y="${Y(v) + 4}" text-anchor="end">${+v.toFixed(2)}</text>`; });
    xt.forEach((v) => { s += `<text x="${X(v)}" y="${H - M.b + 16}" text-anchor="middle">${v}</text>`; });
    s += `<line x1="${M.l}" x2="${W - M.r}" y1="${H - M.b}" y2="${H - M.b}"/>`;
    s += `<text x="${(M.l + W - M.r) / 2}" y="${H - 4}" text-anchor="middle">${opt.xlabel}</text></g>`;
    if (opt.threshold != null) s += `<line class="thr" x1="${M.l}" x2="${W - M.r}" y1="${Y(opt.threshold)}" y2="${Y(opt.threshold)}"/>`;
    opt.series.forEach((se, i) => {
      const band = se.points[0].lo != null
        ? `M${se.points.map((p) => `${X(p.x).toFixed(1)},${Y(p.hi).toFixed(1)}`).join("L")}L${se.points.slice().reverse().map((p) => `${X(p.x).toFixed(1)},${Y(p.lo).toFixed(1)}`).join("L")}Z` : "";
      s += `<g class="series" data-i="${i}">${band ? `<path class="b" d="${band}" fill="${se.color}"/>` : ""}` +
        `<path class="l" d="${path(se.points, "y")}" stroke="${se.color}" stroke-dasharray="${se.dash || ""}"/>`;
      if (opt.labels) {
        const last = se.points[se.points.length - 1];
        s += `<text class="lbl" x="${X(last.x) + 6}" y="${Y(last.y) + 4}" data-ly="${Y(last.y)}">${se.name}</text>`;
      }
      s += `</g>`;
    });
    s += `<line class="cross" y1="${M.t}" y2="${H - M.b}" x1="-10" x2="-10"/><rect x="${M.l}" y="${M.t}" width="${W - M.l - M.r}" height="${H - M.t - M.b}" fill="transparent"/></svg>`;
    el.innerHTML = s;
    if (opt.labels) declutter(el);
    const svg = el.firstChild, cross = svg.querySelector(".cross"), hit = svg.lastChild.previousSibling ? svg.querySelector("rect") : null;
    const move = (e) => {
      const r = svg.getBoundingClientRect(), px = ((e.clientX - r.left) / r.width) * W;
      let bi = 0, bd = Infinity;
      xs.forEach((x, i) => { const d = Math.abs(X(x) - px); if (d < bd) { bd = d; bi = i; } });
      cross.setAttribute("x1", X(xs[bi])); cross.setAttribute("x2", X(xs[bi]));
      const rows = opt.series.map((se) => ({ se, p: se.points[bi] })).sort((a, b) => b.p.y - a.p.y);
      tip.innerHTML = `<div class="muted">${opt.xname || opt.xlabel} = ${+(+xs[bi]).toPrecision(3)}</div>` + rows.map(({ se, p }) =>
        `<div class="row"><span><i style="background:${se.color}"></i>${se.name}</span><b>${fmt(p.y, opt.digits ?? 3)}</b></div>`).join("");
      tip.hidden = false;
      const tx = Math.min(e.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
      tip.style.left = `${tx}px`; tip.style.top = `${e.clientY + 14}px`;
    };
    hit.addEventListener("pointermove", move);
    hit.addEventListener("pointerleave", () => { tip.hidden = true; cross.setAttribute("x1", -10); cross.setAttribute("x2", -10); });
  }
  function declutter(el) {
    const ls = [...el.querySelectorAll(".lbl")].sort((a, b) => a.dataset.ly - b.dataset.ly);
    let prev = -Infinity;
    ls.forEach((t) => { const y = Math.max(+t.dataset.ly, prev + 12); t.setAttribute("y", y + 4); prev = y; });
  }
  function ticks(a, b, n) {
    const step = Math.pow(10, Math.floor(Math.log10((b - a) / n || 1)));
    const err = (b - a) / n / step, k = err >= 5 ? 10 : err >= 2 ? 5 : err >= 1.5 ? 2 : 1;
    const st = step * k, out = [];
    for (let v = Math.ceil(a / st) * st; v <= b + 1e-9; v += st) out.push(+v.toFixed(10));
    return out;
  }
  const shapeSeries = (curves, xkey = "n") => SHAPES.map((sh) => ({
    name: sh, color: color(sh), dash: DASH[sh],
    points: curves[sh].map((p) => ({ x: p[xkey], y: p.mean, lo: p.lo, hi: p.hi })),
  }));

  function renderRecovery() {
    const c = D.curves[state.rcfb];
    lineChart($("#c-regret"), { title: "Normalized regret", xlabel: "N", xlog: true, ymin: 0, ymax: 1,
      threshold: D.recovered_threshold, labels: true, series: shapeSeries(c.regret) });
    lineChart($("#c-epic"), { title: "EPIC distance", xlabel: "N", xlog: true, ymin: 0, ymax: 0.75, digits: 2,
      labels: true, series: shapeSeries(c.epic) });
    const t = $("#rc-table");
    if (!t.hidden) t.innerHTML = recoveryTable(c);
    syncRadios();
  }
  function recoveryTable(c) {
    const head = `<tr><th>shape</th>${D.n_grid.map((n) => `<th>N=${n}</th>`).join("")}<th>N*</th></tr>`;
    const rows = SHAPES.map((sh) => `<tr><td><span class="dot" style="background:var(--c-${sh})"></span>${NAMES[sh]}</td>` +
      c.regret[sh].map((p, i) => `<td>${fmt(p.mean)} <span class="muted">/ ${fmt(c.epic[sh][i].mean, 2)}</span></td>`).join("") +
      `<td>${D.n_star[state.rcfb][sh] ?? ">1000"}</td></tr>`).join("");
    return `<table><caption class="muted small" style="text-align:left;padding:6px 0">regret / EPIC, 10-seed means</caption>${head}${rows}</table>`;
  }

  function renderMetric() {
    const by = D.H2.by, keys = ["all", ...SHAPES];
    const ci = (a) => `[${fmt(a[0], 2)}, ${fmt(a[1], 2)}]`;
    $("#metric-table").innerHTML = `<table><tr><th>runs</th><th>EPIC ρ</th><th>raw Pearson ρ</th><th>difference</th></tr>` +
      keys.map((k) => `<tr><td>${k === "all" ? "<b>All shapes</b>" : `<span class="dot" style="background:var(--c-${k})"></span>${NAMES[k]}`}</td>` +
        `<td>${fmt(by[k].epic, 2)} <span class="muted">${ci(by[k].epic_ci)}</span></td>` +
        `<td>${fmt(by[k].pearson, 2)} <span class="muted">${ci(by[k].pearson_ci)}</span></td>` +
        `<td>${fmt(by[k].diff, 2)} <span class="muted">${ci(by[k].diff_ci)}</span></td></tr>`).join("") + `</table>`;
  }

  function renderAblations() {
    lineChart($("#c-myopic"), { title: "Myopic labeler: regret", xlabel: "N pairs", xlog: true, ymin: 0, ymax: 1,
      threshold: D.recovered_threshold, labels: true, series: shapeSeries(D.myopic.regret) });
    lineChart($("#c-beta"), { title: "Regret against β (N = 300)", xlabel: "β", xname: "β", xlog: true, ymin: 0,
      labels: true, series: SHAPES.map((sh) => ({ name: sh, color: color(sh), dash: DASH[sh],
        points: D.beta[sh]["300"].map((r) => ({ x: r.beta, y: r.mean, lo: r.lo, hi: r.hi })) })) });
  }

  function renderOveropt() {
    const o = D.overopt[state.ooshape], ramp = ["--n1", "--n2", "--n3"];
    lineChart($("#c-overopt"), { title: `${NAMES[state.ooshape]}: true return as pressure rises`, xlabel: "optimization pressure λ", xname: "λ",
      xlog: true, ymin: Math.min(0, ...Object.values(o).flatMap((v) => v.points.map((p) => p.lo))), ymax: 1.02, labels: true,
      xticks: [0.1, 1, 10, 100], height: 260,
      series: Object.keys(o).map((n, i) => ({ name: `N = ${n}`, color: css(ramp[i]),
        points: o[n].points.map((p) => ({ x: p.lambda, y: p.mean, lo: p.lo, hi: p.hi })) })) });
    syncRadios();
  }

  function renderShaping() {
    const sp = D.shaping;
    lineChart($("#c-shaping"), { title: "Regret on the sparse task during Q-learning", xlabel: "episodes", xname: "episode",
      ymin: 0, ymax: 1, threshold: D.recovered_threshold, labels: true, height: 260,
      xticks: [0, 500, 1000, 1500, 2000, 2500, 3000],
      series: Object.keys(sp).map((tr) => ({ name: `trained on ${tr}`, color: color(tr), dash: DASH[tr],
        points: sp[tr].curve.filter((_, i) => i % 3 === 0).map((p) => ({ x: p.episode, y: p.mean, lo: p.lo, hi: p.hi })) })) });
    $("#shaping-note").textContent = Object.keys(sp).map((tr) =>
      `${tr}: ${sp[tr].n_solved}/10 seeds reached regret ≤ 0.05` + (sp[tr].median_solved != null ? ` (median ${sp[tr].median_solved} episodes)` : "")).join(" · ");
  }

  function renderVerdicts() {
    const v = (ok, title, text) => `<div class="verdict"><div class="tag ${ok ? "yes" : "no"}">${ok ? "✓ Supported" : "✕ Not supported"}</div>` +
      `<strong>${title}</strong><p>${text}</p></div>`;
    const h1 = D.H1, h2 = D.H2, h3 = D.H3;
    $("#verdicts").innerHTML =
      v(h1.supported, "H1 · Sparse and lava need ≥3× the preferences dense needs",
        `N* ratios: sparse/dense ${fmt(h1.ratio_sparse_dense, 1)}×, lava/dense ${fmt(h1.ratio_lava_dense, 1)}×.`) +
      v(h2.supported, "H2 · EPIC predicts regret better than raw Pearson, most of all on shaped",
        `ρ difference over all runs ${fmt(h2.by.all.diff, 2)} [${fmt(h2.by.all.diff_ci[0], 2)}, ${fmt(h2.by.all.diff_ci[1], 2)}]; largest gap on ${h2.largest_gap_shape}.`) +
      v(h3.supported, "H3 · A myopic labeler leaves a regret floor, worst for sparse and lava",
        `Regret at N = 1000: ${SHAPES.map((sh) => `${sh} ${fmt(h3.by[sh].myopic_n1000, 2)}`).join(", ")}.`);
  }

  /* ---------- wiring ---------- */
  function renderCharts() { renderRecovery(); renderAblations(); renderOveropt(); renderShaping(); }
  function init() {
    abstract();
    buildGrid($("#g-true")); buildGrid($("#g-learned"));
    chips($("#shape-chips"), "shape", renderExplorer);
    bindRadio($("#fb-seg"), "fb", renderExplorer);
    bindRadio($("#view-seg"), "view", renderExplorer);
    $("#n-in").addEventListener("input", (e) => { state.ni = +e.target.value; save(); renderExplorer(); });
    bindRadio($("#rc-fb"), "rcfb", renderRecovery);
    chips($("#oo-chips"), "ooshape", renderOveropt);
    $("#rc-table-btn").addEventListener("click", (e) => {
      const t = $("#rc-table"); t.hidden = !t.hidden; e.target.textContent = t.hidden ? "Show table" : "Hide table"; renderRecovery();
    });
    // hover on grid cells shows the exact value
    document.querySelectorAll(".grid").forEach((g) => {
      g.addEventListener("pointermove", (e) => {
        const c = e.target.closest(".cell"); if (!c) return;
        const s = +c.dataset.s;
        tip.innerHTML = `<div class="muted">cell (${Math.floor(s / 8)}, ${s % 8})</div><div class="row"><span>reward</span><b>${fmt(+c.dataset.v, 3)}</b></div>`;
        tip.hidden = false; tip.style.left = `${e.clientX + 14}px`; tip.style.top = `${e.clientY + 14}px`;
      });
      g.addEventListener("pointerleave", () => { tip.hidden = true; });
    });
    $("#theme").addEventListener("click", () => {
      const cur = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      const next = cur === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem("rs-theme", next); } catch (e) {}
      renderExplorer(); renderCharts();
    });
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { renderExplorer(); renderCharts(); });
    let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(renderCharts, 120); });
    renderExplorer(); renderVerdicts(); renderMetric(); renderCharts();
  }
  init();
})();
