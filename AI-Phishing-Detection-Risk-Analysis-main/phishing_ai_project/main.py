"""
Ana Çalıştırma Dosyası (Main Entry Point)
Bu modül sistemin ana akışını (pipeline) kontrol eder.
Tüm modülleri sırasıyla çağırarak sistemin sorunsuz çalışmasını sağlar.
"""

import os
import sys

# Klasör yapısının Python tarafından tanınabilmesi için path ayarı yapıyoruz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.web_crawler import crawl_site
from features.url_features import extract_url_features
from features.text_features import extract_text_features
from model.ml_model import train_model, predict_phishing
from risk.risk_score import calculate_risk

def main():
    print("="*50)
    print("AI PHISHING DETECTION SYSTEM - STARTED")
    print("="*50)
    
    # 1. Başlangıç: Model eğitimi (Sentetik verilerle projeyi hazır hale getirmek için)
    train_model()
    
    # 2. Kullanıcıdan araştırılması istenen URL'yi alıyoruz
    print("Lütfen analiz etmek istediğiniz web adresini (URL) girin.")
    print("Örnek: https://www.guvenli-banka.com veya http://login-verify-account.com")
    url = input("URL: ")
    print("-" * 50)
    
    # 3. Crawler: HTML ve sayfa metnini elde ediyoruz
    html_content, page_text = crawl_site(url)
    
    # 4. URL Özellik Çıkarımı
    url_features = extract_url_features(url)
    
    # 5. Metin (NLP) Özellik Çıkarımı
    text_features = extract_text_features(page_text)
    
    # 6. Özellikleri birleştiriyoruz (Modelin beklediği sırayla)
    # Sıra: URL Uzunluğu, HTTPS varlığı, '@' durumu, tire sayısı, IP durumu, metindeki şüpheli kelimeler
    combined_features = url_features + text_features
    print(f"[PIPELINE] Çıkarılan birleştirilmiş özellikler: {combined_features}")
    print("-" * 50)
    
    # 7. Makine Öğrenmesi ile Tahmin ve İhtimal Hesaplama
    prediction_class, probability = predict_phishing(combined_features)
    print(f"[ML MODEL] Makine Öğrenmesi tahmini yapıldı. Ham İhtimal: {probability:.2f}")
    
    # 8. Risk Skoru ve Derecelendirmesi
    risk_score, risk_level = calculate_risk(probability)
    
    # 9. Final Sonucunu Ekrana Yazdır
    print("="*50)
    print("            ANALİZ SONUCU RAPORU")
    print("="*50)
    print(f"İncelenen URL : {url}")
    print(f"Model Tahmini : {'Oltalama (Phishing)' if prediction_class == 1 else 'Güvenli (Legitimate)'}")
    print(f"Risk Skoru    : %{risk_score}")
    print(f"Risk Seviyesi : {risk_level}")
    print("="*50)

if __name__ == "__main__":
    main()
