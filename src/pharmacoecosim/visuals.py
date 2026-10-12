"""Publication figures and self-contained offline Plotly animations."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.animation import FuncAnimation, PillowWriter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

COLORS=['#156082','#E97132','#7A4EAB','#59656f']
STATES=['stable','progressed','dead'];LABELS=['Stabil','İlerlemiş','Ölüm']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def comma(x,pos=None):return f'{x:g}'.replace('.',',')
def clean(ax):
    ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True);ax.xaxis.set_major_formatter(FuncFormatter(comma));ax.yaxis.set_major_formatter(FuncFormatter(comma))
def save(fig,out,name):
    for suffix in ['png','pdf','svg']:fig.savefig(out/(name+'.'+suffix),dpi=320,bbox_inches='tight',facecolor='white')
    plt.close(fig)
def layout(fig,title,x,y):
    fig.update_layout(title=title,template='plotly_white',font=dict(family='Arial',size=15),height=480,
                      xaxis_title=x,yaxis_title=y,margin=dict(l=70,r=25,t=75,b=65),legend=dict(orientation='h',y=1.08))
    return fig

def cohort_plot(traces):
    fig=go.Figure()
    for j,(arm,df) in enumerate(traces):
        for i,(state,label) in enumerate(zip(STATES,LABELS)):
            fig.add_trace(go.Scatter(x=df.year,y=df[state]*100,name=arm+' · '+label,mode='lines',
                       line=dict(color=COLORS[i],dash='dash' if j==0 else 'solid',width=2),hovertemplate='%{x:.1f} yıl · %{y:.2f}%<extra>%{fullData.name}</extra>'))
    return layout(fig,'Durum dağılımı','Yıl','Sanal kohort payı (%)')

def budget_plot(table):
    fig=go.Figure([go.Bar(x=table.year,y=table.delta_cost_bn,name='Yıllık ek maliyet',marker_color=COLORS[0]),
                   go.Scatter(x=table.year,y=table.cumulative_bn,name='Birikimli ek maliyet',mode='lines+markers',line_color=COLORS[2])])
    fig.add_hline(y=0,line_color='#444',line_width=1)
    return layout(fig,'Bütçe akışı','Program yılı (0 = yatırım)','Milyar sabit 2025 TL')

def export(out,config,tables,summary):
    out=Path(out);figdir=out/'figures';htmldir=out/'interactive';animdir=out/'animations'
    for p in [figdir,htmldir,animdir]:p.mkdir(exist_ok=True)
    trace=tables['cohort_trace'];standard=trace[trace.arm=='Standart'];candidate=trace[trace.arm=='Aday'];micro=tables['cohort_microsimulation']
    fig,ax=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    for i,(state,label) in enumerate(zip(STATES,LABELS)):
        ax[0].plot(standard.year,100*standard[state],ls='--',color=COLORS[i]);ax[0].plot(candidate.year,100*candidate[state],label=label,color=COLORS[i])
        ax[1].plot(candidate.year,100*candidate[state],color=COLORS[i]);ax[1].scatter(micro.year,100*micro[state],marker='o',s=13,facecolors='none',edgecolors=COLORS[i])
    ax[0].set(title='A  Analitik kohort',xlabel='Yıl',ylabel='Kohort payı (%)',ylim=(0,100));ax[0].legend(frameon=False)
    ax[1].set(title=f'B  {config["process_simulation"]["patients"]:,} sanal kişi'.replace(',','.'),xlabel='Yıl',ylabel='Kohort payı (%)',ylim=(0,100))
    fig.supxlabel('Kesikli: standart · Düz: aday · Halkalar: tek Monte Carlo tekrarı',fontsize=10)
    for a in ax:clean(a)
    save(fig,figdir,'S1_kohort_dinamikleri')

    s=tables['budget_surface'].pivot(index='delay',columns='discount_pct',values='total_bn')
    fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained')
    x=s.columns.to_numpy();y=s.index.to_numpy();v=max(abs(s.to_numpy().min()),abs(s.to_numpy().max()))
    im=ax.pcolormesh(x,y,s,cmap='PuOr_r',vmin=-v,vmax=v,shading='nearest')
    contour=ax.contour(x,y,s,levels=[0],colors='black',linewidths=1.5);ax.clabel(contour,fmt={0:'Başabaş'},fontsize=10)
    ax.set(xlabel='Net fiyat farkı (%)',ylabel='Gecikme (yıl)',yticks=y,title='Varsayımsal programda fiyat ve gecikme');fig.colorbar(im,ax=ax,label='Beş yıllık ek maliyet (milyar TL)',format=FuncFormatter(comma))
    save(fig,figdir,'S2_fiyat_gecikme_yuzeyi')

    paths=tables['sample_patient_paths'].to_numpy()
    from matplotlib.colors import ListedColormap, BoundaryNorm
    fig,ax=plt.subplots(figsize=(10,4.4),layout='constrained');im=ax.imshow(paths,aspect='auto',interpolation='nearest',cmap=ListedColormap(COLORS[:3]),norm=BoundaryNorm([-.5,.5,1.5,2.5],3))
    ax.set(xlabel='Döngü sonu',ylabel='Sanal kişi',title='İlk 30 sanal kişinin durum geçişleri')
    cb=fig.colorbar(im,ax=ax,ticks=[0,1,2]);cb.ax.set_yticklabels(LABELS);save(fig,figdir,'S3_sanal_hasta_yollari')

    pipe=tables['research_process_draws'];div=tables['research_diversification']
    fig,ax=plt.subplots(1,2,figsize=(12,4.4),layout='constrained')
    last=pipe.iloc[:,-1];bins=np.arange(last.min()-.5,last.max()+1.5)
    ax[0].hist(last,bins=bins,color=COLORS[0],density=True,rwidth=.95);ax[0].axvline(summary['process_checks']['analytic_expected_approvals'],color='#333',ls='--')
    ax[0].set(xlabel='100 adaydan ruhsata ulaşan sayı',ylabel='Göreli sıklık',title='A  Süreç rastlantısallığı')
    for i,rho in enumerate([0,.15,.3]):
        d=div[div.rho==rho];ax[1].plot(d.candidates,d.probability*100,color=COLORS[i],label=f'Korelasyon {rho:g}'.replace('.',','))
    ax[1].set(xlabel='Faz I aday sayısı',ylabel='En az bir başarı olasılığı (%)',ylim=(0,100),title='B  Ortak başarısızlık riski');ax[1].legend(frameon=False)
    for a in ax:clean(a)
    save(fig,figdir,'S4_arastirma_surec_simulasyonu')

    curves=tables['ceac_evpi'];draws=tables['cohort_draws'];bd=tables['budget_draws']
    fig,ax=plt.subplots(1,3,figsize=(14,4.4),layout='constrained')
    ax[0].scatter(draws.delta_qaly[::8],draws.delta_cost[::8]/1000,s=6,alpha=.14,color=COLORS[0],rasterized=True)
    ax[0].axvline(0,color='#555',lw=.8);ax[0].axhline(0,color='#555',lw=.8)
    ax[0].set(xlabel='Ek QALY / kişi',ylabel='Ek maliyet (bin TL / kişi)',title='A  Parametre belirsizliği')
    ax[1].plot(curves.threshold/1000,curves.probability*100,color=COLORS[0]);ax[1].set(xlabel='Örnek eşik (bin TL/QALY)',ylabel='Maliyet etkili olma olasılığı (%)',ylim=(0,100),title='B  Kabul edilebilirlik')
    ax[2].plot(curves.threshold/1000,curves.evpi/1000,color=COLORS[2]);ax[2].set(xlabel='Örnek eşik (bin TL/QALY)',ylabel='EVPI (bin TL / kişi)',title='C  Tam bilginin değeri')
    for a in ax:clean(a)
    save(fig,figdir,'S5_karar_belirsizligi')

    front=tables['portfolio_frontier'];allp=tables['portfolio_all']
    fig,ax=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
    for i,threshold in enumerate([500000,1000000,1500000]):
        d=front[front.threshold==threshold];ax[0].step(d.budget_bn,d.enmb_bn,where='post',color=COLORS[i],label=f'{threshold/1e6:g} milyon TL/QALY'.replace('.',','))
    ax[0].set(xlabel='Bütçe sınırı (milyar TL)',ylabel='Beklenen net sağlık değeri (milyar TL)',title='A  Proje seçim sınırı');ax[0].legend(frameon=False,fontsize=9)
    for valid,color,lab in [(False,'#bfc4ca','Koşulları sağlamayan'),(True,COLORS[0],'Uygun portföy')]:
        d=allp[allp.feasible==valid];ax[1].scatter(d.spent_bn,d.enmb_bn,color=color,label=lab,s=25)
    opt=summary['portfolio'];ax[1].scatter([opt['spent_bn']],[opt['enmb_bn']],s=90,marker='*',color=COLORS[1],label='Seçilen')
    ax[1].set(xlabel='Yatırım (milyar TL)',ylabel='Beklenen net sağlık değeri (milyar TL)',title='B  64 proje bileşimi');ax[1].legend(frameon=False,fontsize=9)
    for a in ax:clean(a)
    save(fig,figdir,'S6_portfoy_secimi')

    fig,ax=plt.subplots(figsize=(8.5,4.8));lines=[ax.plot([],[],color=COLORS[i],label=l,lw=2)[0] for i,l in enumerate(LABELS)]
    ax.set(xlim=(0,config['cohort']['horizon']),ylim=(0,100),xlabel='Yıl',ylabel='Kohort payı (%)');ax.legend(frameon=False);clean(ax)
    def update(k):
        for line,state in zip(lines,STATES):line.set_data(candidate.year.iloc[:k+1],100*candidate[state].iloc[:k+1])
        ax.set_title(f'Varsayımsal aday tedavi · yıl {candidate.year.iloc[k]:g}')
        return lines
    anim=FuncAnimation(fig,update,frames=len(candidate),interval=180,blit=False);anim.save(animdir/'kohort.gif',writer=PillowWriter(fps=5),dpi=110);plt.close(fig)

    plots=[('Kohort dinamikleri',cohort_plot([('Standart',standard),('Aday',candidate)])),('Bütçe etkisi',budget_plot(tables['budget_annual']))]
    heat=go.Figure(go.Heatmap(x=x,y=y,z=s.to_numpy(),colorscale='PuOr',zmid=0,colorbar=dict(title='Milyar TL'),hovertemplate='Fark %{x:.1f}%<br>Gecikme %{y} yıl<br>Ek maliyet %{z:.3f} milyar TL<extra></extra>'))
    plots.append(('Fiyat ve gecikme',layout(heat,'Fiyat ve gecikme duyarlılığı','Net fiyat farkı (%)','Gecikme (yıl)')))
    frames=[]
    # Named frames use explicit state values; all frames are computed in Python.
    for _,row in candidate.iterrows():frames.append(go.Frame(name=str(row.year),data=[go.Bar(x=LABELS,y=row[STATES].to_numpy(dtype=float)*100,marker_color=COLORS[:3])]))
    animation=go.Figure(data=frames[0].data,frames=frames);layout(animation,'Yıllara göre durum dağılımı','Durum','Kohort payı (%)');animation.update_yaxes(range=[0,100])
    animation.update_layout(updatemenus=[dict(type='buttons',direction='left',y=-.2,buttons=[dict(label='Oynat',method='animate',args=[None,{'frame':{'duration':250,'redraw':True},'fromcurrent':True}]),dict(label='Duraklat',method='animate',args=[[None],{'frame':{'duration':0},'mode':'immediate'}])])],sliders=[dict(currentvalue={'prefix':'Yıl '},steps=[dict(label=f.name,method='animate',args=[[f.name],{'mode':'immediate','frame':{'duration':0,'redraw':True}}]) for f in frames])],height=570)
    plots.append(('Kohort animasyonu',animation))
    fig=go.Figure()
    for i,rho in enumerate([0,.15,.3]):
        d=div[div.rho==rho];fig.add_trace(go.Scatter(x=d.candidates,y=d.probability*100,name=f'Korelasyon {rho}',line_color=COLORS[i]))
    plots.append(('Ar-Ge riski',layout(fig,'Aday sayısı ve ortak risk','Aday sayısı','En az bir başarı olasılığı (%)')))
    fig=go.Figure()
    for i,threshold in enumerate([500000,1000000,1500000]):
        d=front[front.threshold==threshold];fig.add_trace(go.Scatter(x=d.budget_bn,y=d.enmb_bn,line=dict(shape='hv',color=COLORS[i]),name=f'{threshold/1e6:g} milyon TL/QALY',customdata=d.selected,hovertemplate='Bütçe %{x:.1f}<br>Değer %{y:.3f}<br>Seçim %{customdata}<extra></extra>'))
    plots.append(('Portföy',layout(fig,'Portföy sınırı','Bütçe (milyar TL)','Beklenen net sağlık değeri (milyar TL)')))
    from html import escape
    blocks=[]
    for i,(title,plot) in enumerate(plots):
        blocks.append('<section><h2>'+escape(title)+'</h2>'+plot.to_html(full_html=False,include_plotlyjs=True if i==0 else False,div_id=f'model-{i}',config={'responsive':True,'displaylogo':False,'toImageButtonOptions':{'format':'svg'}})+'</section>')
    html='<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>İlaç ekosistemi simülasyonları</title><style>body{margin:0;background:#f4f7fa;color:#182b3a;font:17px/1.6 Arial,sans-serif}main{max-width:1150px;margin:auto;padding:32px 18px}section{background:white;padding:20px;margin:28px 0;border-radius:8px}h1{line-height:1.2}h2{font-size:22px}.note{border-left:4px solid #156082;padding:12px 18px;background:#e9f2f6}</style><main><p>PHARMACOECOSIM · v1.0.0</p><h1>İlaç ekosistemi simülasyonları</h1><p class="note">Bütün karar modelleri varsayımsaldır. Bunlar Türkiye için doğrulanmış sonuçlar değildir. Bu dosya çevrimdışı çalışır; önceden hesaplanmış eğriler ve animasyonlar içerir. Girdileri değiştirip yeniden hesaplamak için Streamlit uygulamasını kullanın.</p>'+''.join(blocks)+'</main></html>'
    (htmldir/'simulasyonlar.html').write_text(html,encoding='utf8')
