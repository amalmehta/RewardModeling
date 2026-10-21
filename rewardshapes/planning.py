"""Exact tabular planning: value iteration, policy evaluation, soft policies.

Every function takes an env with a transition tensor env.T[s, a, s'] and a reward that is
either a table R[s, a, s'] or an expected reward r[s, a]; sizes come from env.T, so the
gridworld and the point mass's planning model share this code.
"""
import numpy as np
from scipy.special import logsumexp

from .env import N_STATES


def expected_reward(R, T):
    """r(s, a) = sum_s' T(s'|s,a) R(s,a,s'); an (S, A) reward is already r(s, a)."""
    if R.ndim == 2:
        return R
    return (T * R).sum(-1)


def q_optimal(R, env, tol=1e-10, max_iter=5000):
    r = expected_reward(R, env.T)
    V = np.zeros(len(env.T))
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
    V = np.zeros(len(env.T))
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
    return np.linalg.solve(np.eye(len(env.T)) - env.gamma * P_pi, r_pi)


def J(pi, R, env):
    """True expected discounted return from a uniform start state."""
    return policy_value(pi, R, env).mean()


def uniform_policy(n_actions=4, n_states=N_STATES):
    return np.full((n_states, n_actions), 1.0 / n_actions)


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
    return np.exp(finite_horizon_soft_logpolicy(R, env, horizon, temperature))


def finite_horizon_soft_logpolicy(R, env, horizon=None, temperature=1.0):
    """log pi[t, s, a] of finite_horizon_soft_policy (finite even where pi underflows)."""
    H = horizon or env.horizon
    r = expected_reward(R, env.T) / temperature
    V = np.zeros(len(env.T))
    logpis = np.zeros((H,) + r.shape)
    for t in reversed(range(H)):
        Q = r + env.gamma * env.T @ V
        V = logsumexp(Q, axis=1)
        logpis[t] = Q - V[:, None]
    return logpis
