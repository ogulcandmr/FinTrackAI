"""
Makine Öğrenmesi (Machine Learning) Modülü
Makine öğrenmesi modeli burada eğitilir ve tahmin işlemleri gerçekleştirilir.
Amacı: Özellikleri kullanarak RandomForest sınıflandırıcısı (classifier) ile modeli eğitmek
ve tahminde bulunmak.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Global model nesnesi (program çalıştığında kullanılacak)
rf_model = None

def train_model():
    """
    Program ilk çalıştığında küçük ve sentetik bir veri seti (dataset) üreterek
    makine öğrenmesi modelini eğitir. Bu sayede proje hemen çalıştırılabilir durumda olur.
    """
    global rf_model
    
    print("[ML MODEL] Sentetik veri seti oluşturuluyor ve model eğitiliyor...")
    
    # Sentetik veri oluşturma (URL uzunluğu, HTTPS, @ var mı, tire sayısı, IP var mı, şüpheli kelime sayısı)
    # Target: 0 (Normal / Güvenli), 1 (Phishing / Oltalama)
    data = {
        'url_length': [20, 150, 45, 80, 25, 200],
        'https':      [1, 0, 1, 0, 1, 0],
        'has_at':     [0, 1, 0, 1, 0, 1],
        'dash_count': [0, 5, 1, 4, 0, 6],
        'has_ip':     [0, 1, 0, 0, 0, 1],
        'suspicious_words': [0, 5, 0, 3, 1, 8],
        'target':     [0, 1, 0, 1, 0, 1]  # 0: Legitimate, 1: Phishing
    }
    
    df = pd.DataFrame(data)
    
    # Özellik (X) ve Hedef (y) ayrımı
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Modeli tanımla ve eğit
    # Random Forest modeli daha kararlı kararlar alabilmek için kullanılıyor
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    print("[ML MODEL] Model eğitimi tamamlandı!\n")

def predict_phishing(features):
    """
    Eğitilmiş modele sayısal özellikleri vererek, oranın phishing (oltalama) 
    olma olasılığını hesaplar.
    
    Parametreler:
    features (list): URL ve metin analizinden gelen birleştirilmiş sayısal özellikler.
    
    Dönen Değerler:
    tuple: (tahmin_sonucu, oltalama_ihtimali) 
           Tahmin 0 (Güvenli) ya da 1 (Phishing), İhtimal ise 0.0 ile 1.0 arası değerdir.
    """
    global rf_model
    
    if rf_model is None:
        raise Exception("Model eğitilmemiş! Tahmin öncesi train_model() çağrılmalı.")
    
    # Modeli tablo formatında beklediği için özellik listesini dönüştürüyoruz
    X_test = pd.DataFrame([features], columns=[
        'url_length', 'https', 'has_at', 'dash_count', 'has_ip', 'suspicious_words'
    ])
    
    # Tahmin sınıfı (0 veya 1)
    prediction = rf_model.predict(X_test)[0]
    
    # Phishing olma ihtimalinin olasılığı (Probability)
    # predict_proba bize her sınıf [Güvenli, Phishing] için olasılık verir.
    # Biz [1] indeksini yani Phishing olma olasılığını alıyoruz.
    probability = rf_model.predict_proba(X_test)[0][1]
    
    return prediction, probability
