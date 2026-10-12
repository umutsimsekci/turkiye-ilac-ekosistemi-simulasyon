# Makale dosyaları

- `Makale_simulasyon_entegre.docx` ve PDF: 18 sayfa, yazar incelemesi için özel depo bağlantısını içerir. Bölüm 2.6 yazılım yöntemini ve yeni süreç simülasyonlarını açıklar; kaynaklardan önce veri/kod erişim beyanı vardır.
- `Makale_simulasyon_anonim.docx` ve PDF: aynı metnin depo bağlantısı ve commit kimliği maskelenmiş kopyası. Bu dosyada makale yazarlarının kimliği eklenmez. Simülasyon ekindeki bağlantı ise maskelenmemiştir; dergiye anonim paket hazırlanırken ayrıca ele alınmalıdır.
- `Matematiksel_simulasyon_eki.docx` ve PDF: 7 sayfa, altı yeni şekil, denklemler, kod eşleştirmesi ve çalıştırma adımları.
- `source/Makale_23Eylul2026.docx`: biçimi korunmuş önceki ana metin. Kaynak olarak saklandı; yeni sürüm bunun üzerine yazılmadı.
- `KOD_ERISIMI.md`: eklenen yöntem ve erişim beyanının düzenlenebilir düz metni.

Hesaplama sürümü: **v1.0.0**, commit `33d88bf72326d19aa1a0c527b9d55f810f0cfcec`. Bu sürüm etiketi hesaplama kodunu sabitler; Word/PDF entegrasyonu sonraki belge commit'inde bulunur. Depo özeldir ve dergiye gönderim yapılmadı. Kaynak kesimi 22 Eylül 2026'dır.

Belgeleri yeniden üretmek için `python-docx` kurulu Python ortamında `python scripts/integrate_manuscript.py` çalıştırın. Belge oluşturma hesabın yeniden çalıştırılmasından ayrıdır. Yeni model girdileriyle sonuç değiştirildiğinde makale metni ve sayılarının ayrıca güncellenmesi gerekir. PDF'ler Word/LibreOffice ile dışa aktarılabilir; sayfa yerleşimi kullanılan yazılım ve yazı tipine bağlı olabilir.
