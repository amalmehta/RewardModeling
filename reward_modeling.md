PROJECT NAME: reward_modeling

META-INSTRUCTIONS:

<Read it all before acting. Ask about anything unclear, contradictory or
 underspecified — before starting and mid-build. Ask in the question widget
 (AskUserQuestion): related questions batched, concrete options, your
 recommendation first. Plain text only if the widget isn't available.>

<Make answering easy. Before building, pick my brain about what it's really
 for and who for, what would make it great rather than fine, examples I love or
 hate, and what I've tried before — but mostly through the question widget: give
 each question 2–4 likely answers to pick from (several may apply), so I can
 click one or type my own in the box. Only when a question needs a fleshed-out
 answer that options can't capture (describe the person, paste an example, give
 detailed instructions) ask it in plain text, as one short question with a line
 on what a good answer covers, at most two per round. Never a long numbered list
 of open questions. Wait for my answers and follow up where they open something
 up.>

<Don't expand scope. Anything not listed here is a proposal, including changes
 to this file — propose it, don't do it.>

<Prefer doing over describing: run the code, write the files, test it.>

<As soon as a first working version (the MVP) exists, open it for me before
 carrying on: launch the app, open the page in the browser, or run it on a real
 sample, and say in a line or two what to try. Do the same after each big change.>

<Always in scope, no proposal needed: when it goes on GitHub, a README that is
 easy to read at a glance — a line on what it is, then clear visuals
 (screenshots, a diagram or a chart), then links. Everything else goes in
 linked files: docs/INSTRUCTIONS.md (setup, run, use),
 docs/SYSTEM-DESIGN.md (see below) and docs/FILE-STRUCTURE.md (what's where). If what you're
 building is an application rather than a script, also a small unobtrusive feedback tab, and a settings
 button or tab (⌘, on the Mac) that gathers its preferences in one place.>

<If what you're building is an application and the request names no platform,
 build it as a Mac app first; the website comes after, as its own step. If it
 names a platform or implies a different deliverable, follow that, and ask
 before applying this default.>

<Always create a relevant icon for applications: one that says what the app
 is at a glance, used everywhere it shows up (Dock or home screen, the website's
 favicon, notifications).>

<Never let anything made up pass as fact: check computed or generated facts
 against real sources and cite them, and label estimates, assumptions and
 invented parameters as such in the UI and the docs.>

<Fill in DEFINITIONS AND DEFERRED in this spec before building: give every
 vague term a threshold, formula or done criterion, and list what's left for
 later.>

<Keep the interface clean and restrained: a warm, light palette with sparing
 accents, and dark mode checked on every component. When the visuals are open-
 ended, offer two or three mockups to pick from. Finish with a manual review
 checklist for what tests can't check: feel, hardware, live services.>

<Make it buttery smooth; this is a priority, not polish. Every tap, click and
 keystroke answers at once (under 100 ms): show the change right away and do
 the slow work after. Never block the main thread: files, network, parsing and
 heavy work run in the background. Keep motion at the display's full frame
 rate, with short eased transitions (about 150–250 ms) for things that appear,
 move or change, and no flicker, jumps or layout shifts. Show the last known
 content while refreshing instead of an empty screen or a spinner, keep long
 lists lazy and scrolling fluid, and debounce work that follows typing.
 Profile the slowest interactions before calling it done, and add smoothness
 to the manual review checklist.>

<Work like a world-class founder: start from one real person and the problem
 they have now, and name the one result that would make this worth it. Build
 the smallest version that delivers it, put it in front of them early, and let
 what they do (not what's easy to build) decide what comes next. Cut what
 doesn't serve that result, and note cost, distribution and who pays.>

<Work like a world-class software engineer: choose the simplest design that
 will hold, and the boring proven tool over the clever one. Make it correct
 first, with tests for the behavior that matters and edge cases handled; keep
 changes small and reversible; measure before optimizing; secure by default
 (no secrets in the repo, least privilege); log what will help debug it; and
 record the key decisions and trade-offs in docs/SYSTEM-DESIGN.md.>

<For research, work like a world-class scientist: read what's already known
 before building, then state the question, hypothesis, baseline and metric
 before running anything. Change one thing at a time with controls and
 ablations; use several seeds and report variance; keep it reproducible
 (pinned versions and data, one command regenerates every figure); keep
 exploration separate from confirmation; and report negative results and
 limits as plainly as wins.>

<Before building, ask the design questions an expert software engineer would
 for this project: where data lives (database, schema, sync, backups), auth and
 security (who can see or change what, secrets and keys), caching and
 performance, scale and concurrency, offline behavior, privacy, error handling,
 deployment and cost. Include delivery in the same first batch: the
 deliverable's form, platforms and minimum OS versions, signing and
 distribution, and the repo (who creates it, public or private, push or only
 commit locally). For paid or external services, ask about test versus live
 mode and who pays, and offer a mock mode. Ask for real sample inputs and
 working credentials before building. Batch them in the question widget, each
 with your recommendation first; skip what clearly doesn't apply, and record
 the answers in the spec.>

<When an application takes files as input, offer a visible Upload button that
 opens the file picker, accept files dragged anywhere onto the window (not
 only onto a small drop zone), and accept pasting them with ⌘V.>

<Color-code tags, categories and types by similarity: related ones share a
 hue family, with shades far enough apart to tell them apart at a glance, in
 both light and dark mode.>

<Name things the way a person would say them — "Goal Tracker", not
 goal_tracker — for the app, its windows, titles, files people open, repo
 descriptions and README headings. When you create the GitHub repo, name it
 with no "_" or "-": one word or joined words, e.g. GoalTracker.>

<Always in scope: a system design doc in the codebase, docs/SYSTEM-DESIGN.md,
 kept current as the build changes. Cover the architecture (with a Mermaid
 diagram), each component's job, the main flows, where data lives, the key
 design decisions and their trade-offs, how it's tested, and known limits.>

<Finish by listing every deliverable: path, what it is, how to check it works.>

<Git rules (no Claude attribution, never commit .claude/) are in
 ~/.claude/CLAUDE.md and apply on their own — nothing to repeat here.>

<Keep the changelog at the bottom current.>

LEARNED ACROSS PROJECTS:

<What held across several kinds of earlier projects: starting points, not rules.>

<Decide which data sources, external services and licenses are allowed, test versus live mode, key storage, who pays, spending limits, privacy, and offline behavior. (across 12 kinds)>

<Settle the deliverable's form, target platforms, minimum versions and distribution up front, including packaging, signing, hosting and who runs it. (across 11 kinds)>

<Define vague terms, scope boundaries and scoring rules with concrete thresholds, formulas and done criteria, recording what is deferred. (across 10 kinds)>

<Validate generated or computed content against real sources, cite them, and label estimates or invented parameters so nothing fabricated passes as fact. (across 8 kinds)>

<Settle version control policy early: who creates and hosts the repository, its visibility, and whether to push or only commit locally. (across 8 kinds)>

<Gather real sample inputs and working credentials early, then verify live APIs, model output and system tools, keeping a fallback ready. (across 8 kinds)>

<Define each output's specs, tone and visual style before building, offering a few concrete concepts or mockups to pick from when open-ended. (across 7 kinds)>

<Plan a manual or human review checklist for what automated tests can't verify, such as hardware, live services, feel or taste. (across 3 kinds)>

LEARNED FOR ML / DATA MODEL PROJECTS:

<Starting points from 14 earlier ml / data model projects, not rules: use what fits this one, and ask when it differs.>

<Settle the core question and what is in scope (features, experiments, variants, sweeps, content size) versus deferred, so nothing gets added halfway through. (seen in 12)>

<Settle what produces adaptive judgments or content (an LLM, pretrained or learned model, programmatic functions, bundled data) and which decisions stay in deterministic code. (seen in 8)>

<Settle how vague goals become measurable: metrics, rating scales, splits, budgets, thresholds, scoring weights and their calibration, and local stand-ins for hidden tests. (seen in 7)>

<Settle the audience, accounts and login, which source material stays out, whether user data persists, where, and who may read it. (seen in 5)>

<Settle data and reference sources, licenses, keys, citation standards, refresh schedule, stored history, and an offline fallback snapshot before building. (seen in 4)>

<Settle the concrete task, observations or sensors, action space, and units, matching the conventions of the chosen model or framework. (seen in 3)>

<Settle how unmeasurable targets are estimated from proxies, and how assumptions, uncertainty ranges and limitations are disclosed to users. (seen in 2)>

<Settle whether required API keys or credentials exist yet, and how model-dependent paths are verified or demoed without them. (tentative)>

CONTEXT:

Project type: ML / data model (training and evaluating a model on data, with reproducible runs).

figure out a reward-modeling suite of projects that can figure out the shape of different rewards in different environments

DELIVERABLES:

website + experiments + writeup etc

DEFINITIONS AND DEFERRED:

Decisions (from the question rounds, 2026-10-20):
- Purpose: a workshop-length research paper (arXiv-ready, 4–6 pages LaTeX) plus a static
  paper-companion website (one long page: abstract, interactive true-vs-learned reward
  explorer, results charts, links). GitHub Pages; public repo "RewardModeling", created and
  pushed only after the user says go. Until then: local git commits only.
- Stack: uv, Python 3.12, PyTorch 2.2.2 (the last Intel-macOS wheel), numpy<2, matplotlib,
  scipy. CPU only. Website: plain HTML/CSS/JS, no build step, data from precomputed JSON.
- No external services, keys, or paid APIs. All data is synthetic and generated by seeded code.

Research question: across reward shapes in the same gridworld, how much feedback (pairwise
trajectory preferences, or demonstrations) does it take to recover the reward well enough to
act on it, and which distance metric tells you that?

- Environment: 8×8 gridworld, 4 actions (up/down/left/right), slip probability 0.1 (the move
  goes in a uniformly random direction instead), walls keep you in place, continuing task with
  γ = 0.95, no terminal states. Trajectories have horizon H = 20 and start from uniform states.
- Reward shapes (ground truth R(s,a,s'), each rescaled to unit std over feasible transitions):
  sparse = +1 for entering goal (7,7); dense = −manhattan(s', goal)/14; shaped = sparse +
  γΦ(s') − Φ(s) with Φ = −manhattan(s, goal) (Ng et al. 1999 potential shaping); multi = +1
  goal (7,7) and +0.6 goal (0,7); lava = +1 goal, −1 for entering 6 lava cells, −0.02 per step.
- Reward model: tabular R_θ(s,a,s') = u(s) + w(s,a) + v(s'), with 384 parameters. Every
  ground truth above lies in this class.
- Preference feedback: trajectory pairs from a mix of ε-greedy policies built on the true
  optimal policy, with ε ~ U[0,1] per trajectory. Synthetic Boltzmann labeler
  P(τ1 ≻ τ2) = σ(β·(G(τ1) − G(τ2))), G = γ-discounted return (γ = 0.95), and pairs share a start
  state. β = 1 by default. (Changed after the pilot: undiscounted G made shaped-reward regret grow with N.)
  The model is fit by Bradley–Terry maximum likelihood (Adam, L2 1e-3).
- Demonstration feedback: H = 20 trajectories from the soft-optimal (Boltzmann, temperature 1)
  finite-horizon policy. MaxEnt IRL (Ziebart et al. 2008) is fit as maximum likelihood through
  differentiable finite-horizon soft value iteration.
- N grid: {1, 3, 10, 30, 100, 300, 1000} pairs or demos; 10 seeds per cell. (Extended down to 1 after the
  pilot showed regret near 0 by N = 10.)
- Normalized regret = (J(π*_true) − J(π_learned)) / (J(π*_true) − J(π_uniform)), where J is
  the true expected discounted return from a uniform start and π_learned is greedy-optimal
  for the learned reward. 0 = perfect, 1 = no better than acting uniformly at random.
- "Recovered": mean normalized regret ≤ 0.05 across seeds. Sample complexity N* = the
  smallest N on the grid that achieves it (reported as ">1000" if none does).
- EPIC distance (Gleave et al. 2021): canonicalize both rewards with uniform D_S and D_A,
  then take the Pearson distance sqrt((1−ρ)/2) over the uniform product S×A×S'. Computed
  exactly (tabular), with no sampling. Baseline metric: raw Pearson distance on feasible
  transitions (uniform s and a, s' ~ T).
- Hypotheses (stated before running):
  H1: sparse and lava rewards need ≥3× the preferences dense needs to reach N*.
  H2: across all runs, EPIC distance has a higher Spearman correlation with normalized regret
      than raw Pearson distance does, with the largest gap on the shaped reward.
  H3: a myopic labeler (it judges with discount 0.8 instead of the task's 0.95) leaves a regret floor
      that does not shrink with N, and the floor is largest for sparse/lava.
- Baselines/controls: N = 0 (a random-init reward model) and a random-reward control
  (θ ~ N(0,1)), giving the regret and EPIC of an uninformed model.
- Ablations (preferences only): β ∈ {0.3, 1, 3, 10} at N ∈ {30, 300}; the myopic labeler over the full N grid.
  H3's "does not shrink" test: mean regret at N = 1000 > 0.05 and ≥ (N = 300) − 0.02.
- Overoptimization: the soft-optimal policy for a proxy (learned, rescaled to unit std) reward at inverse
  temperature λ ∈ logspace(−1, 2, 13). Plot true normalized return against λ (and KL from
  uniform) for proxies learned at N ∈ {3, 30, 300} (moved down with the new N grid), by shape.
- Shaping-speed study: tabular Q-learning (α = 0.1, ε = 0.1, 50-step episodes) trained on
  sparse, dense, or shaped reward, and scored by normalized regret on the sparse task.
  Metric: episodes until greedy regret ≤ 0.05 (cap 3000), 10 seeds.
- Exploration vs confirmation: tuning (learning rates, steps, L2) only on seeds 100–104; all
  reported numbers use seeds 0–9. Intervals are 95% percentile bootstraps over seeds (switched from
  t-intervals, which went below 0 for regret).
- Reproducibility: `uv run python -m rewardshapes.run_all` regenerates every result, figure,
  site JSON and paper number. Target runtime under 2 hours on this Mac.
- Website "smooth": every control updates the view in under 100 ms (all data preloaded, no
  network on interaction); transitions 150–250 ms; light and dark themes.

Deferred (not in v1): 16×16 scaling check; classic control; text/LLM reward models; neural
(non-tabular) reward models; real human labels; dynamics-aware metrics (DARD); a Mac app
(the deliverable is a paper plus a static site, so none was built); a feedback/settings tab
beyond a feedback link and a theme toggle.

OPEN QUESTIONS / ASSUMPTIONS:

Outcomes (confirmatory run, 2026-10-20): H1 not supported (N* sparse = dense = 3 pairs; lava 10).
H2 supported (Spearman with regret: EPIC 0.61 vs raw Pearson 0.54, difference CI [0.02, 0.10]; shaped
0.46 vs 0.05). H3 not supported as stated (a large residual regret, but it shrinks from N = 300 to 1000,
and the worst shapes are lava and shaped). Unexplained: preference regret is non-monotone in N for dense
and shaped, and myopic-labeler regret is U-shaped (lowest near N = 10). An exploratory check ruled out
the optimizer and the action term w(s,a) as causes.

- Assumed the website counts as a document companion, not an application. So: a GitHub-issues
  feedback link and a light/dark toggle instead of a full settings tab, and an SVG favicon
  icon instead of an app icon.
- The labeler's β, the slip probability, the lava layout, the multi-goal values and the
  ε-mixture for trajectory sampling are invented parameters. They are labelled as such in the
  paper and on the site.
- Reward rescaling to unit std makes β comparable across shapes. It is a design choice, not a
  fact about the shapes.
- The paper uses a plain article layout (labelled "workshop preprint"), not an official venue
  template; it can be retargeted later.

CHANGELOG:

- 2026-10-20 — created
- 2026-10-20 — filled DEFINITIONS AND DEFERRED and OPEN QUESTIONS from the question rounds; started the build
- 2026-10-20 — after the pilot: discounted labeler with shared starts, N grid down to 1, overopt and β N values moved; bootstrap CIs; recorded the confirmatory outcomes; built the site, paper and docs
- 2026-09-15 — added meta-instruction: built-out applications include a small feedback tab
- 2026-09-15 — added meta-instruction: no "Claude" attribution in commits, PRs, or branches
- 2026-09-16 — added meta-instruction: always include a README when adding to GitHub
- 2026-09-16 — changed meta-instruction: ask clarifying questions in the question widget
- 2026-09-17 — added meta-instructions: Claude never a contributor; never commit .claude/
- 2026-09-26 — compressed the meta-instructions and every field prompt; git rules moved to the global instruction file
- 2026-09-27 — added meta-instruction: applications are built as a Mac app first, then a website
- 2026-09-28 — folded inputs, instructions, constraints, deliverables and done criteria into one free-form CONTEXT
- 2026-09-28 — changed meta-instruction: a README on GitHub always includes a visual
- 2026-09-28 — added meta-instruction: name things like a person would, never snake_case
- 2026-09-28 — changed meta-instruction: README leads with visuals; instructions live in a linked guide
- 2026-09-28 — changed meta-instruction: README is visuals and links; details in docs/INSTRUCTIONS.md and docs/FILE-STRUCTURE.md
- 2026-09-29 — changed meta-instruction: GitHub repo names have no "_" or "-"
- 2026-10-02 — added a DELIVERABLES field after CONTEXT
- 2026-10-02 — added meta-instruction: every project has a system design doc at docs/SYSTEM-DESIGN.md
- 2026-10-05 — added meta-instruction: applications include a settings button or tab
- 2026-10-08 — added meta-instruction: color-code tags by similarity (related share a hue family, each distinct)
- 2026-10-09 — added meta-instruction: apps that take files have an Upload button, drop anywhere, and paste
- 2026-10-17 — added meta-instruction: before building, ask the design questions an expert engineer would (data, security, caching, scale, deployment…)
- 2026-10-18 — added meta-instruction: open the MVP for me as soon as a first working version exists, and after each big change
- 2026-10-18 — added meta-instruction: always create a relevant icon for applications
- 2026-10-18 — added meta-instructions: work like a world-class founder, software engineer and (for research) scientist
- 2026-10-18 — added meta-instruction: pick my brain with open questions answered in my own words, as well as multiple choice
- 2026-10-18 — changed meta-instruction: Mac app first only when the request names no platform (from the meta report)
- 2026-10-18 — changed meta-instruction: the first batch of questions also covers delivery, the repo, test versus live mode, who pays, mocks, and real inputs and credentials (from the meta report)
- 2026-10-18 — added meta-instructions: nothing made up passes as fact; fill in DEFINITIONS AND DEFERRED; a clean, restrained interface with mockups and a manual review checklist (from the meta report)
- 2026-10-18 — added a DEFINITIONS AND DEFERRED section
- 2026-10-19 — changed meta-instruction: questions mostly as multiple choice (with a box for my own answer); plain-text questions only when a detailed answer is needed, at most two per round
- 2026-10-20 — added meta-instruction: make the UI/UX buttery smooth (instant response, nothing blocking the main thread, full-frame-rate motion, no flicker or jumps)
