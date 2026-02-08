from playwright.async_api import async_playwright
import csv
import asyncio
from concurrent.futures import ThreadPoolExecutor

LIST_URL = "https://kariyer.baykartech.com/tr/open-positions/?type=232"
CSV_FILE_ALL = "baykar_tum_ilanlar.csv"
CSV_FILE_FILTERED = "baykar_bilgisayar_muh_staj.csv"

# Aranan anahtar kelimeler (küçük harfli)
KEYWORDS = [
    "bilgisayar mühendisliği",
    "bilgisayar mühendisi",
    "yazılım mühendisliği",
    "yazılım mühendisi",
    "computer engineering",
    "software engineering",
    "bilgisayar müh",
    "yazılım müh"
]

def check_if_computer_engineering(text):
    """Verilen metinde bilgisayar mühendisliği anahtar kelimelerini arar"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

async def scrape_job_detail(page, job_url, index, total):
    """Tek bir ilanın detayını asenkron olarak çeker"""
    try:
        await page.goto(job_url, wait_until="networkidle", timeout=20000)
        await asyncio.sleep(0.5)
        
        # İlan başlığını al
        title_element = await page.query_selector('h1, h2, .job-title, [class*="title"]')
        title = await title_element.inner_text() if title_element else "Başlık bulunamadı"
        title = title.strip()
        
        # Sayfanın tüm metnini al
        page_text = await page.inner_text('body')
        
        # Bilgisayar mühendisliği kontrolü
        is_suitable = check_if_computer_engineering(page_text)
        
        status = "✅" if is_suitable else "❌"
        print(f"[{index}/{total}] {status}", flush=True)
        
        return {
            "ilan_adi": title,
            "ilan_linki": job_url,
            "bilgisayar_muhendisi_basvurabilir": "EVET" if is_suitable else "HAYIR"
        }
    except Exception as e:
        print(f"[{index}/{total}] ⚠️", flush=True)
        return {
            "ilan_adi": "Hata oluştu",
            "ilan_linki": job_url,
            "bilgisayar_muhendisi_basvurabilir": "HATA"
        }

async def scrape_page_links(page, page_num):
    """Tek bir sayfa listesinden linkleri asenkron olarak çeker"""
    page_url = f"{LIST_URL}&page={page_num}"
    await page.goto(page_url, wait_until="networkidle", timeout=30000)
    await asyncio.sleep(1)
    
    cards = await page.query_selector_all('a[href*="/acik-pozisyonlar/detay/"]')
    
    job_links = []
    for card in cards:
        href = await card.get_attribute('href')
        if href and '/acik-pozisyonlar/detay/' in href:
            # Sadece 2026-yaz-donemi içeren ilanları al
            if '2026-yaz-donemi' in href.lower():
                full_url = "https://kariyer.baykartech.com" + href if href.startswith('/') else href
                if full_url not in job_links:
                    job_links.append(full_url)
    
    return job_links

async def main():
    print("🚀 Tarayıcı başlatılıyor (arka planda)...")
    
    async with async_playwright() as p:
        # Tarayıcıyı headless modda başlat (hiç sekme açılmaz)
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Context oluştur (gerçek browser gibi görünmek için)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Paralel link toplama için 3 sayfa aç
        print("📋 Tüm sayfalardan ilan linkleri toplanıyor...")
        
        pages_for_listing = [await context.new_page() for _ in range(3)]
        
        all_job_links = []
        tasks = []
        
        # 10 sayfayı 3 paralel page ile topla
        for page_num in range(1, 11):
            page_index = (page_num - 1) % 3
            task = scrape_page_links(pages_for_listing[page_index], page_num)
            tasks.append((page_num, task))
        
        # Her 3 görevde bir batch işle
        for i in range(0, len(tasks), 3):
            batch = tasks[i:i+3]
            results = await asyncio.gather(*[task for _, task in batch])
            
            for j, (page_num, _) in enumerate(batch):
                links = results[j]
                all_job_links.extend(links)
                print(f"   📄 Sayfa {page_num}/10 → {len(links)} ilan bulundu")
        
        # Listing page'leri kapat
        for page in pages_for_listing:
            await page.close()
        
        # Duplicate linkleri temizle
        job_links = list(dict.fromkeys(all_job_links))
        
        print(f"\n📌 Toplam {len(job_links)} ilan bulundu")
        print("🔍 İlanlar kontrol ediliyor (5 paralel)...\n")
        
        # Detay sayfaları için 5 paralel page aç
        pages_for_details = [await context.new_page() for _ in range(5)]
        
        results = []
        
        # Her 5 ilanı aynı anda işle
        for i in range(0, len(job_links), 5):
            batch_links = job_links[i:i+5]
            batch_tasks = []
            
            for j, job_url in enumerate(batch_links):
                page_index = j % 5
                task = scrape_job_detail(
                    pages_for_details[page_index],
                    job_url,
                    i + j + 1,
                    len(job_links)
                )
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
        
        # Detay page'leri kapat
        for page in pages_for_details:
            await page.close()
        
        await context.close()
        await browser.close()
    
    # CSV dosyalarına kaydet
    print(f"\n\n💾 Sonuçlar kaydediliyor...")
    
    # 1. TÜM İLANLARI KAYDET
    with open(CSV_FILE_ALL, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ilan_adi", "ilan_linki", "bilgisayar_muhendisi_basvurabilir"]
        )
        writer.writeheader()
        writer.writerows(results)
    
    # 2. SADECE BİLGİSAYAR MÜHENDİSLİĞİ İÇİN UYGUN OLANLARI KAYDET
    filtered_results = [r for r in results if r['bilgisayar_muhendisi_basvurabilir'] == 'EVET']
    
    with open(CSV_FILE_FILTERED, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ilan_adi", "ilan_linki", "bilgisayar_muhendisi_basvurabilir"]
        )
        writer.writeheader()
        writer.writerows(filtered_results)
    
    print(f"\n📁 İşlem tamamlandı!")
    print(f"➡ Tüm ilanlar: '{CSV_FILE_ALL}' dosyasına kaydedildi")
    print(f"➡ Bilgisayar Müh. ilanları: '{CSV_FILE_FILTERED}' dosyasına kaydedildi")
    print(f"\n📊 ÖZET:")
    print(f"   • Toplam ilan: {len(results)}")
    print(f"   • Bilgisayar Müh. için uygun: {len(filtered_results)} ilan")
    print(f"   • Uygun olmayan: {len(results) - len(filtered_results)} ilan")

if __name__ == "__main__":
    asyncio.run(main())
