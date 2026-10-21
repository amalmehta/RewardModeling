"""Aggregate raw runs into summary statistics, hypothesis verdicts, paper macros and site data."""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from . import env as E
from .experiments import BETA_N, BETAS, LAMBDAS, N_GRID, OVEROPT_N, RECOVERED, RESULTS, SHAPING_TRAIN

ROOT = RESULTS.parent
BOOT = 2000


def load(tag="confirm"):
    d = RESULTS / tag
    return {name: [json.loads(l) for l in open(d / f"{name}.jsonl")]
            for name in ("recovery", "overopt", "shaping")}


_CI_RNG = np.random.default_rng(12345)


def mean_ci(x):
    """Mean with a 95% percentile-bootstrap interval over seeds (stays inside the metric's range)."""
    x = np.asarray(x, float)
    m = float(x.mean())
    if len(x) < 2:
        return m, m, m
    boots = x[_CI_RNG.integers(len(x), size=(BOOT, len(x)))].mean(1)
    return m, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def curves(rows, study, fb, metric, labeler=None, beta=1.0):
    out = {}
    for shape in E.SHAPES:
        pts = []
        for n in N_GRID:
            xs = [r[metric] for r in rows if r["study"] == study and r["shape"] == shape
                  and r["feedback"] == fb and r["n"] == n]
            m, lo, hi = mean_ci(xs)
            pts.append({"n": n, "mean": m, "lo": lo, "hi": hi, "sd": float(np.std(xs, ddof=1)),
                        "k": len(xs)})
        out[shape] = pts
    return out


def n_star(curve):
    for p in curve:
        if p["mean"] <= RECOVERED:
            return p["n"]
    return None


def spearman_by_seed(rows, metric, shapes):
    """Spearman(metric, regret) over all main runs for the given shapes, with a seed-cluster
    bootstrap 95% CI."""
    sel = [r for r in rows if r["study"] == "main" and r["shape"] in shapes]
    seeds = sorted({r["seed"] for r in sel})
    by_seed = defaultdict(list)
    for r in sel:
        by_seed[r["seed"]].append((r[metric], r["regret"]))
    pts = np.array([p for s in seeds for p in by_seed[s]])
    rho = stats.spearmanr(pts[:, 0], pts[:, 1]).statistic
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(BOOT):
        pick = rng.choice(seeds, len(seeds))
        b = np.array([p for s in pick for p in by_seed[s]])
        boots.append(stats.spearmanr(b[:, 0], b[:, 1]).statistic)
    return float(rho), boots


def diff_ci(a_boot, b_boot):
    d = np.array(a_boot) - np.array(b_boot)
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def summarize(tag="confirm"):
    data = load(tag)
    rec = data["recovery"]
    S = {"recovered_threshold": RECOVERED, "n_grid": N_GRID, "shapes": E.SHAPES}

    S["curves"] = {fb: {m: curves(rec, "main", fb, m) for m in ("regret", "epic", "pearson")}
                   for fb in ("prefs", "demos")}
    S["myopic"] = {m: curves(rec, "myopic", "prefs", m) for m in ("regret", "epic")}
    S["n_star"] = {fb: {sh: n_star(S["curves"][fb]["regret"][sh]) for sh in E.SHAPES}
                   for fb in ("prefs", "demos")}

    # Controls
    S["random_control"] = {sh: {m: mean_ci([r[m] for r in rec if r["study"] == "random"
                                             and r["shape"] == sh]) for m in ("regret", "epic")}
                           for sh in E.SHAPES}

    # H1: sparse and lava need >= 3x the preferences dense needs
    ns = S["n_star"]["prefs"]
    big = 10 * N_GRID[-1]  # "not recovered on the grid" counts as beyond the grid

    def ratio(a, b):
        return (ns[a] or big) / (ns[b] or big)
    S["H1"] = {"n_star_prefs": ns, "ratio_sparse_dense": ratio("sparse", "dense"),
               "ratio_lava_dense": ratio("lava", "dense")}
    S["H1"]["supported"] = bool(S["H1"]["ratio_sparse_dense"] >= 3 and S["H1"]["ratio_lava_dense"] >= 3)

    # H2: EPIC predicts regret better than raw Pearson (Spearman), largest gap on shaped
    h2 = {}
    for name, shapes in [("all", E.SHAPES)] + [(sh, [sh]) for sh in E.SHAPES]:
        re_, be = spearman_by_seed(rec, "epic", shapes)
        rp, bp = spearman_by_seed(rec, "pearson", shapes)
        lo, hi = diff_ci(be, bp)
        h2[name] = {"epic": re_, "epic_ci": [float(np.percentile(be, 2.5)), float(np.percentile(be, 97.5))],
                    "pearson": rp, "pearson_ci": [float(np.percentile(bp, 2.5)), float(np.percentile(bp, 97.5))],
                    "diff": re_ - rp, "diff_ci": [lo, hi]}
    gaps = {sh: h2[sh]["diff"] for sh in E.SHAPES}
    S["H2"] = {"by": h2, "largest_gap_shape": max(gaps, key=gaps.get),
               "supported": bool(h2["all"]["diff_ci"][0] > 0 and max(gaps, key=gaps.get) == "shaped")}

    # H3: myopic labeler leaves a regret floor that does not shrink with N, largest for sparse/lava
    h3 = {}
    for sh in E.SHAPES:
        last = S["myopic"]["regret"][sh][-1]
        prev = S["myopic"]["regret"][sh][-2]
        std_last = S["curves"]["prefs"]["regret"][sh][-1]
        h3[sh] = {"myopic_n1000": last["mean"], "myopic_n300": prev["mean"],
                  "standard_n1000": std_last["mean"],
                  "floor": bool(last["mean"] > RECOVERED and last["mean"] >= prev["mean"] - 0.02)}
    order = sorted(E.SHAPES, key=lambda sh: -h3[sh]["myopic_n1000"])
    S["H3"] = {"by": h3, "worst_two": order[:2],
               "supported": bool(all(h3[sh]["floor"] for sh in ("sparse", "lava"))
                                 and set(order[:2]) == {"sparse", "lava"})}

    # beta ablation
    beta = {}
    for sh in E.SHAPES:
        beta[sh] = {}
        for n in BETA_N:
            row = []
            for b in BETAS:
                study = "main" if b == 1.0 else "beta"
                xs = [r["regret"] for r in rec if r["study"] == study and r["shape"] == sh
                      and r["feedback"] == "prefs" and r["n"] == n and r.get("beta", 1.0) == b]
                e = [r["epic"] for r in rec if r["study"] == study and r["shape"] == sh
                     and r["feedback"] == "prefs" and r["n"] == n and r.get("beta", 1.0) == b]
                m, lo, hi = mean_ci(xs)
                row.append({"beta": b, "mean": m, "lo": lo, "hi": hi, "epic": float(np.mean(e))})
            beta[sh][str(n)] = row
    S["beta"] = beta

    # Overoptimization
    oo = {}
    for sh in E.SHAPES:
        oo[sh] = {}
        for n in OVEROPT_N:
            runs = [r["curve"] for r in data["overopt"] if r["shape"] == sh and r["n"] == n]
            pts = []
            for i, lam in enumerate(LAMBDAS):
                m, lo, hi = mean_ci([c[i]["true"] for c in runs])
                pts.append({"lambda": lam, "kl": float(np.mean([c[i]["kl"] for c in runs])),
                            "mean": m, "lo": lo, "hi": hi})
            peak = max(pts, key=lambda p: p["mean"])
            oo[sh][str(n)] = {"points": pts, "peak_lambda": peak["lambda"],
                              "drop_from_peak": peak["mean"] - pts[-1]["mean"]}
    S["overopt"] = oo

    # Shaping-speed
    sh_rows = data["shaping"]
    sp = {}
    for tr in SHAPING_TRAIN:
        runs = [r for r in sh_rows if r["train"] == tr]
        solved = [r["solved"] for r in runs]
        eps = [c[0] for c in runs[0]["curve"]]
        pts = []
        for i, ep in enumerate(eps):
            m, lo, hi = mean_ci([r["curve"][i][1] for r in runs])
            pts.append({"episode": ep, "mean": m, "lo": lo, "hi": hi})
        solved_num = [s for s in solved if s is not None]
        sp[tr] = {"curve": pts, "solved": solved, "n_solved": len(solved_num),
                  "median_solved": float(np.median(solved_num)) if solved_num else None,
                  "final_regret": pts[-1]["mean"]}
    S["shaping"] = sp
    S["n_runs"] = {k: len(v) for k, v in data.items()}
    S["seconds_total"] = float(sum(r.get("seconds", 0) for r in rec))
    return S, rec


def write_all(tag="confirm"):
    S, rec = summarize(tag)
    (RESULTS / "summary.json").write_text(json.dumps(S, indent=1))
    write_paper_numbers(S)
    write_site_data(S, rec)
    return S


def _fmt_n(n):
    return r"$>$1000" if n is None else str(n)


def write_paper_numbers(S):
    """Every number quoted in the paper comes from here, never typed by hand."""
    m = {}
    ns = S["n_star"]
    for fb in ("prefs", "demos"):
        for sh in E.SHAPES:
            m[f"nstar{fb}{sh}"] = _fmt_n(ns[fb][sh])
    for fb in ("prefs", "demos"):
        for sh in E.SHAPES:
            last = S["curves"][fb]["epic"][sh][-1]
            m[f"epic{fb}{sh}"] = f"{last['mean']:.2f}"
            m[f"regret{fb}{sh}"] = f"{S['curves'][fb]['regret'][sh][-1]['mean']:.3f}"
    words = dict(zip(N_GRID, ["one", "three", "ten", "thirty", "hundred", "threehundred", "thousand"]))
    for sh in E.SHAPES:
        for i, n in enumerate(N_GRID):
            for fb in ("prefs", "demos"):
                m[f"reg{fb}{sh}{words[n]}"] = f"{S['curves'][fb]['regret'][sh][i]['mean']:.2f}"
            m[f"regmyopic{sh}{words[n]}"] = f"{S['myopic']['regret'][sh][i]['mean']:.2f}"
        for n in BETA_N:
            for b in BETAS:
                row = next(r for r in S["beta"][sh][str(n)] if r["beta"] == b)
                bw = {0.3: "low", 1.0: "one", 3.0: "three", 10.0: "ten"}[b]
                m[f"regbeta{sh}{words[n]}{bw}"] = f"{row['mean']:.2f}"
    h2 = S["H2"]["by"]
    for k in ["all"] + E.SHAPES:
        m[f"rhoepic{k}"] = f"{h2[k]['epic']:.2f}"
        m[f"rhopearson{k}"] = f"{h2[k]['pearson']:.2f}"
        m[f"rhodiff{k}"] = f"{h2[k]['diff']:.2f}"
        m[f"rhodifflo{k}"] = f"{h2[k]['diff_ci'][0]:.2f}"
        m[f"rhodiffhi{k}"] = f"{h2[k]['diff_ci'][1]:.2f}"
    m["Hone"] = "supported" if S["H1"]["supported"] else "not supported"
    m["Htwo"] = "supported" if S["H2"]["supported"] else "not supported"
    m["Hthree"] = "supported" if S["H3"]["supported"] else "not supported"
    m["ratiosparsedense"] = f"{S['H1']['ratio_sparse_dense']:.1f}"
    m["ratiolavadense"] = f"{S['H1']['ratio_lava_dense']:.1f}"
    m["largestgap"] = S["H2"]["largest_gap_shape"]
    for sh in E.SHAPES:
        h = S["H3"]["by"][sh]
        m[f"myopic{sh}"] = f"{h['myopic_n1000']:.3f}"
        m[f"standard{sh}"] = f"{h['standard_n1000']:.3f}"
        m[f"randregret{sh}"] = f"{S['random_control'][sh]['regret'][0]:.2f}"
        m[f"randepic{sh}"] = f"{S['random_control'][sh]['epic'][0]:.2f}"
        for n in OVEROPT_N:
            m[f"oodrop{sh}{['a','b','c'][OVEROPT_N.index(n)]}"] = f"{S['overopt'][sh][str(n)]['drop_from_peak']:.3f}"
    for tr in SHAPING_TRAIN:
        sp = S["shaping"][tr]
        m[f"qsolved{tr}"] = str(sp["n_solved"])
        m[f"qmedian{tr}"] = "never" if sp["median_solved"] is None else f"{sp['median_solved']:.0f}"
        m[f"qfinal{tr}"] = f"{sp['final_regret']:.3f}"
    m["nruns"] = str(S["n_runs"]["recovery"])
    m["cpuminutes"] = f"{S['seconds_total'] / 60:.0f}"
    lines = ["% generated by rewardshapes.analysis - do not edit"]
    for k, v in m.items():
        assert k.isalpha(), k
        lines.append(rf"\newcommand{{\{k}}}{{{v}}}")
    (ROOT / "paper" / "numbers.tex").write_text("\n".join(lines) + "\n")


def write_site_data(S, rec):
    env = E.make_env()
    from .metrics import canonicalize, entry_map
    from .planning import greedy_policy, q_optimal
    truth = {}
    for sh in E.SHAPES:
        R = E.true_reward(sh, env)
        truth[sh] = {"map_raw": entry_map(R, env.coverage).round(4).tolist(),
                     "map_canon": entry_map(canonicalize(R, env.gamma), env.coverage).round(4).tolist(),
                     "policy": greedy_policy(q_optimal(R, env)).round(3).tolist()}
    examples = {}
    for r in rec:
        if r["study"] == "main" and r["seed"] == 0:
            examples[f"{r['shape']}|{r['feedback']}|{r['n']}"] = {
                k: r[k] for k in ("map_raw", "map_canon", "policy", "regret", "epic", "pearson")}
    site = {k: S[k] for k in ("n_grid", "shapes", "curves", "myopic", "n_star", "H1", "H2", "H3",
                              "beta", "overopt", "shaping", "recovered_threshold", "random_control")}
    site.update(truth=truth, examples=examples, layout={
        "size": E.SIZE, "goal": E.GOAL, "second_goal": E.SECOND_GOAL, "lava": E.LAVA})
    (ROOT / "site" / "data.js").write_text("window.RS_DATA = " + json.dumps(site, separators=(",", ":")) + ";\n")


if __name__ == "__main__":
    S = write_all()
    print(json.dumps({k: S[k] for k in ("n_star", "H1")}, indent=1))
    print("H2", {k: (round(v["epic"], 2), round(v["pearson"], 2), [round(x, 2) for x in v["diff_ci"]])
                 for k, v in S["H2"]["by"].items()}, S["H2"]["supported"])
    print("H3", S["H3"])
