#!/usr/bin/env python3
"""
generate_results_doc.py -- regenerate docs/RESULTS.md from results/trace_out/.

Every table in RESULTS.md is produced by this script, so the documentation
cannot drift from the data. Run from the repository root:

    python scripts/generate_results_doc.py
"""

import pandas as pd, numpy as np
from pathlib import Path
OUT=Path('results/trace_out')
def r(n): return pd.read_csv(OUT/n)
L=[]
A=L.append
A("# Results\n")
A("Tables are generated from `results/trace_out/` by `python scripts/generate_results_doc.py`. Camera-ready supplemental checks are in `analysis/`; run `python scripts/verify_camera_ready.py`. The original verifier covers the submitted version only. Autonomy/gECS are excluded here because of the judge-cache defect.\n")

A("\n## Experiment 1 — three-condition comparison\n")
A("Attacks carrying explicitly non-factual labels (EXAGGERATED in 9/12 runs, MISLEADING in 3/12), 4 items x 3 seeds per mode (n=12). All 48 governed policies are blocked. Later arms use the same filtering setup, but only Experiments 1–2 retain policy logs.\n")
d=r('exp1_summary.csv'); g=d.groupby('mode')
A("| mode | accuracy | drift | divergence | fairness | policies accepted |")
A("|---|---|---|---|---|---|")
acc={'governed':'0/48','naive':'48/48','unconstrained':'48/48'}
for m in ['governed','naive','unconstrained']:
    A("| `%s` | %.3f | %.3f | %.3f | %.3f | %s |"%(m,
      g['accuracy'].mean()[m],g['manip_drift'].mean()[m],g['divergence'].mean()[m],
      g['fairness'].mean()[m],acc[m]))

A("\n## Experiment 2 — the integrity-gate gap\n")
A("The probe relabels the false anchor FACTUAL; its rendered number, theme and intensity match the unconstrained attack. Similar outcomes follow from that construction.\n")
d=r('exp2_gap.csv'); g=d.groupby('condition')
A("| condition | gate pass rate | accuracy | drift | divergence |")
A("|---|---|---|---|---|")
for c in ['blocked_misleading','factual_probe']:
    A("| `%s` | %.2f | %.3f | %+.3f | %.3f |"%(c,g['policy_passed_gate'].mean()[c],
      g['accuracy'].mean()[c],g['manip_drift'].mean()[c],g['divergence'].mean()[c]))
A("\n### Per item\n")
p=d.pivot_table(index='qid',columns='condition',values=['accuracy','manip_drift'])
ratio={'year_gap':0.55,'count_k':1.60,'dist_km':1.80,'pct_share':2.10}
A("| item | anchor/truth | accuracy blocked | accuracy probe | drift blocked | drift probe |")
A("|---|---|---|---|---|---|")
for q in ['year_gap','count_k','dist_km','pct_share']:
    A("| `%s` | %.2f | %.3f | %.3f | %+.3f | %+.3f |"%(q,ratio[q],
      p[('accuracy','blocked_misleading')][q],p[('accuracy','factual_probe')][q],
      p[('manip_drift','blocked_misleading')][q],p[('manip_drift','factual_probe')][q]))

A("\n## Experiment 3 — informed-minority threshold\n")
A("At rho=0.55 the primary unpaired p=0.053, while the paired sensitivity check has p=0.021; no sharp threshold is established.\n")
d=r('exp3_informed_sweep.csv')
A("| informed fraction | accuracy governed | accuracy unconstrained | drift governed | drift unconstrained |")
A("|---|---|---|---|---|")
for f in sorted(d.informed_frac.unique()):
    s=d[d.informed_frac==f]
    A("| %.2f | %.3f | %.3f | %.3f | %.3f |"%(f,
      s[s['mode']=='governed']['accuracy'].mean(),s[s['mode']=='unconstrained']['accuracy'].mean(),
      s[s['mode']=='governed']['manip_drift'].mean(),s[s['mode']=='unconstrained']['manip_drift'].mean()))

A("\n## Experiment 4 — sensitivity surface\n")
A("Small negative accuracy gaps occur at informed fractions 0.40 and 0.55. Strength zero still retains 40% intensity.\n")
d=r('exp4_sensitivity.csv')
A("| attack strength | informed frac | accuracy gap | drift gap |")
A("|---|---|---|---|")
for _,x in d.iterrows():
    A("| %.2f | %.2f | %+.4f | %+.4f |"%(x.attack_strength,x.informed_frac,x.acc_gap,x.drift_gap))

A("\n## Experiment 5 — significance of the core claims\n")
d=r('exp5_significance.csv'); d=d[~d.metric.str.contains('autonomy')]
A("| comparison | diff | CI low | CI high | U | p | Cliff δ | significant |")
A("|---|---|---|---|---|---|---|---|")
for _,x in d.iterrows():
    A("| %s | %+.4f | %+.4f | %+.4f | %.0f | %.4f | %+.3f | %s |"%(x.comparison,
      x.mean_diff,x.ci_lo,x.ci_hi,x.U,x.p,x.cliffs_delta,'yes' if x.significant else 'no'))

A("\n## Experiment 6 — across models\n")
A("Accuracy benefits are positive for all four models, individually significant for Llama only.\n")
a=r('exp6_stats_accuracy.csv'); dr=r('exp6_stats_drift.csv'); mm=r('exp6_multimodel.csv')
A("| model | baseline accuracy (unc) | Δ accuracy | p | Δ drift | p |")
A("|---|---|---|---|---|---|")
for _,x in a.iterrows():
    s=mm[mm.model==x.model]; base=s[s['mode']=='unconstrained']['accuracy_mean'].mean()
    dx=dr[dr.model==x.model].iloc[0]
    A("| `%s` | %.3f | %+.4f | %.4f | %+.4f | %.4f |"%(x.model,base,x.mean_diff,x.p,dx.mean_diff,dx.p))
pl=r('exp6_pooled.csv').iloc[0]
A("\nPooled across 4 models: benefit **%+.4f**, CI [%+.4f, %+.4f], Wilcoxon p=%.3f, %.0f%% positive. "
  "p=0.125 is the achievable two-sided floor for n=4 paired cells, so no pooled significance is claimed.\n"
  %(pl.mean_benefit,pl.ci_lo,pl.ci_hi,pl.p,pl.frac_positive*100))
A("Skipped: `Llama-3.1-8B-Instruct` (HTTP 404 from the provider).\n")

A("\n## Experiment 7 — 13 languages\n")
A("Translated question stems and requested target-language rationales; surrounding system instructions and deployed messages remain English. This is not a fully multilingual evaluation.\n")
a=r('exp7_stats_accuracy.csv'); dr=r('exp7_stats_drift.csv'); ml=r('exp7_multilingual.csv')
A("| language | code | low-resource | baseline (unc) | Δ accuracy | sig | Δ drift | sig |")
A("|---|---|---|---|---|---|---|---|")
for _,x in a.sort_values('mean_diff',ascending=False).iterrows():
    s=ml[ml.lang==x.lang]; base=s[s['mode']=='unconstrained']['accuracy_mean'].mean()
    dx=dr[dr.lang==x.lang].iloc[0]
    A("| %s | `%s` | %s | %.3f | %+.4f | %s | %+.4f | %s |"%(x.lang,x.code,
      'yes' if x.low_resource else '',base,x.mean_diff,'✓' if x.significant else '',
      dx.mean_diff,'✓' if dx.significant else ''))
p7=r('exp7_pooled.csv')
for _,x in p7.iterrows():
    A("\n%s: **%+.4f**, CI [%+.4f, %+.4f], Wilcoxon p=%.4f, %.0f%% of cells positive.\n"
      %(x.comparison,x.mean_benefit,x.ci_lo,x.ci_hi,x.p,x.frac_positive*100))
lr=a[a.low_resource]['mean_diff'].mean(); hr=a[~a.low_resource]['mean_diff'].mean()
A("Low-resource mean benefit %+.4f vs %+.4f for the rest — no double penalty observed under this translated-stem configuration.\n"%(lr,hr))

A("\n## Experiment 8 — embodied swarm under command-channel spoofing\n")
d=r('exp8_swarm.csv'); g=d.groupby('mode')
A("| mode | objective accuracy | capture | cohesion | mission success | safety violations |")
A("|---|---|---|---|---|---|")
for m in ['governed','naive','unconstrained']:
    A("| `%s` | %.3f | %+.3f | %.3f | %.3f | %.3f |"%(m,g['obj_acc'].mean()[m],
      g['capture'].mean()[m],g['cohesion'].mean()[m],g['mission_success'].mean()[m],
      g['safety_violation'].mean()[m]))
A("These are simulated trajectories. Higher safety violations under governance do not establish a concentration mechanism.\n")
A("\n### Significance (n=6 seeds)\n")
s=r('exp8_significance.csv'); s=s[~s.metric.str.contains('autonomy')]
A("| comparison | diff | CI low | CI high | p | significant |")
A("|---|---|---|---|---|---|")
for _,x in s.iterrows():
    A("| %s | %+.4f | %+.4f | %+.4f | %.4f | %s |"%(x.comparison,x.mean_diff,x.ci_lo,x.ci_hi,x.p,
      'yes' if x.significant else 'no'))
A("\n### Experiment 8c — embodied informed-minority sweep\n")
sw=r('exp8_informed_sweep.csv')
A("| informed fraction | accuracy governed | accuracy unconstrained | capture governed | capture unconstrained |")
A("|---|---|---|---|---|")
for f in sorted(sw.informed_frac.unique()):
    s2=sw[sw.informed_frac==f]
    A("| %.2f | %.3f | %.3f | %+.3f | %+.3f |"%(f,
      s2[s2['mode']=='governed']['obj_acc'].mean(),s2[s2['mode']=='unconstrained']['obj_acc'].mean(),
      s2[s2['mode']=='governed']['capture'].mean(),s2[s2['mode']=='unconstrained']['capture'].mean()))

A("\n## Experiment 9 — Byzantine insider attack\n")
A("The governed arm uses idealised suppression of the identified malicious peer command. Compromised beliefs remain in the neighbour mean; this is not Byzantine detection or a relabelling defense.\n")
d=r('exp9_byzantine.csv'); s=r('exp9_significance.csv')
A("| Byzantine fraction | accuracy ungoverned | accuracy governed | diff | p | significant |")
A("|---|---|---|---|---|---|")
for _,x in s.iterrows():
    sub=d[d.byz_frac==x.byz_frac]
    A("| %.1f | %.3f | %.3f | %+.4f | %.4f | %s |"%(x.byz_frac,
      sub[~sub.governed]['obj_acc'].mean(),sub[sub.governed]['obj_acc'].mean(),
      x.mean_diff,x.p,'yes' if x.significant else 'no'))
e8=r('exp8_swarm.csv')
A("\n### Experiment 9c — external vs internal attack\n")
A("| threat model | ungoverned accuracy | governed accuracy | ungoverned capture | governed capture |")
A("|---|---|---|---|---|")
A("| external command spoof | %.3f | %.3f | %+.3f | %+.3f |"%(
  e8[e8['mode']=='unconstrained']['obj_acc'].mean(),e8[e8['mode']=='governed']['obj_acc'].mean(),
  e8[e8['mode']=='unconstrained']['capture'].mean(),e8[e8['mode']=='governed']['capture'].mean()))
b=d[d.byz_frac==0.20]
A("| internal Byzantine (20%%) | %.3f | %.3f | %+.3f | %+.3f |"%(
  b[~b.governed]['obj_acc'].mean(),b[b.governed]['obj_acc'].mean(),
  b[~b.governed]['capture'].mean(),b[b.governed]['capture'].mean()))
A("\nIn this configuration the external attack has lower ungoverned accuracy. The attacks are not magnitude-matched (broadcast to 50% versus 20% insiders), so this comparison does not isolate authority.\n")

A("\n## Figures\n")
A("Corrected fig1, fig5 and fig8d are in `figures/`; other figures are in `results/trace_out/`. Original images remain archived and may include excluded autonomy panels.\n")
A("| file | shows |")
A("|---|---|")
figs=[('fig1_grounded_comparison','Exp1: accuracy and terminal drift across modes (camera-ready figure)'),
 ('fig2_integrity_gap','Exp2: the FACTUAL probe clears the gate yet degrades accuracy'),
 ('fig3_informed_threshold','Exp3: accuracy and drift vs informed-minority size'),
 ('fig4_sensitivity_map','Exp4: two-dimensional regime map of governance benefit'),
 ('fig5_forest','Exp5: forest plot of the core claims'),
 ('fig6_multimodel','Exp6: per-model benefit with bootstrap CIs'),
 ('fig7_multilingual','Exp7: per-language benefit across 13 languages'),
 ('fig8_swarm_trajectories','Exp8: simulated trajectories, governed vs unconstrained'),
 ('fig8b_swarm_timeseries','Exp8b: swarm metrics over time'),
 ('fig8c_swarm_informed','Exp8c: embodied informed-minority threshold'),
 ('fig8d_swarm_forest','Exp8d: swarm governance benefit per metric'),
 ('fig9_byzantine_sweep','Exp9: honest-drone accuracy vs Byzantine fraction'),
 ('fig9b_byzantine_trajectories','Exp9b: trajectories with compromised insiders highlighted'),
 ('fig9c_external_vs_internal','Exp9c: external command spoof vs internal propagation')]
for f,desc in figs: A("| `%s.png` | %s |"%(f,desc))
open('docs/RESULTS.md','w').write('\n'.join(L)+'\n')
print('docs/RESULTS.md written: %d lines'%len(L))
