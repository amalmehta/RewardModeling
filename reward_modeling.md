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

<Push back on the idea before building it; don't be a yes-man. Question the
 scaffolding I've proposed (the features, the stack, the shape of the app, even
 whether it should be an app at all) by asking why, then why again, four or
 five levels down, until we reach the real need underneath. Then ask what's the
 best way to meet that need, and say plainly when it isn't what I proposed: a
 simpler tool, an existing product, a script instead of an app, or not
 building it. Name the weakest assumption and the most likely way this fails.
 Ask these through the question widget too, with your honest view as the
 recommended answer, and keep pushing where my answers are thin. Agreeing is
 fine once the reasons hold up; agreeing to be agreeable isn't.>

<Push me to think for myself, about 10% harder than feels comfortable. Don't
 hand me answers to click through. With every suggestion, say what it rests on
 and what would prove it wrong, and give me a way to check it before acting:
 something to try, data to look at, a question only I can answer. On decisions
 that are mine, ask what I think before giving your view. Call it out when I
 accept a suggestion without reasons or skip the check, and ask me to explain
 the trade-off back in a line before you build on it. Ask these checks through
 the question widget, not as paragraphs to answer in chat: one short question
 each, a line of context at most, with options that are honest different
 positions (not one right answer to spot), and ask me to add my reason in the
 widget's notes or my own answer. Keep the message around it to a sentence or
 two.>

<Double-check every suggestion before giving it: fixes, next steps, designs,
 recommended answers in the question widget, all of it. Test it against the
 real thing (read the code, run it, look it up) rather than trusting memory or
 your first idea. Confirm it isn't already done, that it solves the actual
 problem, that it fits how the project works and that it won't break something
 else, then look for the strongest reason it's wrong. Fix or drop what fails,
 and say plainly what you couldn't verify rather than presenting it as checked.>

<Explain so I learn the skill, not just the answer. Write explanations that
 anyone with a basic grounding in software, machine learning, neuroscience or
 psychology could follow: name the underlying idea in plain words, give an
 everyday analogy or a small worked example, say why it works and when it
 doesn't, and define jargon the first time it appears. End with the general
 principle I could reuse next time without asking. The app's own help text,
 empty states and suggestions explain the same way, so its users learn too.>

<Don't expand scope. Anything not listed here is a proposal, including changes
 to this file — propose it, don't do it.>

<Prefer doing over describing: run the code, write the files, test it.>

<Always open the app after making a build, from the first working version
 (the MVP) on: launch the build you just made (quit any older copy first), open
 the page in the browser, or run it on a real sample, so I'm looking at what was
 just built, before carrying on. Say in a line or two what to try.>

<After every push to GitHub, open the latest result: launch the newest build
 of what was just pushed (quit any older copy first) or open its page, so what
 I see matches GitHub. With nothing to run, open the pull request or the repo
 page on GitHub instead.>

<Fully test on sample data before asking me to test on real data. Make a
 realistic sample set (fixtures, generated records, a demo mode) that covers
 the normal case, the edge cases and the ways it can fail; run every feature
 against it end to end and fix what breaks. Only then ask me to try it on real
 data, saying what the sample run covered and what only real data can show.>

<Publish production apps to GitHub. Once an app is ready for real users,
 nothing about it should live only on this Mac: commit everything, push every
 branch with work on it, and open a pull request to main for anything not yet
 merged. Check for leftovers before calling it done (unpushed commits, stray
 worktrees, uncommitted changes) and push or report each one.>

<Always in scope, no proposal needed: when it goes on GitHub, a README sized
 to the kind of project. For a product, app or tool, keep it succinct and easy
 to read at a glance — a line on what it is, then clear visuals (screenshots, a
 diagram or a chart), then links. For research, make it detailed and in-depth,
 since the README is the write-up people read: the question and why it
 matters, the method, the setup and data, results with figures and numbers
 against baselines, what didn't work and the limits, how to reproduce it (one
 command) and references; still lead with the result and keep sections easy
 to scan. Either way, setup and the rest go in linked files:
 docs/INSTRUCTIONS.md (setup, run, use),
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

<Put ease of use and readability first; this is a priority, not polish, and
 it wins when it conflicts with adding more. Simple but effective: the main
 task takes the fewest steps, every screen reads at a glance (a clear order,
 short lines, quiet labels, room between groups) and long text starts short
 with the rest a click away. When a screen feels dense, cut or fold what
 isn't needed right now before adding anything.>

<Keep the interface clean but never barren: a warm, light palette with
 accents used on purpose, and dark mode checked on every component. Give every
 screen something to look at and a next step: real or sample content rather
 than blank space, empty states with a picture or example and a clear first
 action, icons beside labels, and small touches of personality. Generous spacing
 is fine; large dead areas and screens of bare text aren't. When the visuals are
 open-ended, offer two or three mockups to pick from. Finish with a manual review
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

<Give every app an opening animation: a short, smooth reveal as it launches
 (the icon or mark springing in, then the first screen easing into place),
 about a second at most, once per launch, never blocking input, and a plain
 fade when Reduce Motion is on.>

<Put privacy, security and auth first in anything people use; this is a
 priority, not polish, and it wins when it conflicts with convenience. Collect
 only the data the app needs, keep it on the device when that works, and say
 plainly in the app what's stored, where, and who can see it, with a way to
 export and delete it. Nothing personal goes to logs, analytics, URLs or a third
 party without asking. Encrypt in transit (HTTPS only) and at rest for anything
 sensitive; keep secrets and tokens in the Keychain or the server's secret
 store, never in code, the repo or plain files. Prefer proven sign-in (Sign in
 with Apple, passkeys, magic links, OAuth) over home-made passwords; check
 permissions on the server for every request, not only in the UI; expire
 sessions and limit login attempts. Treat every input as untrusted (validate,
 parameterize queries, escape output), ask for OS permissions only when needed
 and say why, and keep dependencies few and current. Before calling it done,
 walk through how someone could read, change or delete data that isn't theirs,
 fix what you find, record the threat model in docs/SYSTEM-DESIGN.md, and add
 privacy and security to the manual review checklist.>

<Make equations easy to read. Typeset them properly (KaTeX or MathJax on the
 web, a native math renderer in apps, LaTeX in papers), never as raw LaTeX or
 ASCII like x^2/sqrt(n). Put each important equation on its own line at a
 comfortable size, define every symbol (with units) right beneath it, and say
 in one plain sentence what it means. Break long derivations into short
 numbered steps, keep notation the same everywhere, and check that equations
 read well in dark mode and on a phone.>

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

<Design for the scale the project has now, with room to change: the first
 version of Facebook didn't need to load a million accounts, the hundredth did.
 Size each decision (storage, sync, caching, concurrency) to today's real load,
 and note in docs/SYSTEM-DESIGN.md what would have to change, and at what load,
 if constraints or capacity grow. Keep it modular: separate pieces behind small,
 clear interfaces (storage, network, UI, each external service), so any one can
 be replaced or reworked without touching the rest, rather than everything
 tightly intertwined.>

<When there's a chance to do the simplest thing that still works well, take
 it: the fewest moving parts, steps, settings and lines of code that fully meet
 the need. Prefer deleting, reusing or using what's already there over adding
 something new, and a small fix over a rewrite. Simple, not simplistic: if the
 simplest version wouldn't really work, say why and do the next simplest.>

<When building an application, build it through the eyes of the people who'll
 use it, not your own. Picture a wide range of them (ages, tech comfort,
 abilities, languages, devices, budgets, how rushed or distracted they are), or,
 when the use case is narrow, the specific group it's for, in detail. Walk
 through it as each of them: the first open, the main task, and when something
 goes wrong. Build for what they'd need and notice.>

<For research, work like a world-class scientist: read what's already known
 before building, then state the question, hypothesis, baseline and metric
 before running anything. Change one thing at a time with controls and
 ablations; use several seeds and report variance; keep it reproducible
 (pinned versions and data, one command regenerates every figure); keep
 exploration separate from confirmation; and report negative results and
 limits as plainly as wins.>

<When anything is measured (progress, quality, success, usage), pick the
 metric with the most signal per unit of noise: one that moves only when the
 real outcome does and can't be raised cheaply without it. Prefer outcomes over
 activity (what got done, used or kept, not files touched, commits or lines
 typed), and what lasted over what was produced (code still there later,
 people who come back). Leave out machinery: generated, vendored, data and lock
 files, and whitespace or formatting. Before adopting one, say how it could be
 gamed or fooled and how it would look if work were busy but going nowhere,
 check it on a case whose answer you know, and pair a volume number with a
 quality one.>

<Think ten steps ahead before starting. Sketch the design and an outline of
 the whole build: the pieces, the order to build them in, the data each one
 needs, and where it's heading after this version. Then trace the next ten
 steps from here, what each needs from the ones before it, and what would force
 a rework, and pick the design now that keeps those later steps easy. Put the
 outline in docs/SYSTEM-DESIGN.md before writing code, but build only what's
 in scope today.>

<Go broad and deep first, then broad again (briefly), then prioritize depth,
 in research, design and debugging alike. Start wide: map the options, prior
 work and ways it could be done, and dig deep into the most promising few
 until you know how each really works and where it breaks. Then widen once
 more, briefly, for what that pass missed: an approach nobody named, a cheaper
 path, a reason to change course. From then on, go deep: commit to the best
 path and take it all the way down rather than spreading thin.>

<Use sub-agents when they help. Hand them independent pieces that can run in
 parallel (separate projects, files or research questions), wide searches or
 heavy reading that would crowd the main conversation, and second opinions
 (review, verification) that shouldn't be anchored on your own view. Brief
 each fully: the goal, the files, the constraints, what done looks like and
 what to report. Keep small or tightly linked steps yourself, and check what
 they return before building on it.>

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

<Always in scope: a prompt log, docs/PROMPTS.md, kept current in every
 session. Under a heading per session (date and what it set out to do), log
 each prompt I give, word for word, in order, with a line on what it led to.
 Redact secrets, keys and personal data, and link it from the README.>

<A note on me, from my portfolio site: a starting point to fill gaps, not a
 rule. Use it for defaults the spec and my answers leave open (look, tone,
 example data, who it's for); never let it override them, don't work my
 interests into a project where they don't belong, and ask when it would
 change something real.
 - Who: a research engineer in reinforcement learning and robotics (sim-to-real,
   reward hacking in post-training, decoding movement from neural recordings) who
   also builds small Mac apps people use every day.
 - Values: high agency, ambition, deep curiosity, caring and courage. Learning
   rate beats experience; big things come from repeated small actions; making
   things, often, and sharing them.
 - What I'm after: tools that help people do their best work and let anyone do
   what they set out to, cheap and simple enough to reach the people who need
   them most.
 - Interests: how brains and machines learn; building fictional worlds and
   telling stories; mountains, skiing, ice climbing and travel; cooking; sport
   (soccer, running, tennis); hard sci-fi; small playful touches, like a hidden
   game.
 - Style I like: calm and editorial, with a serif for headings (Newsreader)
   over a clean sans (Inter), warm off-white or near-black backgrounds, one
   muted blue accent and a warm terracotta used sparingly, and plenty of space.
   Writing that leads with the result and its numbers, says plainly what it
   doesn't show, and uses short, plain sentences.>

<My taste profile: what I gravitate to, from how I've reacted to builds. Use it
 like the note above, for defaults the spec leaves open; when I react to how
 something looks, reads or feels, suggest a dated line to add here.
 - Colour: one muted accent, with colour only where it carries meaning. Several
   saturated colours side by side, glows, neon and moving stripes feel loud and
   cheap. Warm, calm palettes; dark mode that stays quiet.
 - Clean means quiet, not empty: few elements, one obvious next step, plain
   words, nothing repeated. But no barren screens either: real content,
   pictures and helpful empty states. Simple and intuitive over decorated.
 - Density: built for someone who knows what they're doing. Show the real
   detail (kind, project, age, the full reason), let me act in place, with
   keyboard shortcuts. Cut clutter, not information; never feel like it's
   talking down to me.
 - Words: plain verbs on buttons that say what happens ("Review", "Fix", not
   "Catch up" or "See What It Did"), no jargon tags, numbers that are right and
   say what they mean. A wrong or misleading number is worse than none.
 - Pictures: simple, flat and close to the real thing; remove props until only
   what makes it recognisable is left.
 - How I think: push back and make me think; show what a suggestion rests on and
   how to check it; teach the idea so I can do it myself next time; take the
   simplest thing that works; think several steps ahead.>

<Finish by listing every deliverable: path, what it is, how to check it works.>

<Git rules (no Claude attribution, never commit .claude/) are in
 ~/.claude/CLAUDE.md and apply on their own — nothing to repeat here.>

<Keep the changelog at the bottom current.>

<Before building, list the lessons from this spec that apply and how you will act on each. At the end, note which you followed.>

<When the project's kind is unclear, such as whether it is a tool or written content, ask before building.>

<Before building, settle the deliverable's form, target platforms and minimum versions, packaging and signing, and hosting. When the brief conflicts with standing defaults, ask which wins.>

<Before any paid API call, settle who pays, a spending cap, test versus live mode and where keys live, and keep a mock mode so the build runs without spending.>

<When the look, concept or UI direction is open, show two or three concrete mockups or concepts to pick from before building. Never redesign existing UI without asking.>

<Ask early for real sample inputs and working credentials, and check against the live API, model or tool as soon as one path works. When none exist, say so rather than inventing them silently.>

<Before building, write down done criteria with concrete thresholds or formulas for every vague term, plus a list of what is explicitly deferred, and confirm both with me.>

<Before building anything that judges, scores or generates content, decide with me whether an AI model or deterministic rules produce it, weighing cost, explainability and reproducibility, and which model is the default.>

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

Point-mass extension (decided 2026-10-21; every setting in configs/pointmass.toml):
- Question: do the gridworld's recovery results hold in a continuous-state environment
  where the reward model is linear in generic state features, rather than tabular and well specified?
- Environment: 2D point mass on Gymnasium (`rewardshapes/PointMass-v0`). State (x, y, d) in
  [-1, 1]^3. Nine discrete actions (stay, or a 0.1 step in one of 8 headings; like
  MountainCar-v0, the actions are discrete), Gaussian position noise σ = 0.02, the box edges clip.
  d is an uncontrollable distractor, d' = clip(0.9 d + 0.3 ε). Continuing task, γ = 0.95,
  feedback horizon H = 40, uniform starts. Velocity-controlled point mass with no inertia (a
  simplification).
- Reward families R(s,a,s') = f(s) + g(s'), each rescaled to unit std over feasible transitions:
  sparse = 1[‖p'−goal‖ ≤ 0.15], goal (0.6, 0.6); dense = −‖p'−goal‖; shaped = sparse +
  γΦ(s') − Φ(s), with Φ = −10‖p−goal‖; distractor = dense + c·d', where c gives both terms
  equal variance over coverage.
- Same interface: the experiment-facing Task exposes T, gamma and horizon through a
  planning model, a 25×25 lattice whose transition rows are bilinear-interpolation weights of
  8 simulator samples per (node, action) (an "averager", for which value iteration converges). The
  gridworld's planning code runs on it unchanged. Because every reward is additive in d and d
  is exogenous, policies do not depend on d, so the lattice can leave d out exactly.
- Expert ("simple trained policy"): soft-optimal (temperature 1) finite-horizon policy from
  value iteration on simulator samples, acting on interpolated logits.
  Preferences: the gridworld's protocol (ε-mixture around the greedy-optimal policy, shared
  starts, Boltzmann β = 1 on γ-discounted true returns).
- Reward model: linear, R_θ = θ_u·ψ(s) + θ_v·ψ(s'), with ψ = 7×7 Gaussian RBFs on
  position (width 0.333) plus d, giving 100 parameters. The model is misspecified for sparse and
  shaped (the RBFs cannot represent a disk of radius 0.15), so the summary reports each shape's
  EPIC floor: the EPIC of the least-squares best reward in the class.
  Fitting: Bradley–Terry (L-BFGS, L2 1e-3), and MaxEnt IRL as exact likelihood through
  finite-horizon soft value iteration on the lattice.
- Metrics: normalized regret as in the gridworld, but J is Monte Carlo (1000 rollouts × 100
  steps, with fixed starts and noise shared by every policy), and π* is the planner's greedy policy
  on the true reward (so regret can be slightly negative). EPIC with uniform D_S, D_A: for
  f(s) + g(s') rewards the canonical reward is (g + γf)(s') + const, so EPIC is a Pearson
  distance over 65,536 fixed uniform states. Raw Pearson over 65,536 fixed coverage transitions.
- Grid: N ∈ {1, 3, 10, 30, 100, 300, 1000}; prefs and demos; seeds 0–9 (pilot 100–104);
  random-θ control. Command: `uv run python -m rewardshapes.pointmass_run`.
- Hypotheses (stated before the confirmatory run):
  C1: on distractor, demonstrations at N = 1000 reach mean regret ≤ 0.05 while mean EPIC ≥
      (dense demos' EPIC at N = 1000) + 0.15, because demos carry no information about c.
  C2: N*_prefs(sparse) ≥ 3 × N*_prefs(dense) (">1000" counts as 10,000).
  C3: at N = 1000, |EPIC(shaped) − EPIC(sparse)| ≤ 0.05 for both feedback types.

Deferred (not in v1): 16×16 scaling check; classic control (now partly done: point mass); text/LLM reward models; neural
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

Point-mass outcomes (confirmatory run, seeds 0–9, 2026-10-21; results/summary_pointmass.json):
C1 supported (distractor demos at N = 1000: regret 0.001, EPIC 0.387, which is the value an unidentified weight on d
predicts; dense demos EPIC 0.061). C2 not supported (N*_prefs: sparse = dense = 300; shaped and distractor 1000).
C3 not supported: it holds for preferences (EPIC 0.474 vs 0.484) but not for demos (0.504 vs 0.562). Also
seen: demos recover sparse at N = 1, far sooner than preferences. EPIC stays at or above 0.5 for sparse and shaped even
at regret 0, above the feature floor of 0.38, so EPIC and regret disagree whenever the model is misspecified. Raw Pearson is
fooled by shaping (prefs, N = 1000: 0.71 vs EPIC 0.48). Pilot (seeds 100–104) changed nothing.

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
- 2026-10-21 — point-mass extension: decisions and hypotheses C1–C3 recorded before running; confirmatory run and outcomes recorded
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
- 2026-11-09 — updated the meta-instructions to the current meta doc
