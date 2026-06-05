# 🏠 UniEv
Üniversite Ev Bulma ve Ev Arkadaşı Eşleştirme Platformu
Kocaeli Sağlık ve Teknoloji Üniversitesi
Yazılım Laboratuvarı II – Proje 3
2025-2026 Bahar Dönemi

📖 Proje Açıklaması
UniEv, üniversite öğrencilerinin güvenli ve hızlı bir şekilde konaklama bulabilmesi amacıyla geliştirilmiş modern bir web platformudur.

Platform sayesinde öğrenciler:

Ev ilanlarını görüntüleyebilir,
Ev sahipleriyle iletişim kurabilir,
Ev arkadaşı bulabilir,
Favori ilanlarını kaydedebilir,
Gerçek zamanlı mesajlaşabilir,
Güvenlik analizlerinden yararlanabilir.
Sistem aynı zamanda kullanıcı güvenliğini artırmak amacıyla çeşitli doğrulama ve güvenlik mekanizmaları içermektedir.

🎯 Projenin Amacı
Öğrencilerin güvenli, hızlı ve kolay şekilde konaklama bulabilmesini sağlamak.

Ayrıca:

Güvenli ilanların öne çıkarılması,
Dolandırıcılık riskinin azaltılması,
Ev sahibi ve öğrenciler arasındaki iletişimin kolaylaştırılması,
Uyumlu ev arkadaşlarının eşleştirilmesi
amaçlanmıştır.

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

🛠 Kullanılan Teknolojiler
Backend
Python
FastAPI
SQLAlchemy
Socket.IO
JWT Authentication
Argon2 Password Hashing
Frontend
HTML5
CSS3
JavaScript
Jinja2 Templates
Veritabanı
SQLite
Diğer Araçlar
Git
GitHub
REST API
E-Posta Servisleri

⚙️ Kurulum Adımları
1. Projeyi Klonlayın

2. Proje Klasörüne Girin
cd UniEv
3. Sanal Ortam Oluşturun
python -m venv venv
4. Sanal Ortamı Aktifleştirin
Windows
venv\Scripts\activate
Linux / MacOS
source venv/bin/activate
5. Bağımlılıkları Kurun
pip install -r requirements.txt
▶️ Projeyi Çalıştırma
uvicorn main:socket_app --host 0.0.0.0 --port 8000
Uygulama:

http://localhost:8000
adresinde çalışacaktır.

🎥 Lansman Videosu
🔴🔴🔴 BURAYA LANSMAN VİDEOSU LİNKİNİ EKLEYİN 🔴🔴🔴

[Projeyi İzle](VIDEO_LINKI)
🗂 Klasör Yapısı
UniEv/
│
├── core/
│   ├── auth.py
│   └── security.py
│
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── listings.py
│   ├── messages.py
│   ├── match.py
│   ├── ratings.py
│   ├── admin.py
│   └── ...
│
├── services/
├── sockets/
├── templates/
├── static/
├── uploads/
├── screenshots/
├── documentation/
├── tests/
│
├── database.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
🔄 Geliştirme Önerileri
Mobil uygulama geliştirilmesi
Yapay zeka destekli eşleştirme sistemi
Harita entegrasyonu
Üniversite doğrulama sistemi
Çoklu dil desteği
Online ödeme sistemi
Gelişmiş güvenlik analizleri
🧪 Testler
pytest
🔴 Test dosyalarınız varsa burada açıklayın.

👥 Proje Ekibi
Grup Adı
CodeForge Şarjör Projesi
Öğrenci No	Ad Soyad	Rol
230501002	Kusai Aksoy	Takım Lideri
230502064	Hashem Salem	Veri Modeli
230501055	Namik Hasan	UML Diyagramları
230502053	Rama Hasanatu	Arayüz Tasarımı
230501059	Melih Kamil Uslu	Dokümantasyon & Arayüz Tasarımı

📄 Lisans
Bu proje, Kocaeli Sağlık ve Teknoloji Üniversitesi Yazılım Laboratuvarı II dersi kapsamında eğitim ve değerlendirme amacıyla geliştirilmiştir. Tüm hakları proje ekibine aittir.
