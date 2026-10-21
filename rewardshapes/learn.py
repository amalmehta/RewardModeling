"""Reward models R(s,a,s') = u(s) + w(s,a) + v(s'), fit from preferences or demos."""
import numpy as np
import torch

from .env import N_ACTIONS, N_STATES

N_PARAMS = N_STATES + N_STATES * N_ACTIONS + N_STATES
torch.set_num_threads(1)  # experiments parallelise over processes instead


def theta_to_table(theta):
    u = theta[:N_STATES]
    w = theta[N_STATES:N_STATES + N_STATES * N_ACTIONS].reshape(N_STATES, N_ACTIONS)
    v = theta[-N_STATES:]
    return u[:, None, None] + w[:, :, None] + v[None, None, :]


def trajectory_features(S, A, discount=1.0):
    """Discounted counts of s, (s,a) and s' along each trajectory: return = phi . theta."""
    n, H = A.shape
    phi = np.zeros((n, N_PARAMS))
    rows = np.repeat(np.arange(n), H)
    w = np.tile(discount ** np.arange(H), n)
    np.add.at(phi, (rows, S[:, :-1].ravel()), w)
    np.add.at(phi, (rows, N_STATES + (S[:, :-1] * N_ACTIONS + A).ravel()), w)
    np.add.at(phi, (rows, N_STATES + N_STATES * N_ACTIONS + S[:, 1:].ravel()), w)
    return phi


def _lbfgs(loss_fn, theta, max_iter):
    opt = torch.optim.LBFGS([theta], lr=1, max_iter=max_iter, history_size=20,
                            tolerance_grad=1e-7, tolerance_change=1e-10,
                            line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = loss_fn()
        loss.backward()
        return loss

    opt.step(closure)
    return theta.detach().numpy().astype(float)


def fit_preferences(traj1, traj2, y, discount, l2=1e-3, beta=1.0, max_iter=300):
    """Bradley-Terry maximum likelihood; convex (logistic regression on phi1 - phi2).

    The model assumes the labeler discounts by `discount` (the task's gamma): under the
    myopic-labeler ablation this assumption is deliberately wrong.
    """
    d = torch.tensor(trajectory_features(*traj1, discount) - trajectory_features(*traj2, discount))
    yt = torch.tensor(y)
    theta = torch.zeros(N_PARAMS, dtype=torch.float64, requires_grad=True)

    def loss():
        logits = beta * (d @ theta)
        nll = torch.nn.functional.binary_cross_entropy_with_logits(logits, yt)
        return nll + l2 * (theta ** 2).sum()

    return theta_to_table(_lbfgs(loss, theta, max_iter))


def fit_maxent(S, A, env, l2=1e-3, max_iter=200):
    """MaxEnt IRL as maximum likelihood under finite-horizon soft value iteration."""
    T = torch.tensor(env.T)
    St, At = torch.tensor(S[:, :-1]), torch.tensor(A)
    H = env.horizon
    theta = torch.zeros(N_PARAMS, dtype=torch.float64, requires_grad=True)

    def loss():
        u = theta[:N_STATES]
        w = theta[N_STATES:N_STATES + N_STATES * N_ACTIONS].reshape(N_STATES, N_ACTIONS)
        v = theta[-N_STATES:]
        r = u[:, None] + w + T @ v
        V = torch.zeros(N_STATES, dtype=torch.float64)
        ll = 0.0
        for t in reversed(range(H)):
            Q = r + env.gamma * T @ V
            V = torch.logsumexp(Q, 1)
            logpi = Q - V[:, None]
            ll = ll + logpi[St[:, t], At[:, t]].sum()
        return -ll / len(S) + l2 * (theta ** 2).sum()

    return theta_to_table(_lbfgs(loss, theta, max_iter))


def random_reward(rng):
    return theta_to_table(rng.normal(size=N_PARAMS))
