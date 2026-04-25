"""
Risk Hesaplama Modülü
Sistemdeki risk skorlama ve derecelendirme işlemleri burada yapılır.
Amacı: Makine öğrenmesi algoritmalarından dönen ihtimal değerini referans alarak
kullanıcı dostu (0-100 arası) bir risk skoru ve risk seviyesi belirlemek.
"""

def calculate_risk(probability):
    """
    Modelden gelen 0.0 - 1.0 arası olasılık değerini 0 ile 100 arası bir
    skora çevirir ve ardından risk seviyesini etiketler.
    
    Skor Aralıkları:
    0–30  -> Düşük Risk (Low Risk)
    31–70 -> Orta Risk (Medium Risk)
    71–100 -> Yüksek Risk (High Risk)
    
    Parametreler:
    probability (float): Modelin tahmini olasılık değeri (Örn: 0.85).
    
    Dönen Değerler:
    tuple: (risk_score, risk_level)
    """
    
    # İhtimal değerini 0-100 arasında bir skora çevirme (Yuvarlama yapılır)
    risk_score = int(round(probability * 100))
    
    # Risk seviyesini sınıflandırma
    if risk_score <= 30:
        risk_level = "Düşük Risk (Low Risk)"
    elif risk_score <= 70:
        risk_level = "Orta Risk (Medium Risk)"
    else:
        risk_level = "Yüksek Risk (High Risk)"
        
    return risk_score, risk_level
