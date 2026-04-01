"""
Metin Analizi (NLP) Modülü
TODO: Bu modül ileride implement edilecektir.
Amacı: Web sayfasındaki metni analiz edip, şüpheli (oltalama) kelimeleri tespit etmek.
"""

def extract_text_features(page_text):
    """
    Sayfa metninden oltalama (phishing) belirtisi olan kelimelerin varlığını kontrol eder.
    
    Aranacak bazı örnek kelimeler:
    login, verify, password, bank, account, secure
    
    ÖNEMLİ: Bu fonksiyon yer tutucu (placeholder) olarak bırakılmıştır.
    İleride doğal dil işleme (NLP) yöntemleriyle daha detaylı analiz yapılacaktır.
    
    Parametreler:
    page_text (str): Web sayfasından çekilen ham metin içeriği.
    
    Dönen Değerler:
    list: Tespit edilen özelliklerin sayısal listesi.
    """
    # TODO: Kelime analizi yapılıp, özellik sayıları burada hesaplanacaktır.
    
    print("[TEXT FEATURES] Metin içeriği NLP ile analiz ediliyor... (Modül henüz implement edilmedi)")
    
    # Bazı anahtar kelimeler (şüpheli)
    keywords = ["login", "verify", "password", "bank", "account", "secure", "giriş", "şifre"]
    
    # Şimdilik basit bir sayım yapıyoruz. Olası şüpheli kelimelerin listesini sayıyoruz.
    phishing_word_count = sum(1 for word in keywords if word in page_text.lower())
    
    # Özellik: [Metin içindeki şüpheli kelime sayısı]
    features = [phishing_word_count]
    
    return features
