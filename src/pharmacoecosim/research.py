"""Investor cash flow and illustrative development attrition, separately from health NMB."""
from dataclasses import dataclass
import numpy as np
from scipy.special import betaln

@dataclass(frozen=True)
class Research:
    probabilities: tuple = (.65,.35,.60,.90)
    costs_bn: tuple = (.15,.45,1.2,.15)
    years: tuple = (0,2,5,8)
    rate: float = .1
    launch: int = 9
    cash_years: int = 10
    annual_cash_bn: float = 4

    def validate(self):
        if not len(self.probabilities)==len(self.costs_bn)==len(self.years)>0: raise ValueError('Aşama dizileri eşleşmelidir.')
        if not np.isfinite([*self.probabilities,*self.costs_bn,*self.years,self.rate,self.launch,self.cash_years,self.annual_cash_bn]).all(): raise ValueError('Sonlu Ar-Ge girdileri gerekli.')
        if min(self.probabilities)<0 or max(self.probabilities)>1 or min(self.costs_bn)<0 or min(self.years)<0 or self.rate<0 or self.annual_cash_bn<0: raise ValueError('Geçersiz Ar-Ge olasılığı veya maliyeti.')
        if np.any(np.diff(self.years)<0) or self.launch<=max(self.years) or self.cash_years<1 or int(self.cash_years)!=self.cash_years: raise ValueError('Gelir dönemi aşamalardan sonra başlamalıdır.')

def evaluate(p=Research(),delay=0):
    p.validate()
    if not isinstance(delay,int) or delay<0: raise ValueError('Gecikme negatif olmayan tam sayı olmalıdır.')
    probs=np.array(p.probabilities);reach=np.r_[1,np.cumprod(probs)[:-1]];success=float(probs.prod())
    cost=float(np.sum(np.array(p.costs_bn)*reach/(1+p.rate)**np.array(p.years)))
    annuity=float(np.sum((1+p.rate)**(-np.arange(p.launch+delay,p.launch+delay+p.cash_years,dtype=float))))
    revenue=success*p.annual_cash_bn*annuity
    return {'success':success,'reach':reach.tolist(),'expected_cost_bn':cost,'expected_cash_bn':revenue,'rnpv_bn':revenue-cost,
            'break_even_cash_bn':cost/(success*annuity) if success>0 else None}

def at_least_one(probability,n,correlation=0):
    if not 0<=probability<=1 or not 0<=correlation<1 or n<0 or int(n)!=n: raise ValueError('Geçersiz aday sayısı veya korelasyon.')
    if n==0 or probability==0:return 0.
    if probability==1:return 1.
    if correlation==0:return float(-np.expm1(n*np.log1p(-probability)))
    concentration=1/correlation-1;a=probability*concentration;b=(1-probability)*concentration
    return float(-np.expm1(betaln(a,b+n)-betaln(a,b)))

def simulate_pipeline(p=Research(),n=100,replicates=10000,seed=20261012):
    p.validate()
    if n<1 or replicates<1:raise ValueError('Aday ve tekrar sayısı pozitif olmalıdır.')
    rng=np.random.default_rng(seed);counts=np.full(replicates,n,dtype=int);history=[counts.copy()]
    for probability in p.probabilities:counts=rng.binomial(counts,probability);history.append(counts.copy())
    return np.stack(history,axis=1)
