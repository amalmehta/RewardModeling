"""Exact tabular planning: value iteration, policy evaluation, soft policies."""
import numpy as np
from scipy.special import logsumexp

from .env import N_STATES


def expected_reward(R, T):
    """r(s, a) = sum_s' T(s'|s,a) R(s,a,s')."""
    return (T * R).sum(-1)


def q_optimal(R, env, tol=1e-10, max_iter=5000):
    r = expected_reward(R, env.T)
    V = np.zeros(N_STATES)
    for _ in range(max_iter):
        Q = r + env.gamma * env.T @ V
        V_new = Q.max(1)
        if np.abs(V_new - V).max() < tol:
            break
        V = V_new
    return r + env.gamma * env.T @ V


def greedy_policy(Q, tie_tol=1e-8):
    """Uniform over the argmax set, so a constant reward gives the uniform policy."""
    best = Q >= Q.max(1, keepdims=True) - tie_tol * (1 + np.abs(Q).max())
    return best / best.sum(1, keepdims=True)


def soft_policy(R, env, lam, tol=1e-9, max_iter=5000):
    """Infinite-horizon soft-optimal policy at inverse temperature lam."""
    r = expected_reward(R, env.T)
    V = np.zeros(N_STATES)
    for _ in range(max_iter):
        Q = r + env.gamma * env.T @ V
        V_new = logsumexp(lam * Q, axis=1) / lam
        if np.abs(V_new - V).max() < tol:
            break
        V = V_new
    Q = r + env.gamma * env.T @ V
    logits = lam * Q
    logits -= logits.max(1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(1, keepdims=True)


def policy_value(pi, R, env):
    """Exact V^pi by solving (I - gamma P_pi) V = r_pi."""
    r = expected_reward(R, env.T)
    r_pi = (pi * r).sum(1)
    P_pi = np.einsum("sa,sat->st", pi, env.T)
    return np.linalg.solve(np.eye(N_STATES) - env.gamma * P_pi, r_pi)


def J(pi, R, env):
    """True expected discounted return from a uniform start state."""
    return policy_value(pi, R, env).mean()


def uniform_policy(n_actions=4):
    return np.full((N_STATES, n_actions), 1.0 / n_actions)


def normalized_regret(pi, R_true, env, cache=None):
    """0 = optimal, 1 = no better than the uniform-random policy."""
    if cache is None:
        cache = regret_cache(R_true, env)
    j_star, j_unif = cache
    return (j_star - J(pi, R_true, env)) / (j_star - j_unif)


def regret_cache(R_true, env):
    pi_star = greedy_policy(q_optimal(R_true, env))
    return J(pi_star, R_true, env), J(uniform_policy(), R_true, env)


def finite_horizon_soft_policy(R, env, horizon=None, temperature=1.0):
    """Time-indexed soft-optimal policy pi[t, s, a] for the discounted horizon-H task."""
    H = horizon or env.horizon
    r = expected_reward(R, env.T) / temperature
    V = np.zeros(N_STATES)
    pis = np.zeros((H,) + r.shape)
    for t in reversed(range(H)):
        Q = r + env.gamma * env.T @ V
        V = logsumexp(Q, axis=1)
        pis[t] = np.exp(Q - V[:, None])
    return pis
