# Reward Shapes: setup, run, use

## Setup

You need macOS or Linux, [uv](https://docs.astral.sh/uv/), and (for the PDF) [Tectonic](https://tectonic-typesetting.github.io/).

```bash
uv sync
```

This installs Python 3.12 with pinned PyTorch 2.2.2, NumPy < 2, SciPy, Matplotlib and Gymnasium 1.4 (see `uv.lock`).
PyTorch 2.2.2 is the last release with Intel-macOS wheels. Everything runs on the CPU.

## Run

| What | Command | Time (8 cores, idle machine) |
|---|---|---|
| Unit tests | `uv run pytest -q` | ~1.5 min |
| Pilot on the tuning seeds (100–104) | `uv run python -m rewardshapes.experiments --pilot` | ~10 min |
| **Everything**: experiments, summary, figures, site data, PDF | `uv run python -m rewardshapes.run_all` | ~30–60 min |
| Re-analyse existing results only | `uv run python -m rewardshapes.run_all --skip-experiments` | ~1 min |
| **Point-mass extension**: experiments, summary, figure 7 (settings and seeds in `configs/pointmass.toml`) | `uv run python -m rewardshapes.pointmass_run` | ~25 min |
| Point-mass pilot (tuning seeds 100–104, into `results/pilot/`) | `uv run python -m rewardshapes.pointmass_run --pilot` | ~10 min |
| Point-mass re-analysis only | `uv run python -m rewardshapes.pointmass_run --skip-experiments` | ~1 min |

Raw runs are written to `results/confirm/*.jsonl`. `results/summary.json` holds every aggregate and
hypothesis verdict. `paper/numbers.tex` holds every number the paper quotes, and `site/data.js` holds
the site's data.
Point-mass runs go to `results/confirm/pointmass/recovery.jsonl` (the same row schema, plus `env`),
with aggregates and the C1–C3 verdicts in `results/summary_pointmass.json`. For a variant, copy the
config and pass `--config my.toml`. Every job is seeded from the config and its
(shape, feedback, N, seed) key, so `--procs` does not change any result.

## Use the website

Open `site/index.html` in a browser (it works straight from disk), or serve the folder:

```bash
python3 -m http.server -d site 8000
```

- **Explorer**: pick a reward shape, preferences or demonstrations, and N. The left grid is the true
  reward and the right grid is the learned one (seed 0); arrows show the greedy policy. Switch to
  *Raw* to see why potential shaping fools a raw comparison and *Canonical* to see it removed.
  Hover a cell to see its exact value.
- **Charts**: hover for exact values; *Show table* gives the numbers as a table.
- **Theme**: ◐ switches between light and dark (it defaults to your OS setting).

## Publish the site (GitHub Pages)

The `site/` folder is the whole site. `.github/workflows/pages.yml` publishes it on every push to
`main`. Turn it on once under **Settings → Pages → Source: GitHub Actions**.
