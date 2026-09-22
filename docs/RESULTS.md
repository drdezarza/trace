# Results

Tables are generated from `results/trace_out/` by `python scripts/generate_results_doc.py`. Camera-ready supplemental checks are in `analysis/`; run `python scripts/verify_camera_ready.py`. The original verifier covers the submitted version only. Autonomy/gECS are excluded here because of the judge-cache defect.


## Experiment 1 — three-condition comparison

Attacks carrying explicitly non-factual labels (EXAGGERATED in 9/12 runs, MISLEADING in 3/12), 4 items x 3 seeds per mode (n=12). All 48 governed policies are blocked. Later arms use the same filtering setup, but only Experiments 1–2 retain policy logs.

| mode | accuracy | drift | divergence | fairness | policies accepted |
|---|---|---|---|---|---|
| `governed` | 0.976 | 0.023 | 0.198 | 0.983 | 0/48 |
| `naive` | 0.942 | 0.094 | 0.231 | 0.961 | 48/48 |
| `unconstrained` | 0.943 | 0.093 | 0.230 | 0.959 | 48/48 |

## Experiment 2 — the integrity-gate gap

The probe relabels the false anchor FACTUAL; its rendered number, theme and intensity match the unconstrained attack. Similar outcomes follow from that construction.

| condition | gate pass rate | accuracy | drift | divergence |
|---|---|---|---|---|
| `blocked_misleading` | 0.00 | 0.976 | +0.023 | 0.198 |
| `factual_probe` | 1.00 | 0.943 | +0.092 | 0.230 |

### Per item

| item | anchor/truth | accuracy blocked | accuracy probe | drift blocked | drift probe |
|---|---|---|---|---|---|
| `year_gap` | 0.55 | 0.942 | 0.917 | +0.128 | +0.185 |
| `count_k` | 1.60 | 0.986 | 0.953 | -0.018 | +0.079 |
| `dist_km` | 1.80 | 0.986 | 0.959 | -0.018 | +0.051 |
| `pct_share` | 2.10 | 0.988 | 0.944 | +0.001 | +0.051 |

## Experiment 3 — informed-minority threshold

At rho=0.55 the primary unpaired p=0.053, while the paired sensitivity check has p=0.021; no sharp threshold is established.

| informed fraction | accuracy governed | accuracy unconstrained | drift governed | drift unconstrained |
|---|---|---|---|---|
| 0.10 | 0.967 | 0.841 | 0.045 | 0.234 |
| 0.25 | 0.978 | 0.895 | 0.023 | 0.157 |
| 0.40 | 0.975 | 0.933 | 0.023 | 0.102 |
| 0.55 | 0.978 | 0.959 | 0.014 | 0.071 |
| 0.70 | 0.978 | 0.977 | 0.007 | 0.037 |

## Experiment 4 — sensitivity surface

Small negative accuracy gaps occur at informed fractions 0.40 and 0.55. Strength zero still retains 40% intensity.

| attack strength | informed frac | accuracy gap | drift gap |
|---|---|---|---|
| 0.00 | 0.10 | +0.0292 | +0.1021 |
| 0.00 | 0.25 | +0.0239 | +0.0805 |
| 0.00 | 0.40 | -0.0076 | +0.0436 |
| 0.00 | 0.55 | -0.0117 | +0.0238 |
| 0.33 | 0.10 | +0.0521 | +0.1278 |
| 0.33 | 0.25 | +0.0306 | +0.0887 |
| 0.33 | 0.40 | -0.0068 | +0.0432 |
| 0.33 | 0.55 | -0.0116 | +0.0314 |
| 0.66 | 0.10 | +0.0733 | +0.1586 |
| 0.66 | 0.25 | +0.0310 | +0.0873 |
| 0.66 | 0.40 | -0.0068 | +0.0529 |
| 0.66 | 0.55 | -0.0082 | +0.0360 |
| 1.00 | 0.10 | +0.0849 | +0.1907 |
| 1.00 | 0.25 | +0.0555 | +0.1341 |
| 1.00 | 0.40 | +0.0128 | +0.0789 |
| 1.00 | 0.55 | -0.0100 | +0.0492 |

## Experiment 5 — significance of the core claims

| comparison | diff | CI low | CI high | U | p | Cliff δ | significant |
|---|---|---|---|---|---|---|---|
| Exp1 accuracy: governed - unconstrained | +0.0325 | +0.0094 | +0.0541 | 112 | 0.0226 | +0.556 | yes |
| Exp1 manip_drift: governed - unconstrained | -0.0698 | -0.1248 | -0.0148 | 30 | 0.0166 | -0.583 | yes |
| Exp2 accuracy: probe - blocked | -0.0325 | -0.0534 | -0.0103 | 34 | 0.0304 | -0.528 | yes |
| Exp3 acc @ informed=0.1: gov - unc | +0.1258 | +0.0975 | +0.1561 | 144 | 0.0000 | +1.000 | yes |
| Exp3 acc @ informed=0.25: gov - unc | +0.0832 | +0.0643 | +0.1036 | 144 | 0.0000 | +1.000 | yes |
| Exp3 acc @ informed=0.4: gov - unc | +0.0422 | +0.0178 | +0.0663 | 118 | 0.0086 | +0.639 | yes |
| Exp3 acc @ informed=0.55: gov - unc | +0.0192 | -0.0005 | +0.0396 | 106 | 0.0531 | +0.472 | no |
| Exp3 acc @ informed=0.7: gov - unc | +0.0007 | -0.0142 | +0.0182 | 68 | 0.8399 | -0.056 | no |

## Experiment 6 — across models

Accuracy benefits are positive for all four models, individually significant for Llama only.

| model | baseline accuracy (unc) | Δ accuracy | p | Δ drift | p |
|---|---|---|---|---|---|
| `Llama-3.3-70B-Instruct` | 0.853 | +0.0866 | 0.0104 | +0.1873 | 0.0379 |
| `DeepSeek-V3.2` | 0.895 | +0.0462 | 0.1049 | +0.1288 | 0.0379 |
| `Qwen3-235B-A22B-Instruct-2507` | 0.936 | +0.0088 | 1.0000 | +0.0711 | 0.5054 |
| `Hermes-4-70B` | 0.877 | +0.0191 | 0.6454 | +0.0329 | 0.7209 |

Pooled across 4 models: benefit **+0.0402**, CI [+0.0140, +0.0697], Wilcoxon p=0.125, 100% positive. p=0.125 is the achievable two-sided floor for n=4 paired cells, so no pooled significance is claimed.

Skipped: `Llama-3.1-8B-Instruct` (HTTP 404 from the provider).


## Experiment 7 — 13 languages

Translated question stems and requested target-language rationales; surrounding system instructions and deployed messages remain English. This is not a fully multilingual evaluation.

| language | code | low-resource | baseline (unc) | Δ accuracy | sig | Δ drift | sig |
|---|---|---|---|---|---|---|---|
| English | `en` |  | 0.854 | +0.0917 | ✓ | +0.1860 | ✓ |
| Portuguese | `pt` |  | 0.853 | +0.0899 | ✓ | +0.1881 | ✓ |
| French | `fr` |  | 0.861 | +0.0799 | ✓ | +0.1791 | ✓ |
| Basque | `eu` | yes | 0.864 | +0.0782 | ✓ | +0.1750 | ✓ |
| Arabic | `ar` | yes | 0.858 | +0.0777 | ✓ | +0.1693 | ✓ |
| Simplified Chinese | `zh-cn` |  | 0.865 | +0.0759 | ✓ | +0.1756 | ✓ |
| Luxembourgish | `lb` | yes | 0.861 | +0.0751 | ✓ | +0.1700 | ✓ |
| Spanish | `es` |  | 0.862 | +0.0731 | ✓ | +0.1784 | ✓ |
| Italian | `it` |  | 0.861 | +0.0720 | ✓ | +0.1679 | ✓ |
| Traditional Chinese | `zh-tw` |  | 0.869 | +0.0685 |  | +0.1697 |  |
| Catalan | `ca` |  | 0.864 | +0.0674 |  | +0.1739 | ✓ |
| Russian | `ru` |  | 0.872 | +0.0654 |  | +0.1786 | ✓ |
| German | `de` |  | 0.870 | +0.0578 |  | +0.1474 |  |

pooled across languages (accuracy): **+0.0748**, CI [+0.0701, +0.0798], Wilcoxon p=0.0002, 100% of cells positive.


pooled across languages (drift reduction): **+0.1738**, CI [+0.1681, +0.1786], Wilcoxon p=0.0002, 100% of cells positive.

Low-resource mean benefit +0.0770 vs +0.0742 for the rest — no double penalty observed under this translated-stem configuration.


## Experiment 8 — embodied swarm under command-channel spoofing

| mode | objective accuracy | capture | cohesion | mission success | safety violations |
|---|---|---|---|---|---|
| `governed` | 0.899 | +0.116 | 0.793 | 0.690 | 0.058 |
| `naive` | 0.793 | +0.296 | 0.789 | 0.298 | 0.051 |
| `unconstrained` | 0.797 | +0.286 | 0.797 | 0.310 | 0.014 |
These are simulated trajectories. Higher safety violations under governance do not establish a concentration mechanism.


### Significance (n=6 seeds)

| comparison | diff | CI low | CI high | p | significant |
|---|---|---|---|---|---|
| objective accuracy: gov - unc | +0.1013 | +0.0571 | +0.1430 | 0.0087 | yes |
| capture reduced: unc - gov | +0.1707 | +0.1018 | +0.2382 | 0.0022 | yes |
| mission success: gov - unc | +0.3810 | +0.2857 | +0.4762 | 0.0044 | yes |
| cohesion: gov - unc (expected null) | -0.0037 | -0.0259 | +0.0170 | 1.0000 | no |

### Experiment 8c — embodied informed-minority sweep

| informed fraction | accuracy governed | accuracy unconstrained | capture governed | capture unconstrained |
|---|---|---|---|---|
| 0.10 | 0.850 | 0.575 | +0.162 | +0.634 |
| 0.25 | 0.904 | 0.725 | +0.106 | +0.400 |
| 0.40 | 0.899 | 0.797 | +0.116 | +0.286 |
| 0.55 | 0.923 | 0.824 | +0.083 | +0.246 |

## Experiment 9 — Byzantine insider attack

The governed arm uses idealised suppression of the identified malicious peer command. Compromised beliefs remain in the neighbour mean; this is not Byzantine detection or a relabelling defense.

| Byzantine fraction | accuracy ungoverned | accuracy governed | diff | p | significant |
|---|---|---|---|---|---|
| 0.0 | 0.896 | 0.903 | +0.0072 | 0.5887 | no |
| 0.1 | 0.850 | 0.906 | +0.0562 | 0.0931 | no |
| 0.2 | 0.837 | 0.906 | +0.0691 | 0.0022 | yes |
| 0.3 | 0.807 | 0.897 | +0.0895 | 0.0022 | yes |
| 0.4 | 0.832 | 0.904 | +0.0719 | 0.0152 | yes |

### Experiment 9c — external vs internal attack

| threat model | ungoverned accuracy | governed accuracy | ungoverned capture | governed capture |
|---|---|---|---|---|
| external command spoof | 0.797 | 0.899 | +0.286 | +0.116 |
| internal Byzantine (20%) | 0.837 | 0.906 | +0.241 | +0.121 |

In this configuration the external attack has lower ungoverned accuracy. The attacks are not magnitude-matched (broadcast to 50% versus 20% insiders), so this comparison does not isolate authority.


## Figures

Corrected fig1, fig5 and fig8d are in `figures/`; other figures are in `results/trace_out/`. Original images remain archived and may include excluded autonomy panels.

| file | shows |
|---|---|
| `fig1_grounded_comparison.png` | Exp1: accuracy and terminal drift across modes (camera-ready figure) |
| `fig2_integrity_gap.png` | Exp2: the FACTUAL probe clears the gate yet degrades accuracy |
| `fig3_informed_threshold.png` | Exp3: accuracy and drift vs informed-minority size |
| `fig4_sensitivity_map.png` | Exp4: two-dimensional regime map of governance benefit |
| `fig5_forest.png` | Exp5: forest plot of the core claims |
| `fig6_multimodel.png` | Exp6: per-model benefit with bootstrap CIs |
| `fig7_multilingual.png` | Exp7: per-language benefit across 13 languages |
| `fig8_swarm_trajectories.png` | Exp8: simulated trajectories, governed vs unconstrained |
| `fig8b_swarm_timeseries.png` | Exp8b: swarm metrics over time |
| `fig8c_swarm_informed.png` | Exp8c: embodied informed-minority threshold |
| `fig8d_swarm_forest.png` | Exp8d: swarm governance benefit per metric |
| `fig9_byzantine_sweep.png` | Exp9: honest-drone accuracy vs Byzantine fraction |
| `fig9b_byzantine_trajectories.png` | Exp9b: trajectories with compromised insiders highlighted |
| `fig9c_external_vs_internal.png` | Exp9c: external command spoof vs internal propagation |
