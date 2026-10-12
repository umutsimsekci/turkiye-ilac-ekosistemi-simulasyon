# Matematiksel model ve simülasyon yaklaşımı

## 1. Bütçe: mevcut eğilime karşı program

Yıllık uygun nüfus N, mevcut kullanım payı u₀t, program payı u₁t, referans yıllık ilaç fiyatı c, net fiyat farkı d, kişi başına ek izlem m, başlangıç yatırımı F ve yıllık işletme gideri A'dır. Gecikme L, ek kullanım yolunu sağa kaydırır; boş yıllar sıfırla doldurulur ve beş yıllık ufuk sabit kalır. Karşılaştırıcının payı devam eder. Sabit giderler gecikmeyle ertelenmez.

$$n_t=N(u_{1,t-L}-u_{0,t-L}),\quad \Delta C_0=F,\quad \Delta C_t=n_t(-cd+m)+A.$$

$$\Delta C_{PV}=F+\sum_{t=1}^{5}\frac{\Delta C_t}{(1+r)^t},\qquad d^*=\frac{F+5A}{c\sum_t n_t}+\frac{m}{c}.$$

Eşitliklerde TL kullanılır; kod toplamları 10⁹'a böler. Payda sıfır olduğunda başabaş değer **tanımsızdır**. Negatif maliyet farkı tasarruf demektir. %100 üzerindeki kullanım reddedilir.

PSA'da d~U(0,10;0,40) ve kullanım ölçeği k~U(0,50;1,20), iki standart normal değişkenin Φ dönüşümüyle üretilir. **0,35, latent normal korelasyonudur; dönüştürülmüş değerlerin Pearson korelasyonu olduğu ileri sürülmez.** F~Triangular(0,75;1,50;3), A~Triangular(0,05;0,10;0,20) milyar TL; m~Triangular(1000;2000;4000) TL. Diğer değişkenler bağımsızdır. Bir çekilişteki değerler tüm yıllarda sabittir. Bunlar gözlem verisinden kestirilmiş dağılımlar değildir.

## 2. Sağlık: üç durumlu kohort

Stabil (S), ilerlemiş (P) ve ölüm (D) durumları vardır. Hızlar yıllıktır: ilerleme h, stabil ölüm μS ve ilerlemiş ölüm μP. Aday için yalnız h, hız oranı RR ile çarpılır. Geri dönüş yoktur; ölüm emicidir.

$$Q=\begin{pmatrix}-(h+\mu_S)&h&\mu_S\\0&-\mu_P&\mu_P\\0&0&0\end{pmatrix},\quad P(\Delta t)=e^{Q\Delta t},\quad x_{k+1}=x_kP(\Delta t).$$

Başlangıç x₀=(1,0,0). Maliyet vektörü (ilaç+stabil bakım, ilerlemiş bakım,0); fayda vektörü (uS,uP,0). İlaç yalnız stabil durumda ödenir. Ufuk 20 yıl, döngü 1 yıl, iskonto %3'tür.

$$C=\sum_k\frac{[(x_k+x_{k+1})/2]\cdot c\ \Delta t}{(1+r)^{(k+1/2)\Delta t}},\quad QALY=\sum_k\frac{[(x_k+x_{k+1})/2]\cdot u\ \Delta t}{(1+r)^{(k+1/2)\Delta t}}.$$

Geçiş matrisi kesin matris üssüdür; maliyet ve QALY integrali trapez yaklaşımı kullanır. Bu nedenle döngü uzunluğu duyarlılığı anlamlıdır. RR medyanı 0,72 olan lognormal dağılım, standart sapması log ölçekte 0,18 kullanılır; aritmetik ortalama 0,72 değildir. İki kol aynı çekilişte ortak temel hızları, maliyetleri ve faydaları paylaşır. Aday fiyatı standart fiyat + pozitif gamma primidir; ilerlemiş fayda stabil fayda × Beta(62,5;37,5)'tir. Böylece ilgili bağımlılıklar korunur.

$$ICER=\Delta C/\Delta Q,\quad NMB(\lambda)=\lambda\Delta Q-\Delta C.$$

Ek QALY sıfırsa ICER raporlanmaz. Negatif ICER tek başına tercih kuralı değildir; yönlere ve NMB'ye bakılır. Varsayımsal eşik aralığı 0–2 milyon TL/QALY'dir.

$$CEAC(\lambda)=Pr(NMB>0),\quad EVPI=E[\max(0,NMB)]-\max(0,E[NMB]).$$

EVPI bu iki seçenekli karar için kişi başınadır. Ulusal araştırma bütçesi değildir. 20.000 örnek, parametre belirsizliği (ikinci düzey Monte Carlo) analizi içindir. Olasılıkların en kötü durumda Monte Carlo standart hatası yaklaşık 0,35 yüzde puandır.

### Sanal hasta süreci

Sabit P altında 10.000 kişi, her döngüde mevcut durumuna ait satırın kümülatif olasılıklarıyla bir sonraki duruma atanır. Bu, **birinci düzey süreç rastlantısallığıdır**; klinik gözlem veya yeni parametre kestirimi değildir. Kohort payları beklenen analitik yola yaklaşır. İlk 30 yol gösterim içindir; araştırma veri seti sayılmaz. Süreç simülasyonundan yeni bir ICER hesaplanmaz; makale ICER'i analitik kohorttan gelir.

## 3. Ar-Ge: olasılıkla ağırlıklandırılmış nakit akışı

Aşama başarıları p=(0,65;0,35;0,60;0,90), başlangıç yılları (0,2,5,8), aşama maliyetleri (0,15;0,45;1,20;0,15) milyar TL'dir. Maliyet, o aşamaya **ulaşma** olasılığıyla ağırlıklandırılır; o aşamayı bitirme olasılığıyla değil.

$$p_{ruhsat}=\prod_i p_i,\quad rNPV=p_{ruhsat}\sum_{t=9+L}^{18+L}\frac{CF}{(1+r)^t}-\sum_i\frac{c_i\prod_{j<i}p_j}{(1+r)^{t_i}}.$$

CF başarılı ürün için yıllık net nakit akışıdır; satış hasılatı veya sağlık NMB'si değildir. Gecikme gelir başlangıcını öteleyip 10 yıllık gelir penceresini korur. Aşama maliyetleri değişmez. Bu sadeleştirme patent süresi kaybını veya gecikme giderlerini modellemez.

Bağımsız adaylarda en az bir başarı: 1−(1−p)ⁿ. Ortak riskte π~Beta(α,β), Yj|π~Bernoulli(π), α=p(1/ρ−1), β=(1−p)(1/ρ−1):

$$Pr(\text{en az bir başarı})=1-\frac{B(\alpha,\beta+n)}{B(\alpha,\beta)}.$$

ρ adayların nihai başarı göstergeleri arasındaki ortak korelasyondur. Bağımsız aşama süreç simülasyonunda 100 aday, 10.000 tekrar için ardışık binomial çekilişlerle ilerler. Beklenen ruhsat sayısı 100p=12,285'tir. Bu histogram **ρ=0** içindir; korelasyonlu eğri ayrı analitik beta-binomial sonuçtur.

## 4. Portföy: bütün olası seçimlerin taranması

Beş proje için xj∈{0,1}; ortak platform için z∈{0,1}. Toplam 2⁶=64 bileşim taranır:

$$\max_{x,z}\sum_j x_j\{p_j(z)[\lambda Q_j-\Delta C_j]-I_j\}-I_Pz.$$

Koşullar: ΣxjIj+IPz≤B; xN1≤z; xN2≤z. Platform, R/N1/N2 başarılarını göreli %10 artırır ve bağımsız QALY üretmez. Olasılık 1'i aşarsa girdi reddedilir. Sağlık maliyetleri/QALY'ler başarı halinde, yatırım maliyetleri kesin olarak uygulanır. Sağlık değerleri örnek bugünkü değerler olarak tanımlanmıştır; model aynı anda proje nakit akışı zamanlamasını çözmez. Ar-Ge rNPV'si bu amaç fonksiyonuna eklenmez. Model risk nötr beklenen değer optimizasyonudur; korelasyonlu portföy varyansı veya risk iştahı optimizasyonu değildir.

Olumsuz senaryoda tüm başarılar ×0,7; QALY ×0,7; pozitif sağlık maliyeti ×1,2; tasarrufun mutlak büyüklüğü ×0,7. Yatırım ve platform maliyetleri sabittir. İsteğe bağlı koşul en az bir G/B ve bir N1/N2 seçilmesini gerektirir. Boş portföy izin verilen temel karşılaştırıcıdır.

## 5. Ne doğrulandı, ne eksik?

Testler eski makale sonuçlarını, para akışı özdeşliklerini, stok korunmasını, emici ölümü, matris üssünün yarıgrup özelliğini, eşit hız limitini, sıfır sağlık farkını, bütçe kısıtlarını ve arayüzün yeniden hesaplamasını denetler. Bunlar yazılımın iç doğrulamasıdır. Türkiye'ye özgü ürün fiyatları, klinik etkinlik, fayda ağırlıkları, gerçek proje maliyetleri ve teknik başarı veri setleriyle **dış doğrulama yapılmadı**. Bu girdiler gelmeden ulusal politika için sayısal etki iddiasına dönüştürülmemelidir.
