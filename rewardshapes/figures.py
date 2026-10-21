"""Paper figures from results/summary.json (PDF for LaTeX, PNG for the README)."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import env as E  # noqa: E402
from .analysis import ROOT  # noqa: E402
from .experiments import OVEROPT_N, RESULTS, SHAPING_TRAIN  # noqa: E402

# Validated categorical order (dataviz validator, light mode): goal-based shapes are cool
# hues, dense and lava warm.
COLOR = {"sparse": "#2a78d6", "multi": "#1baf7a", "shaped": "#6250d6",
         "dense": "#eda100", "lava": "#e87ba4"}
DASH = {"sparse": "-", "multi": "--", "shaped": "-.", "dense": ":", "lava": (0, (5, 1, 1, 1))}
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
RAMP = ["#86b6ef", "#2a78d6", "#104281"]  # sequential blue, ordinal steps for N
FIG = ROOT / "figures"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8, "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.5, "lines.linewidth": 1.6,
    "legend.frameon": False, "savefig.bbox": "tight", "savefig.dpi": 200,
})


def _save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)


def _band(ax, xs, pts, color, ls, label):
    m = np.array([p["mean"] for p in pts])
    lo = np.array([p["lo"] for p in pts])
    hi = np.array([p["hi"] for p in pts])
    ax.fill_between(xs, lo, hi, color=color, alpha=0.15, lw=0)
    ax.plot(xs, m, color=color, ls=ls, label=label, marker="o", ms=3)


def _heat(ax, grid, title, vmax=None):
    g = np.array(grid).reshape(E.SIZE, E.SIZE)
    v = vmax or max(np.abs(g).max(), 1e-9)
    ax.imshow(g, cmap="RdBu_r", vmin=-v, vmax=v)
    ax.set_xticks([]), ax.set_yticks([])
    ax.grid(False)
    ax.set_title(title, fontsize=7)


def fig_shapes(S, site):
    fig, axes = plt.subplots(3, 5, figsize=(7, 5.0))
    fig.subplots_adjust(hspace=0.45)
    for j, sh in enumerate(E.SHAPES):
        _heat(axes[0, j], site["truth"][sh]["map_raw"], f"{sh}: true (raw)")
        _heat(axes[1, j], site["truth"][sh]["map_canon"], "true (canonical)")
        ex = site["examples"][f"{sh}|prefs|1000"]
        _heat(axes[2, j], ex["map_canon"], f"learned, 1000 prefs\nEPIC {ex['epic']:.2f}")
    fig.suptitle("Reward for entering each cell (red high, blue low, white zero). Canonicalisation removes shaping.",
                 fontsize=8, color=INK)
    _save(fig, "fig1_shapes")


def fig_recovery(S):
    fig, axes = plt.subplots(2, 2, figsize=(7, 4.6), sharex=True)
    for j, fb in enumerate(("prefs", "demos")):
        for i, metric in enumerate(("regret", "epic")):
            ax = axes[i, j]
            for sh in E.SHAPES:
                pts = S["curves"][fb][metric][sh]
                _band(ax, [p["n"] for p in pts], pts, COLOR[sh], DASH[sh], sh)
            ax.set_xscale("log")
            if metric == "regret":
                ax.axhline(S["recovered_threshold"], color=MUTED, lw=0.8, ls="--")
                ax.set_title({"prefs": "Pairwise preferences (Bradley-Terry)",
                              "demos": "Demonstrations (MaxEnt IRL)"}[fb], fontsize=8)
            ax.set_ylabel("normalized regret" if metric == "regret" else "EPIC distance")
            if i == 1:
                ax.set_xlabel("N (pairs or demonstrations)")
    axes[0, 1].legend(loc="upper right", fontsize=7)
    fig.text(0.5, -0.02, "Mean over 10 seeds; bands are 95% bootstrap intervals. Dashed line: recovered "
             "threshold (regret 0.05).", ha="center", fontsize=7, color=MUTED)
    _save(fig, "fig2_recovery")


def fig_metric(S):
    h2 = S["H2"]["by"]
    keys = ["all"] + E.SHAPES
    x = np.arange(len(keys))
    fig, ax = plt.subplots(figsize=(4.6, 2.4))
    for k, (metric, color, off) in enumerate([("epic", "#2a78d6", -0.18), ("pearson", "#eb6834", 0.18)]):
        vals = [h2[s][metric] for s in keys]
        ci = np.array([h2[s][f"{metric}_ci"] for s in keys]).T
        ax.bar(x + off, vals, 0.34, color=color, label={"epic": "EPIC", "pearson": "raw Pearson"}[metric])
        ax.errorbar(x + off, vals, yerr=[np.array(vals) - ci[0], ci[1] - np.array(vals)],
                    fmt="none", ecolor=INK, lw=0.8, capsize=2)
    ax.axhline(0, color="#c3c2b7", lw=0.8)
    ax.set_xticks(x, keys)
    ax.set_ylabel("Spearman ρ with regret")
    ax.legend(fontsize=7)
    ax.set_title("Which distance predicts regret? (seed-cluster bootstrap 95% CI)", fontsize=8)
    _save(fig, "fig3_metric")


def fig_ablations(S):
    fig, axes = plt.subplots(1, 3, figsize=(7, 2.3))
    for sh in E.SHAPES:
        std = S["curves"]["prefs"]["regret"][sh]
        my = S["myopic"]["regret"][sh]
        axes[0].plot([p["n"] for p in my], [p["mean"] for p in my], color=COLOR[sh], ls=DASH[sh],
                     marker="o", ms=3, label=sh)
        for k, n in enumerate(("30", "300")):
            row = S["beta"][sh][n]
            axes[1 + k].plot([r["beta"] for r in row], [r["mean"] for r in row], color=COLOR[sh],
                             ls=DASH[sh], marker="o", ms=3)
    axes[0].set_xscale("log"), axes[0].set_title("Myopic labeler (discount 0.8)", fontsize=8)
    axes[0].set_xlabel("N pairs"), axes[0].set_ylabel("normalized regret")
    axes[0].axhline(S["recovered_threshold"], color=MUTED, lw=0.8, ls="--")
    for k, n in enumerate(("30", "300")):
        axes[1 + k].set_xscale("log"), axes[1 + k].set_xlabel("labeler rationality β")
        axes[1 + k].set_title(f"β ablation, N = {n} pairs", fontsize=8)
    axes[0].legend(fontsize=6)
    _save(fig, "fig4_ablations")


def fig_overopt(S):
    fig, axes = plt.subplots(1, 5, figsize=(7, 1.9), sharey=True)
    for j, sh in enumerate(E.SHAPES):
        ax = axes[j]
        for k, n in enumerate(OVEROPT_N):
            pts = S["overopt"][sh][str(n)]["points"]
            _band(ax, [p["lambda"] for p in pts], pts, RAMP[k], "-", f"N={n}")
        ax.set_xscale("log"), ax.set_title(sh, fontsize=8), ax.set_xlabel("pressure λ")
    axes[0].set_ylabel("true normalized return")
    axes[-1].legend(fontsize=6, loc="lower right")
    _save(fig, "fig5_overopt")


def fig_shaping(S):
    fig, ax = plt.subplots(figsize=(4.6, 2.3))
    for tr in SHAPING_TRAIN:
        pts = S["shaping"][tr]["curve"]
        _band(ax, [p["episode"] for p in pts], pts, COLOR[tr], DASH[tr], f"trained on {tr}")
    for line in ax.get_lines():
        line.set_marker("")
    ax.set_xlabel("Q-learning episodes"), ax.set_ylabel("regret on the sparse task")
    ax.axhline(S["recovered_threshold"], color=MUTED, lw=0.8, ls="--")
    ax.legend(fontsize=7)
    _save(fig, "fig6_shaping")


def make_all():
    S = json.loads((RESULTS / "summary.json").read_text())
    site_js = (ROOT / "site" / "data.js").read_text()
    site = json.loads(site_js[site_js.index("=") + 1:].strip().rstrip(";"))
    fig_shapes(S, site)
    fig_recovery(S)
    fig_metric(S)
    fig_ablations(S)
    fig_overopt(S)
    fig_shaping(S)


if __name__ == "__main__":
    make_all()
