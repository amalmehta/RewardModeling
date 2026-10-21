"""8x8 slippery gridworld and the five ground-truth reward shapes.

Rewards are full tables R[s, a, s'] (S x A x S). Every shape is rescaled to unit
standard deviation over feasible transitions (uniform s, a; s' ~ T), so that the
labeler's rationality beta means the same thing for every shape. That rescaling,
the slip probability, the lava layout and the multi-goal values are invented
parameters of this study, not facts about gridworlds.
"""
from dataclasses import dataclass

import numpy as np

SIZE = 8
N_STATES = SIZE * SIZE
N_ACTIONS = 4  # up, down, left, right
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
GAMMA = 0.95
HORIZON = 20
SLIP = 0.1

GOAL = (7, 7)
SECOND_GOAL = (0, 7)
SECOND_GOAL_VALUE = 0.6
LAVA = [(2, 5), (3, 5), (4, 5), (5, 2), (5, 3), (5, 4)]
STEP_COST = 0.02

SHAPES = ["sparse", "dense", "shaped", "multi", "lava"]


def idx(rc):
    return rc[0] * SIZE + rc[1]


def coords(s):
    return divmod(s, SIZE)


def manhattan_to(target):
    r, c = np.divmod(np.arange(N_STATES), SIZE)
    return np.abs(r - target[0]) + np.abs(c - target[1])


def transitions(slip=SLIP):
    """T[s, a, s']: intended move with prob 1 - slip, else a uniformly random move."""
    T = np.zeros((N_STATES, N_ACTIONS, N_STATES))
    for s in range(N_STATES):
        r, c = coords(s)
        dest = []
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            dest.append(idx((nr, nc)) if 0 <= nr < SIZE and 0 <= nc < SIZE else s)
        for a in range(N_ACTIONS):
            T[s, a, dest[a]] += 1 - slip
            for d in dest:
                T[s, a, d] += slip / N_ACTIONS
    return T


@dataclass
class Env:
    T: np.ndarray
    gamma: float = GAMMA
    horizon: int = HORIZON

    @property
    def coverage(self):
        """Feasible-transition distribution: uniform s, uniform a, s' ~ T."""
        return self.T / (N_STATES * N_ACTIONS)


def make_env():
    return Env(T=transitions())


def _state_reward(r_next):
    """Reward for entering s' (the same for every s, a)."""
    return np.broadcast_to(r_next[None, None, :], (N_STATES, N_ACTIONS, N_STATES)).copy()


def raw_reward(shape, gamma=GAMMA):
    g = np.zeros(N_STATES)
    g[idx(GOAL)] = 1.0
    if shape == "sparse":
        return _state_reward(g)
    if shape == "dense":
        return _state_reward(-manhattan_to(GOAL) / 14.0)
    if shape == "shaped":
        phi = -manhattan_to(GOAL).astype(float)
        return _state_reward(g) + gamma * phi[None, None, :] - phi[:, None, None]
    if shape == "multi":
        g2 = g.copy()
        g2[idx(SECOND_GOAL)] = SECOND_GOAL_VALUE
        return _state_reward(g2)
    if shape == "lava":
        r = g.copy()
        for cell in LAVA:
            r[idx(cell)] = -1.0
        return _state_reward(r - STEP_COST)
    raise ValueError(f"unknown shape {shape!r}")


def weighted_std(R, w):
    m = (R * w).sum()
    return np.sqrt(((R - m) ** 2 * w).sum())


def true_reward(shape, env):
    R = raw_reward(shape, env.gamma)
    return R / weighted_std(R, env.coverage)
