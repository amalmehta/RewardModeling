# Manual review checklist

What the automated tests can't check. Tick these by hand before publishing.

## Smoothness (a priority)
- [ ] Explorer: drag the N slider end to end quickly. Both grids and the stat cards follow every step with no lag or flicker.
- [ ] Switching shape, feedback or Raw/Canonical recolours the cells with a short fade (about 200 ms), and nothing jumps or reflows.
- [ ] Chart hover: the crosshair and tooltip track the pointer at full frame rate, and the tooltip never runs off-screen.
- [ ] Resizing the window re-flows the charts once it settles, without flashing empty.
- [ ] The theme toggle switches instantly, with no white flash on reload in dark mode.
- [ ] Scrolling the page is fluid on a laptop, and on a phone (375 px wide).

## Look and feel
- [ ] Light mode: warm, calm, sparing accents. Nothing shouts.
- [ ] Dark mode: check every component (header, chips, segmented buttons, slider, grids, stat cards, verdict cards, charts, tables, tooltip, footer).
- [ ] Shape colours: the goal-based shapes (sparse, two goals, shaped) read as one cool family and dense/lava as warm, and each one is still distinguishable at a glance in both themes.
- [ ] Line labels at chart ends don't collide; with five lines close together they stay legible.
- [ ] The icon reads as "grid + path to a goal" in a browser tab at 16 px.

## Content and honesty
- [ ] Every number in the abstract, verdict cards and tables matches `results/summary.json`.
- [ ] "What is invented here" lists every invented parameter, and the paper says the same.
- [ ] Hypothesis verdicts in the paper match the site's.
- [ ] The paper PDF link works on the site, and the PDF fits the page limit (4–6 pages plus references).
- [ ] References in the PDF resolve to the right papers (all were checked against arXiv/Crossref/OpenAlex on 2026-10-20).

## Live services
- [ ] After pushing: GitHub Pages deploys from Actions, and the live URL loads the favicon, data and PDF.
- [ ] The Feedback link opens a new GitHub issue on the right repo.
