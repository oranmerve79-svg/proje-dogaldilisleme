# YouTube Video Özetleme ve NLP Analiz Uygulaması

## Proje Açıklaması

Bu proje, Doğal Dil İşleme dersi kapsamında geliştirilmiş bir YouTube video özetleme ve NLP analiz uygulamasıdır.

Uygulama, YouTube videosuna ait transcript verisini alır, metni temizler, konu bloklarına ayırır ve ardından Gemini API desteğiyle yapılandırılmış özet üretir. Proje yalnızca video özetleme işlemi yapmakla sınırlı değildir. Aynı zamanda anahtar kelime çıkarımı, argo / uygunsuz ifade analizi, duygu ve ton analizi, hedef kitle tahmini, çeviri, kullanıcı bazlı geçmiş kayıt sistemi ve PDF raporlama gibi özellikler de sunar.

Uygulamanın ana dili Türkçedir. Varsayılan çıktı dili Türkçe olarak belirlenmiştir. Kullanıcı isterse analiz sonuçlarını farklı dillere çevirebilir.

---

## Projenin Amacı

Günümüzde YouTube üzerinde eğitim, teknoloji, haber, kişisel gelişim ve sosyal medya alanlarında çok sayıda uzun video içeriği bulunmaktadır. Kullanıcıların bu videoların tamamını izlemesi zaman açısından zorlayıcı olabilmektedir.

Bu projenin temel amacı, uzun YouTube videolarını kullanıcılar için daha kısa, anlaşılır ve analiz edilebilir hale getirmektir. Kullanıcı, videonun tamamını izlemek zorunda kalmadan içeriğin özetine, anahtar kelimelerine, duygu / ton analizine, hedef kitle değerlendirmesine ve genel analiz sonucuna ulaşabilir.

---

## Projenin Hedefleri

Bu proje kapsamında hedeflenen temel amaçlar şunlardır:

- YouTube videolarından transcript / altyazı verisi elde etmek
- Alınan metni doğal dil işleme için temizlemek ve düzenlemek
- Uzun video içeriklerinden anlamlı ve yapılandırılmış özet üretmek
- Video içeriğinden anahtar kelimeler çıkarmak
- Metin içerisindeki argo veya uygunsuz ifadeleri tespit etmek
- Video içeriğinin duygu ve ton analizini yapmak
- İçeriğin hedef kitlesi hakkında tahmin üretmek
- Kullanıcıya farklı dil seçenekleriyle çıktı sunmak
- Kullanıcı kayıt / giriş sistemiyle analiz geçmişini saklamak
- Analiz sonuçlarını metin ve PDF raporu olarak indirebilir hale getirmek
- Streamlit arayüzü ile kullanıcı dostu bir web uygulaması geliştirmek
- Projeyi GitHub ve canlı uygulama bağlantısı üzerinden erişilebilir hale getirmek

---

## Projenin Özgün Yönleri

Bu proje, yalnızca basit bir video özetleme uygulaması değildir. YouTube videolarını çok yönlü olarak analiz eden bütünleşik bir NLP sistemi olarak tasarlanmıştır.

Projenin öne çıkan özgün yönleri şunlardır:

- Transcript alma işleminde birden fazla yöntemin desteklenmesi
- YouTube transcript verisi alınamadığında alternatif yöntemlerin kullanılabilmesi
- Metnin konu bloklarına ayrılarak daha kontrollü özetlenmesi
- Gemini API ile yapılandırılmış ve daha anlamlı özet üretilmesi
- Anahtar kelime çıkarımı için Gemini ve fallback yaklaşımlarının kullanılması
- Argo / uygunsuz ifade analizinin sisteme dahil edilmesi
- Duygu ve ton analizinin ayrı bir çıktı olarak sunulması
- Hedef kitle tahmini yapılması
- Kullanıcı bazlı analiz geçmişi tutulması
- Analiz sonuçlarının PDF raporu olarak indirilebilmesi
- Türkçe odaklı kullanıcı deneyimi sunulması
- Streamlit üzerinden erişilebilir canlı web uygulaması oluşturulması

---

## Kullanılan Teknolojiler

Projede kullanılan temel teknolojiler aşağıdaki tabloda verilmiştir.

| Teknoloji / Kütüphane | Kullanım Amacı |
|---|---|
| Python | Ana programlama dili |
| Streamlit | Web arayüzü geliştirme |
| Gemini API | Özetleme, duygu / ton analizi ve bazı NLP işlemleri |
| faster-whisper | Video sesinden transcript çıkarma |
| yt-dlp | YouTube video verilerine erişme |
| youtube-transcript-api | Transcript alma işlemi için alternatif yöntem |
| regex | Metin temizleme ve ön işleme |
| YAKE | Anahtar kelime çıkarımı için fallback yöntem |
| deep-translator | Çeviri işlemleri |
| SQLite | Kullanıcı ve analiz geçmişi saklama |
| reportlab | PDF raporu oluşturma |
| Git / GitHub | Versiyon kontrolü ve proje paylaşımı |
| Streamlit Community Cloud | Canlı uygulama yayınlama |

---

## Kullanılan Yöntemler

### 1. Transcript Alma

Uygulama, YouTube videosuna ait metin verisini elde etmek için transcript alma yöntemlerini kullanır. Video altyazısı erişilebilir durumdaysa transcript verisi alınır ve analiz sürecine aktarılır.

Transcript alma işlemi sırasında YouTube transcript verileri kullanılır. Bazı videolarda altyazı bulunmadığı, video erişimi kısıtlı olduğu veya transcript verisi kapalı olduğu için bu adım başarısız olabilir. Bu durumda uygulama kullanıcıyı bilgilendirir.

### 2. Metin Ön İşleme

Transcript verisi doğrudan analiz için uygun olmayabilir. Bu nedenle metin üzerinde ön işleme uygulanır.

Ön işleme adımları şunlardır:

- Gereksiz boşlukların temizlenmesi
- Metin segmentlerinin düzenlenmesi
- Metnin daha okunabilir hale getirilmesi
- Uzun metnin analiz için uygun parçalara ayrılması
- Konu bloklarının oluşturulması

Bu adım sayesinde özetleme ve analiz işlemleri daha düzenli bir metin üzerinde gerçekleştirilir.

### 3. Özetleme

Özetleme işlemi Gemini API desteğiyle yapılmaktadır. Metin önce konu bloklarına ayrılır. Ardından her blok için ara özetler oluşturulur. Son aşamada bu ara özetler birleştirilerek final yapılandırılmış özet üretilir.

Bu yöntem, uzun video metinlerinin daha düzenli, anlaşılır ve anlamlı şekilde özetlenmesini sağlar.

### 4. Anahtar Kelime Çıkarımı

Anahtar kelime çıkarımı için öncelikli olarak Gemini API kullanılır. Gemini API’den sonuç alınamadığı durumlarda fallback yöntemleri devreye girebilir.

Bu özellik sayesinde video içeriğinde öne çıkan kavramlar kullanıcıya sunulur.

### 5. Argo / Uygunsuz İfade Analizi

Argo analizi sözlük tabanlı bir yaklaşımla yapılmaktadır. Metin içinde belirli argo veya uygunsuz ifadeler tespit edilerek kullanıcıya raporlanır.

Bu özellik, özellikle içerik kalitesini değerlendirmek ve video dilini analiz etmek açısından faydalıdır.

### 6. Duygu ve Ton Analizi

Duygu ve ton analizi Gemini API ile yapılmaktadır. Bu analiz sayesinde video içeriğinin genel tonu, anlatım yapısı ve duygusal yönü hakkında bilgi verilir.

Gemini API yoğunluğu veya kota durumuna bağlı olarak bazı LLM tabanlı analizlerde geçici gecikme veya atlanma yaşanabilir. Bu durumda uygulama mümkün olan analizleri üretmeye devam eder.

### 7. Hedef Kitle Tahmini

Uygulama, video içeriğinin diline, konusuna ve anlatım biçimine göre hedef kitle hakkında tahmin üretir. Bu özellik, içerik üreticileri için videonun hangi kullanıcı grubuna hitap ettiğini anlamada yardımcı olabilir.

### 8. Çeviri

Kullanıcı isterse analiz sonuçlarını farklı dillere çevirebilir. Çeviri işlemleri için `deep-translator` kullanılmaktadır.

### 9. Kullanıcı Yönetimi ve Geçmiş Kayıt

Uygulamada kullanıcı kayıt ve giriş sistemi bulunmaktadır. Kullanıcıların yaptığı analizler SQLite veritabanında saklanır. Böylece kullanıcı daha önce yaptığı analizleri tekrar görüntüleyebilir.

### 10. Raporlama

Analiz sonuçları metin ve PDF olarak indirilebilir. PDF çıktıları `reportlab` kütüphanesi ile oluşturulmaktadır.

---

## Klasör Yapısı

```text
proje-dogaldilisleme/
├── app.py
├── README.md
├── requirements.txt
├── packages.txt
├── youtube_uygulamasi.command
├── youtube_video_summarizer_python.command
└── utils/
    ├── __init__.py
    ├── audience.py
    ├── combined_analysis.py
    ├── keywords.py
    ├── preprocess.py
    ├── report.py
    ├── sentiment.py
    ├── sentiment_audience_bundle.py
    ├── slang.py
    ├── storage.py
    ├── summarizer.py
    ├── summary_keywords_bundle.py
    ├── transcript.py
    └── translator.py
```

---

## Kurulum Adımları

Projeyi bilgisayara indirmek için:

```bash
git clone https://github.com/oranmerve79-svg/proje-dogaldilisleme.git
cd proje-dogaldilisleme
```

Sanal ortam oluşturmak için:

```bash
python3 -m venv .venv
```

Sanal ortamı aktif etmek için:

```bash
source .venv/bin/activate
```

Gerekli kütüphaneleri yüklemek için:

```bash
pip install -r requirements.txt
```

---

## Gemini API Anahtarı

Uygulamanın özetleme ve bazı analiz modüllerinin çalışması için `GEMINI_API_KEY` ortam değişkeni gereklidir.

Mac / Linux için:

```bash
export GEMINI_API_KEY="buraya_gemini_api_key"
```

Windows için:

```bash
set GEMINI_API_KEY=buraya_gemini_api_key
```

API anahtarı güvenlik nedeniyle GitHub reposuna eklenmemelidir.

---

## Çalıştırma Komutu

Projeyi yerel bilgisayarda çalıştırmak için:

```bash
streamlit run app.py
```

Komut çalıştırıldıktan sonra uygulama tarayıcı üzerinden açılır.

---

## Canlı Uygulama Bağlantısı

Canlı uygulama bağlantısı:

```text
BURAYA_CANLI_UYGULAMA_LINKI_EKLE
```

Örnek:

```text
https://proje-dogaldilisleme-9vmezzc4ryrqtc76krjx7.streamlit.app
```

---

## GitHub Repository

GitHub repo bağlantısı:

```text
https://github.com/oranmerve79-svg/proje-dogaldilisleme
```

---

## Proje Tanıtım Videosu

Proje tanıtım videosu bağlantısı:

```text
BURAYA_VIDEO_LINKI_EKLE
```

---

## Ürün Özellikleri

Uygulamada bulunan temel özellikler şunlardır:

- Kullanıcı kayıt sistemi
- Kullanıcı giriş sistemi
- YouTube video linki ile analiz başlatma
- Transcript / altyazı alma
- Metin temizleme ve ön işleme
- Transcripti konu bloklarına ayırma
- Gemini API ile yapılandırılmış özet üretme
- Anahtar kelime çıkarımı
- YAKE fallback desteği
- Argo / uygunsuz ifade analizi
- Duygu ve ton analizi
- Hedef kitle tahmini
- Çıktı dili seçimi
- Çeviri desteği
- Kullanıcı bazlı geçmiş analiz kaydı
- Kayıtlı analizleri tekrar görüntüleme
- Metin raporu indirme
- PDF raporu indirme
- Streamlit tabanlı kullanıcı dostu arayüz

---

## Arayüzde Bulunan Alanlar

Uygulama arayüzünde kullanıcıya sunulan başlıca alanlar şunlardır:

- YouTube video linki giriş alanı
- Çıktı dili seçimi
- Özet uzunluğu seçimi
- Transcript kaynağı bilgisi
- Kullanıcı giriş / kayıt alanı
- Geçmiş analizler alanı
- Analizi Başlat butonu
- Gemini ile oluşturulan yapılandırılmış özet alanı
- Çevrilmiş özet alanı
- Argo analizi alanı
- Duygu analiz tablosu ve grafiği
- Anahtar kelimeler alanı
- Metin raporu indirme butonu
- PDF raporu indirme butonu

---

## Teknik Detaylar

Proje modüler bir yapıda hazırlanmıştır. Ana uygulama dosyası `app.py` dosyasıdır. Yardımcı işlevler ise `utils/` klasörü altında ayrı Python dosyaları halinde düzenlenmiştir.

Bu yapı sayesinde proje daha okunabilir, geliştirilebilir ve sürdürülebilir hale getirilmiştir.

### Temel Modüller

| Dosya | Görevi |
|---|---|
| `app.py` | Streamlit arayüzü ve ana uygulama akışı |
| `transcript.py` | YouTube transcript alma işlemleri |
| `preprocess.py` | Metin temizleme ve ön işleme |
| `summarizer.py` | Gemini API ile özetleme işlemleri |
| `keywords.py` | Anahtar kelime çıkarımı |
| `slang.py` | Argo / uygunsuz ifade analizi |
| `sentiment.py` | Duygu ve ton analizi |
| `audience.py` | Hedef kitle tahmini |
| `translator.py` | Çeviri işlemleri |
| `storage.py` | SQLite ile kullanıcı ve geçmiş kayıt yönetimi |
| `report.py` | Metin ve PDF raporlama işlemleri |
| `combined_analysis.py` | Birleşik analiz işlemleri |
| `summary_keywords_bundle.py` | Özet ve anahtar kelime işlemlerinin birlikte yürütülmesi |
| `sentiment_audience_bundle.py` | Duygu analizi ve hedef kitle analizinin birlikte yürütülmesi |

---

## Elde Edilen Sonuçlar

Proje sonunda YouTube videolarını analiz edebilen, özet çıkarabilen, anahtar kelime ve duygu / ton analizi yapabilen, hedef kitle tahmini sunabilen, kullanıcı bazlı geçmiş kayıt tutabilen ve rapor oluşturabilen çalışır bir NLP uygulaması geliştirilmiştir.

Uygulama, doğal dil işleme tekniklerinin gerçek bir problem üzerinde uygulanmasını sağlamıştır. Ayrıca kullanıcı dostu Streamlit arayüzü sayesinde teknik bilgiye sahip olmayan kullanıcıların da sistemi kolayca kullanabilmesi hedeflenmiştir.

Proje GitHub üzerinde public olarak paylaşılmış ve Streamlit Community Cloud üzerinden canlı uygulama haline getirilmiştir.

---

## Ekip İçi Görev Dağılımı

| Ekip Üyesi | Görev |
|---|---|
| Merve Naz Oran | Proje geliştirme, GitHub düzenleme, README hazırlama, rapor ve dokümantasyon |
| EKIP_UYESI_ADI | Backend / NLP modülleri geliştirme |
| EKIP_UYESI_ADI | Arayüz tasarımı, test ve proje tanıtım videosu |
| EKIP_UYESI_ADI | Raporlama, sunum ve proje kontrolü |

---

## Karşılaşılan Problemler ve Çözümler

Proje geliştirme sürecinde transcript alma, API kullanımı, metin ön işleme, PDF raporlama ve GitHub entegrasyonu gibi aşamalarda çeşitli problemlerle karşılaşılmıştır.

Karşılaşılan bazı problemler şunlardır:

- Bazı YouTube videolarında transcript verisinin alınamaması
- Bazı videolarda altyazı / transcript erişiminin kapalı olması
- Gemini API anahtarı olmadan özetleme işlemlerinin çalışmaması
- Gemini API yoğunluğuna bağlı olarak bazı analizlerin geçici olarak atlanabilmesi
- Uzun metinlerde özetleme işleminin bloklara ayrılma ihtiyacı
- Kullanıcı geçmişinin düzenli şekilde saklanması
- GitHub reposuna proje dosyalarının doğru şekilde yüklenmesi
- Canlı sistemin Streamlit Cloud üzerinde yapılandırılması

Bu problemler için fallback yöntemleri, modüler kod yapısı, SQLite tabanlı veri kaydı, Streamlit secrets kullanımı, `packages.txt` ile sistem bağımlılıklarının belirtilmesi ve düzenli dokümantasyon çözümleri uygulanmıştır.

---

## Gelecekte Yapılabilecek Geliştirmeler

Proje ilerleyen süreçte aşağıdaki özelliklerle geliştirilebilir:

- Canlı sistemin daha profesyonel bir sunucu üzerinde yayınlanması
- Daha gelişmiş kullanıcı paneli eklenmesi
- Daha kapsamlı grafik ve istatistik ekranları oluşturulması
- Farklı LLM modelleriyle karşılaştırmalı özetleme yapılması
- Çoklu video analizi desteği eklenmesi
- PDF rapor tasarımının geliştirilmesi
- Daha kapsamlı argo ve duygu analizi veri setleriyle sistemin güçlendirilmesi
- Mobil uyumlu arayüz tasarımının geliştirilmesi
- Analiz sonuçlarının bulut veritabanında saklanması

---

## Notlar

- Uygulamanın LLM tabanlı özetleme modülü Gemini API ile çalışmaktadır.
- API anahtarı güvenlik nedeniyle GitHub reposuna eklenmemelidir.
- Uygulama Streamlit Community Cloud üzerinde yayınlanmıştır.
- YouTube transcript verisi bulunmayan, erişimi kısıtlı veya altyazısı kapalı videolarda analiz işlemi başlatılamayabilir.
- Gemini API yoğunluğu veya kota durumuna bağlı olarak bazı LLM tabanlı analizlerde geçici gecikme yaşanabilir. Bu durumda uygulama transcript üzerinden mümkün olan analizleri üretmeye devam eder.
- Kullanıcı ve analiz verileri yerel SQLite veritabanında saklanır.
- Proje eğitim amacıyla geliştirilmiştir.

---

## Kaynakça

- Python Documentation: https://docs.python.org/
- Streamlit Documentation: https://docs.streamlit.io/
- GitHub Docs: https://docs.github.com/
- Google Gemini API Documentation: https://ai.google.dev/
- yt-dlp Documentation: https://github.com/yt-dlp/yt-dlp
- faster-whisper Documentation: https://github.com/SYSTRAN/faster-whisper
- youtube-transcript-api Documentation: https://github.com/jdepoix/youtube-transcript-api
- ReportLab Documentation: https://docs.reportlab.com/
- SQLite Documentation: https://www.sqlite.org/docs.html
