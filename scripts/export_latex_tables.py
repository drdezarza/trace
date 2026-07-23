#!/usr/bin/env python3
"""
export_latex_tables.py -- emit the manuscript's result tables as LaTeX
(booktabs) directly from results/trace_out/, so the paper and the artifact
cannot disagree.

    python scripts/export_latex_tables.py            # all tables to stdout
    python scripts/export_latex_tables.py --table exp1
    python scripts/export_latex_tables.py --out tables/     # one .tex per table
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "trace_out"


def _read(name):
    return pd.read_csv(OUT / name)


def _wrap(body, caption, label, colspec, header):
    return (
        "\\begin{table}[t]\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\small\n"
        f"\\begin{{tabular}}{{{colspec}}}\n"
        "\\toprule\n"
        f"{header} \\\\\n"
        "\\midrule\n"
        f"{body}"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n"
    )


def exp1():
    g = _read("exp1_summary.csv").groupby("mode")
    rows = ""
    for m, acc in [("governed", "0/48"), ("naive", "48/48"), ("unconstrained", "48/48")]:
        dag = "$^{\\dagger}$" if m == "governed" else ""
        rows += (f"\\textsc{{{m}}} & {g['accuracy'].mean()[m]:.3f} & "
                 f"{g['manip_drift'].mean()[m]:.3f} & {g['divergence'].mean()[m]:.3f} & "
                 f"{g['measured_autonomy'].mean()[m]:.3f}{dag} & "
                 f"{g['fairness'].mean()[m]:.3f} & {acc} \\\\\n")
    return _wrap(rows,
                 "Experiment~1: grounded three-condition comparison ($n{=}12$ per mode). "
                 "$^{\\dagger}$ default value; no policy clears the gate, so no agent is audited.",
                 "tab:exp1", "lrrrrrr",
                 "mode & $A$ & $\\delta$ & $D$ & $\\alpha$ & $F$ & accept")


def exp2():
    g = _read("exp2_gap.csv").groupby("condition")
    rows = ""
    for c, name in [("blocked_misleading", "blocked \\textsf{MISLEADING}"),
                    ("factual_probe", "\\textsf{FACTUAL} probe")]:
        rows += (f"{name} & {g['policy_passed_gate'].mean()[c]:.2f} & "
                 f"{g['accuracy'].mean()[c]:.3f} & {g['manip_drift'].mean()[c]:+.3f} & "
                 f"{g['divergence'].mean()[c]:.3f} \\\\\n")
    return _wrap(rows,
                 "Experiment~2: the integrity-gate gap under an identical governed "
                 "constitution ($n{=}12$ per condition).",
                 "tab:exp2", "lrrrr",
                 "condition & gate pass & $A$ & $\\delta$ & $D$")


def exp3():
    d = _read("exp3_informed_sweep.csv")
    rows = ""
    for f in sorted(d.informed_frac.unique()):
        s = d[d.informed_frac == f]
        gv, uv = s[s["mode"] == "governed"], s[s["mode"] == "unconstrained"]
        rows += (f"{f:.2f} & {gv['accuracy'].mean():.3f} & {uv['accuracy'].mean():.3f} & "
                 f"{gv['manip_drift'].mean():.3f} & {uv['manip_drift'].mean():.3f} \\\\\n")
    return _wrap(rows,
                 "Experiment~3: accuracy and drift vs.\\ informed-minority size "
                 "($n{=}12$ per cell).",
                 "tab:exp3", "lrrrr",
                 "$\\rho$ & $A$ gov & $A$ unc & $\\delta$ gov & $\\delta$ unc")


def exp5():
    rows = ""
    for _, x in _read("exp5_significance.csv").iterrows():
        rows += (f"{x.comparison} & {x.mean_diff:+.4f} & {x.ci_lo:+.4f} & {x.ci_hi:+.4f} & "
                 f"{x.p:.4f} & {'yes' if x.significant else 'no'} \\\\\n")
    return _wrap(rows,
                 "Experiment~5: significance of the core claims. Bootstrap CI on the mean "
                 "difference (10k resamples), two-sided Mann--Whitney.",
                 "tab:exp5", "lrrrrl",
                 "comparison & diff & CI$_{\\text{lo}}$ & CI$_{\\text{hi}}$ & $p$ & sig.")


def exp7():
    a = _read("exp7_stats_accuracy.csv")
    dr = _read("exp7_stats_drift.csv")
    ml = _read("exp7_multilingual.csv")
    rows = ""
    for _, x in a.sort_values("mean_diff", ascending=False).iterrows():
        base = ml[(ml.lang == x.lang) & (ml["mode"] == "unconstrained")]["accuracy_mean"].mean()
        dx = dr[dr.lang == x.lang].iloc[0]
        star = "${}^{*}$" if x.low_resource else ""
        tick_a = "\\checkmark" if x.significant else ""
        tick_d = "\\checkmark" if dx.significant else ""
        rows += (f"{x.lang}{star} & \\texttt{{{x.code}}} & {base:.3f} & {x.mean_diff:+.3f} & "
                 f"{tick_a} & {dx.mean_diff:+.3f} & {tick_d} \\\\\n")
    return _wrap(rows,
                 "Experiment~7: per-language governance benefit ($n{=}8$ per cell). "
                 "${}^{*}$ marks \\emph{a priori} low-resource languages.",
                 "tab:exp7", "llrrlrl",
                 "language & code & $A_{\\text{unc}}$ & $\\Delta A$ & sig & $\\Delta\\delta$ & sig")


def exp8():
    g = _read("exp8_swarm.csv").groupby("mode")
    rows = ""
    for m in ["governed", "naive", "unconstrained"]:
        rows += (f"\\textsc{{{m}}} & {g['obj_acc'].mean()[m]:.3f} & "
                 f"{g['capture'].mean()[m]:+.3f} & {g['cohesion'].mean()[m]:.3f} & "
                 f"{g['mission_success'].mean()[m]:.3f} & "
                 f"{g['safety_violation'].mean()[m]:.3f} \\\\\n")
    return _wrap(rows,
                 "Experiment~8: swarm outcomes under command-channel spoofing "
                 "($n{=}6$ seeds per mode).",
                 "tab:exp8", "lrrrrr",
                 "mode & obj.\\ acc. & capture & cohesion & mission & viol.")


def exp9():
    d = _read("exp9_byzantine.csv")
    rows = ""
    for _, x in _read("exp9_significance.csv").iterrows():
        sub = d[d.byz_frac == x.byz_frac]
        rows += (f"{x.byz_frac:.1f} & {sub[~sub.governed]['obj_acc'].mean():.3f} & "
                 f"{sub[sub.governed]['obj_acc'].mean():.3f} & {x.mean_diff:+.4f} & "
                 f"{x.p:.4f} & {'yes' if x.significant else 'no'} \\\\\n")
    return _wrap(rows,
                 "Experiment~9: honest-drone objective accuracy vs.\\ Byzantine fraction "
                 "($n{=}6$ seeds per cell).",
                 "tab:exp9", "lrrrrl",
                 "$\\beta$ & ungov. & gov. & diff & $p$ & sig.")


TABLES = {"exp1": exp1, "exp2": exp2, "exp3": exp3, "exp5": exp5,
          "exp7": exp7, "exp8": exp8, "exp9": exp9}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table", choices=sorted(TABLES), help="emit one table only")
    ap.add_argument("--out", type=Path, help="write one .tex file per table into this directory")
    args = ap.parse_args()

    names = [args.table] if args.table else sorted(TABLES)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
    for n in names:
        tex = TABLES[n]()
        if args.out:
            (args.out / f"{n}.tex").write_text(tex)
            print(f"wrote {args.out / f'{n}.tex'}")
        else:
            print(f"% ---- {n} ----")
            print(tex)


if __name__ == "__main__":
    main()
