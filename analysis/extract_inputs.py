"""Extract camera-ready inputs from the archived outputs; no model calls.

Run from any directory: python analysis/extract_inputs.py [--check]
--check verifies the bundled inputs without overwriting them.
"""
from pathlib import Path
import argparse
import json
import shutil
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results' / 'trace_out'
INPUTS = HERE / 'inputs'
SUMMARIES = ('exp1_summary.csv', 'exp3_informed_sweep.csv',
             'exp5_significance.csv', 'exp8_significance.csv')
KEYS = ['mode', 'qid', 'seed', 'idx']


def endpoints():
    rows = []
    directories = sorted((OUT / 'exp1').glob('*/config.json'))
    if len(directories) != 36:
        raise ValueError(f'Expected 36 Experiment 1 runs, found {len(directories)}')
    for config_path in directories:
        data = json.loads(config_path.read_text())
        config, item = data['config'], data['item']
        run = config_path.parent
        agents = pd.read_csv(run / 'agents.csv')
        beliefs = pd.read_json(run / 'beliefs.jsonl', lines=True)
        first = beliefs[beliefs.t == 0].set_index('idx')
        last = beliefs[beliefs.t == beliefs.t.max()].set_index('idx')
        if len(agents) != 20 or len(first) != 20 or len(last) != 20:
            raise ValueError(f'Incomplete agent trail: {run.name}')
        for a in agents.itertuples(index=False):
            if abs(float(last.loc[a.idx, 'value']) - float(a.value)) > 1e-10:
                raise ValueError(f'Final state/trail mismatch: {run.name}, agent {a.idx}')
            rows.append(dict(mode=config['governance_mode'], qid=item['qid'],
                             seed=config['seed'], idx=a.idx, truth=item['truth'],
                             anchor=item['false_anchor'], initial_signal=a.signal,
                             first_logged_value=first.loc[a.idx, 'value'],
                             final_value=a.value))
    return pd.DataFrame(rows).sort_values(KEYS).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    fresh = endpoints()
    if args.check:
        saved = pd.read_csv(INPUTS / 'agent_endpoints.csv').sort_values(KEYS).reset_index(drop=True)
        pd.testing.assert_frame_equal(fresh, saved, check_dtype=False,
                                      check_exact=False, rtol=1e-12, atol=1e-12)
        for name in SUMMARIES:
            pd.testing.assert_frame_equal(pd.read_csv(OUT / name), pd.read_csv(INPUTS / name))
        print('Verified 720 agent endpoints and four archived summary inputs.')
    else:
        INPUTS.mkdir(parents=True, exist_ok=True)
        fresh.to_csv(INPUTS / 'agent_endpoints.csv', index=False)
        for name in SUMMARIES:
            shutil.copyfile(OUT / name, INPUTS / name)
        print('Extracted 720 agent endpoints and four archived summary inputs.')


if __name__ == '__main__':
    main()
