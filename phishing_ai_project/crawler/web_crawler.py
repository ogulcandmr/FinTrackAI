"""
Web Crawler Modülü
TODO: Bu modül ileride implement edilecektir.
Amacı: Verilen URL'ye gidip sayfanın HTML ve metin (text) içeriğini çekmek.
"""

def crawl_site(url):
    """
    Verilen URL adresinden wep sayfasının içeriğini çeker.
    
    ÖNEMLİ: Bu fonksiyon şu an yer tutucu (placeholder) olarak tanımlanmıştır.
    İleride requests ve BeautifulSoup kullanılarak gerçek HTML ve metin çekme işlemi yapılacaktır.
    
    Parametreler:
    url (str): Analiz edilecek web sitesinin adresi.
    
    Dönen Değerler:
    tuple: (html_content, page_text)
    """
    # TODO: İleride buraya requests.get(url) eklenecektir.
    # Şimdilik sahte (fake) bir içerik döndürüyoruz.
    
    print(f"[CRAWLER] '{url}' adresi taranıyor... (Modül henüz implement edilmedi)")
    
    html_content = "<html><body>Sahte (fake) sayfa içeriği</body></html>"
    page_text = "lütfen giriş yapın ve şifrenizi girin hesaba erişin"
    
    return html_content, page_text
