#!/usr/bin/env python3
"""Check camera-ready input provenance, supplemental calculations and roundings.

No API calls. Does not validate cached autonomy or gECS scores, which are
excluded from the camera-ready evidence. The original 109 submitted-version
checks remain available separately in scripts/verify_results.py.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'analysis'
OUT = ROOT / 'results' / 'trace_out'


def main():
    subprocess.run([sys.executable, str(ANALYSIS / 'extract_inputs.py'), '--check'], check=True)
    with tempfile.TemporaryDirectory(prefix='trace-camera-ready-') as tmp:
        work = Path(tmp)
        shutil.copytree(ANALYSIS, work / 'analysis')
        subprocess.run([sys.executable, str(work / 'analysis' / 'recompute.py')],
                       check=True, stdout=subprocess.DEVNULL)
        expected = json.loads((ANALYSIS / 'paired_checks.json').read_text())
        actual = json.loads((work / 'analysis' / 'paired_checks.json').read_text())
        if actual.keys() != expected.keys():
            raise AssertionError('Paired-check names differ')
        for name, values in expected.items():
            if actual[name].keys() != values.keys():
                raise AssertionError(f'Paired-check fields differ: {name}')
            for field, value in values.items():
                np.testing.assert_allclose(actual[name][field], value, rtol=1e-12, atol=1e-12)
        for name in ('per_run_supplement.csv', 'supplementary_summary.csv'):
            pd.testing.assert_frame_equal(pd.read_csv(ANALYSIS / name),
                                          pd.read_csv(work / 'analysis' / name),
                                          check_exact=False, rtol=1e-12, atol=1e-12)
        if len(list((work / 'figures').glob('*.png'))) != 3:
            raise AssertionError('Expected three corrected figures')
    print('Verified paired checks, per-agent summaries and generation of three figures.')

    e1 = pd.read_csv(OUT / 'exp1_summary.csv')
    e3 = pd.read_csv(OUT / 'exp3_informed_sweep.csv')
    e6 = pd.read_csv(OUT / 'exp6_multimodel.csv')
    e8 = pd.read_csv(OUT / 'exp8_swarm.csv')
    e9 = pd.read_csv(OUT / 'exp9_byzantine.csv')
    values = [
        ('Experiment 1 unconstrained divergence', e1.loc[e1['mode'] == 'unconstrained', 'divergence'].mean(), '0.230'),
        ('Experiment 8 unconstrained capture', e8.loc[e8['mode'] == 'unconstrained', 'capture'].mean(), '0.286'),
        ('Experiment 8 unconstrained safety violations', e8.loc[e8['mode'] == 'unconstrained', 'safety_violation'].mean(), '0.014'),
        ('Experiment 6 Qwen unconstrained accuracy', e6.loc[e6.model.str.contains('Qwen') & (e6['mode'] == 'unconstrained'), 'accuracy_mean'].mean(), '0.936'),
        ('Experiment 3 governed accuracy at rho=0.25', e3.loc[np.isclose(e3.informed_frac, .25) & (e3['mode'] == 'governed'), 'accuracy'].mean(), '0.978'),
        ('Experiment 9 governed accuracy at beta=0', e9.loc[np.isclose(e9.byz_frac, 0) & e9.governed, 'obj_acc'].mean(), '0.903'),
    ]
    for label, value, expected in values:
        if f'{value:.3f}' != expected:
            raise AssertionError(f'{label}: {value:.3f} != {expected}')
    print('Verified the six corrected three-decimal table entries.')
    print('Camera-ready checks passed. Historical autonomy comparisons are excluded.')


if __name__ == '__main__':
    main()
