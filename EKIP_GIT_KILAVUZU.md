# 🛠️ FinTrack AI - Ekip Git & Çalışma Disiplini Rehberi

Bu rehber, 5 kişilik ekibin birbirinin kodunu bozmadan, çakışma (merge conflict) yaşamadan aynı anda nasıl çalışacağını anlatır.

## 1. Altın Kurallar (Çakışmasız Çalışma)
- **Kendi Dosyanızda Kalın:** Herkes kendi görev alanına ait yeni dosyalar oluşturmalıdır (Örn: `screens/Portfolio.py`, `utils/portfolio_functions.py`).
- **app.py Kısıtlaması:** `app.py` ana dosyadır. Buraya sadece en son, hazırladığınız ekranı sidebar menüsüne eklemek için 2-3 satır kod yazacaksınız. Mümkünse bu dosyayı en son ekip lideri (Kişi 1) toplasın.
- **Her Zaman Pull Yapın:** Güne başlarken veya bir başkası kod yüklediğinde mutlaka `git pull` yapın.

## 2. Her Kişi İçin Branch (Dal) Yapısı
Repoyu klonladıktan sonra, ana kolda (`main`) çalışmak yerine kendinize ait bir "dal" açın:

| Görev | Branch İsmi | Komut |
| :--- | :--- | :--- |
| **2. Kişi (Portfolio)** | `feat/portfolio` | `git checkout -b feat/portfolio` |
| **3. Kişi (Dividend)** | `feat/dividend` | `git checkout -b feat/dividend` |
| **4. Kişi (AI & Sentiment)** | `feat/ai-analysis` | `git checkout -b feat/ai-analysis` |
| **5. Kişi (Dashboard & UI)** | `feat/dashboard-polish` | `git checkout -b feat/dashboard-polish` |

## 3. Adım Adım Çalışma Akışı

### A. Görevinize Başlarken
```bash
git pull origin main       # En güncel kodu çek
git checkout -b görevim    # Kendi dalını oluştur (Sadece bir kez)
```

### B. Kodunuzu Yazıp Bitirdiğinizde
```bash
git add .
git commit -m "Portföy ekleme modülü eklendi"
git push origin görevim    # Kendi dalını buluta gönder
```

### C. Kodları Birleştirme (Merging)
GitHub üzerinden bir **"Pull Request (PR)"** açın. Bu, "Ben işimi bitirdim, ana koda ekle" demektir. Ekip lideri (Kişi 1) bunu onayladığında kodlarınız `main` ile birleşir.

## 4. Dosya Yapısı Önerisi (Çakışmayı Sıfırlamak İçin)
Herkes arkadaşının dosyasına dokunmamak için şu yapıyı izlesin:
- **Kişi 2:** `screens/Portfolio.py` ve `utils/portfolio_api.py`
- **Kişi 3:** `screens/Dividend.py` ve `utils/dividend_calc.py`
- **Kişi 4:** `screens/AiLab.py` ve `utils/ai_models.py`
- **Kişi 5:** `screens/DashboardUI.py` (Dashboard'un görselini buraya taşırsa çakışma sıfıra iner)

---
**💡 5. Kişi İçin Not:** 5. kişi genelde dekoratör gibidir, her şeyi toplar. Eğer o da kendine ait bir dosya (`DashboardUI.py`) açıp `app.py`'deki `render_dashboard` içeriğini oraya taşırsa, kimseyle çakışmaz. Projenin son gününde tüm sayfalar bittiğinde, herkesin `render_...` fonksiyonlarını `app.py` içinden çağırmak sadece 5 dakikamızı alır.

Bol şans beyler! 💎🚀
