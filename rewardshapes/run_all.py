"""One command regenerates everything: experiments -> summary -> figures -> site data -> paper.

    uv run python -m rewardshapes.run_all            # full run (seeds 0-9)
    uv run python -m rewardshapes.run_all --skip-experiments   # re-analyse existing results
"""
import argparse
import logging
import shutil
import subprocess

from . import analysis, experiments, figures

log = logging.getLogger("rewardshapes")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("--skip-experiments", action="store_true")
    p.add_argument("--procs", type=int, default=8)
    a = p.parse_args()
    if not a.skip_experiments:
        experiments.run(pilot=False, procs=a.procs)
    analysis.write_all()
    figures.make_all()
    log.info("figures -> %s", figures.FIG)
    paper = analysis.ROOT / "paper"
    if shutil.which("tectonic"):
        subprocess.run(["tectonic", "-X", "compile", "main.tex"], cwd=paper, check=True)
        shutil.copy(paper / "main.pdf", analysis.ROOT / "site" / "reward-shapes.pdf")
        log.info("paper -> %s", paper / "main.pdf")
    else:
        log.warning("tectonic not found; skipped the PDF build")


if __name__ == "__main__":
    main()
