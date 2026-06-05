🏠 UniEv – Üniversite Konaklama ve Ev Arkadaşı Eşleştirme Platformu

**Yazılım Laboratuvarı II Projesi** **Kocaeli Sağlık ve Teknoloji Üniversitesi** **2025–2026 Bahar Dönemi** ---

## 📖 Proje Açıklaması ve Amacı
UniEv, üniversite öğrencilerinin güvenli kiralık konut bulmalarına ve kendilerine en uygun ev arkadaşı seçmelerine yardımcı olmak için tasarlanmış tam donanımlı (full-stack) bir web platformudur. 

Öğrencilerin barınma süreçlerinde yaşadığı zorlukları ve dolandırıcılık risklerini azaltmayı hedefleyen bu proje ilan oluşturma, yaşam tarzı ve bütçe analizine dayalı akıllı ev arkadaşıı eşleştirmesi ve gerçek zamanlı mesajlaşma gibi çözümler sunar.

---
✨ Özellikler
🔐 Kimlik Doğrulama ve Güvenlik
Kullanıcı Kayıt Sistemi
JWT Tabanlı Kimlik Doğrulama
E-Posta Doğrulama
Şifre Sıfırlama
Hesap Kilitleme Koruması
Rol Bazlı Yetkilendirme
Yönetici Yetkilendirme Sistemi

👤 Kullanıcı Yönetimi
Profil Oluşturma
Profil Güncelleme
Profil Fotoğrafı Yükleme
Bütçe Tercihleri
Yaşam Tarzı Tercihleri
Kullanıcı Puanlama Sistemi

🏠 İlan Yönetimi
İlan Oluşturma
İlan Güncelleme
İlan Silme
Fotoğraf Yükleme
Fiyat Filtreleme
Şehir Filtreleme
Detaylı İlan Görüntüleme

💬 Gerçek Zamanlı Mesajlaşma
Kullanıcılar Arası Mesajlaşma
Görsel ve Dosya Gönderimi
Socket.IO Desteği
Gerçek Zamanlı Güncellemeler

❤️ Favoriler
Favori İlan Ekleme
Favori İlanları Yönetme

🚨 Güvenlik Özellikleri
Dolandırıcılık Skoru Analizi
Şüpheli İlan Bildirme
Güvenlik İndeksi
Yönetici Moderasyonu

🔔 Bildirim Sistemi
Gerçek Zamanlı Bildirimler
Kullanıcı Uyarıları

🤝 Ev Arkadaşı Eşleştirme
Uyumluluk Analizi
Yaşam Tarzı Bazlı Eşleştirme
Akıllı Öneriler

📊 Yönetici Paneli
Kullanıcı Yönetimi
İlan Yönetimi
Rapor Yönetimi
Denetim Kayıtları (Audit Logs)


## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

### Arka Plan (Backend) & Veri Tabanı
* **Python 3.12** – Ana programlama dili
* **FastAPI** – Yüksek performanslı API altyapısı
* **SQLAlchemy ORM** – Veri tabanı ilişkilendirme modeli
* **SQLite** – Hafif ve hızlı veri tabanı yönetimi
* **Socket.IO** – Anlık ve gerçek zamanlı iletişim altyapısı

### Ön Yüz (Frontend)
* **HTML5 & CSS3** – Temel web yapısı
* **Tailwind CSS** Modern ve duyarlı (responsive) arayüz tasarımı
* **Jinja2 Templates** – Dinamik sayfa motoru

### Güvenlik & Ek Kütüphaneler
* **Google Maps API** – Konum ve harita servisleri
* **python-dotenv** – Çevresel değişken yönetimi
* **aiosmtplib** – E-posta bildirim servisleri
* **cuid2** – Güvenli ve benzersiz kimlik (ID) üretimi

---

## 🚀 Kurulum ve Çalıştırma Adımları

1. **Projeyi Bilgisayarınıza İndirin:**
```bash
git clone https://github.com/namikhasan258/uni-ev-projesi.git
```

2. **Sanal Ortam Oluşturun ve Aktif Edin:**
```bash
python -m venv venv

# Windows için:
venv\Scripts\activate

# Linux / macOS için:
source venv/bin/activate
```

3. **Gerekli Kütüphaneleri Yükleyin ve Çalıştırın:**
```bash
pip install -r requirements.txt
uvicorn main:socket_app --host 0.0.0.0 --port 8000
```
📸 Ekran Görüntüleri

Giriş Sayfası

Kayıt Sayfası

Ana Sayfa

İlanlar Sayfası

İlan Detay Sayfası

Ev Arkadaşı Eşleştirme

Mesajlaşma Sistemi

Profil Sayfası

Yönetici Paneli



🔴🔴🔴 BURAYA LANSMAN VİDEOSU LİNKİNİ EKLEYİN 🔴🔴🔴

[Projeyi İzle](:https://youtu.be/BJKZr4FfNJQ)

## 👥 Proje Ekibi ve Rol Dağılımı

| İsim | Öğrenci No | Görevi |
| :--- | :--- | :--- |
| **Kusai Aksoy** | 230501002 | Takım Lideri |
| **Hashem Salem** | 230502064 | Veri Modelleme |
| **Namık Hasan** | 230501055 | UML Diyagramları |
| **Rama Hasanatu** | 230502053 | Kullanıcı Arayüz |
| **Melih Kamil USLU** | 230501059 | Dokümantasyon & UI Dizayn |

## 📄 Lisans
Bu proje, Kocaeli Sağlık ve Teknoloji Üniversitesi Yazılım Laboratuvarı II dersi kapsamında eğitim ve değerlendirme amacıyla geliştirilmiştir. Tüm hakları proje ekibine aittir.
