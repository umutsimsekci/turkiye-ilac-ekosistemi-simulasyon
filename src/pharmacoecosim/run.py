"""CLI entry point: data, numerical results, static and interactive figures."""
from pathlib import Path
from dataclasses import replace, asdict
import argparse, json, hashlib, platform, importlib.metadata
import numpy as np
import pandas as pd
from . import budget, cohort, research, portfolio, __version__

def run(config_path, out, draws=None, seed=None, visuals=True):
    config_path=Path(config_path);config=json.loads(config_path.read_text('utf8'))
    draws=int(draws if draws is not None else config['draws']);seed=int(seed if seed is not None else config['seed'])
    if draws<1:raise ValueError('En az bir olasılıksal çekiliş gerekli.')
    out=Path(out);data=out/'data';data.mkdir(parents=True,exist_ok=True)
    bp=budget.Budget(**config['budget']);cp=cohort.Cohort(**config['cohort']);rp=research.Research(**config['research'])
    b=budget.evaluate(bp);c=cohort.compare(cp);r=research.evaluate(rp);p=portfolio.optimize(**config['portfolio'])
    rng=np.random.default_rng(seed)
    # Preserve the original paper's draw order: BIA, then cost-utility PSA.
    bd=budget.probabilistic(budget.Budget(),rng,draws)
    cd=cohort.probabilistic(cohort.Cohort(),rng,draws)
    curves=cohort.decision_curves(cd)
    tables={'budget_annual':b['table'],'budget_surface':budget.surface(bp),'budget_draws':bd,
            'cohort_draws':cd,'ceac_evpi':curves,'portfolio_frontier':portfolio.frontier(),
            'portfolio_all':portfolio.enumerate_portfolios(**config['portfolio']),'portfolio_inputs':portfolio.projects()}
    tables['cohort_trace']=pd.concat([v['trace'].assign(arm=arm) for arm,v in [('Standart',c['standard']),('Aday',c['candidate'])]],ignore_index=True)
    rows=[]
    for label,changes,delay,scale in [('Temel',{},0,1),('Fiyat farkı %15',{'discount':.15},0,1),('Fiyat farkı %35',{'discount':.35},0,1),('Yatırım 3 milyar',{'capex_bn':3},0,1),('Bir yıl gecikme',{},1,1),('İki yıl gecikme',{},2,1),('Kullanımın yarısı',{},0,.5)]:
        q=budget.evaluate(replace(bp,**changes),delay,scale);rows.append({'scenario':label,'total_bn':q['total_bn'],'pv_bn':q['pv_bn']})
    tables['budget_scenarios']=pd.DataFrame(rows)
    tables['research_delay']=pd.DataFrame([{'discount':rate,'delay':delay,'rnpv_bn':research.evaluate(replace(rp,rate=rate),delay)['rnpv_bn']} for rate in [.03,.10,.15] for delay in range(4)])
    ps=config['process_simulation'];mic,paths=cohort.simulate_people(cp,int(ps['patients']),int(ps['seed']))
    tables['cohort_microsimulation']=mic;tables['sample_patient_paths']=pd.DataFrame(paths)
    pipe=research.simulate_pipeline(rp,int(ps['candidates']),int(ps['replicates']),int(ps['seed']))
    tables['research_process_draws']=pd.DataFrame(pipe,columns=['Faz I girişi','Faz II girişi','Faz III girişi','Ruhsat başvurusu','Ruhsat başarısı'])
    tables['research_diversification']=pd.DataFrame([{'candidates':n,'rho':rho,'probability':research.at_least_one(r['success'],n,rho)} for rho in [0,.15,.3] for n in range(1,41)])
    tables['cohort_sensitivity']=pd.DataFrame([{'horizon':h,'cycle':dt,'discount':d,'icer':cohort.compare(replace(cp,horizon=h,cycle=dt,discount=d))['icer']} for h in [10,20,40] for dt in [1,.25] for d in [0,.03,.05]])
    for name,df in tables.items():df.to_csv(data/(name+'.csv'),index=False,encoding='utf-8-sig')
    uncertainty={'budget_saving_probability':float((bd.total_bn<0).mean()),'budget_quantiles_bn':np.quantile(bd.total_bn,[.025,.5,.975]).tolist(),
                 'probability_at_500k':float(curves.iloc[25].probability),'evpi_at_500k':float(curves.iloc[25].evpi)}
    summary={'version':__version__,'seed':seed,'draws':draws,'units':'Sabit 2025 TL; toplam bütçe/Ar-Ge/portföy için milyar TL',
             'scope':'Örnek varsayımlar; ulusal veya klinik etki tahmini değil',
             'budget':{k:v for k,v in b.items() if k!='table'},'cohort':{k:v for k,v in c.items() if k not in ['standard','candidate']},
             'research':r,'portfolio':p,'paper_psa':uncertainty,
             'process_checks':{'micro_max_state_difference':float(np.max(np.abs(mic[['stable','progressed','dead']].to_numpy()-c['candidate']['trace'][['stable','progressed','dead']].to_numpy()))),
                               'mean_approvals':float(pipe[:,-1].mean()),'analytic_expected_approvals':ps['candidates']*r['success']}}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'config_used.json').write_text(json.dumps({**config,'draws':draws,'seed':seed},ensure_ascii=False,indent=2),encoding='utf8')
    versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','pandas','matplotlib','plotly']}
    (out/'run_metadata.json').write_text(json.dumps({'python':platform.python_version(),'libraries':versions,'configuration_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),'version':__version__},indent=2),encoding='utf8')
    if visuals:
        from .visuals import export
        export(out,config,tables,summary)
    return summary

def main():
    import sys
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description='Örnek farmakoekonomik simülasyonları yeniden üretir.')
    parser.add_argument('--config',default='config/paper.json');parser.add_argument('--out',default='results')
    parser.add_argument('--draws',type=int);parser.add_argument('--seed',type=int);parser.add_argument('--no-visuals',action='store_true')
    args=parser.parse_args()
    print(json.dumps(run(args.config,args.out,args.draws,args.seed,not args.no_visuals),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
