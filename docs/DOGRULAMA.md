# Doğrulama kaydı

12 Ekim 2026, hesaplama sürümü v1.0.0 / `33d88bf72326d19aa1a0c527b9d55f810f0cfcec`.

- Yerel Windows/Python 3.12.14 ortamında **35 test geçti**.
- Aynı hesaplama commit'i için [GitHub Actions çalıştırması](https://github.com/umutsimsekci/turkiye-ilac-ekosistemi-simulasyon/actions/runs/38221039540) Ubuntu/Python 3.12 üzerinde başarıyla tamamlandı. Bağlantı özel depo erişimi gerektirir.
- Tam 20.000 çekilişli analiz çalıştı; önceki makalenin bütçe, kohort, araştırma ve portföy değerleri toleranslar içinde yeniden üretildi.
- Eğitim defterindeki 8 kod hücresi hatasız çalıştırıldı.
- 10.000 sanal kişide analitik durum paylarından en büyük mutlak fark 0,0105715 (1,057 yüzde puan); bu tek rassal tekrarın çıktısıdır, geçerleme eşiği değildir.
- 100 bağımsız adayın 10.000 tekrarında ortalama onay 12,2568; analitik beklenen sayı 12,285.
- Streamlit AppTest; gecikmeyi 0'dan 2 yıla değiştirince bütçenin −1,68'den +0,62 milyar TL'ye değişmesini ve karşılanamayan portföy koşulunun uyarı vermesini doğruladı.
- Altı yeni statik şekil görsel olarak incelendi. Makale 18, anonim kopya 18, simülasyon eki 7 sayfa olarak render edildi. Ana metinde 3 tablo ve 6 şekil korundu; ek 5 tablo ve 6 şekil içerir. Anonim ve bağlantılı kopyaların ilk 16 sayfası piksel düzeyinde aynıdır; farklı son iki sayfa ayrıca incelendi.

Bu kayıt yazılım iç doğrulamasıdır. Bağımsız klinik veya ulusal veriyle dış doğrulama yapılmadı. Tarayıcı otomasyon ortamı yerel sandbox hatası nedeniyle kullanılamadı; web arayüzü etkileşimleri Streamlit AppTest ile doğrulandı, tarayıcı ekran görüntüsü üzerinden kontrol edilmedi. PDF ve statik şekillerin görsel denetimi tamamlandı.
