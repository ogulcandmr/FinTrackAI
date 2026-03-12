# 🎓 FinTrack AI - Hoca Soru-Cevap Hazırlık Notları (Pro Seviye)

Hoca bu projeyi gördüğünde "Vay canına, bunu sadece Python ile mi yaptın?" diyecektir. İşte muhtemel sorular ve vermen gereken "Senior Developer" cevapları:

---

### 👑 1. "Tasarım Neden Bu Kadar Farklı? Streamlit'e Benzemiyor!"
- **Cevap:** "Hocam, Streamlit'in standart 'veri raporu' görünümünü biz bir **'Bağımsız Web Uygulaması' (Standalone Web App)** kimliğine büründürdük. Özel **CSS Injection** kullanarak Streamlit'in kendi Header, Footer ve Menü bileşenlerini (Deploy butonu dahil) tamamen gizledik. Amacımız, kullanıcının kendisini bir analiz aracında değil, profesyonel bir bankacılık terminalinde hissetmesini sağlamaktı."

---

### ✨ 2. "Animasyonları Nasıl Yaptın? Python Dinamik Değildir Diye Bilirim."
- **Cevap:** "Haklısınız hocam, Python sunucu taraflı çalışır. Ancak biz arayüzde **CSS Keyframe Animations** ve **Cubic-Bezier** geçiş efektleri kullandık. Sayfa her 'rerun' (yeniden yükleme) olduğunda, tarayıcı tarafında tetiklenen bu animasyonlar sayesinde pürüzsüz bir 'Fade-in' ve 'Slide-up' etkisi yarattık. Kayıt ve Giriş ekranları arasındaki geçişi de `st.session_state` ile yöneterek sayfa yenilenmeden mod değişimini sağladık."

---

### 🛡️ 3. "Kayıt Olunca Neden Direkt İçeri Alıyor? E-posta Onayı Nerede?"
- **Cevap:** "Projenin ilk aşamasında kullanıcı deneyimini (UX) ön planda tuttuk. **Supabase Auth** üzerinden 'Email Confirmation' adımını devre dışı bıraktık. Böylece kullanıcı kayıt olduğu anda sistemi kullanmaya başlayabiliyor. Gerçek dünyada bu bir güvenlik terciğidir, biz hızlı prototipleme için bu yolu seçtik."

---

### 📂 4. "Neden 'screens' Klasörü Kullandın?"
- **Cevap:** "Streamlit `pages` klasöründeki dosyaları alfabetik sırayla yan menüye otomatik ekler. Biz bu basitliği istemedik; navigasyonu **özel CSS ve Sidebar kodlarıyla** kendimiz inşa ettik. Bu yüzden bu dosyaları `screens` klasörüne çekerek Streamlit'in otomatik menü yapısını bypass ettik ve kendi profesyonel navigasyonumuzu kurduk."

---

### 💎 5. "Glassmorphism Nedir?"
- **Cevap:** "Kullandığımız şeffaf, buzlu cam benzeri form yapısıdır hocam. `backdrop-filter: blur(20px)` özelliğiyle arka plandaki renklerin kart içinden süzülmesini sağladık. Bu, modern finans uygulamalarında (Apple, Revolut vb.) sıkça gördüğümüz bir 'Premium' tasarım trendidir."
