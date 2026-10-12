# Makale ile kodun eşleştirilmesi

Veri/literatür kesimi: 22 Eylül 2026. Yazılım genişletmesi: 12 Ekim 2026. Yeni simülasyonlar veri kesim tarihini değiştirmez.

| Makale konusu | Kod | Sonuç dosyası | Ek görsel |
|---|---|---|---|
| Ek kullanım ve net bütçe | budget.evaluate | budget_annual.csv | S2 fiyat/gecikme yüzeyi |
| Bütçe belirsizliği | budget.probabilistic | budget_draws.csv; summary.json | Uygulama belirsizlik sekmesi |
| Kohort maliyeti ve QALY | cohort.transition/evaluate | cohort_trace.csv; summary.json | S1 durum payları |
| Sanal hasta yolları | cohort.simulate_people | cohort_microsimulation.csv; sample_patient_paths.csv | S3 yollar; kohort.gif |
| CEAC ve EVPI | cohort.probabilistic/decision_curves | ceac_evpi.csv | S5 belirsizlik |
| Aşamalı araştırma ve rNPV | research.evaluate/simulate_pipeline | research_delay.csv; research_process_draws.csv | S4 aday başarı dağılımı |
| Ortak araştırma riski | research.at_least_one | research_diversification.csv | S4 korelasyon eğrileri |
| Bütçeli proje seçimi | portfolio.enumerate_portfolios/optimize | portfolio_all.csv; portfolio_frontier.csv | S6 seçim sınırı |

Ana makaledeki önceki altı şekil ve temel sonuçlar korunur. Yeni altı görsel, ayrı **Matematiksel simülasyon ve yazılım eki** içinde S1–S6 olarak verilir. Ana makaleye uygulama/yeniden üretilebilirlik yöntemi ve kod erişim beyanı eklenir. Depo kullanıcıyı tanımlayan adres içerdiği için bağlantılı yazar inceleme kopyasından ayrıca bağlantısı maskelenmiş anonim ana metin hazırlanır.

Araştırma histogramı bağımsız adaylara, korelasyon eğrileri beta-binomial modele aittir. Sanal hasta yolları, aynı sabit geçiş matrisinin rassal örneklemesidir. Yeni şekiller yeni klinik veri veya ulusal veri analizi olarak sunulmaz.
