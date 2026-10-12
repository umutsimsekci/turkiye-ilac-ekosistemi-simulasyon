"""Local, Turkish simulation laboratory; no external data or account required."""
from dataclasses import replace, asdict
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pharmacoecosim import budget, cohort, research, portfolio
from pharmacoecosim.visuals import cohort_plot, budget_plot, layout, COLORS

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='İlaç ekosistemi | Simülasyon',page_icon='🧮',layout='wide')
st.title('Türkiye ilaç ekosistemi: simülasyon laboratuvarı')
st.caption('PHARMACOECOSIM 1.0.0 · Makalenin yeniden üretilebilir hesaplama eki')
st.info('Karar modellerindeki değerler örnek varsayımlardır. Sonuçlar Türkiye için doğrulanmış tasarruf, klinik etkinlik veya yatırım getirisi tahmini değildir. Parasal değerler sabit 2025 TL olarak tanımlanmıştır.')
tabs=st.tabs(['Nasıl okunur?', 'Bütçe etkisi', 'Sağlık kazanımı', 'Ar-Ge riski', 'Portföy seçimi', 'Makale belirsizliği'])

def number(value,digits=2):
    return f'{value:,.{digits}f}'.replace(',','X').replace('.',',').replace('X','.')

def chart(fig):st.plotly_chart(fig,width='stretch',theme=None)

with tabs[0]:
    st.subheader('Aynı sorunun dört farklı hesabı')
    st.markdown('1. **Bütçe:** Program, mevcut eğilime göre beş yılda ne kadar ek harcama veya tasarruf getirir?\n2. **Sağlık:** Örnek bir adayın ek maliyeti, kazandırdığı kaliteli yaşam yılına değer mi?\n3. **Ar-Ge:** Başarısızlık olasılığı ve bekleme süresi, yatırım değerini nasıl değiştirir?\n4. **Portföy:** Sınırlı bütçeyle hangi proje bileşimi en yüksek beklenen net sağlık değerini sağlar?')
    st.markdown('Kaydırıcılar deterministik hesapları anında yeniden yapar. **Makale belirsizliği** sekmesi ise makalenin sabit dağılımlarını ve 20.000 çekilişini kullanır; diğer sekmelerdeki değişiklikler bu dağılımları değiştirmez.')
    st.subheader('Gözlem verisi')
    st.caption('Kaynakların 22 Eylül 2026 tarihli makale derlemesi. Bu göstergeler hastalık modeline kalibrasyon sağlamaz. Farklı yıl, para birimi ve kapsamlar tek toplamda birleştirilmez.')
    path=ROOT/'data/observed/observed_macro.csv'
    if path.exists():st.dataframe(pd.read_csv(path),width='stretch',hide_index=True)
    st.markdown('Matematik ve kaynak ayrıntıları: `docs/MATEMATIK.md`, `docs/PARAMETRELER.csv`, `data/observed/README.md`.')

with tabs[1]:
    left,right=st.columns([1,2])
    with left:
        discount=st.slider('Net fiyat farkı (%)',0,50,25,key='bia_discount')/100
        delay=st.slider('Programa giriş gecikmesi (yıl)',0,5,0,key='bia_delay')
        capex=st.slider('Başlangıç yatırımı (milyar TL)',0.,4.,1.5,.1,key='bia_capex')
        scale=st.slider('Ek kullanım ölçeği',0.,1.2,1.,.05,key='bia_scale')
        n=st.number_input('Uygun kişi sayısı',1000,1000000,100000,1000,key='bia_n')
    bp=replace(budget.Budget(),discount=discount,capex_bn=capex,population=n)
    br=budget.evaluate(bp,delay,scale)
    with right:
        a,b,c=st.columns(3)
        a.metric('Beş yıllık ek maliyet',number(br['total_bn'])+' milyar TL')
        b.metric('İskontolu ek maliyet',number(br['pv_bn'])+' milyar TL')
        c.metric('Başabaş fiyat farkı','Tanımsız' if br['threshold'] is None else number(br['threshold']*100)+'%')
        st.caption('Negatif ek maliyet tasarruftur. Kullanım artışı gerçekleşmese de yatırım ve yıllık program maliyeti ödenir.')
        chart(budget_plot(br['table']))
    st.download_button('Yıllık bütçe tablosunu indir',br['table'].to_csv(index=False).encode('utf-8-sig'),'butce.csv','text/csv')

with tabs[2]:
    left,right=st.columns([1,2])
    with left:
        rr=st.slider('İlerleme hız oranı (aday / standart)',.2,1.4,.72,.01,key='cua_rr')
        price=st.slider('Aday yıllık ilaç maliyeti (TL)',50000,250000,140000,5000,key='cua_price')
        horizon=st.select_slider('İzlem ufku (yıl)',[10,20,40],20,key='cua_horizon')
        threshold=st.slider('Örnek karar eşiği (TL/QALY)',0,2000000,500000,50000,key='cua_lambda')
        cycle=st.selectbox('Döngü uzunluğu (yıl)',[1.,.25],key='cua_cycle')
    cp=replace(cohort.Cohort(),relative_rate=rr,price_candidate=price,horizon=horizon,cycle=cycle)
    cr=cohort.compare(cp)
    with right:
        a,b,c=st.columns(3)
        a.metric('Ek QALY / kişi',number(cr['delta_qaly'],3));b.metric('Ek maliyet / kişi',number(cr['delta_cost'],0)+' TL')
        c.metric('Net parasal sağlık faydası / kişi',number(threshold*cr['delta_qaly']-cr['delta_cost'],0)+' TL')
        if cr['delta_qaly']>0 and cr['delta_cost']>=0:st.caption('ICER: '+number(cr['icer'],0)+' TL/QALY. Eşik varsayımsaldır; Türkiye için resmî eşik olarak yorumlanamaz.')
        elif abs(cr['delta_qaly'])<1e-12:st.caption('Sağlık kazanımı farkı sıfır: ICER tanımsızdır; maliyet farkını değerlendirin.')
        elif cr['delta_qaly']<=0 and cr['delta_cost']>=0:st.caption('Aday, bu girdilerle daha iyi sağlık sonucu sağlamadan daha pahalıdır.')
        else:st.caption('Maliyet ve sağlık etkisinin yönünü birlikte değerlendirin; tek başına negatif ICER karar kuralı değildir.')
        chart(cohort_plot([('Standart',cr['standard']['trace']),('Aday',cr['candidate']['trace'])]))
    st.caption('Stabil → ilerlemiş → ölüm. İlaç maliyeti yalnız stabil durumda uygulanır. Durum olasılıkları matris üssüyle, maliyet ve QALY döngü ortası iskonto ve trapez düzeltmesiyle hesaplanır.')

with tabs[3]:
    left,right=st.columns([1,2])
    with left:
        count=st.slider('Bağımsız veya ortak risk taşıyan aday sayısı',1,40,10,key='rd_n')
        rho=st.slider('Adaylar arası ortak risk korelasyonu',0.,.6,.15,.05,key='rd_rho')
        rate=st.slider('Reel yatırım iskonto oranı (%)',0,25,10,key='rd_rate')/100
        lag=st.slider('Gelir başlangıcı gecikmesi (yıl)',0,5,0,key='rd_delay')
        cash=st.slider('Başarı halinde yıllık net nakit (milyar TL)',0.,8.,4.,.1,key='rd_cash')
    rp=replace(research.Research(),rate=rate,annual_cash_bn=cash);rrr=research.evaluate(rp,lag)
    with right:
        a,b,c=st.columns(3)
        a.metric('Tek aday başarı olasılığı',number(rrr['success']*100)+'%')
        b.metric('En az bir başarı',number(100*research.at_least_one(rrr['success'],count,rho))+'%')
        c.metric('Tek aday rNPV',number(rrr['rnpv_bn'],3)+' milyar TL')
        fig=go.Figure()
        for corr,label,color in [(0,'Bağımsız',COLORS[0]),(rho,'Seçilen ortak risk',COLORS[2])]:
            fig.add_trace(go.Scatter(x=list(range(1,41)),y=[100*research.at_least_one(rrr['success'],k,corr) for k in range(1,41)],name=label,line_color=color))
        chart(layout(fig,'Çeşitlendirme ve ortak risk','Aday sayısı','En az bir başarı olasılığı (%)'))
    st.caption('Korelasyon beta-binomial ortak risk modeliyle tanımlanır. Grafikte aday sayısına bağlı başarı olasılığı; rNPV kutusunda ise tek adayın değeri vardır. Gelir gecikmesi aşama maliyetlerini ötelemez ve 10 yıllık gelir süresini kısaltmaz.')

with tabs[4]:
    left,right=st.columns([1,2])
    with left:
        pb=st.slider('Toplam yatırım bütçesi (milyar TL)',0.,12.,8.,.1,key='port_budget')
        pl=st.slider('Portföy eşiği (TL/QALY)',0,2000000,1000000,50000,key='port_lambda')
        gain=st.slider('Platformun göreli başarı artışı (%)',0,30,10,key='port_gain')/100
        stress=st.checkbox('Birleşik olumsuz senaryo',key='port_stress')
        floor=st.checkbox('En az bir erişim ve bir yenilik projesi zorunlu',key='port_floor')
    pk=dict(budget=pb,threshold=pl,platform_gain=gain,stress=stress,innovation_floor=floor)
    allp=portfolio.enumerate_portfolios(**pk)
    with right:
        try:
            pr=portfolio.optimize(**pk)
            a,b,c=st.columns(3);a.metric('Seçilen projeler',pr['selected'] or 'Yatırım yok');b.metric('Yatırım',number(pr['spent_bn'])+' milyar TL');c.metric('Beklenen net sağlık değeri',number(pr['enmb_bn'],3)+' milyar TL')
        except ValueError:st.warning('Bu bütçe ve zorunlu proje koşullarıyla uygun portföy yok.')
        fig=go.Figure()
        for valid,label,color in [(False,'Uygun olmayan','#bfc4ca'),(True,'Uygun',COLORS[0])]:
            subset=allp[allp.feasible==valid];fig.add_trace(go.Scatter(x=subset.spent_bn,y=subset.enmb_bn,text=subset.selected,mode='markers',name=label,marker_color=color,hovertemplate='%{text}<br>Yatırım %{x:.2f}<br>Değer %{y:.3f}<extra></extra>'))
        chart(layout(fig,'64 proje bileşimi','Yatırım (milyar TL)','Beklenen net sağlık değeri (milyar TL)'))
    st.dataframe(portfolio.projects(),hide_index=True,width='stretch')
    st.caption('P: ortak platform; N1 ve N2 için zorunlu. Platformun tek başına QALY getirisi yoktur. Ar-Ge bölümündeki ticari nakit akışı bu sağlık değerine eklenmez.')

@st.cache_data
def paper_uncertainty():
    rng=np.random.default_rng(20260922)
    bd=budget.probabilistic(budget.Budget(),rng,20000)
    cd=cohort.probabilistic(cohort.Cohort(),rng,20000)
    return bd,cohort.decision_curves(cd)

with tabs[5]:
    st.subheader('Sabit makale senaryosu: 20.000 parametre çekilişi')
    st.caption('Tohum: 20260922. Bu sekme diğer sekmelerdeki kaydırıcıları kullanmaz. Aralıklar varsayılan parametre dağılımlarının sonucudur; gözlemsel güven aralığı değildir.')
    bd,curves=paper_uncertainty();row=curves[curves.threshold==500000].iloc[0]
    a,b,c=st.columns(3);a.metric('Bütçe tasarrufu olasılığı',number(100*(bd.total_bn<0).mean())+'%');b.metric('500.000 TL/QALY eşiğinde olasılık',number(100*row.probability)+'%');c.metric('EVPI / kişi',number(row.evpi,0)+' TL')
    fig=go.Figure(go.Scatter(x=curves.threshold,y=curves.probability*100,line_color=COLORS[0]));chart(layout(fig,'Maliyet etkililik kabul edilebilirlik eğrisi','Örnek eşik (TL/QALY)','Olasılık (%)'))
    st.caption('EVPI kişi başına tam bilgi değeridir; araştırma bütçesi olarak kullanmak için uygun nüfus, zaman ve uygulanabilirlik hesabı ayrıca gerekir.')

st.divider()
settings={'budget':asdict(bp),'budget_delay':delay,'budget_uptake_scale':scale,'cohort':asdict(cp),'cohort_threshold':threshold,'research':asdict(rp),'research_delay':lag,'research_candidates':count,'research_correlation':rho,'portfolio':pk}
st.download_button('Ekrandaki senaryo girdilerini indir',json.dumps(settings,ensure_ascii=False,indent=2),'ekran_girdileri.json','application/json')
st.caption('Ekran girdileri kullanıcı senaryosunun kaydıdır; CLI için config/paper.json şemasına ilgili model alanlarını aktarın.')
