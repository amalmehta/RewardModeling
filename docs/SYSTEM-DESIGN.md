# Reward Shapes: system design

## What it is

A reproducible research pipeline and a static companion website. Python code generates
synthetic feedback in a gridworld, fits reward models, and scores them. The outputs are a JSON
summary, paper figures, LaTeX number macros and the site's data file. The site renders that
data with plain JavaScript; it never computes anything that the paper does not also report.

```mermaid
flowchart LR
  subgraph py["rewardshapes (Python, CPU)"]
    env["env.py<br/>8×8 slippery grid<br/>5 reward shapes"] --> fb["feedback.py<br/>prefs (Boltzmann labeler)<br/>demos (soft-optimal)"]
    fb --> learn["learn.py<br/>Bradley–Terry<br/>MaxEnt IRL"]
    learn --> eval["metrics.py + planning.py<br/>EPIC, raw Pearson,<br/>normalized regret"]
    eval --> exp["experiments.py<br/>process pool, seeded jobs"]
    exp --> raw[("results/confirm/*.jsonl")]
    raw --> an["analysis.py<br/>CIs, N*, H1–H3, bootstrap"]
  end
  an --> sum[("results/summary.json")]
  an --> nums[("paper/numbers.tex")]
  an --> data[("site/data.js")]
  sum --> figs["figures.py"] --> pdfs[("figures/*.pdf, *.png")]
  nums --> tex["paper/main.tex<br/>(Tectonic)"]
  pdfs --> tex --> pdf[("paper/main.pdf")]
  data --> site["site/ (HTML/CSS/JS)<br/>GitHub Pages"]
  pdf --> site
```

## Components

| Component | Job |
|---|---|
| `env.py` | Transition tensor `T[s,a,s']` (slip 0.1, walls). The five ground-truth reward tables `R[s,a,s']`, each rescaled to unit std over feasible transitions. |
| `planning.py` | Exact value iteration, exact policy evaluation (a linear solve), soft-optimal policies (infinite-horizon, and finite-horizon time-indexed), normalized regret. |
| `feedback.py` | Vectorised rollouts. Preference pairs share a start state, and the labels come from `σ(β·ΔG)` with the task's discount. Demonstrations come from the finite-horizon soft-optimal policy. |
| `learn.py` | Reward model `R(s,a,s') = u(s) + w(s,a) + v(s')` (384 parameters). Bradley–Terry is convex logistic regression on discounted feature counts. MaxEnt IRL is maximum likelihood through differentiable soft value iteration (PyTorch autograd, L-BFGS). |
| `metrics.py` | Exact EPIC (canonicalisation with uniform D_S, D_A, then Pearson distance over S×A×S'). The raw Pearson baseline on the feasible-transition distribution. Entry maps for plots. |
| `experiments.py` | Builds every job config (main grid, myopic labeler, β ablation, random control, overoptimization, Q-learning shaping study). Runs them in a process pool and writes JSONL. |
| `analysis.py` | 95% t-intervals over seeds, N* (the first N with mean regret ≤ 0.05), Spearman correlations with a seed-cluster bootstrap, and the hypothesis verdicts. Writes the summary, the paper macros and the site data. |
| `figures.py` | Matplotlib figures for the paper, using the validated palette. |
| `run_all.py` | The one command that regenerates everything. |
| `pointmass.py` | Point-mass extension: the Gymnasium env (`rewardshapes/PointMass-v0`), the batched dynamics it shares with the experiments, four reward families as `f(s) + g(s')`, RBF features, the `Task` (planning lattice behind `T`, plus fixed metric and evaluation samples), rollouts, feedback, sampled EPIC and raw Pearson. |
| `pointmass_run.py` | Point-mass jobs, runner, summary (`C1`–`C3` verdicts) and figure, all driven by `configs/pointmass.toml`. |
| `site/` | Static page: the explorer, verdict cards, SVG line charts with crosshair tooltips, tables, light/dark themes. |

## Point-mass extension

```mermaid
flowchart LR
  cfg[("configs/pointmass.toml")] --> task
  subgraph pm["pointmass.py"]
    gym["PointMassEnv<br/>(Gymnasium)"] -.same step().-> sim["batched step()"]
    sim --> task["Task: 25×25 lattice T<br/>(interpolated samples),<br/>metric + eval samples"]
  end
  task --> plan["planning.py<br/>(shared, size-generic)"]
  plan --> fbk["prefs / expert demos<br/>in the continuous sim"]
  fbk --> fit["learn.py<br/>Bradley–Terry, MaxEnt<br/>(linear θ·ψ)"]
  fit --> ev["regret (Monte Carlo),<br/>EPIC, raw Pearson"]
  ev --> raw2[("results/confirm/pointmass/recovery.jsonl")]
  raw2 --> sum2[("results/summary_pointmass.json")]
  sum2 --> fig7[("figures/fig7_pointmass")]
```

- **Same interface, different backing.** `Task` exposes `T`, `gamma` and `horizon`, so `planning.q_optimal`
  and `finite_horizon_soft_logpolicy` run unchanged. `T` is a `LatticeT`, a sparse CSR with about 8
  nonzeros per row that supports `k * T`, `T @ V` and `len(T)`. A dense `T` would be 28 MB and made
  value iteration memory-bound (6 s, against about 0.1 s sparse). The gridworld numbers are bit-identical
  after the refactor: committed rows were recomputed and compared.
- **The lattice is only for planning.** Feedback, returns and both metrics use the continuous
  simulator. The policy at a continuous state acts on bilinearly interpolated Q-values (or log-policies)
  from the lattice. MaxEnt's likelihood interpolates the same way, so the demonstrator and the model agree.
- **d is left out of the lattice exactly.** Every reward is additive in d and d is exogenous, so
  Q-differences across actions do not depend on d. A test checks that dense and distractor give the
  same greedy policy.
- **EPIC in closed form over s'.** For `f(s) + g(s')` rewards the canonical reward is `(g + γf)(s')`
  plus a constant. A test checks this against the definition computed by sampled expectations.
- **Regret by Monte Carlo with common random numbers.** Every policy sees the same 1000 starts and
  noise, so differences between policies are not sampling noise. π* is the planner's own optimum, so
  regret can be slightly below 0.
- **MaxEnt backward pass.** A custom autograd op runs scipy CSR `T V` forward and `Tᵀ g` backward
  (torch.sparse was about 20× slower here).

## Main flows

1. **Recovery job** (`recovery_job`): config → deterministic RNG from `(shape, feedback, N, seed, β,
   labeler)` → feedback → fit → greedy policy for the learned reward → regret, EPIC and Pearson
   against the truth. For seed 0, it also stores maps and the policy for the site.
2. **Overoptimization job**: fit a proxy from N preferences, rescale it to unit std, then for each λ
   compute the soft-optimal policy, its true normalized return, and its KL from uniform.
3. **Shaping job**: tabular Q-learning on the sparse, dense or shaped reward, with the greedy policy
   scored on the *sparse* task every 10 episodes.
4. **Analysis → outputs**: `summary.json` → figures; `numbers.tex` → paper; `data.js` → site.

## Where data lives

There is no database. All data is synthetic and regenerated from seeds.
- `results/confirm/*.jsonl`: one line per run, committed so that the figures can be rebuilt without
  re-running the experiments.
- `results/summary.json`, `paper/numbers.tex`, `site/data.js`: derived, and regenerated by `run_all`.
- `results/pilot/`: tuning runs, git-ignored (exploration is kept apart from confirmation).

## Key decisions and trade-offs

- **Tabular, exact everything.** Regret comes from a linear solve and EPIC is computed in closed form
  over the full product space, so there is no sampling error in the metrics. All variance comes from
  feedback sampling and is measured across seeds. Trade-off: the results say nothing direct about
  neural reward models.
- **Additive reward model u(s) + w(s,a) + v(s').** It is small (384 parameters), every ground truth
  lies in the class (including potential shaping), and it is defined on all of S×A×S', so EPIC's
  canonicalisation never queries undefined values. Trade-off: it is a well-specified setting, and the
  model is never misspecified except under the myopic-labeler ablation.
- **Labeler and demonstrator use the task's discount γ, and preference pairs share a start.** The
  pilot (seeds 100–104) showed that undiscounted returns identify rewards only up to γ=1 shaping,
  which is not policy-invariant at γ=0.95: shaped-reward regret *rose* with N. Matching the discount
  and sharing starts (as RLHF shares prompts) removes that confound. It is recorded as a pilot
  finding, not hidden.
- **Unit-std rescaling of every true reward.** It makes β mean the same "noise per unit reward"
  across shapes. It is an invented normalisation and is labelled as such.
- **Greedy ties broken uniformly.** A constant reward therefore yields the uniform policy and regret
  exactly 1, so the "no information" baseline is well defined.
- **L-BFGS over Adam.** Bradley–Terry is convex here, so L-BFGS converges deterministically in a few
  dozen iterations and needs no learning-rate tuning.
- **Process pool, one torch thread per worker.** Jobs are independent and small, so parallelism goes
  across processes, not threads.
- **Site: no framework, no build step, data in a `<script>`.** It opens from `file://` and on GitHub
  Pages alike. All interaction re-renders from memory (well under 100 ms), and charts are re-drawn
  only on resize (debounced at 120 ms) or a theme change.

## Testing

`tests/test_core.py` (23 tests) covers: transition rows sum to 1; unit-std rewards; EPIC is zero
between sparse and its shaped version while raw Pearson is not; EPIC is scale/shift invariant,
symmetric, and gives 1 for negation; a constant reward gives EPIC √½ and regret 1; optimal policies
give regret 0; shaping preserves the optimal policy; features reproduce discounted returns; rollouts
follow the dynamics; Bradley–Terry and MaxEnt recover rewards with enough data; soft policies
approach greedy; preference pairs share starts.

Point mass: `tests/test_pointmass.py` (18 tests) covers: Gymnasium's env checker; the Gymnasium env and
the batched dynamics give identical trajectories; lattice rows are distributions; the Task is
deterministic; unit-std rewards; closed-form canonicalisation equals the sampled definition; EPIC
ignores shaping (raw Pearson does not), is scale/shift invariant and symmetric, and gives 1 for
negation; a constant reward gives EPIC √½ and regret ≈ 1; the true reward gives regret 0, and shaping
keeps the policy; the distractor does not change the policy; features reproduce returns; preference
pairs share starts; Bradley–Terry and MaxEnt recover the dense reward.

## Known limits

- One small gridworld; the 16×16 scaling check is deferred.
- Point mass: velocity-controlled (no inertia), with discrete actions; planning on a 25×25 lattice
  (interpolation error). The linear RBF model cannot represent the sparse goal disk, so sparse and
  shaped have an EPIC floor of 0.38 that no amount of data removes.
- Simulated labelers: Boltzmann-rational, or myopic in one specific way. No human data.
- The ε-greedy trajectory mixture is generous: many compared trajectories are near-optimal, which
  makes preference learning easier than with uninformed sampling.
- Regret saturates: in a gridworld many rewards induce near-optimal policies. EPIC is the more
  discriminating metric at large N, regret at small N.
- EPIC with uniform coverage counts unvisited (s,a) pairs, which no feedback ever constrains, so its
  floor is above 0 even with unlimited data.
