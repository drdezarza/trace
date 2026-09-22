#!/usr/bin/env python3
"""
verify_results.py -- historical numerical audit of the submitted version.

These 109 checks retain the submitted values, tolerances and autonomy rows.
Autonomy/gECS comparisons are excluded from the camera-ready evidence because
judge cache keys omit changing inputs. Passing this historical audit does not
validate those comparisons or the original scientific interpretations.
For camera-ready additions and corrected roundings, run:
    python scripts/verify_camera_ready.py

This is an independent audit path: it does NOT re-run the notebook and makes no
API calls. It reads only `results/trace_out/` and reimplements the notebook's
statistical machinery (seeded bootstrap, Mann-Whitney U, Cliff's delta,
Wilcoxon signed-rank) so that any discrepancy between the artifact and the
submitted manuscript is surfaced automatically.

Usage:
    python scripts/verify_results.py            # summary
    python scripts/verify_results.py --verbose  # show every computed value

Exit status is 0 if all checks pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "trace_out"

# ---------------------------------------------------------------------------
# Statistical machinery, identical to the notebook (same seeds, same defaults).
# ---------------------------------------------------------------------------


def bootstrap_ci(x, n_boot=10_000, ci=95, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    bs = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(axis=1)
    lo, hi = np.percentile(bs, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    return float(x.mean()), float(lo), float(hi)


def boot_diff_ci(a, b, n_boot=10_000, ci=95, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed)
    da = rng.choice(a, size=(n_boot, len(a)), replace=True).mean(axis=1)
    db = rng.choice(b, size=(n_boot, len(b)), replace=True).mean(axis=1)
    d = da - db
    lo, hi = np.percentile(d, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    return float(a.mean() - b.mean()), float(lo), float(hi)


def cliffs_delta(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return np.nan
    gt = sum((ai > b).sum() for ai in a)
    lt = sum((ai < b).sum() for ai in a)
    return float((gt - lt) / (len(a) * len(b)))


def compare(a, b, label="A vs B"):
    a, b = np.asarray(a, float), np.asarray(b, float)
    diff, lo, hi = boot_diff_ci(a, b)
    try:
        U, p = mannwhitneyu(a, b, alternative="two-sided")
    except ValueError:
        U, p = (np.nan, np.nan)
    d = cliffs_delta(a, b)
    try:
        min_p = 2.0 / comb(len(a) + len(b), min(len(a), len(b)))
    except (ValueError, ZeroDivisionError):
        min_p = 1.0
    low_power = min_p > 0.05
    ci_excl = lo > 0 or hi < 0
    p_ok = (p < 0.05) if (p == p and not low_power) else None
    sig = ci_excl and (p_ok if p_ok is not None else True)
    return dict(label=label, diff=diff, lo=lo, hi=hi, U=U, p=p, delta=d,
                n_a=len(a), n_b=len(b), low_power=low_power, significant=bool(sig))


def pooled_paired_test(g, u, label="pooled"):
    g, u = np.asarray(g, float), np.asarray(u, float)
    benefit = g - u
    m, lo, hi = bootstrap_ci(benefit)
    try:
        W, p = wilcoxon(g, u)
    except ValueError:
        W, p = (np.nan, np.nan)
    return dict(label=label, n_cells=len(benefit), mean=m, lo=lo, hi=hi, W=W, p=p,
                frac_positive=float((benefit > 0).mean()),
                significant=bool((lo > 0 or hi < 0) and p == p and p < 0.05))


# ---------------------------------------------------------------------------
# Check harness
# ---------------------------------------------------------------------------

CHECKS: list[tuple[str, bool, str]] = []


def check(name, got, expected, tol=5e-4, fmt="{:.4f}"):
    ok = (abs(float(got) - float(expected)) <= tol) if expected is not None else True
    CHECKS.append((name, ok, f"got {fmt.format(got)}  expected {fmt.format(expected)}"))
    return ok


def check_bool(name, got, expected):
    ok = bool(got) == bool(expected)
    CHECKS.append((name, ok, f"got {got}  expected {expected}"))
    return ok


def csv(name):
    path = OUT / name
    if not path.exists():
        sys.exit(f"ERROR: missing {path}. Unpack results/trace_out/ first.")
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# Experiment 1 -- three-condition comparison
# ---------------------------------------------------------------------------


def exp1():
    d = csv("exp1_summary.csv")
    check("Exp1 n runs", len(d), 36, tol=0, fmt="{:.0f}")
    g = d.groupby("mode")
    for mode, acc, drift in [("governed", 0.9755, 0.0232),
                             ("naive", 0.9416, 0.0937),
                             ("unconstrained", 0.9430, 0.0930)]:
        check(f"Exp1 {mode} accuracy", g["accuracy"].mean()[mode], acc)
        check(f"Exp1 {mode} drift", g["manip_drift"].mean()[mode], drift)
    check("Exp1 governed autonomy (definitional 1.0)",
          g["measured_autonomy"].mean()["governed"], 1.0)
    check("Exp1 sanitize rate (%)", d["sanitize_rate"].mean() * 100, 0.0104,
          tol=5e-3, fmt="{:.4f}")

    # Caveat 1: the governed autonomy value of 1.0 is a DEFAULT, not a measurement.
    # No policy clears the gate, so no agent is ever audited. Assert that directly
    # instead of letting the default pass silently.
    judged = {}
    for mode in ("governed", "naive", "unconstrained"):
        rows = 0
        for f in sorted((OUT / "exp1").glob(f"{mode}-*/judgments.csv")):
            try:
                rows += len(pd.read_csv(f))
            except pd.errors.EmptyDataError:
                pass
        judged[mode] = rows
    check("Exp1 governed judged updates (0 => autonomy is a default)",
          judged["governed"], 0, tol=0, fmt="{:.0f}")
    check("Exp1 naive judged updates", judged["naive"], 384, tol=0, fmt="{:.0f}")
    check("Exp1 unconstrained judged updates", judged["unconstrained"], 384,
          tol=0, fmt="{:.0f}")

    # every proposed policy is rejected under the governed constitution
    proposed = rejected = 0
    for f in sorted((OUT / "exp1").glob("governed-*/policy_log.csv")):
        pl = pd.read_csv(f)
        proposed += len(pl)
        rejected += int((~pl["accepted"]).sum())
        assert set(pl["reject_reason"]) <= {"claims"}, f
    check("Exp1 governed policies proposed", proposed, 48, tol=0, fmt="{:.0f}")
    check("Exp1 governed policies rejected", rejected, 48, tol=0, fmt="{:.0f}")


# ---------------------------------------------------------------------------
# Experiment 2 -- the integrity-gate gap
# ---------------------------------------------------------------------------


def exp2():
    d = csv("exp2_gap.csv")
    g = d.groupby("condition")
    check("Exp2 probe gate-pass rate", g["policy_passed_gate"].mean()["factual_probe"], 1.0)
    check("Exp2 blocked gate-pass rate", g["policy_passed_gate"].mean()["blocked_misleading"], 0.0)
    check("Exp2 probe accuracy", g["accuracy"].mean()["factual_probe"], 0.9430)
    check("Exp2 probe drift", g["manip_drift"].mean()["factual_probe"], 0.0916)
    check("Exp2 blocked accuracy", g["accuracy"].mean()["blocked_misleading"], 0.9755)

    # every proposed policy under the probe carries claims=FACTUAL and passes
    passed = accepted = 0
    for f in sorted((OUT / "exp2").glob("factual_probe-*/policy_log.csv")):
        pl = pd.read_csv(f)
        passed += len(pl)
        accepted += int(pl["accepted"].sum())
        assert set(pl["proposed_claims"]) <= {"FACTUAL"}, f
    check("Exp2 probe policies proposed", passed, 48, tol=0, fmt="{:.0f}")
    check("Exp2 probe policies accepted", accepted, 48, tol=0, fmt="{:.0f}")


# ---------------------------------------------------------------------------
# Experiment 5 -- significance of the core claims
# ---------------------------------------------------------------------------


def exp5():
    e1 = csv("exp1_summary.csv")
    g = e1[e1["mode"] == "governed"]
    u = e1[e1["mode"] == "unconstrained"]

    r = compare(g["accuracy"].values, u["accuracy"].values)
    check("Exp5 accuracy gap", r["diff"], 0.0325)
    check("Exp5 accuracy CI lo", r["lo"], 0.0094)
    check("Exp5 accuracy CI hi", r["hi"], 0.0541)
    check("Exp5 accuracy p", r["p"], 0.0226)
    check("Exp5 accuracy Cliff delta", r["delta"], 0.556, tol=1e-3)
    check_bool("Exp5 accuracy significant", r["significant"], True)

    r = compare(g["manip_drift"].values, u["manip_drift"].values)
    check("Exp5 drift gap", r["diff"], -0.0698)
    check("Exp5 drift p", r["p"], 0.0166)

    r = compare(g["measured_autonomy"].values, u["measured_autonomy"].values)
    check("Exp5 autonomy gap", r["diff"], 0.3125)
    check("Exp5 autonomy Cliff delta", r["delta"], 1.0)

    e2 = csv("exp2_gap.csv")
    r = compare(e2[e2.condition == "factual_probe"]["accuracy"].values,
                e2[e2.condition == "blocked_misleading"]["accuracy"].values)
    check("Exp5 probe-blocked gap", r["diff"], -0.0325)
    check("Exp5 probe-blocked p", r["p"], 0.0304)
    check_bool("Exp5 probe-blocked significant", r["significant"], True)


# ---------------------------------------------------------------------------
# Experiment 3 -- informed-minority threshold
# ---------------------------------------------------------------------------


def exp3():
    d = csv("exp3_informed_sweep.csv")
    check("Exp3 n runs", len(d), 120, tol=0, fmt="{:.0f}")
    expected = {0.10: (0.9666, 0.8408, True),
                0.25: (0.9785, 0.8953, True),
                0.40: (0.9749, 0.9328, True),
                0.55: (0.9779, 0.9586, False),
                0.70: (0.9779, 0.9771, False)}
    for rho, (ga, ua, sig) in expected.items():
        sub = d[d.informed_frac == rho]
        gv = sub[sub["mode"] == "governed"]["accuracy"].values
        uv = sub[sub["mode"] == "unconstrained"]["accuracy"].values
        check(f"Exp3 rho={rho:.2f} governed acc", gv.mean(), ga)
        check(f"Exp3 rho={rho:.2f} unconstrained acc", uv.mean(), ua)
        check_bool(f"Exp3 rho={rho:.2f} significant", compare(gv, uv)["significant"], sig)


# ---------------------------------------------------------------------------
# Experiment 4 -- sensitivity surface
# ---------------------------------------------------------------------------


def exp4():
    d = csv("exp4_sensitivity.csv")
    check("Exp4 grid cells", len(d), 16, tol=0, fmt="{:.0f}")
    top = d[(d.attack_strength == 1.0) & (d.informed_frac == 0.10)].iloc[0]
    check("Exp4 max accuracy benefit (a=1.0, rho=0.10)", top["acc_gap"], 0.0849)
    check("Exp4 max drift benefit (a=1.0, rho=0.10)", top["drift_gap"], 0.1907)
    neg = d[d.informed_frac == 0.55]["acc_gap"]
    check_bool("Exp4 accuracy benefit negative at rho=0.55 (all a)", bool((neg < 0).all()), True)
    check_bool("Exp4 drift benefit positive everywhere",
               bool((d["drift_gap"] > 0).all()), True)


# ---------------------------------------------------------------------------
# Experiment 6 -- across models
# ---------------------------------------------------------------------------


def exp6():
    d = csv("exp6_multimodel.csv")
    check("Exp6 models that ran", d["model"].nunique(), 4, tol=0, fmt="{:.0f}")
    check("Exp6 n runs", len(d), 64, tol=0, fmt="{:.0f}")

    benefits = {}
    for m in d["model"].unique():
        s = d[d.model == m]
        ga = s[s["mode"] == "governed"]["accuracy_mean"].values
        ua = s[s["mode"] == "unconstrained"]["accuracy_mean"].values
        benefits[m] = (ga.mean() - ua.mean(), compare(ga, ua)["p"])
    check("Exp6 Llama-3.3-70B benefit", benefits["Llama-3.3-70B-Instruct"][0], 0.0866)
    check("Exp6 Llama-3.3-70B p", benefits["Llama-3.3-70B-Instruct"][1], 0.0104)
    check_bool("Exp6 all four benefits positive",
               all(b > 0 for b, _ in benefits.values()), True)

    pg = [d[(d.model == m) & (d["mode"] == "governed")]["accuracy_mean"].mean()
          for m in d["model"].unique()]
    pu = [d[(d.model == m) & (d["mode"] == "unconstrained")]["accuracy_mean"].mean()
          for m in d["model"].unique()]
    pool = pooled_paired_test(pg, pu)
    check("Exp6 pooled benefit", pool["mean"], 0.0402)
    check("Exp6 pooled p (n=4 floor)", pool["p"], 0.125)
    check_bool("Exp6 pooled NOT significant", pool["significant"], False)

    # vulnerability correlation reported in the text as a direction only
    base = [d[(d.model == m) & (d["mode"] == "unconstrained")]["accuracy_mean"].mean()
            for m in d["model"].unique()]
    ben = [g - u for g, u in zip(pg, pu)]
    check("Exp6 vulnerability correlation r", np.corrcoef(base, ben)[0, 1], -0.778, tol=2e-3)


# ---------------------------------------------------------------------------
# Experiment 7 -- multilingual
# ---------------------------------------------------------------------------


def exp7():
    d = csv("exp7_multilingual.csv")
    a = csv("exp7_stats_accuracy.csv")
    check("Exp7 languages", d["lang"].nunique(), 13, tol=0, fmt="{:.0f}")
    check("Exp7 n runs", len(d), 208, tol=0, fmt="{:.0f}")
    check_bool("Exp7 benefit positive in 13/13", bool((a["mean_diff"] > 0).all()), True)

    langs = list(a["lang"])
    pg = [d[(d.lang == l) & (d["mode"] == "governed")]["accuracy_mean"].mean() for l in langs]
    pu = [d[(d.lang == l) & (d["mode"] == "unconstrained")]["accuracy_mean"].mean() for l in langs]
    pool = pooled_paired_test(pg, pu)
    check("Exp7 pooled accuracy benefit", pool["mean"], 0.0748)
    check("Exp7 pooled p", pool["p"], 0.0002, tol=1e-4)
    check_bool("Exp7 pooled significant", pool["significant"], True)

    lr = a[a.low_resource]["mean_diff"].mean()
    hr = a[~a.low_resource]["mean_diff"].mean()
    check("Exp7 low-resource benefit", lr, 0.0770, tol=1e-3)
    check("Exp7 high-resource benefit", hr, 0.0742, tol=1e-3)
    check_bool("Exp7 NO low-resource penalty (lr >= hr)", bool(lr >= hr), True)


# ---------------------------------------------------------------------------
# Experiment 8 -- embodied swarm
# ---------------------------------------------------------------------------


def exp8():
    d = csv("exp8_swarm.csv")
    check("Exp8 n runs", len(d), 18, tol=0, fmt="{:.0f}")
    g = d[d["mode"] == "governed"]
    u = d[d["mode"] == "unconstrained"]

    r = compare(g["obj_acc"].values, u["obj_acc"].values)
    check("Exp8 objective accuracy benefit", r["diff"], 0.1013)
    check("Exp8 objective accuracy p", r["p"], 0.0087)
    r = compare(u["capture"].values, g["capture"].values)
    check("Exp8 capture reduction", r["diff"], 0.1707)
    r = compare(g["mission_success"].values, u["mission_success"].values)
    check("Exp8 mission success benefit", r["diff"], 0.3810)
    check("Exp8 mission success governed", g["mission_success"].mean(), 0.6905)
    check("Exp8 mission success unconstrained", u["mission_success"].mean(), 0.3095)
    r = compare(g["cohesion"].values, u["cohesion"].values)
    check_bool("Exp8 cohesion is a measured null", r["significant"], False)
    check_bool("Exp8 safety violations HIGHER under governance",
               bool(g["safety_violation"].mean() > u["safety_violation"].mean()), True)

    # Exp8c -- embodied informed-minority sweep
    s = csv("exp8_informed_sweep.csv")
    check("Exp8c n runs", len(s), 48, tol=0, fmt="{:.0f}")
    expected = {0.10: 0.2748, 0.25: 0.1787, 0.40: 0.1013, 0.55: 0.0983}
    for rho, diff in expected.items():
        sub = s[s.informed_frac == rho]
        r = compare(sub[sub["mode"] == "governed"]["obj_acc"].values,
                    sub[sub["mode"] == "unconstrained"]["obj_acc"].values)
        check(f"Exp8c rho={rho:.2f} accuracy benefit", r["diff"], diff, tol=1e-3)
        check_bool(f"Exp8c rho={rho:.2f} significant", r["significant"], True)

    # the rho=0.40 cell must reproduce the saved Exp8 significance file exactly
    saved = csv("exp8_significance.csv")
    saved_diff = float(saved[saved.metric == "obj_acc"]["mean_diff"].iloc[0])
    sub = s[s.informed_frac == 0.40]
    r = compare(sub[sub["mode"] == "governed"]["obj_acc"].values,
                sub[sub["mode"] == "unconstrained"]["obj_acc"].values)
    check("Exp8c rho=0.40 reproduces exp8_significance.csv", r["diff"], saved_diff, tol=1e-4)


# ---------------------------------------------------------------------------
# Experiment 9 -- Byzantine insiders
# ---------------------------------------------------------------------------


def exp9():
    d = csv("exp9_byzantine.csv")
    check("Exp9 n runs", len(d), 60, tol=0, fmt="{:.0f}")
    expected = {0.0: (0.0072, False), 0.1: (0.0562, False),
                0.2: (0.0691, True), 0.3: (0.0895, True), 0.4: (0.0719, True)}
    for beta, (diff, sig) in expected.items():
        sub = d[d.byz_frac == beta]
        r = compare(sub[sub.governed]["obj_acc"].values,
                    sub[~sub.governed]["obj_acc"].values)
        check(f"Exp9 beta={beta:.1f} benefit", r["diff"], diff, tol=1e-3)
        check_bool(f"Exp9 beta={beta:.1f} significant", r["significant"], sig)

    # external vs internal: ungoverned harm is larger for the command-channel spoof
    e8 = csv("exp8_swarm.csv")
    ext = e8[e8["mode"] == "unconstrained"]["obj_acc"].mean()
    internal = d[(d.byz_frac == 0.20) & (~d.governed)]["obj_acc"].mean()
    check("Exp9c external ungoverned accuracy", ext, 0.7972)
    check("Exp9c internal ungoverned accuracy", internal, 0.8366)
    check_bool("Exp9c external attack strictly more damaging", bool(ext < internal), True)


# ---------------------------------------------------------------------------
# Global accounting
# ---------------------------------------------------------------------------


def totals():
    belief = (len(csv("exp1_summary.csv")) + len(csv("exp2_gap.csv"))
              + len(csv("exp3_informed_sweep.csv")) + 128  # Exp4: 16 cells x 8 runs
              + len(csv("exp6_multimodel.csv")) + len(csv("exp7_multilingual.csv")))
    embodied = (len(csv("exp8_swarm.csv")) + len(csv("exp8_informed_sweep.csv"))
                + len(csv("exp9_byzantine.csv")))
    check("Total belief-space runs", belief, 580, tol=0, fmt="{:.0f}")
    check("Total embodied runs", embodied, 126, tol=0, fmt="{:.0f}")
    check("Total simulation runs", belief + embodied, 706, tol=0, fmt="{:.0f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="print every computed value, not just failures")
    args = ap.parse_args()

    print(f"TRACE submitted-version verification (historical)\nreading: {OUT}\n")
    print("Autonomy rows are archival only; use verify_camera_ready.py for the revised analysis.\n")
    for name, fn in [("Experiment 1", exp1), ("Experiment 2", exp2),
                     ("Experiment 5", exp5), ("Experiment 3", exp3),
                     ("Experiment 4", exp4), ("Experiment 6", exp6),
                     ("Experiment 7", exp7), ("Experiment 8", exp8),
                     ("Experiment 9", exp9), ("Run accounting", totals)]:
        before = len(CHECKS)
        fn()
        n = len(CHECKS) - before
        bad = sum(1 for _, ok, _ in CHECKS[before:] if not ok)
        status = "OK  " if bad == 0 else "FAIL"
        print(f"  [{status}] {name:<16} {n - bad}/{n} checks passed")

    failures = [(n, d) for n, ok, d in CHECKS if not ok]
    print()
    if args.verbose:
        for n, ok, d in CHECKS:
            print(f"  {'ok  ' if ok else 'FAIL'}  {n:<52} {d}")
        print()
    if failures:
        print(f"{len(failures)} of {len(CHECKS)} checks FAILED:\n")
        for n, d in failures:
            print(f"  - {n}: {d}")
        return 1
    print(f"All {len(CHECKS)} checks passed. "
          f"Historical submitted-version numerical checks reproduced; excluded autonomy is not validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
