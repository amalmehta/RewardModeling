import gymnasium as gym
import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from rewardshapes import learn, planning
from rewardshapes import pointmass as P


@pytest.fixture(scope="module")
def task():
    return P.make_task()


@pytest.fixture(scope="module")
def truth(task):
    return {sh: P.true_reward(sh, task) for sh in P.SHAPES}


def test_gymnasium_env_passes_checker():
    env = gym.make(P.ENV_ID)
    check_env(env.unwrapped, skip_render_check=True)


def test_gymnasium_env_matches_batched_dynamics(task, truth):
    env = P.PointMassEnv(reward=truth["dense"])
    s, _ = env.reset(seed=3)
    ref = np.random.default_rng(3)
    s_ref = P.uniform_states(ref, 1)
    assert np.allclose(s, s_ref[0])
    for a in [1, 4, 0, 8]:
        s2, r, term, trunc, _ = env.step(a)
        s_ref2 = P.step(s_ref, np.array([a]), task.params, ref.standard_normal((1, 3)))
        assert np.allclose(s2, s_ref2[0])
        assert r == pytest.approx(truth["dense"](s_ref, [a], s_ref2)[0])
        assert not term and not trunc
        s_ref = s_ref2
    assert (np.abs(s2) <= 1).all()


def test_lattice_transitions_are_distributions(task):
    T = task.T.toarray()
    assert np.allclose(T.sum(-1), 1)
    assert (T >= 0).all()


def test_task_is_deterministic(task):
    again = P.make_task()
    assert (again.T.csr != task.T.csr).nnz == 0
    assert np.array_equal(again.ds, task.ds) and np.array_equal(again.eval_noise, task.eval_noise)


@pytest.mark.parametrize("shape", P.SHAPES)
def test_true_rewards_have_unit_std(task, truth, shape):
    assert truth[shape](*task.coverage).std() == pytest.approx(1.0)


def test_closed_form_canonical_matches_definition(task):
    """EPIC's canonicalisation by sampled expectations differs from (g + gamma f)(s') by a constant."""
    rng = np.random.default_rng(0)
    R = P.LinearReward(rng.normal(size=2 * task.feats.K), task.feats)
    s, s2 = P.uniform_states(rng, 500), P.uniform_states(rng, 500)
    a = rng.integers(P.N_ACTIONS, size=500)
    Sj, Sj2 = P.uniform_states(rng, 300), P.uniform_states(rng, 300)
    Aj = rng.integers(P.N_ACTIONS, size=300)

    def mean_from(x):  # E[R(x, A, S')] for each row of x
        return np.array([R(np.repeat(xi[None], 300, 0), Aj, Sj2).mean() for xi in x])

    brute = R(s, a, s2) + task.gamma * mean_from(s2) - mean_from(s) - task.gamma * R(Sj, Aj, Sj2).mean()
    diff = brute - P.canonical(R, task.gamma, s2)
    assert np.ptp(diff) < 1e-9


def test_epic_ignores_potential_shaping(task, truth):
    assert P.epic(truth["sparse"], truth["shaped"], task) < 1e-6
    assert P.raw_pearson(truth["sparse"], truth["shaped"], task) > 0.2


def test_epic_scale_shift_invariant_and_symmetric(task, truth):
    a, b = truth["distractor"], truth["dense"]
    moved = P.Reward(lambda s: 3 * a.f(s) + 7, lambda s: 3 * a.g(s))
    assert P.epic(a, moved, task) < 1e-6
    assert P.epic(a, b, task) == pytest.approx(P.epic(b, a, task))
    assert P.epic(a, a.scaled(-1), task) == pytest.approx(1.0)


def test_constant_reward_is_uninformative(task, truth):
    R = truth["dense"]
    const = P.LinearReward(np.zeros(2 * task.feats.K), task.feats)
    assert P.epic(R, const, task) == pytest.approx(np.sqrt(0.5))
    assert P.normalized_regret(task, R, const, P.regret_cache(R, task)) == pytest.approx(1, abs=0.1)


def test_true_reward_has_zero_regret_and_shaping_keeps_the_policy(task, truth):
    sparse = truth["sparse"]
    cache = P.regret_cache(sparse, task)
    assert P.normalized_regret(task, sparse, sparse, cache) == 0
    assert P.normalized_regret(task, sparse, truth["shaped"], cache) < 0.05


def test_distractor_weight_does_not_change_the_policy(task, truth):
    Q1, Q2 = P.q_star(truth["dense"], task), P.q_star(truth["distractor"], task)
    assert np.array_equal(planning.greedy_policy(Q1) > 0, planning.greedy_policy(Q2) > 0)


def test_features_reproduce_discounted_returns(task):
    rng = np.random.default_rng(1)
    R = P.LinearReward(rng.normal(size=2 * task.feats.K), task.feats)
    S, A = P.rollout(rng, task, P.uniform, 5)
    phi = P.trajectory_features(S, A, task.feats, task.gamma)
    assert np.allclose(phi @ R.theta, P.returns(S, A, R, task.gamma))


def test_preference_pairs_share_starts(task, truth):
    R = truth["dense"]
    (S1, _), (S2, _), y = P.preferences(np.random.default_rng(2), task, R, P.q_star(R, task), 20)
    assert np.array_equal(S1[:, 0], S2[:, 0]) and set(np.unique(y)) <= {0.0, 1.0}


def test_bradley_terry_recovers_dense(task, truth):
    R = truth["dense"]
    t1, t2, y = P.preferences(np.random.default_rng(4), task, R, P.q_star(R, task), 1000)
    d = (P.trajectory_features(*t1, task.feats, task.gamma)
         - P.trajectory_features(*t2, task.feats, task.gamma))
    R_hat = P.LinearReward(learn.fit_bradley_terry(d, y), task.feats)
    assert P.normalized_regret(task, R, R_hat, P.regret_cache(R, task)) < 0.05
    assert P.epic(R, R_hat, task) < 0.3


def test_maxent_recovers_dense(task, truth):
    R = truth["dense"]
    S, A = P.demonstrations(np.random.default_rng(5), task, R, 100)
    R_hat = P.LinearReward(learn.fit_maxent_linear(S, A, task, max_iter=60), task.feats)
    assert P.normalized_regret(task, R, R_hat, P.regret_cache(R, task)) < 0.05
    assert P.epic(R, R_hat, task) < 0.3
