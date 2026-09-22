# Camera-ready supplemental analysis

These files reproduce the paired and per-agent checks added to the accepted
paper. They use saved data; no new simulations or API calls are required.

From the repository root:

```sh
python analysis/extract_inputs.py --check
python scripts/verify_camera_ready.py
python analysis/recompute.py
```

`extract_inputs.py` reconstructs `inputs/agent_endpoints.csv` from Experiment 1
`config.json`, `agents.csv` and `beliefs.jsonl`, and copies the four input summary
CSVs from `results/trace_out/`. Omit `--check` to regenerate those inputs.
There are 720 agent rows: 36 runs × 20 agents. All three conditions are retained;
the paired comparisons use governed versus unconstrained.

`recompute.py` writes `per_run_supplement.csv`, `supplementary_summary.csv`,
`paired_checks.json` and three corrected images in the repository's `figures/`.
The input CSVs retain historical columns; autonomy and gECS are excluded from
the camera-ready comparisons and images because the judge cache omits changing
inputs. The original images in `results/trace_out/` are retained as archival
outputs, including their excluded audit panels.

Per-agent error is absolute error divided by the absolute truth. Anchor
proximity is the fraction of agents strictly closer to the false anchor than
to the truth. Movement is `(final_value - first_logged_value)/(anchor - truth)`;
the baseline is the first logged update at `t=0`, not the pre-update signal.
Agent metrics are averaged within runs first. Two-sided Wilcoxon sensitivity
tests pair the 12 item × seed cells; these complement the original unpaired
tests and do not establish generalization beyond the four-item bank.

`verify_camera_ready.py` checks the bundled inputs against the raw archive,
recomputes the supplemental outputs in a temporary directory, and verifies the
six corrected three-decimal table entries. `scripts/verify_results.py` remains
an explicitly labelled historical audit of the submitted version.
