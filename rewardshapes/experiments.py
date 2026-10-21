"""All experiment grids. Each job is a pure function of its config and seed.

Seeds 0-9 are confirmation seeds (every reported number); seeds 100-104 were used
for tuning only (see --pilot).
"""
import argparse
import json
import logging
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from . import env as E
from . import feedback, learn, metrics, planning

log = logging.getLogger("rewardshapes")
RESULTS = Path(__file__).resolve().parent.parent / "results"

N_GRID = [1, 3, 10, 30, 100, 300, 1000]
SEEDS = list(range(10))
PILOT_SEEDS = list(range(100, 105))
BETAS = [0.3, 1.0, 3.0, 10.0]
BETA_N = [30, 300]
MYOPIC_DISCOUNT = 0.8
OVEROPT_N = [3, 30, 300]
LAMBDAS = list(np.logspace(-1, 2, 13))
RECOVERED = 0.05  # normalized-regret threshold for "recovered"
SHAPING_TRAIN = ["sparse", "dense", "shaped"]
Q_EPISODES, Q_EP_LEN, Q_EVAL_EVERY = 3000, 50, 10

_ENV = None


def _env():
    global _ENV
    if _ENV is None:
        _ENV = E.make_env()
    return _ENV


def _rng(*key):
    """Deterministic generator from a tuple of ints/strings."""
    ints = [k if isinstance(k, int) else sum(ord(c) * 31 ** i for i, c in enumerate(k)) % 2**31
            for k in key]
    return np.random.default_rng(np.random.SeedSequence(ints))


def learn_reward(shape, fb, n, seed, beta=1.0, labeler=None):
    env = _env()
    R = E.true_reward(shape, env)
    rng = _rng(shape, fb, n, seed, int(beta * 1000), int((labeler or 0) * 1000))
    if fb == "prefs":
        t1, t2, y = feedback.preferences(rng, env, R, n, beta=beta, labeler_discount=labeler)
        return R, learn.fit_preferences(t1, t2, y, env.gamma, beta=beta)
    if fb == "demos":
        S, A = feedback.demonstrations(rng, env, R, n)
        return R, learn.fit_maxent(S, A, env)
    if fb == "random":
        return R, learn.random_reward(rng)
    raise ValueError(fb)


def evaluate(R, R_hat, env):
    pi = planning.greedy_policy(planning.q_optimal(R_hat, env))
    return {
        "regret": float(planning.normalized_regret(pi, R, env)),
        "epic": metrics.epic(R, R_hat, env.gamma),
        "pearson": metrics.raw_pearson(R, R_hat, env.coverage),
    }


def recovery_job(cfg):
    t = time.time()
    R, R_hat = learn_reward(cfg["shape"], cfg["feedback"], cfg["n"], cfg["seed"],
                            cfg.get("beta", 1.0), cfg.get("labeler"))
    out = dict(cfg, **evaluate(R, R_hat, _env()), seconds=round(time.time() - t, 2))
    if cfg["seed"] == 0 and cfg["study"] == "main":
        env = _env()
        pi = planning.greedy_policy(planning.q_optimal(R_hat, env))
        out["map_raw"] = metrics.entry_map(R_hat, env.coverage).round(4).tolist()
        out["map_canon"] = metrics.entry_map(metrics.canonicalize(R_hat, env.gamma),
                                             env.coverage).round(4).tolist()
        out["policy"] = pi.round(3).tolist()
    return out


def overopt_job(cfg):
    env = _env()
    R, R_hat = learn_reward(cfg["shape"], "prefs", cfg["n"], cfg["seed"])
    R_hat = R_hat / max(E.weighted_std(R_hat, env.coverage), 1e-12)
    j_star, j_unif = planning.regret_cache(R, env)
    rows = []
    for lam in LAMBDAS:
        pi = planning.soft_policy(R_hat, env, lam)
        kl = float((pi * np.log(np.maximum(pi, 1e-300) * E.N_ACTIONS)).sum(1).mean())
        rows.append({"lambda": float(lam), "kl": kl,
                     "true": float((planning.J(pi, R, env) - j_unif) / (j_star - j_unif)),
                     "proxy_regret": float(planning.normalized_regret(
                         planning.greedy_policy(planning.q_optimal(R_hat, env)), R, env))})
    return dict(cfg, curve=rows)


def q_learning_job(cfg):
    """Tabular Q-learning on a training reward, scored by regret on the sparse task."""
    env = _env()
    R_task = E.true_reward("sparse", env)
    R_train = E.true_reward(cfg["train"], env)
    cache = planning.regret_cache(R_task, env)
    rng = _rng("qlearn", cfg["train"], cfg["seed"])
    cum_T = env.T.cumsum(-1)
    Q = np.zeros((E.N_STATES, E.N_ACTIONS))
    curve, solved = [], None
    for ep in range(Q_EPISODES + 1):
        if ep % Q_EVAL_EVERY == 0:
            reg = float(planning.normalized_regret(planning.greedy_policy(Q), R_task, env, cache))
            curve.append([ep, round(reg, 4)])
            if solved is None and reg <= RECOVERED:
                solved = ep
        if ep == Q_EPISODES:
            break
        s = int(rng.integers(E.N_STATES))
        for _ in range(Q_EP_LEN):
            if rng.random() < 0.1:
                a = int(rng.integers(E.N_ACTIONS))
            else:
                best = np.flatnonzero(Q[s] == Q[s].max())
                a = int(rng.choice(best))
            s2 = min(int((cum_T[s, a] < rng.random()).sum()), E.N_STATES - 1)
            Q[s, a] += 0.1 * (R_train[s, a, s2] + env.gamma * Q[s2].max() - Q[s, a])
            s = s2
    return dict(cfg, solved=solved, curve=curve)


def recovery_configs(seeds):
    cfgs = []
    for shape in E.SHAPES:
        for n in N_GRID:
            for seed in seeds:
                for fb in ("prefs", "demos"):
                    cfgs.append(dict(study="main", shape=shape, feedback=fb, n=n, seed=seed))
                cfgs.append(dict(study="myopic", shape=shape, feedback="prefs", n=n, seed=seed,
                                 labeler=MYOPIC_DISCOUNT))
            for beta in BETAS:
                if beta != 1.0 and n in BETA_N:
                    cfgs += [dict(study="beta", shape=shape, feedback="prefs", n=n, seed=s,
                                  beta=beta) for s in seeds]
        cfgs += [dict(study="random", shape=shape, feedback="random", n=0, seed=s) for s in seeds]
    return cfgs


def run(pilot=False, procs=8):
    seeds = PILOT_SEEDS if pilot else SEEDS
    tag = "pilot" if pilot else "confirm"
    out = RESULTS / tag
    out.mkdir(parents=True, exist_ok=True)
    jobs = [("recovery", recovery_job, recovery_configs(seeds)),
            ("overopt", overopt_job, [dict(shape=sh, n=n, seed=s) for sh in E.SHAPES
                                      for n in OVEROPT_N for s in seeds]),
            ("shaping", q_learning_job, [dict(train=tr, seed=s) for tr in SHAPING_TRAIN
                                         for s in seeds])]
    # longest jobs first keeps the pool busy until the end
    with Pool(procs) as pool:
        for name, fn, cfgs in jobs:
            t = time.time()
            cfgs = sorted(cfgs, key=lambda c: -(c.get("n", 0) * (3 if c.get("feedback") == "demos" else 1)))
            rows = []
            for i, row in enumerate(pool.imap_unordered(fn, cfgs, chunksize=1)):
                rows.append(row)
                if (i + 1) % 100 == 0:
                    log.info("%s: %d/%d (%.0fs)", name, i + 1, len(cfgs), time.time() - t)
            with open(out / f"{name}.jsonl", "w") as f:
                for row in rows:
                    f.write(json.dumps(row) + "\n")
            log.info("%s: %d jobs in %.0fs -> %s", name, len(rows), time.time() - t, out / f"{name}.jsonl")
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", action="store_true", help="tuning seeds 100-104 only")
    p.add_argument("--procs", type=int, default=8)
    a = p.parse_args()
    run(a.pilot, a.procs)
