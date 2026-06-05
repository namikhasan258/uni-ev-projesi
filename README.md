# 🏠 UniEv
🏠 UniEv – Üniversite Ev Bulma ve Ev Arkadaşı Eşleştirme Platformu

Kocaeli Sağlık ve Teknoloji Üniversitesi
Yazılım Laboratuvarı II – Proje 3
2025-2026 Bahar Dönemi

📖 Proje Hakkında

UniEv, üniversite öğrencilerinin güvenli, hızlı ve kolay bir şekilde konaklama bulabilmeleri amacıyla geliştirilmiş modern bir web platformudur.

Platform sayesinde kullanıcılar:

🏠 Ev ilanlarını görüntüleyebilir
📞 Ev sahipleriyle iletişim kurabilir
🤝 Uygun ev arkadaşı bulabilir
❤️ Favori ilanlarını kaydedebilir
💬 Gerçek zamanlı mesajlaşabilir
🛡️ Güvenlik analizlerinden yararlanabilir

Sistem, kullanıcı güvenliğini artırmak amacıyla çeşitli doğrulama, yetkilendirme ve güvenlik mekanizmaları içermektedir.

🎯 Projenin Amacı

UniEv'in temel amacı öğrencilerin güvenli ve uygun konaklama seçeneklerine daha kolay ulaşmasını sağlamaktır.

Hedefler
Güvenilir ilanları öne çıkarmak
Dolandırıcılık riskini azaltmak
Ev sahipleri ve öğrenciler arasındaki iletişimi kolaylaştırmak
Uyumlu ev arkadaşlarını eşleştirmek
Öğrenciler için güvenli bir konaklama ekosistemi oluşturmak
✨ Temel Özellikler
🔐 Kimlik Doğrulama ve Güvenlik
Kullanıcı kayıt sistemi
JWT tabanlı kimlik doğrulama
E-posta doğrulama
Şifre sıfırlama
Hesap kilitleme koruması
Rol bazlı yetkilendirme
Yönetici yetkilendirme sistemi
👤 Kullanıcı Yönetimi
Profil oluşturma
Profil güncelleme
Profil fotoğrafı yükleme
Bütçe tercihleri
Yaşam tarzı tercihleri
Kullanıcı puanlama sistemi
🏠 İlan Yönetimi
İlan oluşturma
İlan güncelleme
İlan silme
Fotoğraf yükleme
Fiyat filtreleme
Şehir filtreleme
Detaylı ilan görüntüleme
💬 Gerçek Zamanlı Mesajlaşma
Kullanıcılar arası mesajlaşma
Görsel ve dosya paylaşımı
Socket.IO desteği
Anlık güncellemeler
❤️ Favoriler Sistemi
Favori ilan ekleme
Favori ilanları görüntüleme
Favori ilanları yönetme
🚨 Güvenlik Özellikleri
Dolandırıcılık riski analizi
Şüpheli ilan bildirme
Güvenlik indeksi sistemi
Yönetici moderasyonu
🔔 Bildirim Sistemi
Gerçek zamanlı bildirimler
Sistem uyarıları
Kullanıcı bildirimleri
🤝 Ev Arkadaşı Eşleştirme
Uyumluluk analizi
Yaşam tarzı bazlı eşleştirme
Akıllı öneri sistemi
📊 Yönetici Paneli
Kullanıcı yönetimi
İlan yönetimi
Rapor yönetimi
Sistem denetim kayıtları (Audit Logs)
🛠️ Kullanılan Teknolojiler
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
SMTP E-Posta Servisleri
⚙️ Kurulum
1️⃣ Projeyi Klonlayın
git clone REPOSITORY_LINK
2️⃣ Proje Klasörüne Girin
cd UniEv
3️⃣ Sanal Ortam Oluşturun
python -m venv venv
4️⃣ Sanal Ortamı Aktifleştirin
Windows
venv\Scripts\activate
Linux / macOS
source venv/bin/activate
5️⃣ Bağımlılıkları Kurun
pip install -r requirements.txt
▶️ Uygulamayı Çalıştırma
uvicorn main:socket_app --host 0.0.0.0 --port 8000

Uygulama aşağıdaki adreste çalışacaktır:

http://localhost:8000
🎥 Lansman Videosu

📺 Proje Tanıtım Videosu:

BURAYA YOUTUBE VİDEO LİNKİ EKLENECEK

Örnek:

[🎬 Projeyi İzle](https://youtube.com/...)
📁 Proje Yapısı
UniEv
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
🚀 Gelecekteki Geliştirmeler
📱 Mobil uygulama geliştirilmesi
🤖 Yapay zeka destekli eşleştirme sistemi
🗺️ Harita entegrasyonu
🎓 Üniversite doğrulama sistemi
🌍 Çoklu dil desteği
💳 Online ödeme sistemi
🔒 Gelişmiş güvenlik analizleri
🧪 Testler

Projedeki testleri çalıştırmak için:

pytest

Mevcut testler:

Kullanıcı doğrulama testleri
JWT güvenlik testleri
API endpoint testleri
Veritabanı işlemleri testleri
👥 Proje Ekibi
Grup Adı

CodeForge Şarjör Projesi

Öğrenci No	Ad Soyad	Görev
230501002	Kusai Aksoy	Takım Lideri
230502064	Hashem Salem	Veri Modeli
230501055	Namık Hasan	UML Diyagramları
230502053	Rama Hasanatu	Arayüz Tasarımı
230501059	Melih Kamil Uslu	Dokümantasyon & Arayüz Tasarımı
📄 Lisans

Bu proje, Kocaeli Sağlık ve Teknoloji Üniversitesi Yazılım Laboratuvarı II dersi kapsamında eğitim ve değerlendirme amacıyla geliştirilmiştir.

© 2026 CodeForge Takımı. Tüm hakları saklıdır.
