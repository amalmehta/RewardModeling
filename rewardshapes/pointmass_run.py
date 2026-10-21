"""Point-mass extension: experiments -> raw runs -> summary -> figure, from one config.

    uv run python -m rewardshapes.pointmass_run                    # confirmatory run (seeds 0-9)
    uv run python -m rewardshapes.pointmass_run --pilot            # tuning seeds 100-104
    uv run python -m rewardshapes.pointmass_run --skip-experiments # re-analyse existing runs

Every job is a pure function of the config and its (shape, feedback, N, seed) key. Raw
rows use the gridworld's recovery.jsonl schema (study, shape, feedback, n, seed, regret,
epic, pearson, seconds) plus env = "pointmass".
"""
import argparse
import json
import logging
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from . import learn
from . import pointmass as P
from .analysis import curves, mean_ci, n_star
from .experiments import RECOVERED, RESULTS, _rng

log = logging.getLogger("rewardshapes")

_CFG, _TASK, _CACHE = None, None, {}


def _init(cfg):
    global _CFG, _TASK
    _CFG, _TASK = cfg, None
    _CACHE.clear()


def _task():
    global _TASK
    if _TASK is None:
        _TASK = P.make_task(_CFG)
    return _TASK


def _truth(shape):
    """True reward, its optimal lattice Q, and (J*, J_uniform), cached per worker."""
    if shape not in _CACHE:
        task = _task()
        R = P.true_reward(shape, task)
        _CACHE[shape] = (R, P.q_star(R, task), P.regret_cache(R, task))
    return _CACHE[shape]


def learn_reward(shape, fb, n, seed):
    task, L = _task(), _CFG["learn"]
    R, Q, _ = _truth(shape)
    rng = _rng("pointmass", shape, fb, n, seed, int(L["beta"] * 1000), 0)
    if fb == "prefs":
        t1, t2, y = P.preferences(rng, task, R, Q, n, beta=L["beta"])
        d = (P.trajectory_features(*t1, task.feats, task.gamma)
             - P.trajectory_features(*t2, task.feats, task.gamma))
        theta = learn.fit_bradley_terry(d, y, L["l2"], L["beta"], L["bt_max_iter"])
    elif fb == "demos":
        S, A = P.demonstrations(rng, task, R, n)
        theta = learn.fit_maxent_linear(S, A, task, L["l2"], L["maxent_max_iter"])
    elif fb == "random":
        theta = rng.normal(size=2 * task.feats.K)
    else:
        raise ValueError(fb)
    return P.LinearReward(theta, task.feats)


def recovery_job(cfg):
    t = time.time()
    task = _task()
    R, _, cache = _truth(cfg["shape"])
    R_hat = learn_reward(cfg["shape"], cfg["feedback"], cfg["n"], cfg["seed"])
    out = dict(cfg, regret=float(P.normalized_regret(task, R, R_hat, cache)),
               epic=P.epic(R, R_hat, task), pearson=P.raw_pearson(R, R_hat, task),
               seconds=round(time.time() - t, 2))
    if cfg["seed"] == 0 and cfg["study"] == "main":
        out["theta"] = R_hat.theta.round(5).tolist()
    return out


def recovery_configs(cfg, seeds):
    r = cfg["run"]
    base = dict(env="pointmass")
    cfgs = [dict(base, study="main", shape=sh, feedback=fb, n=n, seed=s)
            for sh in r["shapes"] for n in r["n_grid"] for s in seeds for fb in r["feedback"]]
    cfgs += [dict(base, study="random", shape=sh, feedback="random", n=0, seed=s)
             for sh in r["shapes"] for s in seeds]
    return cfgs


def out_dir(pilot):
    return RESULTS / ("pilot" if pilot else "confirm") / "pointmass"


def run(cfg, pilot=False, procs=None):
    seeds = cfg["run"]["pilot_seeds" if pilot else "seeds"]
    out = out_dir(pilot)
    out.mkdir(parents=True, exist_ok=True)
    # MaxEnt fits dominate; longest jobs first keeps the pool busy until the end
    cfgs = sorted(recovery_configs(cfg, seeds),
                  key=lambda c: -(c["n"] * (20 if c["feedback"] == "demos" else 1)))
    t = time.time()
    rows = []
    with Pool(procs or cfg["run"]["procs"], initializer=_init, initargs=(cfg,)) as pool:
        for i, row in enumerate(pool.imap_unordered(recovery_job, cfgs, chunksize=1)):
            rows.append(row)
            if (i + 1) % 50 == 0:
                log.info("pointmass: %d/%d (%.0fs)", i + 1, len(cfgs), time.time() - t)
    rows.sort(key=lambda r: (r["study"], r["shape"], r["feedback"], r["n"], r["seed"]))
    with open(out / "recovery.jsonl", "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    log.info("pointmass: %d jobs in %.0fs -> %s", len(rows), time.time() - t, out / "recovery.jsonl")


# ---------------------------------------------------------------- analysis


def summarize(cfg, pilot=False):
    rec = [json.loads(line) for line in open(out_dir(pilot) / "recovery.jsonl")]
    shapes, n_grid, fbs = cfg["run"]["shapes"], cfg["run"]["n_grid"], cfg["run"]["feedback"]
    S = {"env": "pointmass", "recovered_threshold": RECOVERED, "n_grid": n_grid, "shapes": shapes}
    S["curves"] = {fb: {m: curves(rec, "main", fb, m, shapes=shapes, n_grid=n_grid)
                        for m in ("regret", "epic", "pearson")} for fb in fbs}
    S["n_star"] = {fb: {sh: n_star(S["curves"][fb]["regret"][sh]) for sh in shapes} for fb in fbs}
    S["random_control"] = {sh: {m: mean_ci([r[m] for r in rec if r["study"] == "random"
                                             and r["shape"] == sh]) for m in ("regret", "epic")}
                           for sh in shapes}
    _init(cfg)
    task = _task()
    S["epic_floor"] = {sh: P.epic_floor(_truth(sh)[0], task) for sh in shapes}
    S["reference_returns"] = {sh: {"optimal": _truth(sh)[2][0], "uniform": _truth(sh)[2][1]}
                              for sh in shapes}

    def last(fb, m, sh):
        return S["curves"][fb][m][sh][-1]["mean"]

    # C1: demos cannot identify the distractor's weight, so EPIC overstates the error there
    c1 = {"regret_distractor": last("demos", "regret", "distractor"),
          "epic_distractor": last("demos", "epic", "distractor"),
          "epic_dense": last("demos", "epic", "dense")}
    c1["supported"] = bool(c1["regret_distractor"] <= RECOVERED
                           and c1["epic_distractor"] >= c1["epic_dense"] + 0.15)
    # C2: with generic RBF features, sparse needs >= 3x the preferences dense needs
    big = 10 * n_grid[-1]
    ns = S["n_star"]["prefs"]
    c2 = {"n_star_prefs": ns, "ratio_sparse_dense": (ns["sparse"] or big) / (ns["dense"] or big)}
    c2["supported"] = bool(c2["ratio_sparse_dense"] >= 3)
    # C3: shaped and sparse reach a similar EPIC at the largest N (EPIC removes shaping)
    c3 = {fb: {"epic_sparse": last(fb, "epic", "sparse"), "epic_shaped": last(fb, "epic", "shaped")}
          for fb in fbs}
    c3["supported"] = bool(all(abs(c3[fb]["epic_sparse"] - c3[fb]["epic_shaped"]) <= 0.05
                               for fb in fbs))
    S["C1"], S["C2"], S["C3"] = c1, c2, c3
    S["n_runs"] = len(rec)
    S["seconds_total"] = float(sum(r.get("seconds", 0) for r in rec))
    S["config"] = cfg
    return S


def write_summary(cfg, pilot=False):
    S = summarize(cfg, pilot)
    path = (out_dir(True) / "summary.json") if pilot else (RESULTS / "summary_pointmass.json")
    path.write_text(json.dumps(S, indent=1))
    log.info("summary -> %s", path)
    return S


# ---------------------------------------------------------------- figure

# Validated with the dataviz palette checker (light mode, all pairs): blue, yellow, aqua,
# magenta. Dashes are the second cue for the closest pair (aqua and magenta under deutan).
COLOR = {"sparse": "#2a78d6", "dense": "#eda100", "shaped": "#1baf7a", "distractor": "#e87ba4"}
DASH = {"sparse": "-", "dense": ":", "shaped": "-.", "distractor": (0, (5, 1, 1, 1))}


def make_figure(S, name="fig7_pointmass"):
    from . import figures as F  # matplotlib only when drawing
    plt = F.plt
    fbs = list(S["curves"])
    fig, axes = plt.subplots(2, len(fbs), figsize=(6.4, 4.4), sharex=True)
    titles = {"prefs": "preferences (pairs)", "demos": "demonstrations"}
    for j, fb in enumerate(fbs):
        for i, m in enumerate(("regret", "epic")):
            ax = axes[i, j]
            for sh in S["shapes"]:
                pts = S["curves"][fb][m][sh]
                F._band(ax, [p["n"] for p in pts], pts, COLOR[sh], DASH[sh], sh)
                if m == "epic":
                    ax.axhline(S["epic_floor"][sh], color=COLOR[sh], ls=DASH[sh], lw=0.8, alpha=0.6)
            ax.set_xscale("log")
            if m == "regret":
                ax.axhline(S["recovered_threshold"], color=F.MUTED, lw=0.6)
                ax.set_title(titles.get(fb, fb), fontsize=8)
            ax.set_ylabel("normalized regret" if m == "regret" else "EPIC distance")
            if i == 1:
                ax.set_xlabel("N (feedback items)")
    axes[0, -1].legend(fontsize=7, loc="upper right")
    fig.text(0.01, -0.02, "Thin horizontal lines in the EPIC panels: best EPIC reachable with the "
             "linear features (per shape). Mean over seeds, 95% bootstrap band.", fontsize=6,
             color=F.MUTED)
    F._save(fig, name)
    return F.FIG / f"{name}.png"


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=P.DEFAULT_CONFIG)
    p.add_argument("--pilot", action="store_true", help="tuning seeds only, into results/pilot/")
    p.add_argument("--skip-experiments", action="store_true")
    p.add_argument("--procs", type=int)
    a = p.parse_args()
    cfg = P.load_config(a.config)
    if not a.skip_experiments:
        run(cfg, a.pilot, a.procs)
    S = write_summary(cfg, a.pilot)
    if not a.pilot:
        log.info("figure -> %s", make_figure(S))
    print(json.dumps({k: S[k] for k in ("n_star", "epic_floor", "C1", "C2", "C3")}, indent=1))


if __name__ == "__main__":
    main()
