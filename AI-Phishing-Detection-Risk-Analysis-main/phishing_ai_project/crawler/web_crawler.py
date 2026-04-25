import requests
from bs4 import BeautifulSoup
import re
import html
import os
from urllib.parse import urlparse

# Sabit User-Agent (Bot engelleme için)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_text(text):
    """
    Metni HTML gürültüsünden temizler ve normalize eder.
    """
    # HTML entity'leri normalize et (&nbsp; -> space vb.)
    text = html.unescape(text)
    # Gereksiz boşlukları ve satır sonlarını temizle
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def save_to_file(url, text):
    """
    Temizlenen metni bir .txt dosyasına kaydeder.
    """
    # URL'den güvenli bir dosya adı oluştur
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    path = parsed_url.path.replace('/', '_').strip('_')
    filename = f"{domain}_{path if path else 'root'}.txt"
    
    # Çıktı dizini
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'crawled_texts')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_path = os.path.join(output_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"[CRAWLER] İçerik şuraya kaydedildi: {file_path}")
    except Exception as e:
        print(f"[CRAWLER] Dosya kaydetme hatası: {e}")

def crawl_site(url):
    """
    Verilen URL adresinden web sayfasının içeriğini çeker ve temizler.
    
    Parametreler:
    url (str): Analiz edilecek web sitesinin adresi.
    
    Dönen Değerler:
    tuple: (html_content, page_text)
    """
    try:
        print(f"[CRAWLER] '{url}' adresi taranıyor...")
        
        # 1. Sayfa İsteği (Timeout eklenmeli)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # 4xx veya 5xx hatalarında exception fırlatır
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 2. Gereksiz etiketleri tamamen kaldır (<script> ve <style>)
        for tag in soup(['script', 'style']):
            tag.decompose()
            
        # 3. Belirtilen etiketlerden metinleri çek (div, p, a)
        found_texts = []
        for tag in soup.find_all(['div', 'p', 'a']):
            tag_text = tag.get_text(separator=' ', strip=True)
            if tag_text:
                found_texts.append(tag_text)
                
        # 4. Tüm metinleri birleştir ve temizle
        full_text = ' '.join(found_texts)
        cleaned_text = clean_text(full_text)
        
        # 5. Sonucu dosyaya kaydet
        save_to_file(url, cleaned_text)
        
        return html_content, cleaned_text
        
    except requests.exceptions.RequestException as e:
        print(f"[CRAWLER ERROR] '{url}' taranırken bir hata oluştu: {e}")
        # Hata durumunda boş içerik dön ama programın çökmesini engelle
        return "", ""
    except Exception as e:
        print(f"[CRAWLER ERROR] Beklenmedik bir hata oluştu: {e}")
        return "", ""

def crawl_multiple_sites(urls):
    """
    Verilen URL listesini dolaşır ve her birini tarar.
    
    Parametreler:
    urls (list): Tarancak URL'lerin listesi.
    """
    results = []
    for url in urls:
        html, text = crawl_site(url)
        results.append((url, text))
    return results
