<USER_REQUEST>
# PROJE: ONLINE KÜTÜPHANE YÖNETİM SİSTEMİ

## 1. Rolün ve projenin amacı

Sen kıdemli bir yazılım mimarı, full-stack geliştirici, veritabanı tasarımcısı ve UML uzmanısın.

Bana **Online Kütüphane Yönetim Sistemi** isimli, çalışır durumda, güvenli, modern, anlaşılır ve geliştirilebilir bir  web uygulaması tasarla ve geliştir.

Proje, 11. sınıf yazılım tasarımı ve UML modelleme dersindeki uygulama ödevine uygun olmalıdır. Kodun gerçek bir uygulama olarak çalışması ve UML diyagramlarının geliştirilen yazılımla tutarlı olması zorunludur.

Yalnızca açıklama, taslak veya örnek kod verme. Projenin mimarisini tasarla, dosya yapısını oluştur, kodları eksiksiz hazırla, veritabanını kur, uygulamanın çalıştırılmasını açıkla ve istenen UML diyagramlarını üret.

Tüm arayüz metinleri, açıklamalar, hata mesajları, butonlar ve dokümantasyon Türkçe olsun.

## 2. Teknoloji ve mimari

Aşağıdaki teknolojileri kullan:

- Frontend: React ve TypeScript.
- Arayüz tasarımı: CSS veya Tailwind CSS.
- Backend: Python ve FastAPI.
- API mimarisi: REST API.
- Veritabanı: PostgreSQL.
- ORM: SQLAlchemy.
- Veritabanı şema yönetimi: Alembic.
- Kimlik doğrulama: Güvenli oturum veya uygun şekilde uygulanan JWT tabanlı kimlik doğrulama.
- Parola saklama: Argon2 veya bcrypt gibi güvenli bir parola hash algoritması.
- Test: pytest ve frontend için uygun test araçları.
- Dağıtım: Docker ve Docker Compose.
- UML diyagramları: PlantUML.

Teknolojilerin güncel ve birbiriyle uyumlu kararlı sürümlerini seç. Sürüm numaralarını proje dosyalarında sabitle.

Uygulamayı üç temel katmana ayır:

1. Web arayüzü.
2. Backend API ve iş mantığı.
3. Veritabanı.

Frontend doğrudan veritabanına bağlanmamalı. Tüm veri işlemleri API üzerinden gerçekleştirilmelidir.

## 3. Sistem senaryosu

Bir üniversite kütüphanesi için online yönetim sistemi geliştirilmektedir.

Öğrenciler sisteme kayıt olabilir, giriş yapabilir, kitap arayabilir, kitapların uygunluk durumunu inceleyebilir, ödünç kitap alabilir, aldıkları kitapları iade edebilir ve kendi ödünç alma geçmişlerini görüntüleyebilir.

Yönetici kitap ekleyebilir, kitap bilgilerini güncelleyebilir, kitapları pasifleştirebilir, stokları yönetebilir, ödünç işlemlerini inceleyebilir ve süresi geçen kitaplar için gecikme raporu oluşturabilir.

Sistem kitap stoklarını doğru tutmalı ve aynı kitabın mevcut olmayan bir kopyasının ödünç verilmesini engellemelidir.

## 4. Kullanıcı rolleri ve yetkileri

### A. Öğrenci

Öğrenci aşağıdaki işlemleri yapabilmelidir:

- Hesap oluşturmak ve giriş yapmak.
- Güvenli biçimde oturumu kapatmak.
- Kitapları listelemek.
- Kitapları isim, yazar, ISBN ve kategoriye göre aramak.
- Kitapları kategoriye göre filtrelemek.
- Kitabın ayrıntılarını ve mevcut stok sayısını görüntülemek.
- Uygun kitapları ödünç almak.
- Kendi aktif ödünç kitaplarını görüntülemek.
- Son iade tarihlerini görmek.
- Aldığı kitapları iade etmek.
- Geçmiş ödünç ve iade kayıtlarını incelemek.
- Gecikmiş kitapları varsa görüntülemek.
- Profil bilgilerini görüntülemek ve izin verilen bilgileri güncellemek.

Bir öğrenci başka bir öğrencinin özel ödünç alma geçmişini görememelidir.

### B. Yönetici

Yönetici aşağıdaki işlemleri yapabilmelidir:

- Güvenli biçimde giriş yapmak.
- Yeni kitap eklemek.
- Kitap bilgilerini güncellemek.
- Kitapları kategorilere atamak.
- Kitap stoklarını yönetmek.
- Kitapları silmek yerine gerekli durumlarda pasifleştirmek.
- Kitap listesini ve uygunluk durumlarını incelemek.
- Kullanıcı listesini görüntülemek.
- Aktif ödünç işlemlerini görüntülemek.
- Kitap iade işlemlerini denetlemek.
- Gecikmiş kitapları listelemek.
- Gecikme raporunu tarih aralığına, öğrenciye veya kitaba göre filtrelemek.
- Sistem genelindeki kitap ve ödünç istatistiklerini görüntülemek.

Yetkisiz öğrenciler yönetici sayfalarına yalnızca arayüzden değil, API istekleri üzerinden de erişememelidir.

## 5. İş kuralları

Aşağıdaki kuralları iş mantığına dahil et. Yapılandırılabilir olması gereken değerleri ayrı bir ayar mekanizmasıyla yönet.

1. Varsayılan ödünç süresi 14 gün olsun.
2. Bir öğrencinin aynı anda en fazla 3 aktif ödünç kaydı bulunabilsin.
3. Stokta uygun kopya yoksa ödünç alma işlemi reddedilsin.
4. Bir kitabın mevcut stok sayısı hiçbir zaman sıfırın altına düşmesin.
5. Öğrenci aynı kitabın bir kopyasını zaten ödünç almışsa ikinci bir aktif ödünç kaydı oluşturamasın.
6. Bir kitap ödünç verildiğinde mevcut stok bir azalsın.
7. Bir kitap iade edildiğinde mevcut stok bir artsın.
8. İade işlemi aynı ödünç kaydı üzerinde yalnızca bir kez başarılı olabilsin.
9. Son iade tarihi geçmiş ve henüz iade edilmemiş kayıtlar gecikmiş kabul edilsin.
10. Gecikme durumu hesaplanırken iade tarihi, son iade tarihi ve geçerli tarih dikkate alınsın.
11. İade edilmiş bir kayıt gecikmiş aktif ödünç olarak raporlanmasın.
12. Aktif ödünç kaydı bulunan bir kitabın geçmişi bozulacak şekilde fiziksel olarak silinmesine izin verilmesin.
13. Pasif kullanıcılar yeni kitap ödünç alamamalı.
14. Pasifleştirilmiş kitaplar yeni ödünç işlemine kapalı olmalı.
15. Hatalı girişler, geçersiz tarihler, bulunamayan kayıtlar ve yetkisiz işlemler uygun hata mesajlarıyla sonuçlanmalı.
16. Stok güncelleme ve ödünç işlemleri veritabanı transaction işlemleriyle korunmalı. Eş zamanlı isteklerde aynı son kopyanın iki öğrenciye verilmesi engellenmeli.
17. Ödünç ve iade geçmişi korunmalı; raporlar kayıtların geçmişini değiştirmeden üretilmeli.

Gecikme raporu oluşturmak zorunludur. Gecikme cezası veya para tahsilatı istenmiyor; bu nedenle ödeme sistemi ekleme. Varsayımları README dosyasında açıkla.

## 6. Veritabanı tasarımı

En az aşağıdaki tabloları oluştur:

### users
Alanlar:
- id
- student_number
- full_name
- email
- password_hash
- role
- is_active
- created_at
- updated_at

E-posta adresi benzersiz olmalı. Öğrenci numarası gerekiyorsa benzersiz olmalı. Parola hiçbir zaman düz metin olarak saklanmamalı.

### categories
Alanlar:
- id
- name
- description
- is_active
- created_at

Kategori adı için uygun benzersizlik ve doğrulama kuralları kullan.

### books
Alanlar:
- id
- isbn
- title
- author
- description
- publisher
- publication_year
- category_id
- shelf_location
- total_copies
- available_copies
- is_active
- created_at
- updated_at

Stok sayıları negatif olamamalı. Toplam ve mevcut kopya sayıları arasındaki tutarlılık korunmalı. ISBN için uygun benzersizlik kuralı uygulanmalı.

### loans
Alanlar:
- id
- user_id
- book_id
- borrowed_at
- due_at
- returned_at
- created_at
- updated_at

Ödünç kaydı ilgili öğrenciyi ve kitabı referans göstermeli. İade edilmemiş bir kayıt aktif kabul edilmeli. Gecikme durumu, iade edilmemiş olması ve son iade tarihinin geçmesi üzerinden hesaplanmalı.

Gerektiğinde denetim kayıtları gibi destekleyici tablolar ekleyebilirsin ancak gereksiz karmaşıklık oluşturma.

Veritabanında birincil anahtarlar, yabancı anahtarlar, benzersiz kısıtlar, NOT NULL koşulları ve uygun indeksler tanımla.

SQLAlchemy modellerini, Alembic migration dosyalarını ve örnek verileri oluştur.

## 7. UML Class Diagram

Ödevin zorunlu koşulu olan en az dört sınıf içeren bir UML Class Diagram hazırla.

En az şu sınıfları kullan:

### User veya Uye
Özellikler:
- id
- studentNumber
- fullName
- email
- passwordHash
- role
- isActive

Metotlar:
- login()
- logout()
- searchBooks()
- borrowBook()
- returnBook()

### Book veya Kitap
Özellikler:
- id
- isbn
- title
- author
- category
- totalCopies
- availableCopies
- isActive

Metotlar:
- isAvailable()
- updateStock()
- updateDetails()

### Loan veya Odunc
Özellikler:
- id
- borrowedAt
- dueAt
- returnedAt

Metotlar:
- borrow()
- returnBook()
- isOverdue()

### Category veya Kategori
Özellikler:
- id
- name
- description

Metotlar:
- addBook()
- removeBook()

İhtiyaç duyulursa raporlama için OverdueReport veya GecikmeRaporu gibi ek bir sınıf ekle.

Sınıfların özelliklerini ve metotlarını gerçek uygulamayla tutarlı yap. Türkçe isimleri tercih edebilirsin ancak bir isimlendirme standardı belirle ve her diyagramda bu standardı koru.

Diyagramda:

- Her sınıfın adı bulunmalı.
- Özellikler ve metotlar ayrı bölümlerde gösterilmeli.
- Uygun görünürlük işaretleri (+, -, #) kullanılmalı.
- Sınıflar arasındaki ilişkiler çizilmeli.
- İlişki türleri doğru belirtilmeli.
- Çokluklar (multiplicity) açıkça gösterilmeli.
- Gerekli yerlerde association, dependency, composition veya aggregation kullanılmalı.
- Öğrenci, kitap, kategori ve ödünç kaydı arasındaki ilişkiler açıklanmalı.

Örneğin bir öğrenci birçok ödünç kaydına sahip olabilir; her ödünç kaydı belirli bir öğrenciyi ve belirli bir kitabı işaret etmelidir. Bir kategori birçok kitaba sahip olabilir. Bu ilişkilerin sayısal çokluklarını UML gösterimiyle belirt.

Class Diagram kodunu eksiksiz PlantUML formatında üret ve görsel olarak oluşturulabilmesini sağla.

## 8. UML Object Diagram

Gerçek nesne örneklerini gösteren bir Object Diagram hazırla.

Aşağıdaki örnek senaryoyu kullan:

Öğrenci:
- studentNumber: "2026001"
- fullName: "Ahmet Yılmaz"
- role: STUDENT

Kitap:
- isbn: "9780000000001"
- title: "Nesne Yönelimli Programlama"
- author: "Mehmet Demir"
- totalCopies: 5
- availableCopies: 4

Ödünç kaydı:
- borrowedAt: "2026-10-10"
- dueAt: "2026-10-24"
- returnedAt: null

Kategori:
- name: "Bilgisayar"

Object Diagram üzerinde sınıf adları yerine nesne örneklerini, örnek alan değerlerini ve nesneler arasındaki bağlantıları göster.

Örneğin:
- ahmet:User
- programlamaKitabi:Book
- odunc001:Loan
- bilgisayar:Category

Diyagramda Ahmet isimli öğrencinin ilgili kitabı ödünç aldığı anlaşılmalı. Örnek nesnelerin alan değerleri veritabanındaki ve Class Diagram'daki tasarımla tutarlı olmalı.

Object Diagram'ı eksiksiz PlantUML koduyla oluştur.

## 9. UML Package Diagram

En az üç mantıksal paket içeren UML Package Diagram hazırla.

Aşağıdaki paket yapısını kullan:

1. Presentation
   - Sayfalar
   - Bileşenler
   - Formlar
   - Arayüz ve kullanıcı etkileşimleri

2. Application
   - Servisler
   - Kullanım senaryoları
   - Ödünç alma iş akışı
   - İade iş akışı
   - Raporlama iş akışı

3. Domain
   - User
   - Book
   - Loan
   - Category
   - İş kuralları

4. Infrastructure
   - Veritabanı bağlantısı
   - SQLAlchemy repository katmanı
   - Migration işlemleri
   - Güvenlik ve yapılandırma

5. API
   - HTTP endpoint'leri
   - Request ve response şemaları
   - Kimlik doğrulama
   - Yetki kontrolleri

Her paketin görevini ve diğer paketlerle bağımlılıklarını göster.

Bağımlılıklar mantıklı yönde olmalı. Domain katmanı doğrudan web arayüzüne veya framework'e bağımlı olmamalı.

Package Diagram'ı PlantUML formatında üret.

## 10. UML Deployment Diagram

Web, API ve veritabanını içeren ayrıntılı bir Deployment Diagram oluştur.

En az şu düğümleri göster:

### Client Device
- Öğrencinin veya yöneticinin bilgisayarı.
- Web tarayıcısı.
- HTTPS bağlantısı.

### Web Server
- React ile oluşturulmuş web uygulamasının yayınlanması.
- Statik HTML, CSS ve JavaScript dosyaları.
- Nginx veya uygun bir statik içerik sunucusu.

### API Server
- Python FastAPI uygulaması.
- Kimlik doğrulama.
- İş mantığı.
- Kitap, kullanıcı, ödünç ve rapor servisleri.
- Veritabanı erişim katmanı.

### Database Server
- PostgreSQL.
- users, books, categories ve loans tabloları.
- İlişkiler, kısıtlar ve indeksler.
- Kalıcı veri saklama.

### Bağlantılar
- Tarayıcı ile web sunucusu arasındaki HTTPS bağlantısı.
- Web istemcisi ile API arasındaki HTTPS/REST bağlantısı.
- API ile veritabanı arasındaki PostgreSQL bağlantısı.

Docker Compose kullanılıyorsa ilgili container'ları ayrı çalıştırılabilir bileşenler olarak belirt.

Deployment Diagram; donanım veya çalıştırma düğümlerini, bu düğümlerde dağıtılan yazılım bileşenlerini ve iletişim bağlantılarını göstermeli.

Eksiksiz PlantUML kodu üret.

## 11. REST API tasarımı

Aşağıdaki endpoint'leri geliştir ve her birinin HTTP metodunu, amacını, yetki gereksinimini ve örnek yanıtını dokümante et.

### Kimlik doğrulama
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

### Kitaplar
- GET /api/books
- GET /api/books/{id}
- POST /api/books
- PATCH /api/books/{id}
- PATCH /api/books/{id}/stock
- DELETE /api/books/{id}

Silme endpoint'i, geçmiş ödünç kayıtlarıyla ilişkili kitaplarda fiziksel silme yerine pasifleştirme uygulamalı.

### Kategoriler
- GET /api/categories
- POST /api/categories
- PATCH /api/categories/{id}
- DELETE /api/categories/{id}

### Öğrenciler
- GET /api/users/me
- PATCH /api/users/me
- GET /api/users/me/loans

Yalnızca yöneticinin erişebileceği kullanıcı listeleme ve yönetme endpoint'lerini de ekle.

### Ödünç ve iade
- POST /api/loans
- GET /api/loans
- GET /api/loans/{id}
- POST /api/loans/{id}/return
- GET /api/loans/my

### Raporlama
- GET /api/reports/overdue
- GET /api/reports/dashboard

Yöneticiye özel rapor endpoint'lerinde yetki kontrolü yap.

Tüm endpoint'lerde uygun durum kodlarını kullan. Örneğin:
- 200: başarılı sorgu veya güncelleme.
- 201: başarılı oluşturma.
- 400: geçersiz iş kuralı isteği.
- 401: kimlik doğrulaması yok veya geçersiz.
- 403: yetki yok.
- 404: kayıt bulunamadı.
- 409: çakışma veya tekrarlanan işlem.
- 422: doğrulama hatası.

Hata cevaplarını tutarlı bir JSON formatında döndür.

Kitap listeleme endpoint'inde arama, filtreleme, sıralama ve sayfalama özellikleri olsun.

Girdi verilerini Pydantic şemalarıyla doğrula. Kullanıcıdan gelen verilere güvenme.

## 12. Frontend sayfaları

Aşağıdaki ekranları oluştur:

1. Giriş sayfası.
2. Kayıt sayfası.
3. Kitap listeleme ve arama sayfası.
4. Kitap ayrıntı sayfası.
5. Öğrenci kontrol paneli.
6. Öğrencinin ödünç kitaplarım sayfası.
7. Öğrencinin ödünç geçmişi sayfası.
8. Yönetici kontrol paneli.
9. Kitap ekleme ve düzenleme sayfası.
10. Kategori yönetimi sayfası.
11. Ödünç işlemleri yönetim sayfası.
12. Gecikme raporu sayfası.
13. Yetkisiz erişim ve bulunamayan sayfalar.

Arayüz modern, sade, responsive ve erişilebilir olmalı. Bilgisayar, tablet ve telefon ekranlarında çalışmalı.

Tasarımda okunabilir tipografi, tutarlı boşluklar, anlaşılır navigasyon, durum rozetleri, arama alanları, filtreler, tablolar ve doğrulama mesajları kullan.

Türkçe tarih gösterimini dd.MM.yyyy biçiminde kullan. Tarih ve saatlerin sunucu ve istemci arasında doğru yorumlandığını doğrula.

İşlem sırasında yükleniyor göstergesi, başarılı işlem mesajı, hata mesajı ve boş liste durumları göster.

Ödünç alma ve iade işlemlerinden önce kullanıcıya işlemin ne olduğunu açıklayan uygun onay ekranı göster.

Öğrenci arayüzünde yönetici işlemlerini gösterme. Ancak güvenliği yalnızca arayüz kontrollerine bırakma; backend'de de yetkilendirme yap.

## 13. Backend iş mantığı

Kodları anlaşılır bir katmanlı mimaride düzenle:

- API/router katmanı.
- Request ve response şemaları.
- Domain modelleri.
- Application/service katmanı.
- Veritabanı erişim katmanı.
- Kimlik doğrulama ve yetkilendirme.
- Raporlama servisleri.

Ödünç alma işlemi tek bir güvenli transaction içinde yürütülmeli:

1. Kullanıcının kimliği doğrulanır.
2. Kullanıcının öğrenci rolüne ve aktif durumda olduğuna bakılır.
3. Mevcut ödünç sayısı kontrol edilir.
4. Kitabın varlığı ve aktif durumda olduğu doğrulanır.
5. Mevcut stok kilitleme veya eş değer eşzamanlılık kontrolü ile güvenli biçimde değerlendirilir.
6. Ödünç kaydı oluşturulur.
7. Kitabın mevcut stok sayısı güncellenir.
8. İşlem başarılıysa commit yapılır; hata varsa rollback uygulanır.

İade işlemi de güvenli bir transaction ile çalışmalı ve aynı kayıt için ikinci kez stok artışı yapılmasını engellemeli.

Veritabanı işlemleri yarıda kaldığında stok ile ödünç kayıtlarının tutarsızlaşmasına izin verme.

## 14. Güvenlik gereksinimleri

- Parolaları hash'leyerek sakla.
- Parolaları loglara yazma.
- Kimlik doğrulama ve rol tabanlı yetkilendirme uygula.
- ORM veya parametreli sorgularla SQL injection riskini azalt.
- Kullanıcı girdilerini doğrula.
- CORS politikasını yapılandır.
- Üretim ortamında HTTPS kullan.
- Gizli bilgileri ortam değişkenlerinden yükle.
- .env dosyasını Git deposuna ekleme.
- .env.example dosyası oluştur.
- Üretim için DEBUG modunu kapat.
- Hassas hata ayrıntılarını kullanıcıya gösterme.
- Yönetici endpoint'lerinde sunucu tarafı rol kontrolü yap.
- Gerekli kimlik doğrulama ve parola denemesi korumalarını uygula.
- Bağımlılıkların güvenli sürümlerini seç.
- Kullanıcıların kendi kayıtları dışındaki özel bilgileri görüntülemesini engelle.

## 15. Raporlama ve kontrol paneli

Yönetici panelinde aşağıdaki istatistikleri sun:

- Toplam aktif kitap başlığı sayısı.
- Toplam kitap kopyası sayısı.
- Ödünç verilmeye uygun kopya sayısı.
- Aktif ödünç kayıtları.
- Gecikmiş ödünç kayıtları.
- Toplam aktif öğrenci sayısı.
- Yakın zamanda gerçekleştirilen ödünç ve iade işlemleri.

Gecikme raporunda en az aşağıdaki sütunlar bulunsun:

- Öğrenci numarası.
- Öğrencinin adı soyadı.
- Kitap adı.
- ISBN.
- Ödünç alma tarihi.
- Son iade tarihi.
- Gecikme günü.

Gecikme günü negatif olamaz. İade edilmiş kitaplar aktif gecikme raporunda yer almamalı.

Filtreler ve sayfalama uygulanmalı. Rapor verileri gerçek veritabanı kayıtlarından üretilmeli; örnek sabit sayılar kullanılmamalı.

## 16. Testler

Automatik testler yaz.

En az aşağıdaki senaryoları kapsa:

1. Yeni öğrencinin başarıyla kayıt olması.
2. Aynı e-posta adresiyle ikinci kez kayıt girişiminin reddedilmesi.
3. Doğru ve yanlış parolayla giriş.
4. Öğrencinin kitap listesini görüntülemesi.
5. Yönetici tarafından yeni kitap eklenmesi.
6. Öğrencinin uygun kitabı ödünç alması.
7. Stokta kitap yokken ödünç işleminin reddedilmesi.
8. Öğrenci ödünç limitini aştığında işlemin reddedilmesi.
9. Aynı öğrencinin aynı kitaba ilişkin ikinci aktif ödünç işleminin engellenmesi.
10. Başarılı iade işleminde stok sayısının doğru artması.
11. Aynı ödünç kaydının ikinci kez iade edilmesinde stok artışı olmaması.
12. Gecikmiş kayıtların doğru raporlanması.
13. Öğrencinin başka bir öğrencinin ödünç kayıtlarına erişememesi.
14. Öğrencinin yönetici endpoint'ine erişememesi.
15. Geçersiz veri gönderildiğinde anlamlı doğrulama hatası dönmesi.
16. Kitabın eşzamanlı olarak ödünç alınmaya çalışılması durumunda stok tutarlılığının korunması.

Testlerde gerekli veritabanı yalıtımını sağla. Her test diğer testlerden bağımsız çalışabilsin.

## 17. Proje klasör yapısı

Frontend ve backend'i ayrı klasörlerde organize et.

Örnek yapı:

online-kutuphane/
  frontend/
    src/
      components/
      pages/
      layouts/
      services/
      hooks/
      types/
      utils/
    package.json
    Dockerfile
  backend/
    app/
      api/
      core/
      models/
      schemas/
      services/
      repositories/
      db/
      main.py
    tests/
    alembic/
    requirements.txt
    Dockerfile
  uml/
    class-diagram.puml
    object-diagram.puml
    package-diagram.puml
    deployment-diagram.puml
  docker-compose.yml
  .env.example
  .gitignore
  README.md

Gerekirse yapıyı iyileştirebilirsin. Ancak bütün dosyaların sorumluluklarını açıkla ve kodu tutarlı şekilde bu yapıya yerleştir.

## 18. Docker ve çalıştırma

Docker Compose ile aşağıdaki servisleri ayağa kaldır:

- frontend/web
- backend/api
- PostgreSQL veritabanı

Gerekli ağları, ortam değişkenlerini, portları, servis bağımlılıklarını ve kalıcı veritabanı volume'ünü tanımla.

Uygulama yeniden başlatıldığında veritabanı verileri korunmalı.

Veritabanı migration'larının nasıl çalıştırılacağını belirt. Veritabanı hazır olmadan API'nin sorgulara başlamamasını sağla.

Gerekli örnek verileri yükleyen bir seed mekanizması ekle. En az bir yönetici, birkaç öğrenci, çeşitli kitaplar, kategoriler ve örnek ödünç kayıtları oluştur.

Örnek yönetici hesabı varsa parolasını dokümantasyonda yalnızca yerel geliştirme amacıyla belirt ve üretim ortamında ilk kurulumda değiştirilmesini zorunlu kıl. Üretim için sabit veya varsayılan yönetici parolası bırakma.

README içerisinde aşağıdaki işlemleri adım adım anlat:

1. Gerekli yazılımların kurulumu.
2. Projenin indirilmesi veya klasörün açılması.
3. .env dosyasının hazırlanması.
4. Docker servislerinin başlatılması.
5. Veritabanı migration'larının uygulanması.
6. Örnek verilerin yüklenmesi.
7. Uygulamaya tarayıcıdan erişilmesi.
8. API dokümantasyonunun açılması.
9. Testlerin çalıştırılması.
10. Uygulamanın durdurulması ve yeniden başlatılması.

API dokümantasyonu FastAPI'nin OpenAPI/Swagger desteğiyle erişilebilir olmalı.

## 19. UML diyagramlarının doğrulanması

Dört zorunlu diyagramı ayrı ayrı üret:

1. Class Diagram.
2. Object Diagram.
3. Package Diagram.
4. Deployment Diagram.

Her diyagramın geçerli, eksiksiz ve PlantUML ile oluşturulabilir kaynak kodunu ayrı dosyada tut.

Ayrıca her diyagramın altında Türkçe açıklama ver.

Şunları kontrol et:

- Class Diagram'da en az dört sınıf var.
- Sınıfların özellikleri, metotları ve ilişkileri gösterilmiş.
- İlişki çoklukları doğru belirtilmiş.
- Object Diagram gerçek nesne örnekleri ve aralarındaki bağlantıları gösteriyor.
- Object Diagram'daki örnek değerler tutarlı.
- Package Diagram'da en az üç mantıksal paket bulunuyor.
- Deployment Diagram'da web istemcisi veya web sunucusu, API sunucusu ve veritabanı yer alıyor.
- Paket bağımlılıkları ve deployment bağlantıları anlaşılır biçimde gösterilmiş.
- Diyagram isimleri ve modeller uygulama koduyla tutarlı.
- PlantUML kaynakları sözdizimi bakımından geçerli.

## 20. Teslim edilecek çıktılar

Çalışmayı aşağıdaki sırayla tamamla:

1. Projenin kapsamını ve varsayımlarını açıkla.
2. Gereksinim analizini hazırla.
3. Kullanıcı rolleri ve kullanım senaryolarını belirt.
4. Sistem mimarisini açıkla.
5. Veritabanı şemasını ve tablo ilişkilerini hazırla.
6. REST API endpoint'lerini ve erişim yetkilerini açıkla.
7. Dört UML diyagramını ve PlantUML kaynak dosyalarını üret.
8. Çalışan backend kodunu oluştur.
9. Çalışan frontend kodunu oluştur.
10. Veritabanı migration ve seed dosyalarını hazırla.
11. Docker dosyalarını oluştur.
12. Otomatik testleri yaz.
13. README ve kurulum talimatlarını yaz.
14. Gereksinimlerin karşılandığını gösteren bir kontrol listesi sun.

Kod verirken dosyanın tam yolunu belirt ve her dosyanın içeriğini eksiksiz yaz. Bir dosyaya ait kodu başka bir dosyanın içine karıştırma.

Eksik import, tanımlanmamış fonksiyon, hayali API endpoint'i, uyumsuz model alanı, placeholder veya yalnızca örnek amaçlı sahte bir işlem bırakma.

Gerçek dosya sistemi üzerinde çalışabiliyorsan dosyaları doğrudan oluştur, bağımlılıkları uyumlu hale getir, testleri çalıştır ve ortaya çıkan hataları düzelt. Doğrulayamadığın işlemleri başarılı olmuş gibi gösterme.

Bütün projeyi tek bir aşamada üretmek mümkün değilse çalıştırılabilir bir temel sürümle başla ve aşamalar hâlinde tamamla. Her aşamada kod ile UML diyagramlarının tutarlılığını koru.

## 21. Son kabul kriterleri

Proje ancak aşağıdaki koşullar karşılandığında tamamlanmış sayılsın:

- Öğrenci hesap oluşturup giriş yapabiliyor.
- Kitaplar aranıp görüntülenebiliyor.
- Yönetici kitap ve kategori yönetimi yapabiliyor.
- Uygun kitap ödünç alınabiliyor.
- Kitap iade edilebiliyor.
- Stok sayıları doğru tutuluyor.
- Ödünç limitleri ve yetki kontrolleri çalışıyor.
- Gecikmiş kitaplar doğru raporlanıyor.
- Veriler PostgreSQL üzerinde kalıcı olarak saklanıyor.
- Frontend, API ve veritabanı birlikte çalışıyor.
- Docker Compose ile uygulama başlatılabiliyor.
- Otomatik testler çalıştırılabiliyor.
- Dört UML diyagramının kaynak kodu mevcut.
- UML çoklukları, ilişkiler ve nesne örnekleri tutarlı.
- README üzerinden başka bir geliştirici sistemi kurup çalıştırabiliyor.

Şimdi gereksinimlerden başlayarak bu projeyi eksiksiz tasarla ve uygula. Önceliğin doğruluk, çalışan kod, anlaşılır mimari, güvenli veri işlemleri ve ödevde istenen bütün UML çıktılarının tamamlanması olsun.

</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-10-18T16:12:50+03:00.

The user's current state is as follows:
Active Document: /Untitled-1 (LANGUAGE_UNSPECIFIED)
Cursor is on line: 1
</ADDITIONAL_METADATA>
<USER_SETTINGS_CHANGE>
The user changed setting `Model Selection` from None to Claude Opus 5.5 (Medium). No need to comment on this change if the user doesn't ask about it. If reporting what model you are, please use a human readable name instead of the exact string.
</USER_SETTINGS_CHANGE>