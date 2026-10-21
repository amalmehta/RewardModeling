# Reward Shapes: what's where

```
reward_modeling/
├── README.md                 at-a-glance overview with figures and links
├── reward_modeling.md        project spec: decisions, definitions, deferred, changelog
├── pyproject.toml, uv.lock   pinned Python environment
├── rewardshapes/             the research code
│   ├── env.py                gridworld dynamics + the five reward shapes
│   ├── planning.py           value iteration, policy evaluation, soft policies, regret
│   ├── feedback.py           trajectory sampling, preference labels, demonstrations
│   ├── learn.py              reward model; Bradley–Terry and MaxEnt IRL fitting
│   ├── metrics.py            EPIC, raw Pearson distance, entry maps
│   ├── experiments.py        every experiment grid; parallel runner (--pilot for tuning seeds)
│   ├── analysis.py           statistics, hypothesis verdicts, paper numbers, site data
│   ├── figures.py            paper figures
│   ├── run_all.py            one command regenerates everything (gridworld)
│   ├── pointmass.py          point-mass Gymnasium env, reward families, planning lattice, metrics
│   └── pointmass_run.py      point-mass experiments, summary, figure (one command)
├── configs/pointmass.toml    every setting and seed of the point-mass run
├── tests/test_core.py        unit tests for the behaviour that matters
├── tests/test_pointmass.py   unit tests for the point-mass extension
├── results/
│   ├── confirm/*.jsonl       raw confirmatory runs (seeds 0–9)
│   ├── confirm/pointmass/recovery.jsonl   point-mass raw runs (seeds 0–9)
│   ├── summary.json          every aggregate and verdict
│   ├── summary_pointmass.json   point-mass aggregates and C1–C3 verdicts
│   ├── confirm_pointmass_run.log   log of the point-mass run
│   └── confirm_run.log       log of the confirmatory run
├── figures/                  fig1–fig6 as PDF (paper) and PNG (README); fig7 = point mass
├── paper/
│   ├── main.tex              the paper
│   ├── refs.bib              verified references
│   ├── numbers.tex           generated numbers (do not edit)
│   └── main.pdf              compiled paper
├── site/                     the static website (GitHub Pages)
│   ├── index.html, style.css, app.js
│   ├── data.js               generated data (do not edit)
│   ├── icon.svg              app icon / favicon
│   └── reward-shapes.pdf     copy of the paper
├── docs/
│   ├── INSTRUCTIONS.md       setup, run, use
│   ├── SYSTEM-DESIGN.md      architecture, decisions, testing, limits
│   ├── FILE-STRUCTURE.md     this file
│   └── REVIEW-CHECKLIST.md   manual checks that tests can't cover
└── .github/workflows/pages.yml   publishes site/ to GitHub Pages
```
