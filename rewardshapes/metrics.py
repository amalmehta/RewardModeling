"""Reward distances: EPIC (Gleave et al. 2021) and a raw Pearson baseline, both exact."""
import numpy as np


def canonicalize(R, gamma):
    """EPIC canonical reward with uniform D_S and D_A:
    C(R)(s,a,s') = R(s,a,s') + gamma E[R(s',A,S')] - E[R(s,A,S')] - gamma E[R(S,A,S')].
    Removes any potential shaping gamma*phi(s') - phi(s) and constant shifts exactly.
    """
    m = R.mean(axis=(1, 2))
    return R + gamma * m[None, None, :] - m[:, None, None] - gamma * R.mean()


def _weighted_corr(x, y, w):
    w = w / w.sum()
    xc, yc = x - (w * x).sum(), y - (w * y).sum()
    vx, vy = (w * xc * xc).sum(), (w * yc * yc).sum()
    if vx <= 1e-20 or vy <= 1e-20:
        return 0.0  # a constant reward carries no information: treat as uncorrelated
    return float((w * xc * yc).sum() / np.sqrt(vx * vy))


def pearson_distance(rho):
    return float(np.sqrt(max(0.0, (1 - rho) / 2)))


def epic(R1, R2, gamma):
    """Pearson distance of canonical rewards over the uniform product S x A x S'."""
    c1, c2 = canonicalize(R1, gamma), canonicalize(R2, gamma)
    return pearson_distance(_weighted_corr(c1, c2, np.ones_like(c1)))


def raw_pearson(R1, R2, coverage):
    """Pearson distance of raw rewards on feasible transitions (no canonicalisation)."""
    return pearson_distance(_weighted_corr(R1, R2, coverage))


def entry_map(R, coverage):
    """Average reward for entering each cell under the coverage distribution (for plots)."""
    w = coverage.sum(axis=(0, 1))
    return (R * coverage).sum(axis=(0, 1)) / np.maximum(w, 1e-12)
