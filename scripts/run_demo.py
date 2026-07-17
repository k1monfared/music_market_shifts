"""One entry point that reproduces the whole demonstration end to end.

Steps:
  1. Generate synthetic data          -> data/*.csv
  2. Run the analysis                  -> outputs/findings.json
  3. Render the figures                -> docs/images/*.png
  4. Render the PR-ready press report  -> outputs/press_report.md

Run:  python scripts/run_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import analysis, data_gen, figures, report
from src import config as C


def main() -> None:
    print("=" * 68)
    print("Music market shifts during the pandemic (synthetic demonstration)")
    print("=" * 68)

    print("\n[1/4] Generating synthetic data ...")
    written = data_gen.save_dataset(seed=C.SEED)
    for key, path in written.items():
        print(f"      {key:8s} -> {path}")

    print("\n[2/4] Running analysis (before/after + regression discontinuity) ...")
    findings = analysis.build_findings()
    json_path = analysis.save_findings(findings)
    print(f"      findings -> {json_path}")
    print(f"      headline: {findings['headline']}")

    print("\n[3/4] Generating figures ...")
    fig_paths = figures.generate_all(findings=findings)
    for key, path in fig_paths.items():
        print(f"      {key:14s} -> {path}")

    print("\n[4/4] Rendering press report ...")
    report_path = report.save_report(findings)
    print(f"      report -> {report_path}")

    # Also publish a slim findings copy next to the interactive dashboard so
    # docs/index.html can load it with a relative fetch.
    dash_json = analysis.save_findings(findings, path=C.IMAGES_DIR.parent / "findings.json")
    print(f"      dashboard data -> {dash_json}")

    # Quick sanity summary printed for the run log.
    commute = next(r for r in findings["context"] if r["context"] == "commute")
    focus = next(r for r in findings["context"] if r["context"] == "focus_work")
    rdd_c = findings["rdd"]["commute"]
    print("\nKey numbers:")
    print(f"      total streams change (pre -> lockdown): "
          f"{findings['totals']['pct_change']:+.1f}%")
    print(f"      commute listening change: {commute['pct_change']:+.1f}%")
    print(f"      focus/work listening change: {focus['pct_change']:+.1f}%")
    print(f"      commute RDD level break: {rdd_c['level_break']*100:+.1f} pts "
          f"(p={rdd_c['level_break_pvalue']:.3g})")
    print("\nDone. All outputs are synthetic and for demonstration only.")


if __name__ == "__main__":
    main()
