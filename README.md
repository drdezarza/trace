# TRACE — Truth-Referenced Auditable Cooperative Epistemics

**“Constitutional Filtering of Manipulative Influence in Grounded LLM Multi-Agent Systems.”**

![status](https://img.shields.io/badge/artifact-complete-brightgreen)
![runs](https://img.shields.io/badge/simulation%20runs-706-blue)
![checks](https://img.shields.io/badge/verification-109%2F109%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

Frameworks for governing LLM multi-agent systems are usually evaluated inside
closed simulations, where “cooperation” and “manipulation” are defined only
against quantities the simulation itself invents. Nothing in the loop has an
external referent, so the system can never be *wrong about anything*.

TRACE closes the loop on ground truth. Agents are legible epistemic subjects
holding persistent natural-language beliefs about questions with a known true
value; an LLM influence compiler emits structured directives; a constitutional
layer filters them. **Cooperation** becomes collective truth-tracking,
**manipulation** becomes measured drift toward a false anchor, and **autonomy**
is read by an auditing judge from the agents’ own written reasoning rather than
posited as a scalar.

This repository contains the complete notebook, every experiment output, and an
independent script that recomputes each headline number in the paper.

---

## Headline results

| # | Question | Finding |
|---|---|---|
| 1 | Does constitutional filtering protect grounded accuracy? | Yes: **+0.033** accuracy (*p*=0.023), drift cut by **0.070** (*p*=0.017) |
| 2 | Does a `FACTUAL`-labelled attack defeat the honesty gate? | **Yes.** Passes **48/48** policy proposals, still degrades accuracy (*p*=0.030) |
| 3 | When does governance matter? | Only while the informed minority is small: **+0.126** at ρ=0.10, null at ρ≥0.55 |
| 4 | Where on the regime map? | Benefit grows to **+0.085** under strong attack; slightly **negative** at ρ=0.55 |
| 6 | Does it generalise across models? | Positive for **4/4** models; magnitude tracks baseline vulnerability |
| 7 | Across languages? | **13/13** positive, pooled **+0.075** (*p*=0.0002); **no** low-resource penalty |
| 8 | Embodied, under command-channel spoofing? | Mission success **0.31 → 0.69**; cohesion a measured null |
| 9 | Embodied, under Byzantine insiders? | Peer filter holds honest accuracy flat at ≈0.90; significant for β≥0.2 |

The central claim is a limitation: **constitutional honesty filtering is
necessary but not sufficient for grounded epistemic protection.** The gate is
label-bound, not truth-bound — an adversary who never lies still moves the crowd.

---

## Repository layout

```
.
├── trace_nebius_v16.ipynb        # the complete experiment notebook (Exp 1–9)
├── requirements.txt
├── scripts/
│   ├── verify_results.py         # recompute every paper number from the CSVs
│   └── export_latex_tables.py    # emit the manuscript tables as LaTeX
├── results/
│   └── trace_out/                # verbatim experiment output, as written by the notebook
│       ├── exp*_*.csv            # 18 summary and statistics tables
│       ├── fig*.png              # 14 figures
│       ├── exp1/<mode>-<item>-s<seed>/     # 36 per-run directories
│       └── exp2/<cond>-<item>-s<seed>/     # 24 per-run directories
└── docs/
    ├── EXPERIMENTS.md            # what each experiment does, and its grid
    ├── RESULTS.md                # every result table, in Markdown
    └── ANONYMITY.md              # notes for the double-blind mirror
```

Each per-run directory under `results/trace_out/exp1/` and `exp2/` holds:

| file | contents |
|---|---|
| `timeseries.csv` | per-step grounded metrics (accuracy, drift, divergence, fairness, gECS) |
| `agents.csv` | final agent state, including the `informed` flag |
| `policy_log.csv` | every compiled policy, whether it cleared the gate, and why not |
| `judgments.csv` | per-agent autonomy audits (empty under `governed` — see caveat 1) |
| `beliefs.jsonl` | **the belief trail**: every agent’s value, reason tag and rationale, every step |
| `config.json` | the exact configuration and item for that run |

`beliefs.jsonl` is the file that makes the “legible epistemic subject” claim
checkable. It is natural-language reasoning, not a trajectory of scalars.

---

## Quickstart

### Verify the results (no API key, ~20 seconds)

```bash
pip install -r requirements.txt
python scripts/verify_results.py
```

```
  [OK  ] Experiment 1     9/9 checks passed
  [OK  ] Experiment 2     7/7 checks passed
  ...
All 109 checks passed. Every headline number in the paper is reproduced from the artifact.
```

This makes no API calls. It reads `results/trace_out/` and reimplements the
notebook’s statistical machinery — seeded bootstrap (10,000 resamples),
two-sided Mann–Whitney *U*, Cliff’s δ, Wilcoxon signed-rank — then checks each
value against what the paper reports. Use `--verbose` to print all 109.

### Re-run the experiments (needs an API key)

Open `trace_nebius_v16.ipynb` and set `NEBIUS_API_KEY` as an environment
variable or Colab secret. Without a key the notebook falls back to a
deterministic mock backend, which produces non-degenerate dynamics for offline
inspection but **is not** what the paper reports.

```bash
export NEBIUS_API_KEY=...   # then run the notebook top to bottom
```

Expect roughly 2.2 × 10⁵ agent decisions before caching. Responses are
content-addressed and cached, so re-running a cell is cheap; a cold full run is
not. Experiments 5, 8d and 9c read saved CSVs and issue no calls at all.

---

## Experimental design

706 simulation runs: 580 in belief space, 126 embodied.

| Exp | Grid | Runs |
|---|---|---|
| 1 | 3 governance modes × 4 items × 3 seeds | 36 |
| 2 | 2 conditions × 4 items × 3 seeds | 24 |
| 3 | 5 informed fractions × 2 modes × 4 items × 3 seeds | 120 |
| 4 | 4 attack strengths × 4 informed fractions × 2 modes × 2 items × 2 seeds | 128 |
| 5 | statistical analysis of saved runs | 0 |
| 6 | 4 models × 2 modes × 2 items × 4 seeds | 64 |
| 7 | 13 languages × 2 modes × 2 items × 4 seeds | 208 |
| 8 | 3 modes × 6 seeds, plus 4 informed fractions × 2 modes × 6 seeds | 66 |
| 9 | 5 Byzantine fractions × 2 filter settings × 6 seeds | 60 |

**Belief-space engine.** 20 agents on a Barabási–Albert graph (*m*=3), 15 steps,
a policy compiled every 3rd step and pushed to the top 40% of agents by the
requested targeting order. Resistance ~ 𝒩(0.35, 0.12) clipped to [0.05, 0.9].

**Swarm engine.** 14 drones in a 100×100 plane, 26 steps, dynamic geometric
comm graph (radius 32), true objective (80,82) against a spoofed waypoint
(82,20), Reynolds control (goal 0.9, cohesion 0.06, alignment 0.10,
separation 14).

**Constitution.** `governed` rejects `MISLEADING`/`EXAGGERATED` claims and
`FEAR` themes and caps intensity at 0.80; `naive` clips only `MISLEADING`
policies above intensity 0.85; `unconstrained` accepts everything.

**Inference.** `meta-llama/Llama-3.3-70B-Instruct` via Nebius AI Studio,
temperature 0.3, 60 s timeout, 3 retries. Experiment 6 additionally covers
DeepSeek-V3.2, Qwen3-235B-A22B-Instruct-2507 and Hermes-4-70B.

See [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) for the full description and
[`docs/RESULTS.md`](docs/RESULTS.md) for every table.

---

## Caveats, stated plainly

These are in the paper too. They are reproduced here because an artifact that
hides them is worse than no artifact.

1. **The autonomy gap is partly definitional.** The judge audits only agents
   that were *targeted*, and under `governed` no policy is ever deployed, so
   `measured_autonomy` takes its default of 1.0. Every
   `results/trace_out/exp1/governed-*/judgments.csv` is empty — check for
   yourself. The defensible reading is “governance removes the exposure that
   produces non-autonomous updates”, not “governed agents reason more
   autonomously”. `verify_results.py` asserts this file is empty rather than
   quietly relying on the default.
2. **Experiment 6’s pooled *p* = 0.125 is the achievable floor** for 4 paired
   cells. The CI excludes zero and 4/4 cells are positive, but the test has no
   resolution; no pooled significance is claimed.
3. **Governance increases swarm safety violations** (0.058 vs 0.015). The
   governed swarm actually arrives, and arrival concentrates 14 drones inside a
   16-unit radius. Protection shifts risk into terminal approach.
4. **The accuracy benefit is negative at ρ = 0.55** at every attack strength.
   With an informed majority, filtering the coordinator also removes some
   corrective social signal.
5. **The pre-designated low-resource penalty was not observed.** Arabic, Basque
   and Luxembourgish average +0.077 against +0.074 for the other ten. Reported
   as a negative result. Translation quality itself varied — the Basque question
   stem renders “two named cities” as “three”.
6. **The adversary is non-adaptive.** The compiler never observes the
   constitution or optimises against it. A strategic adversary searching for
   `FACTUAL`-labelled anchors would likely widen the Experiment 2 gap.
7. **Agent susceptibility is a modelling assumption**, not calibrated against
   human persuasion data. TRACE measures manipulation of *LLM* epistemics.

---

## Reproducibility notes

- All randomness is seeded; agent and judge calls within a step run
  concurrently, but belief updates are **synchronous**, so results do not depend
  on worker count.
- LLM sampling at temperature 0.3 is not bit-reproducible. Cell-level means are
  stable across re-runs; individual agent rationales are not.
- `Llama-3.1-8B-Instruct` was in the Experiment 6 model list but returned
  HTTP 404 from the provider and was skipped by the reachability probe. Models
  falling back to defaults on more than 20% of calls are excluded from the
  statistics by design.
- A sanitizer clamps agent outputs to a plausible band; the flagged fraction is
  logged, not hidden. Over Experiment 1 it was 0.01% of updates, all on
  `count_k`.

