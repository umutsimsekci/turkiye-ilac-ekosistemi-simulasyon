"""Continuous-time transition generator, discrete rewards, half-cycle correction."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.linalg import expm

@dataclass(frozen=True)
class Cohort:
    progression: float = .18
    death_stable: float = .03
    death_progressed: float = .25
    relative_rate: float = .72
    price_standard: float = 90000
    price_candidate: float = 140000
    care_stable: float = 20000
    care_progressed: float = 140000
    utility_stable: float = .8
    utility_progressed: float = .5
    horizon: float = 20
    cycle: float = 1
    discount: float = .03

    def validate(self):
        if not np.isfinite(list(vars(self).values())).all(): raise ValueError('Kohort girdileri sonlu olmalıdır.')
        if min(self.progression,self.death_stable,self.death_progressed,self.relative_rate,self.price_standard,self.price_candidate,self.care_stable,self.care_progressed,self.discount)<0:
            raise ValueError('Hızlar, fiyatlar ve iskonto negatif olamaz.')
        if self.cycle<=0 or self.horizon<=0 or not np.isclose(self.horizon/self.cycle,round(self.horizon/self.cycle)):
            raise ValueError('Ufuk, pozitif döngü uzunluğunun tam katı olmalıdır.')
        if not 0<=self.utility_progressed<=self.utility_stable<=1: raise ValueError('Bu modelde 0 ≤ ilerlemiş fayda ≤ stabil fayda ≤ 1 olmalıdır.')

def transition(p=Cohort(), candidate=False):
    p.validate();h=p.progression*(p.relative_rate if candidate else 1)
    return expm(np.array([[-h-p.death_stable,h,p.death_stable],[0,-p.death_progressed,p.death_progressed],[0,0,0]])*p.cycle)

def evaluate(p=Cohort(), candidate=False):
    p.validate();P=transition(p,candidate);state=np.array([1.,0.,0.]);trace=[state.copy()]
    price=p.price_candidate if candidate else p.price_standard
    rewards=np.array([price+p.care_stable,p.care_progressed,0]);utilities=np.array([p.utility_stable,p.utility_progressed,0])
    costs=[];qalys=[]
    for i in range(round(p.horizon/p.cycle)):
        nxt=state@P;occupancy=(state+nxt)/2;factor=p.cycle/(1+p.discount)**((i+.5)*p.cycle)
        costs.append(float(occupancy@rewards*factor));qalys.append(float(occupancy@utilities*factor))
        state=nxt;trace.append(state.copy())
    table=pd.DataFrame(trace,columns=['stable','progressed','dead']);table.insert(0,'year',np.arange(len(trace))*p.cycle)
    return {'cost':sum(costs),'qaly':sum(qalys),'trace':table,'transition':P,'annual_cost':costs,'annual_qaly':qalys}

def compare(p=Cohort()):
    standard=evaluate(p);candidate=evaluate(p,True);dc=candidate['cost']-standard['cost'];dq=candidate['qaly']-standard['qaly']
    return {'standard':standard,'candidate':candidate,'delta_cost':dc,'delta_qaly':dq,'icer':dc/dq if abs(dq)>1e-12 else None}

def vector_rewards(prog,ds,dp,rr,price,cs,cp,us,up,horizon=20,cycle=1,discount=.03):
    """Analytic transition; equal exit rates use the exact limit to avoid 0/0."""
    prog,ds,dp,rr,price,cs,cp,us,up=np.broadcast_arrays(prog,ds,dp,rr,price,cs,cp,us,up)
    a=prog*rr+ds;ps=np.exp(-a*cycle);pp=np.exp(-dp*cycle);gap=dp-a
    close=np.abs(gap*cycle)<1e-8
    # Equivalent to h*(exp(-a*dt)-exp(-dp*dt))/(dp-a), stable near equality.
    ratio=np.empty_like(a,dtype=float)
    np.divide(-np.expm1(-gap*cycle),gap,out=ratio,where=~close)
    ratio[close]=cycle*(1-gap[close]*cycle/2+(gap[close]*cycle)**2/6)
    sp=prog*rr*ps*ratio
    s=np.ones_like(a);q=np.zeros_like(a);cost=np.zeros_like(a);qaly=np.zeros_like(a)
    for i in range(round(horizon/cycle)):
        ns=s*ps;nq=s*sp+q*pp;sm=(s+ns)/2;qm=(q+nq)/2;factor=cycle/(1+discount)**((i+.5)*cycle)
        cost+=(sm*(price+cs)+qm*cp)*factor;qaly+=(sm*us+qm*up)*factor;s,q=ns,nq
    return cost,qaly

def probabilistic(p, rng, draws=20000):
    """Paper parameter distributions are fixed and exposed in docs/parameters.csv."""
    p.validate()
    if draws<1: raise ValueError('Çekiliş sayısı pozitif olmalıdır.')
    prog=rng.gamma(100,.18/100,draws);ds=rng.gamma(100,.03/100,draws);dp=rng.gamma(100,.25/100,draws)
    rr=rng.lognormal(np.log(.72),.18,draws);cp=rng.gamma(25,140000/25,draws);cs=rng.gamma(25,20000/25,draws)
    price=rng.gamma(100,90000/100,draws);premium=rng.gamma(25,50000/25,draws)
    us=rng.beta(80,20,draws);up=us*rng.beta(62.5,37.5,draws)
    kwargs=dict(horizon=p.horizon,cycle=p.cycle,discount=p.discount)
    c0,q0=vector_rewards(prog,ds,dp,1,price,cs,cp,us,up,**kwargs)
    c1,q1=vector_rewards(prog,ds,dp,rr,price+premium,cs,cp,us,up,**kwargs)
    return pd.DataFrame({'delta_cost':c1-c0,'delta_qaly':q1-q0,'relative_rate':rr})

def decision_curves(draws, thresholds=None):
    thresholds=np.linspace(0,2000000,101) if thresholds is None else np.asarray(thresholds)
    if len(draws)==0 or not np.isfinite(draws[['delta_cost','delta_qaly']].to_numpy()).all(): raise ValueError('Geçerli çekilişler gerekli.')
    rows=[]
    for threshold in thresholds:
        nb=threshold*draws.delta_qaly.to_numpy()-draws.delta_cost.to_numpy();mean=nb.mean()
        rows.append({'threshold':float(threshold),'probability':float(np.mean(nb>0)),'expected_nmb':float(mean),
                     'evpi':float(np.maximum(nb,0).mean()-max(0,mean))})
    return pd.DataFrame(rows)

def simulate_people(p=Cohort(), n=10000, seed=42, candidate=True):
    """First-order discrete-time Monte Carlo; does not generate clinical evidence."""
    if not isinstance(n,int) or n<1: raise ValueError('Sanal kişi sayısı pozitif tam sayı olmalıdır.')
    P=transition(p,candidate);rng=np.random.default_rng(seed);states=np.zeros(n,dtype=int);trace=[];paths=[states[:30].copy()]
    for i in range(round(p.horizon/p.cycle)+1):
        trace.append(np.bincount(states,minlength=3)/n)
        if i==round(p.horizon/p.cycle): break
        u=rng.random(n);states=(u[:,None]>np.cumsum(P[states],axis=1)).sum(axis=1);states=np.minimum(states,2);paths.append(states[:30].copy())
    df=pd.DataFrame(trace,columns=['stable','progressed','dead']);df.insert(0,'year',np.arange(len(df))*p.cycle)
    return df,np.array(paths).T
