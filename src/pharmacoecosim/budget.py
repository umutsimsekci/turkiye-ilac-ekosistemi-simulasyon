"""Budget impact in billion constant 2025 TRY; negative delta cost is saving."""
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd
from scipy.stats import norm

@dataclass(frozen=True)
class Budget:
    population: int = 100000
    price: float = 100000.0
    discount: float = .25
    monitoring: float = 2000.0
    capex_bn: float = 1.5
    annual_bn: float = .1
    rate: float = .03
    usual: tuple = (.1, .15, .2, .25, .3)
    programme: tuple = (.1, .35, .6, .75, .8)

    def validate(self):
        values=[self.population,self.price,self.discount,self.monitoring,self.capex_bn,self.annual_bn,self.rate,*self.usual,*self.programme]
        if not np.isfinite(values).all(): raise ValueError('Bütçe girdileri sonlu olmalıdır.')
        if self.population<=0 or self.price<=0 or not 0<=self.discount<=1: raise ValueError('N ve fiyat pozitif, fiyat farkı 0–1 olmalıdır.')
        if min(self.monitoring,self.capex_bn,self.annual_bn,self.rate)<0: raise ValueError('Maliyet ve iskonto negatif olamaz.')
        if not len(self.usual)==len(self.programme)>0: raise ValueError('Kullanım serileri aynı uzunlukta olmalıdır.')
        if np.any(np.array(self.programme)<self.usual) or min(*self.usual,*self.programme)<0 or max(*self.usual,*self.programme)>1:
            raise ValueError('Paylar 0–1 olmalı; program payı karşılaştırıcıdan düşük olamaz.')

def evaluate(p=Budget(), delay=0, uptake_scale=1.0):
    p.validate();h=len(p.usual)
    if not isinstance(delay,(int,np.integer)) or delay<0: raise ValueError('Gecikme negatif olmayan tam yıl olmalıdır.')
    if not np.isfinite(uptake_scale) or uptake_scale<0: raise ValueError('Kullanım ölçeği negatif olamaz.')
    delta=(np.array(p.programme)-p.usual)*uptake_scale
    delta=np.r_[np.zeros(min(delay,h)),delta][:h]
    if np.any(np.array(p.usual)+delta>1+1e-12): raise ValueError('Program kullanım payı %100 değerini aşıyor.')
    switched=p.population*delta;t=np.arange(1,h+1)
    drug=-switched*p.price*p.discount/1e9;monitor=switched*p.monitoring/1e9
    annual=drug+monitor+p.annual_bn;cost=np.r_[p.capex_bn,annual]
    table=pd.DataFrame({'year':np.arange(h+1),'additional_patient_years':np.r_[0,switched],
                        'drug_delta_bn':np.r_[0,drug],'monitor_delta_bn':np.r_[0,monitor],
                        'programme_cost_bn':np.r_[p.capex_bn,np.full(h,p.annual_bn)],
                        'delta_cost_bn':cost,'cumulative_bn':np.cumsum(cost)})
    exposure=switched.sum()*p.price/1e9;pvexp=np.sum(switched/(1+p.rate)**t)*p.price/1e9
    threshold=(p.capex_bn+h*p.annual_bn)/exposure+p.monitoring/p.price if exposure else None
    pvthreshold=(p.capex_bn+np.sum(p.annual_bn/(1+p.rate)**t))/pvexp+p.monitoring/p.price if pvexp else None
    return {'total_bn':float(cost.sum()),'pv_bn':float(p.capex_bn+np.sum(annual/(1+p.rate)**t)),
            'threshold':threshold,'pv_threshold':pvthreshold,'table':table}

def probabilistic(p, rng, draws=20000):
    """Historical paper priors; fixed across years per draw, not patient randomness."""
    p.validate()
    if draws<1: raise ValueError('Çekiliş sayısı pozitif olmalıdır.')
    if len(p.usual)!=5: raise ValueError('Makale PSA dağılımları beş yıllık ufuk içindir.')
    z=rng.multivariate_normal([0,0],[[1,.35],[.35,1]],draws)
    discount=.1+.3*norm.cdf(z[:,0]);scale=.5+.7*norm.cdf(z[:,1])
    capex=rng.triangular(.75,1.5,3,draws);annual=rng.triangular(.05,.1,.2,draws)
    monitoring=rng.triangular(1000,2000,4000,draws)
    sw=p.population*(np.array(p.programme)-p.usual)[None,:]*scale[:,None]
    if np.any(np.array(p.usual)[None,:]+sw/p.population>1+1e-12): raise ValueError('PSA kullanım dağılımı fiziksel pay sınırını aşıyor.')
    costs=sw*(-p.price*discount[:,None]+monitoring[:,None])/1e9+annual[:,None]
    return pd.DataFrame({'discount':discount,'uptake_scale':scale,'capex_bn':capex,'annual_bn':annual,
                         'monitoring_tl':monitoring,'total_bn':capex+costs.sum(1),
                         'pv_bn':capex+np.sum(costs/(1+p.rate)**np.arange(1,6),axis=1)})

def surface(p=Budget()):
    return pd.DataFrame([{'discount_pct':float(d*100),'delay':lag,'total_bn':evaluate(replace(p,discount=float(d)),lag)['total_bn']}
                         for lag in range(5) for d in np.linspace(.05,.45,81)])
