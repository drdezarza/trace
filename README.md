# TRACE — Truth-Referenced Auditable Cooperative Epistemics

**“Constitutional Filtering of Manipulative Influence in Grounded LLM Multi-Agent Systems.”**

TRACE evaluates collective truth-tracking against stipulated true values.
Agents maintain natural-language beliefs, an LLM compiler emits structured
influence policies, and a constitutional layer filters those policies.
The archive contains outputs covering 706 simulation runs, the experiment
notebook, and reproducible camera-ready supplemental analyses.

## Headline results and scope

| Exp | Finding | Interpretation |
|---|---|---|
| 1 | Accuracy **+0.033** (*p*=0.023); terminal drift **−0.070** (*p*=0.017) | The governed arm rejected all 48 proposals, so this is operationally a block-all control. |
| 2 | The `FACTUAL` probe passes **48/48** proposals and reduces accuracy (*p*=0.030). | It relabels the false anchor; the number, theme and intensity match the unconstrained attack, and agents do not see the label. Similar outcomes follow from this construction. |
| 3 | Accuracy benefit **+0.126** at ρ=0.10; smaller at high informed fractions. | At ρ=0.55, the primary unpaired test has *p*=0.053; a paired sensitivity test has *p*=0.021. This is not a sharp 40% threshold. |
| 4 | Benefits reach **+0.085**; small negative gaps occur at ρ=0.40 and 0.55. | Attack strength zero still retains 40% intensity. The negative gaps do not establish a corrective-message mechanism. |
| 6 | Accuracy benefit positive for **4/4** models. | Individually significant for Llama only; pooled *p*=0.125. |
| 7 | **13/13** language conditions positive; pooled **+0.075** (*p*=0.0002). | Question stems are translated and rationales requested in the target language; system instructions and deployed messages remain English. This is not a fully multilingual evaluation. |
| 8 | Mission success **0.31 → 0.69**. | A 2D simulation; safety violations increase from **0.014 to 0.058**. |
| 9 | Honest-drone accuracy remains near **0.90** in the governed arm. | Idealised suppression uses simulator-known malicious commands. This is not a test of Byzantine detection or resistance to relabelling. |

The label-based gate is useful against the tested explicitly non-factual
attacks but insufficient for grounded epistemic protection. Experiment 2
exposes reliance on a self-declared label; it does not demonstrate truthful
selective evidence or establish that constitutional filtering is necessary.

## Repository layout

```
trace_nebius_v16.ipynb          Original experiment notebook
requirements.txt
analysis/
  extract_inputs.py           Rebuild/check inputs from archived Experiment 1 logs
  recompute.py                Reproduce per-agent summaries, paired tests and figures
  inputs/                     Four archived summary CSVs and 720 agent endpoints
  paired_checks.json          Camera-ready paired sensitivity results
  per_run_supplement.csv
  supplementary_summary.csv
  README.md                   Definitions and provenance
figures/                      Three corrected camera-ready figures
scripts/
  verify_camera_ready.py      Check new analysis, provenance and corrected roundings
  verify_results.py           Historical 109-check submitted-version audit
  generate_results_doc.py     Generate current result tables and scope notes
  export_latex_tables.py      Export result tables with autonomy excluded
docs/
  EXPERIMENTS.md              Designs and limitations
  RESULTS.md                  Tables generated from the saved CSVs
results/trace_out/            Original summaries, statistics and figures
  exp1/                      36 retained per-run logs
  exp2/                      24 retained per-run logs
```

Each retained run has `config.json`, `agents.csv`, `beliefs.jsonl`,
`timeseries.csv`, `policy_log.csv` and `judgments.csv`. Only Experiments 1–2
retain detailed logs; the later governed arms use the same filtering setup,
but their rejection rates cannot be separately verified from retained logs.

## Reproduce and verify (no API key)

```sh
pip install -r requirements.txt
python scripts/verify_camera_ready.py
python analysis/recompute.py
python scripts/verify_results.py
```

The camera-ready verifier checks the 720 extracted endpoints against the
original trails, all four copied CSVs, paired and per-agent outputs, generation
of the three revised figures, and the six corrected table roundings. See
[`analysis/README.md`](analysis/README.md) for extraction and metric definitions.

The final command is the **historical submitted-version audit**. Its 109 checks
include autonomy values and original roundings that are no longer camera-ready
evidence. Passing that audit confirms archival numerical consistency; it does
not validate the excluded autonomy comparisons or the original interpretations.
Use `--verbose` to inspect its computed values. All four commands run offline.

The supplemental paired results are accuracy +0.03248 (*p*=0.00342), drift
−0.06983 (*p*=0.000488), and movement from the first logged update −0.05309
(*p*=0.000488), governed minus unconstrained across 12 matched item–seed cells.
Mean per-agent normalized absolute error is 0.07927 versus 0.10215; 1.7% versus
2.1% of agents end closer to the anchor than to truth. Pairing does not remove
the limitations of a four-item bank and shared seed structure.

## Experimental design

706 runs: 580 belief-space and 126 simulated swarm runs.

| Exp | Grid | Runs |
|---|---|---|
| 1 | 3 modes × 4 items × 3 seeds | 36 |
| 2 | 2 conditions × 4 items × 3 seeds | 24 |
| 3 | 5 informed fractions × 2 modes × 4 items × 3 seeds | 120 |
| 4 | 4 attack strengths × 4 informed fractions × 2 modes × 2 items × 2 seeds | 128 |
| 5 | Statistical analysis of saved runs | 0 |
| 6 | 4 models × 2 modes × 2 items × 4 seeds | 64 |
| 7 | 13 languages × 2 modes × 2 items × 4 seeds | 208 |
| 8 | 3 modes × 6 seeds; plus 4 informed fractions × 2 modes × 6 seeds | 66 |
| 9 | 5 Byzantine fractions × 2 filter settings × 6 seeds | 60 |

The belief engine uses 20 agents, a Barabási–Albert graph (*m*=3), 15 steps,
and a policy compiled every third step targeting 40% of agents. Resistance has
mean 0.35 and standard deviation 0.12, clipped to [0.05, 0.9]. The swarm has
14 drones, 26 steps, deterministic Reynolds motion in a 100×100 plane and a
dynamic geometric communication graph of radius 32.

`governed` rejects `MISLEADING`/`EXAGGERATED` claims and `FEAR` themes and caps
intensity at 0.80. `naive` clips only `MISLEADING` policies above 0.85;
`unconstrained` accepts all policies. The principal backbone is
`meta-llama/Llama-3.3-70B-Instruct`, temperature 0.3, via Nebius AI Studio.
Experiment 6 also covers DeepSeek-V3.2, Qwen3-235B-A22B-Instruct-2507 and
Hermes-4-70B. See [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) and
[`docs/RESULTS.md`](docs/RESULTS.md).

## Limitations and archival caveats

- **Autonomy and gECS are excluded from the camera-ready evidence.** Judge
  cache keys (`jd|qid|t|idx|seed`, and `sj|t|i|seed` for the swarm) omit both
  condition and rationale. Scores can therefore be reused across different
  inputs. No deployed policy also defaults autonomy to 1.0. Corrected caching
  and independent rationale-faithfulness validation are required; the saved
  notebook retains the original implementation for provenance. The judge does
  not control belief updates.
- **No benign-coordinator control.** Experiment 1 cannot establish an advantage
  over blocking every coordinator message. Benign/mixed-message controls and
  classical robust-aggregation comparisons remain future work.
- **Limited tasks.** Four synthetic numerical items in one Gaussian-signal
  estimation family do not support task-level generalization. Susceptibility
  is a modelling assumption, not calibrated human persuasion behavior.
- **Languages.** The low-resource penalty was not observed under translated
  stems with English surrounding instructions/messages. Translation quality
  also varies; the Basque stem renders “two named cities” as “three”.
- **Swarm.** Motion is simulated. The explanation that concentration near the
  objective raises collision risk has not been separately tested. Experiment 9
  suppresses the identified malicious command while compromised beliefs remain
  in the neighbour mean. External broadcasts target 50% of drones, whereas the
  insider comparison uses β=0.20; the comparison is not magnitude-matched and
  cannot isolate the effect of authority.
- **Adversary and sampling.** The compiler is non-adaptive. Seeded initialization
  and synchronous updates do not make stochastic LLM responses reproducible
  bit-for-bit or establish stability across new runs.

## Re-run the original notebook

Set `NEBIUS_API_KEY` as an environment variable or Colab secret, then open
`trace_nebius_v16.ipynb`. Without a key it uses a deterministic mock backend,
which does **not** reproduce the reported experimental data. A full cold run
requires substantial API usage. Responses are cached, with the judge-key
limitation above; correct those keys before any new autonomy evaluation.
Experiments 5, 8d and 9c only read saved data.

`Llama-3.1-8B-Instruct` was skipped after a provider HTTP 404. The notebook
excludes model cells with more than 20% fallback calls. Its sanitizer clamps
agent estimates to a plausible band and logs the flagged fraction; in
Experiment 1 this was 0.01% of updates, all on `count_k`.
