🏠 UniEv – Üniversite Ev Bulma ve Ev Arkadaşı Eşleştirme Platformu

Yazılım Laboratuvarı II – Proje 3 Kocaeli Sağlık ve Teknoloji Üniversitesi 2025-2026 Bahar Dönemi

📖 Proje Hakkında

UniEv, üniversite öğrencilerinin güvenli, hızlı ve kolay bir şekilde konaklama bulabilmeleri amacıyla geliştirilmiş modern bir web platformudur.

🌟 Platform Sayesinde Kullanıcılar:

🏠 Ev ilanlarını görüntüleyebilir

📞 Ev sahipleriyle iletişim kurabilir

🤝 Uygun ev arkadaşı bulabilir

❤️ Favori ilanlarını kaydedebilir

💬 Gerçek zamanlı mesajlaşabilir

🛡️ Güvenlik analizlerinden yararlanabilir

Sistem, kullanıcı güvenliğini artırmak amacıyla çeşitli doğrulama, yetkilendirme ve güvenlik mekanizmaları içermektedir.

🎯 Projenin Amacı

UniEv'in temel amacı öğrencilerin güvenli ve uygun konaklama seçeneklerine daha kolay ulaşmasını sağlamaktır.

📌 Hedefler:

Güvenilir ilanları öne çıkarmak

Dolandırıcılık riskini azaltmak

Ev sahipleri ve öğrenciler arasındaki iletişimi kolaylaştırmak

Uyumlu ev arkadaşlarını eşleştirmek

Öğrenciler için güvenli bir konaklama ekosistemi oluşturmak

✨ Temel Özellikler

🔐 Kimlik Doğrulama ve Güvenlik

Kullanıcı kayıt ve giriş sistemi

JWT tabanlı kimlik doğrulama altyapısı

E-posta doğrulama ve şifre sıfırlama mekanizması

Hesap kilitleme koruması ve rol bazlı yetkilendirme

Yönetici yetkilendirme sistemi

👤 Kullanıcı Yönetimi

Profil oluşturma ve güncelleme

Profil fotoğrafı yükleme desteği

Bütçe ve yaşam tarzı tercihleri (sigara, evcil hayvan vb.)

Güvenli topluluk için kullanıcı oylama/puanlama sistemi

🏠 İlan Yönetimi

İlan oluşturma, güncelleme ve silme (CRUD)

Çoklu fotoğraf yükleme desteği

Fiyat ve şehir bazlı gelişmiş filtreleme

Detaylı ilan görüntüleme sayfası

💬 Gerçek Zamanlı Mesajlaşma

Socket.IO destekli kullanıcılar arası anlık sohbet

Görsel ve dosya paylaşımı desteği

Canlı mesaj bildirimleri ve anlık güncellemeler

❤️ Favoriler Sistemi

Beğenilen ilanları favorilere ekleme

Favori ilanları tek ekrandan görüntüleme ve yönetme

🚨 Güvenlik Özellikleri & Bildirimler

Dolandırıcılık riski analizi (FraudScore) ve güvenlik indeksi

Şüpheli ilan bildirme/şikayet altyapısı

Yönetici moderasyonu ve gerçek zamanlı sistem uyarıları

📊 Yönetici Paneli (Admin Dashboard)

Merkezi kullanıcı ve ilan yönetimi

Rapor yönetimi ve şikayet inceleme paneli

Sistem denetim kayıtları (Audit Logs)

🛠️ Kullanılan Teknolojiler

Backend: Python, FastAPI, SQLAlchemy, Socket.IO, JWT Authentication, Argon2

Frontend: HTML5, CSS3, JavaScript, Jinja2 Templates, Tailwind CSS

Veritabanı: SQLite

Diğer Araçlar: Git, GitHub, REST API, SMTP E-Posta Servisleri

🚀 Kurulum ve Çalıştırma Adımları

Projeyi Klonlayın ve Klasöre Girin:

git clone [https://github.com/namikhasan258/uni-ev-projesi.git](https://github.com/namikhasan258/uni-ev-projesi.git)
cd uni-ev-projesi


Sanal Ortam Oluşturun ve Aktif Edin:

python -m venv venv

# Windows için:
venv\Scripts\activate

# Linux / macOS için:
source venv/bin/activate


Bağımlılıkları Kurun ve Uygulamayı Başlatın:

pip install -r requirements.txt
uvicorn main:socket_app --host 0.0.0.0 --port 8000


Uygulama tarayıcınızda http://localhost:8000 adresinde çalışacaktır.

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

🎥 Lansman Videosu

Platformun tanıtım ve lansman videosunu izlemek için aşağıdaki bağlantıya tıklayabilirsiniz:

🔴 UniEv Proje Tanıtım Videosunu İzle

🗂 Proje Yapısı

UniEv/

core/ (auth.py, security.py)

routers/ (auth.py, users.py, listings.py, messages.py, match.py, ratings.py, admin.py)

services/

sockets/

templates/

static/

uploads/

screenshots/

documentation/

tests/

database.py

main.py

requirements.txt

.gitignore

README.md

🧪 Testler

Projedeki entegrasyon ve birim testlerini çalıştırmak için terminalde şu komutu çalıştırın:

pytest


Mevcut Test Senaryoları: Kullanıcı doğrulama testleri, JWT güvenlik testleri, API endpoint testleri ve veritabanı işlemleri testleri.

💡 Gelecekteki Geliştirmeler

📱 Mobil uygulama (Flutter/React Native) geliştirilmesi

🤖 Yapay zeka destekli akıllı eşleştirme algoritması

🗺️ İnteraktif harita ve lokasyon entegrasyonu

🎓 Kurumsal üniversite e-postası ile doğrulama sistemi

🌍 Çoklu dil desteği (Multi-language)

💳 Güvenli online ödeme ve kapora sistemi

👥 Proje Ekibi

Grup Adı: CodeForge

Proje Adı: Şarjör Projesi

Öğrenci No

Ad Soyad

Görev

230501002

Kusai Aksoy

Takım Lideri

230502064

Hashem Salem

Veri Modeli

230501055

Namık Hasan

UML Diyagramları

230502053

Rama Hasanatu

Arayüz Tasarımı

230501059

Melih Kamil Uslu

Dokümantasyon & Arayüz Tasarımı

📄 Lisans

Bu proje, Kocaeli Sağlık ve Teknoloji Üniversitesi Yazılım Laboratuvarı II dersi kapsamında eğitim ve değerlendirme amacıyla geliştirilmiştir.

© 2026 CodeForge Takımı. Tüm hakları saklıdır.
