"""Create the teaching notebook. Run from the repository root."""
from pathlib import Path
import nbformat as nbf

cells=[
nbf.v4.new_markdown_cell('# İlaç ekosistemi: modelden simülasyona\n\nBu defterdeki bütün klinik ve ekonomik model girdileri varsayımsaldır. Amaç, makalenin matematiğini çalıştırmak ve parametre değişikliklerinin sonuçlarını incelemektir. Önce depo kökünde `python -m pip install -e ".[app,dev]"` çalıştırın. Python 3.12 çekirdeğini seçin.'),
nbf.v4.new_code_cell('from dataclasses import replace\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\nfrom pharmacoecosim import budget, cohort, research, portfolio\n%matplotlib inline'),
nbf.v4.new_markdown_cell('## 1. Bütçe\n\nEk maliyet = yatırım + işletme + izlem − ilaç tasarrufu. Negatif sonuç tasarruf demektir. Gecikme kullanım artışını erteler; başlangıç gideri ödenir.'),
nbf.v4.new_code_cell("base=budget.evaluate()\nprint('Toplam ek maliyet (milyar TL):',base['total_bn'])\nprint('İki yıl gecikme:',budget.evaluate(delay=2)['total_bn'])\nbase['table']"),
nbf.v4.new_code_cell("surface=budget.surface().pivot(index='delay',columns='discount_pct',values='total_bn')\nfig,ax=plt.subplots(figsize=(9,4))\nim=ax.pcolormesh(surface.columns,surface.index,surface,cmap='PuOr_r',shading='nearest')\nax.contour(surface.columns,surface.index,surface,levels=[0],colors='black')\nax.set(xlabel='Net fiyat farkı (%)',ylabel='Gecikme (yıl)')\nfig.colorbar(im,ax=ax,label='Ek bütçe (milyar TL)');plt.show()"),
nbf.v4.new_markdown_cell('## 2. Kohort ve sanal hasta\n\nStabil, ilerlemiş ve ölüm durumlarını izleriz. Matris üssü analitik beklenen payları, rassal örnekleme ise 10.000 sanal kişinin yollarını verir. Bu kişiler gerçek hasta kaydı değildir.'),
nbf.v4.new_code_cell("p=cohort.Cohort()\nr=cohort.compare(p)\nprint({k:r[k] for k in ['delta_cost','delta_qaly','icer']})\ntrace=r['candidate']['trace']\nmicro,paths=cohort.simulate_people(p,n=10000,seed=20261012)\nfig,ax=plt.subplots(figsize=(9,4))\nfor state in ['stable','progressed','dead']:\n    line=ax.plot(trace.year,trace[state],label=state)[0]\n    ax.scatter(micro.year,micro[state],s=10,color=line.get_color())\nax.set(xlabel='Yıl',ylabel='Pay');ax.legend();plt.show()"),
nbf.v4.new_markdown_cell('## 3. Parametre belirsizliği\n\nMakaledeki 20.000 çekiliş ve sıralama korunur. Burada fiyat, klinik hız ve fayda ağırlıkları değişir; bu, sabit parametreli sanal hasta rastlantısallığından farklıdır.'),
nbf.v4.new_code_cell("rng=np.random.default_rng(20260922)\nbd=budget.probabilistic(budget.Budget(),rng,20000)\ncd=cohort.probabilistic(cohort.Cohort(),rng,20000)\ncurves=cohort.decision_curves(cd)\nprint('Tasarruf olasılığı:',(bd.total_bn<0).mean())\ncurves[curves.threshold==500000]"),
nbf.v4.new_markdown_cell('## 4. Ar-Ge süreci\n\n100 adayın her aşamadaki başarısı binomial çekilişle örneklenir. Bağımsız modelde beklenen onay sayısı 12,285\'tir. Ortak risk korelasyonu ayrı beta-binomial modelde değerlendirilir.'),
nbf.v4.new_code_cell("r=research.evaluate()\nprocess=research.simulate_pipeline()\nprint('rNPV (milyar TL):',r['rnpv_bn'])\nprint('Ortalama onay sayısı:',process[:,-1].mean())\nprint('10 aday, bağımsız:',research.at_least_one(r['success'],10))\nprint('10 aday, korelasyon 0.15:',research.at_least_one(r['success'],10,.15))\nplt.hist(process[:,-1],bins=np.arange(-.5,31.5),density=True)\nplt.xlabel('100 adaydan onay sayısı');plt.ylabel('Göreli sıklık');plt.show()"),
nbf.v4.new_markdown_cell('## 5. Portföy\n\nBeş proje ve bir platformun 64 bileşimi taranır. Amaç, bütçe ve platform koşulları altında beklenen net sağlık değerini artırmaktır. Ticari rNPV bu değere eklenmez.'),
nbf.v4.new_code_cell("print(portfolio.optimize())\nprint('Düşük eşik:',portfolio.optimize(threshold=500000))\nprint('Olumsuz senaryo:',portfolio.optimize(stress=True))\nportfolio.projects()"),
nbf.v4.new_markdown_cell('## Kendi senaryonuz\n\nAşağıdaki fiyat farkını ve gecikmeyi değiştirip tekrar çalıştırın. Bu deterministik değişiklikler yukarıdaki sabit makale PSA dağılımlarını değiştirmez.'),
nbf.v4.new_code_cell("my_budget=replace(budget.Budget(),discount=.15)\nbudget.evaluate(my_budget,delay=1)['table']"),
]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (pharmacoecosim)','language':'python','name':'python3'}})
path=Path('notebooks/01_model_simulasyonlari.ipynb');path.parent.mkdir(exist_ok=True)
nbf.write(nb,path)
