# Reward Shapes

How the shape of a reward (sparse, dense, potential-shaped, two goals, lava) changes how much feedback it takes to recover it, from pairwise preferences or from demonstrations. Also: which distance metric tells you the learned reward is good enough to act on.

![Explorer: the true reward next to the learned one](figures/site-explorer.png)

![Regret and EPIC distance against amount of feedback, per reward shape](figures/fig2_recovery.png)

![Spearman correlation of EPIC and raw Pearson with regret](figures/fig3_metric.png)

**Beyond the grid:** the same methods on a continuous 2D point mass (Gymnasium), with linear RBF reward features and four reward families (sparse, dense, potential-shaped, uncontrollable distractor). One command: `uv run python -m rewardshapes.pointmass_run` ([config](configs/pointmass.toml)).

![Point mass: regret and EPIC against amount of feedback](figures/fig7_pointmass.png)

**[Website](https://amalmehta.github.io/RewardModeling/)** · **[Paper (PDF)](paper/main.pdf)** · [Setup, run and use](docs/INSTRUCTIONS.md) · [System design](docs/SYSTEM-DESIGN.md) · [What's where](docs/FILE-STRUCTURE.md) · [Manual review checklist](docs/REVIEW-CHECKLIST.md)

<sub>Synthetic gridworld with simulated labelers; every invented parameter is listed in the paper and on the site.</sub>
