"""2D point-mass navigation (a Gymnasium env) and its four ground-truth reward families.

State s = (x, y, d). The agent moves the position (x, y) in [-1, 1]^2; d in [-1, 1] is a
distractor coordinate that drifts on its own (AR(1)) and that no action affects. There are
nine discrete actions (stay, or a step of length `step` in one of eight headings), with
Gaussian position noise; the box edges clip like walls. It is a velocity-controlled point
mass, with no inertia.

Every reward has the form R(s, a, s') = f(s) + g(s'), and is rescaled to unit std over
feasible transitions (uniform s and a, s' from the dynamics), as in the gridworld.

`Task` is the experiment-facing env. It exposes the gridworld's interface (T, gamma,
horizon) through a planning model: a G x G lattice of positions whose transition rows are
bilinear-interpolation weights of simulator samples, an "averager" for which value
iteration converges (Gordon 1995). Feedback, returns and metrics use the continuous
simulator; only planning uses the lattice. Every reward here is additive in d and d is
exogenous, so optimal and soft-optimal policies do not depend on d, and the lattice leaves
d out without approximation (d' is set to its mean, 0, on the lattice).
"""
import tomllib
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import gymnasium as gym
import numpy as np
import scipy.sparse as sp

from . import metrics, planning

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "configs" / "pointmass.toml"
ENV_ID = "rewardshapes/PointMass-v0"

N_ACTIONS = 9
_ANGLES = np.arange(8) * np.pi / 4
HEADINGS = np.vstack([[0.0, 0.0], np.c_[np.cos(_ANGLES), np.sin(_ANGLES)]])
SHAPES = ["sparse", "dense", "shaped", "distractor"]


def load_config(path=DEFAULT_CONFIG):
    with open(path, "rb") as f:
        return tomllib.load(f)


@dataclass(frozen=True)
class Params:
    gamma: float
    horizon: int
    step: float
    noise: float
    goal: tuple
    goal_radius: float
    shaping_scale: float
    distractor_rho: float
    distractor_noise: float

    @classmethod
    def from_config(cls, cfg):
        e = dict(cfg["env"])
        e["goal"] = tuple(e["goal"])
        return cls(**e)


# ---------------------------------------------------------------- dynamics


def uniform_states(rng, n):
    return rng.uniform(-1, 1, size=(n, 3))


def step(s, a, p, eps):
    """Batched dynamics. s (n, 3), a (n,), eps (n, 3) standard normals -> s' (n, 3)."""
    pos = np.clip(s[:, :2] + p.step * HEADINGS[a] + p.noise * eps[:, :2], -1, 1)
    d = np.clip(p.distractor_rho * s[:, 2] + p.distractor_noise * eps[:, 2], -1, 1)
    return np.c_[pos, d]


class PointMassEnv(gym.Env):
    """Gymnasium view of the task: one trajectory at a time, through the same step()."""

    metadata = {"render_modes": []}

    def __init__(self, reward=None, config=None, horizon=None):
        self.params = Params.from_config(config or load_config())
        self.reward = reward
        self.horizon = horizon or self.params.horizon
        self.observation_space = gym.spaces.Box(-1.0, 1.0, (3,), np.float64)
        self.action_space = gym.spaces.Discrete(N_ACTIONS)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._s = uniform_states(self.np_random, 1)
        self._t = 0
        return self._s[0].copy(), {}

    def step(self, action):
        a = np.array([int(action)])
        s2 = step(self._s, a, self.params, self.np_random.standard_normal((1, 3)))
        r = 0.0 if self.reward is None else float(self.reward(self._s, a, s2)[0])
        self._s = s2
        self._t += 1
        return s2[0].copy(), r, False, self._t >= self.horizon, {}


if ENV_ID not in gym.registry:
    gym.register(id=ENV_ID, entry_point="rewardshapes.pointmass:PointMassEnv")


# ---------------------------------------------------------------- rewards


@dataclass
class Reward:
    """R(s, a, s') = f(s) + g(s'); f and g map states (n, 3) -> (n,)."""
    f: object
    g: object

    def __call__(self, s, a, s2):
        return self.f(s) + self.g(s2)

    def scaled(self, k):
        f, g = self.f, self.g
        return Reward(lambda s: f(s) / k, lambda s: g(s) / k)


def _zero(s):
    return np.zeros(len(s))


def raw_reward(shape, p, coverage):
    goal = np.array(p.goal)

    def dist(s):
        return np.linalg.norm(s[:, :2] - goal, axis=1)

    def inside(s):
        return (dist(s) <= p.goal_radius).astype(float)

    def phi(s):
        return -p.shaping_scale * dist(s)

    if shape == "sparse":
        return Reward(_zero, inside)
    if shape == "dense":
        return Reward(_zero, lambda s: -dist(s))
    if shape == "shaped":
        return Reward(lambda s: -phi(s), lambda s: inside(s) + p.gamma * phi(s))
    if shape == "distractor":
        # dense + c*d', with c chosen so the two terms have equal variance over coverage
        s2 = coverage[2]
        c = dist(s2).std() / s2[:, 2].std()
        return Reward(_zero, lambda s: -dist(s) + c * s[:, 2])
    raise ValueError(f"unknown shape {shape!r}")


class Features:
    """psi(s): Gaussian RBFs on a k x k lattice of position centres, then d (K = k^2 + 1)."""

    def __init__(self, cfg):
        k = cfg["features"]["rbf_per_axis"]
        c = np.linspace(-1, 1, k)
        self.centres = np.array([(x, y) for x in c for y in c])
        self.width = cfg["features"]["rbf_width"]
        self.K = k * k + 1

    def __call__(self, s):
        sq = ((s[..., None, :2] - self.centres) ** 2).sum(-1)
        return np.concatenate([np.exp(-sq / (2 * self.width ** 2)), s[..., 2:3]], -1)


class LinearReward(Reward):
    """R_theta(s, a, s') = theta_u . psi(s) + theta_v . psi(s'), with 2K parameters."""

    def __init__(self, theta, feats):
        self.theta = np.asarray(theta, float)
        u, v = self.theta[:feats.K], self.theta[feats.K:]
        super().__init__(lambda s: feats(s) @ u, lambda s: feats(s) @ v)


# ---------------------------------------------------------------- task


class LatticeT:
    """T[s, a, s'] stored sparsely (about 8 nonzeros per row). It supports what the shared
    planning code uses: k * T, T @ V -> (S, A), len(T) and .shape."""

    def __init__(self, csr, n_actions):
        self.csr = csr
        n = csr.shape[1]
        self.shape = (n, n_actions, n)

    def __len__(self):
        return self.shape[0]

    def __rmul__(self, k):
        return LatticeT(k * self.csr, self.shape[1])

    def __matmul__(self, V):
        return (self.csr @ V).reshape(self.shape[:2])

    def toarray(self):
        return self.csr.toarray().reshape(self.shape)


class Task:
    """The continuous env behind the gridworld's interface (T, gamma, horizon) for planning,
    plus the samples the metrics need. Deterministic given the config."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.params = p = Params.from_config(cfg)
        self.gamma, self.horizon = p.gamma, p.horizon
        self.feats = Features(cfg)
        G = self.G = cfg["model"]["grid"]
        x = np.linspace(-1, 1, G)
        self.nodes = np.array([(a, b, 0.0) for a in x for b in x])  # node i = ix * G + iy
        # simulator samples behind each (node, action); d' pinned to its mean (module doc)
        K = cfg["model"]["samples_per_cell"]
        rng = np.random.default_rng(cfg["model"]["seed"])
        n = len(self.nodes)
        s = np.repeat(self.nodes, N_ACTIONS * K, axis=0)
        a = np.tile(np.repeat(np.arange(N_ACTIONS), K), n)
        s2 = step(s, a, p, rng.standard_normal((len(s), 3)))
        s2[:, 2] = 0.0
        self.next_states = s2.reshape(n, N_ACTIONS, K, 3)
        idx, w = self.interp(s2)
        rows = np.repeat(np.arange(n * N_ACTIONS), K * 4)
        csr = sp.csr_matrix((w.ravel() / K, (rows, idx.ravel())), shape=(n * N_ACTIONS, n))
        csr.sum_duplicates()
        csr.eliminate_zeros()
        self.T = LatticeT(csr, N_ACTIONS)
        # metric samples: D_S (uniform states) and coverage (uniform s, a; s' from dynamics)
        mrng = np.random.default_rng(cfg["eval"]["metric_seed"])
        m = cfg["eval"]["metric_samples"]
        self.ds = uniform_states(mrng, m)
        cs = uniform_states(mrng, m)
        ca = mrng.integers(N_ACTIONS, size=m)
        self.coverage = (cs, ca, step(cs, ca, p, mrng.standard_normal((m, 3))))
        # fixed evaluation rollouts: starts and noise shared by every policy
        erng = np.random.default_rng(cfg["eval"]["seed"])
        ne, he = cfg["eval"]["rollouts"], cfg["eval"]["horizon"]
        self.eval_starts = uniform_states(erng, ne)
        self.eval_noise = erng.standard_normal((he, ne, 3))
        self.eval_policy_seed = int(erng.integers(2**31))

    def interp(self, s):
        """Bilinear weights of positions s[..., :2] on the lattice: (idx, w), each (..., 4)."""
        G = self.G
        u = (s[..., :2] + 1) / 2 * (G - 1)
        i0 = np.clip(np.floor(u).astype(int), 0, G - 2)
        fr = u - i0
        ix, iy, fx, fy = i0[..., 0], i0[..., 1], fr[..., 0], fr[..., 1]
        idx = np.stack([ix * G + iy, ix * G + iy + 1, (ix + 1) * G + iy, (ix + 1) * G + iy + 1], -1)
        w = np.stack([(1 - fx) * (1 - fy), (1 - fx) * fy, fx * (1 - fy), fx * fy], -1)
        return idx, w

    def at(self, table, s):
        """Interpolate a per-node table (n_nodes, ...) at continuous states s (n, 3)."""
        idx, w = self.interp(s)
        return np.einsum("nj,nj...->n...", w, table[idx])

    def lattice_reward(self, R):
        """r[i, a] = E[R(node_i, a, s')] over the simulator samples behind T."""
        n, A, K, _ = self.next_states.shape
        g = R.g(self.next_states.reshape(-1, 3)).reshape(n, A, K).mean(-1)
        return R.f(self.nodes)[:, None] + g

    @cached_property
    def lattice_features(self):
        """(psi(node_i), E[psi(s') | node_i, a]) for the linear model on the lattice."""
        return self.feats(self.nodes), self.feats(self.next_states).mean(2)


def make_task(cfg=None):
    return Task(cfg or load_config())


def true_reward(shape, task):
    R = raw_reward(shape, task.params, task.coverage)
    return R.scaled(R(*task.coverage).std())


# ---------------------------------------------------------------- policies and rollouts


def sample_actions(probs, rng):
    return (probs.cumsum(1) < rng.random(len(probs))[:, None]).sum(1).clip(max=N_ACTIONS - 1)


def q_star(R, task):
    """Optimal Q on the lattice (value iteration through the shared planning code)."""
    return planning.q_optimal(task.lattice_reward(R), task)


def greedy(task, Q):
    """Greedy policy at continuous states from interpolated Q, ties broken uniformly."""
    return lambda t, s, rng: sample_actions(planning.greedy_policy(task.at(Q, s)), rng)


def uniform(t, s, rng):
    return rng.integers(N_ACTIONS, size=len(s))


def rollout(rng, task, policy_fn, n, starts=None):
    """n trajectories of length H: S (n, H+1, 3), A (n, H)."""
    H = task.horizon
    S = np.zeros((n, H + 1, 3))
    A = np.zeros((n, H), dtype=int)
    S[:, 0] = uniform_states(rng, n) if starts is None else starts
    for t in range(H):
        A[:, t] = policy_fn(t, S[:, t], rng)
        S[:, t + 1] = step(S[:, t], A[:, t], task.params, rng.standard_normal((n, 3)))
    return S, A


def returns(S, A, R, discount=1.0):
    n, H = A.shape
    r = R(S[:, :-1].reshape(-1, 3), A.ravel(), S[:, 1:].reshape(-1, 3)).reshape(n, H)
    return (r * discount ** np.arange(H)).sum(1)


def policy_return(task, R, policy_fn):
    """Expected discounted return from a uniform start, by Monte Carlo with the task's fixed
    evaluation starts and noise (common random numbers across policies)."""
    s = task.eval_starts.copy()
    rng = np.random.default_rng(task.eval_policy_seed)
    G = np.zeros(len(s))
    for t, eps in enumerate(task.eval_noise):
        a = policy_fn(t, s, rng)
        s2 = step(s, a, task.params, eps)
        G += task.gamma ** t * R(s, a, s2)
        s = s2
    return float(G.mean())


def regret_cache(R_true, task):
    return (policy_return(task, R_true, greedy(task, q_star(R_true, task))),
            policy_return(task, R_true, uniform))


def normalized_regret(task, R_true, R_hat, cache):
    """0 = as good as the planner on the true reward, 1 = no better than uniform-random."""
    j_star, j_unif = cache
    j = policy_return(task, R_true, greedy(task, q_star(R_hat, task)))
    return (j_star - j) / (j_star - j_unif)


# ---------------------------------------------------------------- feedback


def epsilon_mixture_trajectories(rng, task, Q_true, n, starts=None):
    """epsilon-greedy around the true optimal policy, epsilon ~ U[0, 1] per trajectory."""
    eps = rng.random(n)
    pi = greedy(task, Q_true)

    def policy(t, s, rng):
        explore = rng.random(len(s)) < eps
        return np.where(explore, rng.integers(N_ACTIONS, size=len(s)), pi(t, s, rng))

    return rollout(rng, task, policy, n, starts)


def preferences(rng, task, R_true, Q_true, n_pairs, beta=1.0):
    """Pairs from a shared start; P(tau1 > tau2) = sigmoid(beta * (G1 - G2)), G discounted by gamma."""
    starts = np.tile(uniform_states(rng, n_pairs), (2, 1))
    S, A = epsilon_mixture_trajectories(rng, task, Q_true, 2 * n_pairs, starts)
    G = returns(S, A, R_true, task.gamma)
    p = 1 / (1 + np.exp(-beta * (G[:n_pairs] - G[n_pairs:])))
    y = (rng.random(n_pairs) < p).astype(float)
    return (S[:n_pairs], A[:n_pairs]), (S[n_pairs:], A[n_pairs:]), y


def demonstrations(rng, task, R_true, n, temperature=1.0):
    """Expert trajectories: the finite-horizon soft-optimal policy planned on the lattice
    for the true reward, acting on interpolated logits at continuous states."""
    logpis = planning.finite_horizon_soft_logpolicy(task.lattice_reward(R_true), task,
                                                    temperature=temperature)

    def policy(t, s, rng):
        z = task.at(logpis[t], s)
        p = np.exp(z - z.max(1, keepdims=True))
        return sample_actions(p / p.sum(1, keepdims=True), rng)

    return rollout(rng, task, policy, n)


def trajectory_features(S, A, feats, discount):
    """Discounted sums of (psi(s_t), psi(s_t+1)): the return of a LinearReward is phi . theta."""
    w = discount ** np.arange(A.shape[1])
    psi = feats(S)
    return np.concatenate([(w[:, None] * psi[:, :-1]).sum(1), (w[:, None] * psi[:, 1:]).sum(1)], -1)


# ---------------------------------------------------------------- metrics


def canonical(R, gamma, states):
    """EPIC canonical reward (uniform D_S, D_A) of an f(s) + g(s') reward, up to a constant.

    C(R)(s, a, s') = g(s') + gamma f(s') - E[g(S')] - gamma E[f(S)]: it depends on s' only, so
    the Pearson correlation over D_S x D_A x D_S reduces to one over s' ~ D_S.
    """
    return R.g(states) + gamma * R.f(states)


def epic(R1, R2, task):
    c1, c2 = canonical(R1, task.gamma, task.ds), canonical(R2, task.gamma, task.ds)
    return metrics.pearson_distance(metrics._weighted_corr(c1, c2, np.ones(len(c1))))


def raw_pearson(R1, R2, task):
    r1, r2 = R1(*task.coverage), R2(*task.coverage)
    return metrics.pearson_distance(metrics._weighted_corr(r1, r2, np.ones(len(r1))))


def epic_floor(R_true, task):
    """EPIC of the best linear-in-features reward (least squares on the canonical reward):
    the lowest EPIC any learned reward in the model class can reach."""
    c = canonical(R_true, task.gamma, task.ds)
    X = np.c_[task.feats(task.ds), np.ones(len(c))]
    fit = X @ np.linalg.lstsq(X, c, rcond=None)[0]
    return metrics.pearson_distance(metrics._weighted_corr(c, fit, np.ones(len(c))))
