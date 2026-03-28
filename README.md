# FinTrack AI - A+ Luxury Financial Suite

## 🚀 Vizyon
FinTrack AI; sadece bir varlık takip aracı değil, yatırımcının kararlarını destekleyen yüksek teknolojili bir finans terminalidir.

---

## 🛠️ Modül 1: Ultra-Luxury Foundation (1. Kişi)
Bu modül, projenin kurumsal kimliğini ve teknik iskeletini oluşturur.

### 💎 A+ Tasarım Standartları
- **Standalone Experience:** Streamlit'in tüm geliştirici araçları gizlendi, saf bir web sitesi deneyimi sunuldu.
- **Micro-Animations:** Form geçişlerinde ve buton etkileşimlerinde `ease-out` animasyonları uygulandı.
- **Unified Auth Flow:** Giriş ve Kayıt tek bir kart üzerinden dinamik olarak yönetiliyor.
- **Outfit Typography:** Okunabilirliği en yüksek premium finans fontu entegre edildi.

### ⚙️ Teknik Altyapı
- **Backend:** Python + Streamlit (CSS Overridden).
- **Auth:** Supabase Real-time Auth.
- **Navigation:** Custom sidebar logic (By-passing auto-pages).

### 📋 Kurulum
```bash
pip install streamlit supabase yfinance ccxt prophet plotly textblob
streamlit run app.py
```

---

## 📊 Modül 5: UI/UX & Final (5. Kişi)
Bu modül, kullanıcının verilerini anlamlandırması için görselleştirme araçları sunar ve uygulamanın son cilasını atar.

### 📈 Görselleştirmeler (Dashboard)
- **Varlık Dağılımı (Pie Chart):** Plotly kütüphanesi ile kullanıcının portföyündeki varlıkların dağılımını gösteren interaktif pasta grafik eklendi.
- **Fiyat Analizi (Candlestick Chart):** Portföyde en yüksek hacme sahip varlığın son 1 aylık fiyat hareketini gösteren mum grafiği entegre edildi. Gerçek zamanlı veriler yfinance üzerinden sağlanır.

### 🧹 Teknik Temizlik ve İzolasyon
- **Modüler Yapı:** `app.py` içerisindeki statik dashboard kodları ve iş mantığı tamamen kuralına uygun şekilde `screens/dashboard.py` dosyasına taşınarak ayrıştırıldı.
- **Grafik Hata Yönetimi:** BİST hisseleri (.IS formatı) ve Kripto paralar için özel ticker logic yazıldı. Uygulamanın çökmaması için `try-except` blokları uygulandı.
