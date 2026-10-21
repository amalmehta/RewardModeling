"""Synthetic feedback: trajectory sampling, Boltzmann preference labels, demonstrations."""
import numpy as np
from scipy.special import expit

from .env import N_ACTIONS, N_STATES
from .planning import finite_horizon_soft_policy, greedy_policy, q_optimal


def rollout(rng, env, policy_fn, n, starts=None):
    """n trajectories of length H (uniform starts unless given). policy_fn(t, s, rng) -> actions."""
    H = env.horizon
    S = np.zeros((n, H + 1), dtype=int)
    A = np.zeros((n, H), dtype=int)
    S[:, 0] = rng.integers(N_STATES, size=n) if starts is None else starts
    cum_T = env.T.cumsum(-1)
    for t in range(H):
        a = policy_fn(t, S[:, t], rng)
        A[:, t] = a
        u = rng.random(n)
        S[:, t + 1] = (cum_T[S[:, t], a] < u[:, None]).sum(1).clip(max=N_STATES - 1)
    return S, A


def epsilon_mixture_trajectories(rng, env, R_true, n, starts=None):
    """epsilon-greedy around the true optimal policy, epsilon ~ U[0, 1] per trajectory."""
    pi_star = greedy_policy(q_optimal(R_true, env))
    eps = rng.random(n)
    cum_pi = pi_star.cumsum(1)

    def policy(t, s, rng):
        greedy = (cum_pi[s] < rng.random(len(s))[:, None]).sum(1).clip(max=N_ACTIONS - 1)
        explore = rng.random(len(s)) < eps
        return np.where(explore, rng.integers(N_ACTIONS, size=len(s)), greedy)

    return rollout(rng, env, policy, n, starts)


def returns(S, A, R, discount=1.0):
    r = R[S[:, :-1], A, S[:, 1:]]
    w = discount ** np.arange(r.shape[1])
    return (r * w).sum(1)


def preferences(rng, env, R_true, n_pairs, beta=1.0, labeler_discount=None):
    """Pairs (tau1, tau2) from a shared start state, and labels y = 1 if tau1 is preferred.

    P(tau1 > tau2) = sigmoid(beta * (G1 - G2)); G is the return discounted by the task's
    gamma unless labeler_discount says otherwise (the myopic labeler uses 0.8).
    beta = inf gives noiseless labels.
    """
    starts = np.tile(rng.integers(N_STATES, size=n_pairs), 2)
    S, A = epsilon_mixture_trajectories(rng, env, R_true, 2 * n_pairs, starts)
    G = returns(S, A, R_true, env.gamma if labeler_discount is None else labeler_discount)
    diff = G[:n_pairs] - G[n_pairs:]
    if np.isinf(beta):
        p = (diff > 0) + 0.5 * (diff == 0)
    else:
        p = expit(beta * diff)
    y = (rng.random(n_pairs) < p).astype(float)
    return (S[:n_pairs], A[:n_pairs]), (S[n_pairs:], A[n_pairs:]), y


def demonstrations(rng, env, R_true, n, temperature=1.0):
    """Trajectories from the finite-horizon soft-optimal (Boltzmann-rational) policy."""
    pis = finite_horizon_soft_policy(R_true, env, temperature=temperature)
    cum = pis.cumsum(-1)

    def policy(t, s, rng):
        return (cum[t, s] < rng.random(len(s))[:, None]).sum(1).clip(max=N_ACTIONS - 1)

    return rollout(rng, env, policy, n)
