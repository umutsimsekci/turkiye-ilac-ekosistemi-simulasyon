"""Exact binary enumeration, five projects plus one shared platform."""
import itertools
import numpy as np
import pandas as pd

def projects():
    return pd.DataFrame([
        ['G','Kritik eşdeğer',1,.9,1000,-1.5,False,False],
        ['B','Biyobenzer',2.2,.7,1000,-4,False,False],
        ['R','Yeniden konumlandırma',1.3,.45,6000,1.5,True,False],
        ['N1','Faz I adayı',3,.12285,50000,12,True,True],
        ['N2','Faz II adayı',2.5,.189,26000,8,True,True],
    ],columns=['id','name','investment_bn','probability','qaly','health_cost_bn','platform_eligible','platform_required'])

def enumerate_portfolios(budget=8,threshold=1e6,platform_cost=1.2,platform_gain=.1,stress=False,innovation_floor=False):
    if not np.isfinite([budget,threshold,platform_cost,platform_gain]).all() or min(budget,threshold,platform_cost,platform_gain)<0: raise ValueError('Portföy girdileri sonlu ve negatif olmayan değerler olmalıdır.')
    df=projects()
    if (df.probability*(1+platform_gain*df.platform_eligible)>1).any(): raise ValueError('Platform etkisi başarı olasılığını 1 üzerine çıkarıyor.')
    rows=[]
    for bits in itertools.product([0,1],repeat=6):
        x=np.array(bits[:5]);z=bits[5];spent=float(x@df.investment_bn+platform_cost*z)
        feasible=spent<=budget+1e-9 and not (x[3]+x[4]>0 and z==0)
        if innovation_floor:feasible=feasible and x[0]+x[1]>=1 and x[3]+x[4]>=1
        p=df.probability.to_numpy()*np.where(df.platform_eligible & bool(z),1+platform_gain,1)
        q=df.qaly.to_numpy(dtype=float);c=df.health_cost_bn.to_numpy(dtype=float)
        if stress:p=p*.7;q=q*.7;c=np.where(c>0,c*1.2,c*.7)
        value=float(x@(p*(threshold*q/1e9-c))-spent)
        selected=';'.join(df.id[x==1].tolist()+(['P'] if z else []))
        rows.append({'selected':selected,'spent_bn':spent,'enmb_bn':value,'feasible':bool(feasible),'platform':z})
    return pd.DataFrame(rows)

def optimize(**kwargs):
    feasible=enumerate_portfolios(**kwargs).query('feasible').sort_values(['enmb_bn','spent_bn'],ascending=[False,True])
    if feasible.empty: raise ValueError('Bu bütçe ve zorunlu alan koşuluyla uygun portföy yok.')
    return feasible.iloc[0].to_dict()

def frontier(thresholds=(500000,1000000,1500000)):
    # Evaluate at every attainable expenditure, not a grid that shifts thresholds.
    feasible=enumerate_portfolios(budget=12).query('feasible')
    budgets=sorted(set([0.,12.,*np.round(feasible.spent_bn,10)]))
    return pd.DataFrame([{'budget_bn':b,'threshold':lam,**optimize(budget=float(b),threshold=float(lam))}
                         for lam in thresholds for b in budgets])
