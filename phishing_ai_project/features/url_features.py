"""
URL Özellik Çıkarımı Modülü
TODO: Bu modül ileride implement edilecektir.
Amacı: Web adresinin (URL) yapısal özelliklerini analiz etmek.
"""

def extract_url_features(url):
    """
    Verilen URL'den özellik çıkarımı yapar.
    
    Çıkarılacak bazı özellikler:
    - URL uzunluğu
    - HTTPS kullanımı (var/yok)
    - '@' karakteri var mı?
    - '-' (tire) sayısı
    - IP adresi içeriyor mu?
    
    ÖNEMLİ: Bu fonksiyon şu an yer tutucu (placeholder) olarak tanımlanmıştır.
    İleride gerçek analiz fonksiyonları yazılacaktır.
    
    Parametreler:
    url (str): Adresi analiz edilecek olan URL.
    
    Dönen Değerler:
    list: Algoritmaya verilecek olan nümerik (sayısal) özellikler listesi.
    """
    # TODO: Gerçek bağımsız özellikler burada hesaplanacaktır.
    # Şimdilik sahte özellikler (dummy features) döndürüyoruz.
    
    print("[URL FEATURES] URL özellikleri analiz ediliyor... (Modül henüz implement edilmedi)")
    
    # Sırasıyla: [URL Uzunluğu, HTTPS (1=var), '@' (0=yok), tire sayısı, IP (0=yok)]
    features = [len(url), 1, 0, url.count('-'), 0]
    
    return features
