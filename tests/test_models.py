from dataclasses import replace
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from pharmacoecosim import budget, cohort, research, portfolio

GOLD=json.loads((Path(__file__).parent/'fixtures/paper_results.json').read_text('utf8'))

def test_budget_reproduces_paper():
    r=budget.evaluate();g=GOLD['bia']
    assert r['total_bn']==pytest.approx(g['undiscounted_bn'])
    assert r['pv_bn']==pytest.approx(g['pv_bn'])
    assert r['threshold']==pytest.approx(g['break_even_discount_undiscounted'])
    assert r['pv_threshold']==pytest.approx(g['break_even_discount_pv'])

def test_budget_cash_identity_and_break_even():
    r=budget.evaluate();t=r['table']
    np.testing.assert_allclose(t.delta_cost_bn,t.drug_delta_bn+t.monitor_delta_bn+t.programme_cost_bn)
    assert t.cumulative_bn.iloc[-1]==pytest.approx(r['total_bn'])
    assert budget.evaluate(replace(budget.Budget(),discount=r['threshold']))['total_bn']==pytest.approx(0,abs=1e-10)

@pytest.mark.parametrize('lag,expected',[(2,.62),(5,2),(20,2)])
def test_delay_preserves_fixed_costs(lag,expected):assert budget.evaluate(delay=lag)['total_bn']==pytest.approx(expected)

def test_no_uptake_threshold_undefined():
    r=budget.evaluate(uptake_scale=0);assert r['threshold'] is None and r['pv_threshold'] is None

@pytest.mark.parametrize('change',[{'population':0},{'discount':1.1},{'price':float('nan')},{'programme':(1,1)},{'monitoring':-1}])
def test_budget_rejects_invalid(change):
    with pytest.raises(ValueError):budget.evaluate(replace(budget.Budget(),**change))

def test_impossible_uptake_rejected():
    with pytest.raises(ValueError):budget.evaluate(uptake_scale=2)

def test_cohort_reproduces_paper():
    r=cohort.compare();g=GOLD['cua']
    for key in ['delta_cost','delta_qaly','icer']:assert r[key]==pytest.approx(g[key],rel=1e-11)
    for arm,old in [('standard','standard'),('candidate','innovative')]:
        assert r[arm]['cost']==pytest.approx(g['cost_'+old]);assert r[arm]['qaly']==pytest.approx(g['qaly_'+old])

def test_transition_semigroup_and_conservation():
    p=cohort.Cohort();a=cohort.transition(p);half=cohort.transition(replace(p,cycle=.5))
    np.testing.assert_allclose(half@half,a,atol=1e-14)
    np.testing.assert_allclose(a.sum(1),1);assert (a>=0).all()
    np.testing.assert_allclose(a[2],[0,0,1])
    trace=cohort.evaluate()['trace'][['stable','progressed','dead']]
    np.testing.assert_allclose(trace.sum(axis=1),1);assert (trace>=0).all().all()

@pytest.mark.parametrize('gap',[0.,1e-12,-1e-12,.04])
def test_vector_equal_and_near_equal_hazards(gap):
    p=replace(cohort.Cohort(),relative_rate=1,death_progressed=.21+gap)
    cost,q=cohort.vector_rewards(p.progression,p.death_stable,p.death_progressed,1,p.price_standard,p.care_stable,p.care_progressed,p.utility_stable,p.utility_progressed)
    r=cohort.evaluate(p);assert float(cost)==pytest.approx(r['cost'],rel=1e-11);assert float(q)==pytest.approx(r['qaly'],rel=1e-11)

def test_identical_arms_zero_differences():
    r=cohort.compare(replace(cohort.Cohort(),relative_rate=1,price_candidate=90000))
    assert r['delta_cost']==0 and r['delta_qaly']==0 and r['icer'] is None

def test_no_benefit_cost_premium():
    r=cohort.compare(replace(cohort.Cohort(),relative_rate=1))
    assert r['delta_qaly']==0 and r['delta_cost']>0 and r['icer'] is None

def test_cohort_invalid_utilities():
    with pytest.raises(ValueError):cohort.evaluate(replace(cohort.Cohort(),utility_progressed=.9))

def test_microsimulation_converges_and_is_absorbing():
    m,paths=cohort.simulate_people(n=50000,seed=7)
    truth=cohort.evaluate(candidate=True)['trace']
    assert np.max(np.abs(m[['stable','progressed','dead']].values-truth[['stable','progressed','dead']].values))<.015
    assert (np.diff(paths,axis=1)>=0).all();np.testing.assert_allclose(m[['stable','progressed','dead']].sum(axis=1),1)

def test_psa_reproduces_paper_draw_order():
    rng=np.random.default_rng(20260922);bd=budget.probabilistic(budget.Budget(),rng);cd=cohort.probabilistic(cohort.Cohort(),rng)
    assert (bd.total_bn<0).mean()==GOLD['bia']['psa_saving_probability']
    np.testing.assert_allclose(np.quantile(bd.total_bn,[.025,.5,.975]),GOLD['bia']['psa_interval_bn'],rtol=1e-10)
    r=cohort.decision_curves(cd,[500000]).iloc[0]
    assert r.probability==GOLD['cua']['prob_at_500k'];assert r.evpi==pytest.approx(GOLD['cua']['evpi_at_500k'],rel=1e-9)

def test_evpi_handles_negative_expected_nmb():
    draws=pd.DataFrame({'delta_qaly':[1,1],'delta_cost':[3,0]})
    row=cohort.decision_curves(draws,[1]).iloc[0]
    assert row.expected_nmb==-.5 and row.evpi==.5 and row.probability==.5

def test_research_reproduces_paper():
    r=research.evaluate();g=GOLD['rd'];assert r['success']==pytest.approx(g['approval_probability'])
    assert r['rnpv_bn']==pytest.approx(g['rnpv_bn']);assert r['break_even_cash_bn']==pytest.approx(g['break_even_annual_cash_bn'])
    assert research.at_least_one(r['success'],10,.15)==pytest.approx(g['success_10_rho_015'])

@pytest.mark.parametrize('p,n,rho,expected',[(0,10,.2,0),(1,10,.2,1),(.2,0,0,0),(.2,1,.2,.2)])
def test_research_probability_boundaries(p,n,rho,expected):assert research.at_least_one(p,n,rho)==pytest.approx(expected)

def test_pipeline_matches_binomial_expectation():
    p=research.Research();x=research.simulate_pipeline(p,n=100,replicates=10000)
    assert (np.diff(x,axis=1)<=0).all()
    success=np.prod(p.probabilities);se=(100*success*(1-success)/10000)**.5
    assert abs(x[:,-1].mean()-100*success)<5*se

def test_portfolio_paper_scenarios():
    for kwargs,g in zip([{}, {'innovation_floor':True},{'stress':True},{'threshold':500000},{'threshold':1500000}],GOLD['portfolio']):
        r=portfolio.optimize(**kwargs);assert r['selected']==g['selected'];assert r['enmb_bn']==pytest.approx(g['enmb_bn'])

def test_portfolio_budget_and_platform_constraints():
    p=portfolio.enumerate_portfolios();assert len(p)==64
    for row in p[p.feasible].itertuples():
        assert row.spent_bn<=8
        assert not ('N1' in row.selected or 'N2' in row.selected) or 'P' in row.selected
    assert portfolio.optimize(budget=0)['selected']==''
    with pytest.raises(ValueError):portfolio.optimize(budget=0,innovation_floor=True)

def test_portfolio_frontier_monotone():
    df=portfolio.frontier()
    for _,part in df.groupby('threshold'):assert (np.diff(part.enmb_bn)>=-1e-10).all()

def test_cli_exports_summary_and_config(tmp_path):
    from pharmacoecosim.run import run
    r=run(Path(__file__).parents[1]/'config/paper.json',tmp_path,draws=30,visuals=False)
    assert r['draws']==30 and (tmp_path/'data/budget_annual.csv').exists()
    assert json.loads((tmp_path/'config_used.json').read_text('utf8'))['draws']==30
