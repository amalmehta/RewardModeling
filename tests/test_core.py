import numpy as np
import pytest

from rewardshapes import env as E
from rewardshapes import feedback, learn, metrics, planning


@pytest.fixture(scope="module")
def env():
    return E.make_env()


def test_transitions_are_distributions(env):
    assert np.allclose(env.T.sum(-1), 1)
    assert (env.T >= 0).all()


@pytest.mark.parametrize("shape", E.SHAPES)
def test_true_rewards_have_unit_std(env, shape):
    R = E.true_reward(shape, env)
    assert E.weighted_std(R, env.coverage) == pytest.approx(1.0)


def test_epic_ignores_potential_shaping(env):
    sparse, shaped = E.true_reward("sparse", env), E.true_reward("shaped", env)
    assert metrics.epic(sparse, shaped, env.gamma) < 1e-6
    # ...while the raw Pearson baseline is fooled by it
    assert metrics.raw_pearson(sparse, shaped, env.coverage) > 0.2


def test_epic_scale_shift_invariant_and_symmetric(env):
    a, b = E.true_reward("lava", env), E.true_reward("dense", env)
    assert metrics.epic(a, 3 * a + 7, env.gamma) < 1e-6
    assert metrics.epic(a, b, env.gamma) == pytest.approx(metrics.epic(b, a, env.gamma))
    assert metrics.epic(a, -a, env.gamma) == pytest.approx(1.0)


def test_constant_reward_is_uninformative(env):
    a = E.true_reward("sparse", env)
    assert metrics.epic(a, np.zeros_like(a), env.gamma) == pytest.approx(np.sqrt(0.5))
    pi = planning.greedy_policy(planning.q_optimal(np.zeros_like(a), env))
    assert planning.normalized_regret(pi, a, env) == pytest.approx(1.0)


@pytest.mark.parametrize("shape", E.SHAPES)
def test_regret_of_optimal_is_zero(env, shape):
    R = E.true_reward(shape, env)
    pi = planning.greedy_policy(planning.q_optimal(R, env))
    assert planning.normalized_regret(pi, R, env) == pytest.approx(0.0, abs=1e-9)


def test_shaping_preserves_optimal_policy(env):
    sparse, shaped = E.true_reward("sparse", env), E.true_reward("shaped", env)
    pi = planning.greedy_policy(planning.q_optimal(shaped, env))
    assert planning.normalized_regret(pi, sparse, env) == pytest.approx(0.0, abs=1e-9)


def test_features_reproduce_returns(env):
    rng = np.random.default_rng(0)
    theta = rng.normal(size=learn.N_PARAMS)
    R_tab = learn.theta_to_table(theta)
    S, A = feedback.epsilon_mixture_trajectories(rng, env, E.true_reward("sparse", env), 5)
    for d in (1.0, env.gamma):
        assert np.allclose(learn.trajectory_features(S, A, d) @ theta, feedback.returns(S, A, R_tab, d))


def test_rollouts_follow_dynamics(env):
    rng = np.random.default_rng(1)
    S, A = feedback.demonstrations(rng, env, E.true_reward("dense", env), 200)
    assert (env.T[S[:, :-1], A, S[:, 1:]] > 0).all()


@pytest.mark.parametrize("shape", ["dense", "lava", "shaped"])
def test_preference_learning_recovers_reward(env, shape):
    rng = np.random.default_rng(2)
    R = E.true_reward(shape, env)
    t1, t2, y = feedback.preferences(rng, env, R, 2000, beta=10.0)
    R_hat = learn.fit_preferences(t1, t2, y, env.gamma, beta=10.0)
    pi = planning.greedy_policy(planning.q_optimal(R_hat, env))
    assert planning.normalized_regret(pi, R, env) < 0.1


def test_maxent_recovers_reward(env):
    rng = np.random.default_rng(3)
    R = E.true_reward("dense", env)
    S, A = feedback.demonstrations(rng, env, R, 500)
    R_hat = learn.fit_maxent(S, A, env)
    pi = planning.greedy_policy(planning.q_optimal(R_hat, env))
    assert planning.normalized_regret(pi, R, env) < 0.1


def test_soft_policy_approaches_greedy(env):
    R = E.true_reward("sparse", env)
    pi = planning.soft_policy(R, env, lam=200.0)
    assert planning.normalized_regret(pi, R, env) < 0.02


def test_preference_pairs_share_start(env):
    rng = np.random.default_rng(4)
    (S1, _), (S2, _), _ = feedback.preferences(rng, env, E.true_reward("sparse", env), 50)
    assert (S1[:, 0] == S2[:, 0]).all()
