# 💎 FinTrack AI - Geliştirici Kurulum ve Master Görev Rehberi

Bu belge, projenin kurulumunu, çalışma prensiplerini ve 5 kişilik ekibin modül bazlı dosya görev dağılımını içeren **resmi çalışma kılavuzudur.**

---

## 🚀 1. Adım: Yerel Ortamın Kurulması
1.  **Depoyu Klonlayın:** `git clone <repo_url>` ve `cd iptProje`
2.  **Sanal Ortam:** `python -m venv venv` ve aktif edin (`source venv/bin/activate` veya `venv\Scripts\activate`)
3.  **Yükleme:** `pip install -r requirements.txt`

---

## 🔑 2. Adım: Secrets Yapılandırması (ÖNEMLİ)
`.streamlit/secrets.toml` dosyasını oluşturun ve şu bilgileri yapıştırın:
```toml
SUPABASE_URL = "https://vkapxezrzhoxbqpgpbqt.supabase.co"
SUPABASE_KEY = "EKİP_LİDERİNDEN_ALINACAK_ANON_KEY"
```
*Not: Key 'eyJ...' ile başlayan çok uzun koddur.*

---

## 🚦 3. Adım: Git Çalışma Disiplini
- **KURAL:** `main` branch'ine direkt push yapmak yasaktır.
- **YÖNTEM:** `git checkout -b feature/goreviniz` ile dal açın. İşiniz bitince `push` yapıp GitHub'dan **Pull Request** açın.
- **DOSYA KİLİDİ:** `app.py` dosyasına sadece en son menü eklemek için dokunulacaktır. Karmaşayı önlemek için herkes kendi modül dosyalarında çalışmalıdır.

---

## 👥 4. Adım: Detaylı Dosya & Görev Dağılımı

### 🟢 1. Kişi: Altyapı & Auth [TAMAMLANDI]
- **Dosyalar:** `app.py`, `utils/supabase_utils.py`, `screens/onboarding.py`

---

### 🔵 2. Kişi: Veri Katmanı ve Cüzdan Yönetimi
- **Çalışacağı Dosyalar:** `screens/Portfolio.py`, `utils/portfolio_engine.py`
- **Adım Adım Görevler:**
    1.  Supabase `portfolio` tablosu şeması (Asset ID, Alış Tarihi, Fiyat, Adet).
    2.  `yfinance` ve `ccxt` entegrasyonu için yardımcı fonksiyonları `utils/portfolio_engine.py` içine yaz.
    3.  Portföy ekleme/listeleme/silme arayüzünü `screens/Portfolio.py` içine yap.
    4.  Canlı veri çekme ve anlık kar/zarar hesaplama motorunu bitir.
    5.  Özet kartlarını (Toplam Varlık, Günlük Değişim) ekrana bas.

---

### 🟡 3. Kişi: Temettü Emekliliği Motoru
- **Çalışacağı Dosyalar:** `screens/Dividend.py`, `utils/finance_math.py`
- **Adım Adım Görevler:**
    1.  Geçmiş temettü verilerini çekip işleyen motoru `utils/finance_math.py` içine yaz.
    2.  "Yaklaşan Temettü Takvimi" sayfasını aç.
    3.  **Bileşik Getiri (Compound Interest)** modelini kur.
    4.  Simülatör ekranını (5-10-20 yıllık projeksiyon) `screens/Dividend.py` içine kur.
    5.  Sektörel temettü verimliliği tablolarını oluştur.

---

### 🔴 4. Kişi: Yapay Zeka ve Algoritmik Analiz
- **Çalışacağı Dosyalar:** `screens/AiLab.py`, `utils/ai_models.py`
- **Adım Adım Görevler:**
    1.  **Prophet** modeli entegrasyonu (15 günlük tahmin) `utils/ai_models.py` içine.
    2.  Haber çekme ve **Sentiment Analysis (NLTK)** modülünü kur.
    3.  Analiz sonuçlarını veritabanına işle veya anlık göster.
    4.  Risk Profil Uyumluluk Kontrolü (Algoritmik uyarı sistemi) yaz.
    5.  Tahmin grafiklerini `Plotly` ile görselleştir.

---

### 🟣 5. Kişi: Görsel Dashboard ve Optimizasyon
- **Çalışacağı Dosyalar:** `screens/Dashboard.py`, `utils/ui_helpers.py` (ve genel estetik)
- **Adım Adım Görevler:**
    1.  Ana Dashboard ekran tasarımı (Sektörel dağılım pasta grafiği).
    2.  Teknik Mum (Candlestick) grafiklerini dashboard'a göm.
    3.  "Günün Enleri" (En Çok Kazanan/Kaybeden) kartlarını yap.
    4.  Genel kod optimizasyonu ve Refactoring (Temizlik).
    5.  Proje dokümantasyonu (`README.md`) ve final sunum hazırlığı.

---
**💡 Çalıştırma:** `streamlit run app.py`
