# BStaj Başvuru Scripti

Bu proje, Baykar Kariyer sitesinde yayınlanan **2026 Yaz Dönemi Staj** ilanlarını otomatik olarak analiz ederek  
**Bilgisayar Mühendisliği** ve **Yazılım Mühendisliği** öğrencilerinin başvurabileceği pozisyonları tespit etmek amacıyla geliştirilmiştir.

Script, ilan detay sayfalarındaki **Aranan Nitelikler** bölümünü inceleyerek sonuçları CSV formatında raporlar.

---

## Özellikler

- Baykar Kariyer sitesindeki staj ilanlarını otomatik olarak tarar
- Her ilan için detay sayfasını analiz eder
- Bilgisayar Mühendisliği ve Yazılım Mühendisliği ifadelerini algılar
- Sonuçları CSV dosyasına kaydeder
- Manuel inceleme ihtiyacını azaltır

---

## Kullanılan Teknolojiler

- Python 3
- requests
- BeautifulSoup (bs4)
- CSV

---

##  Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/gokaycetinn/Staj-Script.git
cd Staj-Script
```

2. Playwright'ı yükleyin:
```bash
pip3 install playwright
```

3. Playwright tarayıcılarını kurun:
```bash
python3 -m playwright install
```

## Kullanım

Scripti çalıştırın:
```bash
python3 script.py
```

### Çalışma Süreci:
1.  **Link Toplama**: 10 sayfadan tüm ilan linklerini toplar (~10 saniye)
2.  **İlan Kontrolü**: Her ilanın detay sayfasını kontrol eder (5 paralel işlem)
3.  **Sonuç Kaydetme**: 2 ayrı CSV dosyası oluşturur

## Çıktılar

### 1. `baykar_tum_ilanlar.csv`
Tüm staj ilanlarının listesi (116+ ilan)

**Sütunlar:**
- `ilan_adi`: İlan başlığı
- `ilan_linki`: İlan detay URL'i
- `bilgisayar_muhendisi_basvurabilir`: EVET/HAYIR

### 2. `baykar_bilgisayar_muh_staj.csv`
Sadece Bilgisayar/Yazılım Mühendisliği için uygun ilanlar (14+ ilan)

**Örnek içerik:**
```csv
ilan_adi,ilan_linki,bilgisayar_muhendisi_basvurabilir
"Nesne Tabanlı Yazılım Mühendisi","https://kariyer.baykartech.com/tr/acik-pozisyonlar/detay/nesne-tabanli-yazilim-muhendisi","EVET"
"2026 Yaz Dönemi Proje Mühendisi","https://kariyer.baykartech.com/tr/acik-pozisyonlar/detay/2026-yaz-donemi-proje-muhendisi","EVET"
```

## Filtreleme Kriterleri

Script aşağıdaki anahtar kelimeleri arar:
- Bilgisayar Mühendisliği
- Yazılım Mühendisliği
- Computer Engineering
- Software Engineering
- Bilgisayar Müh.
- Yazılım Müh.

## Teknik Detaylar

### Kullanılan Teknolojiler:
- **Playwright (async)**: Web tarayıcı otomasyonu
- **asyncio**: Asenkron programlama
- **Paralel İşleme**: 5 eşzamanlı sayfa işlemi

### Performans Optimizasyonları:
- ✅ Headless mode (görünmez tarayıcı)
- ✅ Async/await pattern
- ✅ Batch processing (5'li gruplar)
- ✅ Minimal bekleme süreleri
- ✅ networkidle yerine domcontentloaded

### Hız Karşılaştırması:
| Mod | Süre |
|-----|------|
| Sync (Tek tek) | ~8-10 dakika |
| Async (5 paralel) | ~2-3 dakika |


## Geliştirici

**Gökay Çetinakdoğan**
- GitHub: [@gokaycetinn](https://github.com/gokaycetinn)

---


