"""Reproduce the camera-ready supplemental checks and three corrected figures.

Inputs are archived run summaries and extracted per-agent endpoints, not new
simulations. Requires numpy, pandas, scipy and matplotlib. No API calls.
Run: python analysis/recompute.py (from the package root).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
DATA=HERE/'inputs'
FIG=HERE.parent/'figures'
FIG.mkdir(parents=True, exist_ok=True)
agent=pd.read_csv(DATA/'agent_endpoints.csv')
agent['relative_absolute_error']=abs(agent.final_value-agent.truth)/abs(agent.truth)
agent['closer_to_anchor']=(abs(agent.final_value-agent.anchor)<abs(agent.final_value-agent.truth)).astype(float)
agent['movement_from_t0']=(agent.final_value-agent.first_logged_value)/(agent.anchor-agent.truth)
run=agent.groupby(['mode','qid','seed'])[['relative_absolute_error','closer_to_anchor','movement_from_t0']].mean().reset_index()
run.to_csv(HERE/'per_run_supplement.csv',index=False)
summary=run.groupby('mode')[['relative_absolute_error','closer_to_anchor','movement_from_t0']].mean()
summary.to_csv(HERE/'supplementary_summary.csv')
e1=pd.read_csv(DATA/'exp1_summary.csv')

def paired(frame,value,group='mode'):
    p=frame.pivot(index=['qid','seed'],columns=group,values=value)
    d=p.governed-p.unconstrained
    return dict(n_pairs=len(d),mean_difference=float(d.mean()),positive=int((d>0).sum()),
                negative=int((d<0).sum()),p=float(wilcoxon(d).pvalue))

checks={m:paired(e1,m) for m in ['accuracy','manip_drift']}
checks['movement_from_t0']=paired(run,'movement_from_t0')
e3=pd.read_csv(DATA/'exp3_informed_sweep.csv')
checks['accuracy_rho_0.55']=paired(e3[np.isclose(e3.informed_frac,.55)],'accuracy')
(HERE/'paired_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
assert checks['accuracy']['positive']==11
assert checks['manip_drift']['negative']==12
assert checks['movement_from_t0']['negative']==12
assert np.isclose(summary.loc['governed','relative_absolute_error'],.079272,atol=1e-6)
assert np.isclose(summary.loc['unconstrained','relative_absolute_error'],.102150,atol=1e-6)

# Preserve the original figure palette and data; exclude unreliable audit panels.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'savefig.dpi':300,'pdf.fonttype':42})
order=['governed','naive','unconstrained'];colors=['#2a9d4a','#e0a219','#d1495b']
fig,ax=plt.subplots(1,2,figsize=(9,3.2))
for a,metric,title in zip(ax,['accuracy','manip_drift'],['Collective accuracy','Terminal drift']):
    g=e1.groupby('mode')[metric]
    a.bar(range(3),g.mean().reindex(order),yerr=g.std().reindex(order),color=colors,capsize=3,width=.65)
    a.set_xticks(range(3));a.set_xticklabels(order,fontsize=9);a.set_title(title)
    a.set_ylabel('Accuracy' if metric=='accuracy' else 'Signed drift')
    if metric=='accuracy':a.set_ylim(0,1.05)
    else:a.axhline(0,color='#555555',lw=.7)
fig.tight_layout()
fig.savefig(FIG/'fig1_grounded_comparison.png',bbox_inches='tight');plt.close(fig)

def forest(source,filename,labels,height):
    d=pd.read_csv(DATA/source)
    d=d[~d.metric.str.contains('autonomy')].copy()
    assert len(d)==len(labels)
    fig,ax=plt.subplots(figsize=(8.7,height))
    yy=np.arange(len(d))[::-1]
    for y,(_,r) in zip(yy,d.iterrows()):
        significant=bool(r.ci_lo>0 or r.ci_hi<0) and r.p<.05
        color='#2a9d4a' if significant else '#999999'
        ax.plot([r.ci_lo,r.ci_hi],[y,y],color=color,lw=2.5,solid_capstyle='round')
        ax.plot(r.mean_diff,y,'o',color=color,ms=5)
    ax.axvline(0,color='#444444',ls='--',lw=.8)
    ax.set_yticks(yy);ax.set_yticklabels(labels,fontsize=10)
    ax.set_xlabel('Mean difference (95% bootstrap CI)')
    ax.grid(axis='x',alpha=.15)
    fig.tight_layout();fig.savefig(FIG/filename,bbox_inches='tight');plt.close(fig)

forest('exp5_significance.csv','fig5_forest.png',[
    'E1: accuracy, gov - unc','E1: drift, gov - unc','E2: accuracy, probe - blocked',
    'E3: accuracy, rho = 0.10','E3: accuracy, rho = 0.25','E3: accuracy, rho = 0.40',
    'E3: accuracy, rho = 0.55','E3: accuracy, rho = 0.70'],4.0)
forest('exp8_significance.csv','fig8d_swarm_forest.png',[
    'Objective accuracy: gov - unc','Capture reduced: unc - gov',
    'Mission success: gov - unc','Cohesion: gov - unc'],2.8)
print(summary.to_string())
print(json.dumps(checks,indent=2))
print('Three figures regenerated; cached autonomy and gECS results excluded.')
