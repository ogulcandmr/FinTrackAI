# 💎 FinTrack AI - Geliştirici Kurulum ve Görev Rehberi

Bu belge, projenin kurulumunu, çalışma prensiplerini ve 5 kişilik ekibin görev dağılımını içeren **resmi çalışma kılavuzudur.** Lütfen her adımı sırasıyla takip edin.

---

## 🚀 1. Adım: Yerel Ortamın Kurulması

1.  **Depoyu Klonlayın:**
    ```bash
    git clone <depo_url-sizinkisi>
    cd iptProje
    ```
2.  **Sanal Ortam Oluşturun (Önerilir):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Mac/Linux
    # venv\Scripts\activate  # Windows
    ```
3.  **Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🔑 2. Adım: API Anahtarları ve Secrets Yapılandırması (KRİTİK)

Güvenlik nedeniyle `.streamlit/secrets.toml` dosyası GitHub'da bulunmaz. Herkes bu dosyayı kendi bilgisayarında **el ile** oluşturmalıdır.

1.  Proje kök dizininde `.streamlit` adında bir klasör oluşturun (başındaki noktayı unutmayın).
2.  İçine `secrets.toml` adında bir dosya oluşturun ve şu bilgileri yapıştırın:
    ```toml
    SUPABASE_URL = "https://vkapxezrzhoxbqpgpbqt.supabase.co"
    SUPABASE_KEY = "BURAYA_ANON_PUBLIC_KEY_GELECEK"
    ```
    *Not: `SUPABASE_KEY` kısmına Supabase panelindeki **anon public** kodunu (eyJ... ile başlayan uzun kod) koymalısınız. Ekip liderinden (Kişi 1) bu kodu isteyin.*

---

## 🚦 3. Adım: Git Branch (Dal) Kuralları

Birbirimizin kodunu silmemek için şu kurallara uymak **ZORUNLUDUR**:

1.  **Main Branch'e Direkt Push Yasak:** Hiç kimse `main` branch'inde kod yazmayacak.
2.  **Kendi Branch'inizi Açın:**
    - `git checkout -b feature/goreviniz` (Örn: `feature/portfolio`)
3.  **Dosya İzolasyonu:** Sadece size atanan `/screens` ve `/utils` dosyalarında çalışın.
4.  **Bitince PR Açın:** Kodunuz bitince `push` yapıp GitHub üzerinden **Pull Request** açın, ekip lideri (Kişi 1) onaylayıp `main` ile birleştirecektir.

---

## 👥 4. Adım: Görev Dağılımı ve Teknik Detaylar

| Görevli | Modül | Sorumluluklar |
| :--- | :--- | :--- |
| **1. Kişi** | **Auth & Onboarding** | **[TAMAMLANDI]** Sistemin girişi, tasarımı ve anket ekranı hazır. |
| **2. Kişi** | **Portfolio Management** | `yfinance/ccxt` ile canlı veri çekme, varlık ekle/sil modülü, kar-zarar hesabı. |
| **3. Kişi** | **Finance Engine** | Temettü takvimi, **Bileşik Getiri** matematiksel modeli, 20 yıllık projeksiyon simülatörü. |
| **4. Kişi** | **AI & Sentiment** | **Facebook Prophet** ile fiyat tahmini, haber kazıma ve **Sentiment Analysis** (NLP). |
| **5. Kişi** | **UI/UX & Final** | Dashboard görselleştirmesi (Pasta/Mum grafikler), teknik temizlik ve README hazırlığı. |

---

## 🛠️ 5. Adım: Uygulamayı Çalıştırma

Tüm kurulum bittikten sonra uygulamayı ayağa kaldırmak için:
```bash
streamlit run app.py
```

---
**💡 İpucu:** `app.py` dosyası projenin kalbidir. Sidebar'a sayfa eklemek dışında bu dosyada köklü değişiklik yapmayın. Herkes kendi `screens/` klasöründeki dosyasını geliştirsin.

Başarılar ekips! 💎🚀
