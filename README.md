# YouTube Video Özetleme ve NLP Analiz Uygulaması

## Proje Açıklaması

Bu proje, Doğal Dil İşleme dersi kapsamında geliştirilen bir YouTube video özetleme ve NLP analiz uygulamasıdır. Uygulama, YouTube videosuna ait transcript verisini alır, metni temizler, konu bloklarına ayırır ve ardından Gemini API desteğiyle yapılandırılmış özet üretir.

Proje yalnızca video özetleme işlemi yapmakla sınırlı değildir. Aynı zamanda anahtar kelime çıkarımı, argo / uygunsuz ifade analizi, duygu ve ton analizi, çeviri, kullanıcı bazlı geçmiş kayıt sistemi ve PDF raporlama gibi özellikler de sunar.

Uygulamanın ana dili Türkçedir. Varsayılan çıktı dili Türkçe olarak belirlenmiştir. Kullanıcı isterse analiz sonuçlarını farklı dillere çevirebilir.

---

## Projenin Amacı

Günümüzde YouTube üzerinde eğitim, teknoloji, haber, kişisel gelişim ve sosyal medya alanlarında çok sayıda uzun video içeriği bulunmaktadır. Kullanıcıların bu videoların tamamını izlemesi zaman açısından zorlayıcı olabilmektedir.

Bu projenin temel amacı, uzun YouTube videolarını kullanıcılar için daha kısa, anlaşılır ve analiz edilebilir hale getirmektir. Kullanıcı, videonun tamamını izlemek zorunda kalmadan içeriğin özetine, anahtar kelimelerine, duygu / ton analizine ve genel değerlendirmesine ulaşabilir.

---

## Projenin Hedefleri

Bu proje kapsamında hedeflenen temel amaçlar şunlardır:

- YouTube videolarından transcript / altyazı verisi elde etmek
- Alınan metni doğal dil işleme için temizlemek ve düzenlemek
- Uzun video içeriklerinden anlamlı ve yapılandırılmış özet üretmek
- Anahtar kelime çıkarımı yapmak
- Metin içerisindeki argo veya uygunsuz ifadeleri tespit etmek
- Video içeriğinin duygu ve ton analizini yapmak
- Kullanıcıya farklı dil seçenekleriyle çıktı sunmak
- Kullanıcı kayıt / giriş sistemiyle analiz geçmişini saklamak
- Analiz sonuçlarını metin ve PDF raporu olarak indirebilir hale getirmek
- Streamlit arayüzü ile kullanıcı dostu bir web uygulaması geliştirmek

---

## Projenin Özgün Yönleri

Bu proje, yalnızca basit bir video özetleme uygulaması değildir. YouTube videolarını çok yönlü olarak analiz eden bütünleşik bir NLP sistemi olarak tasarlanmıştır.

Projenin öne çıkan özgün yönleri:

- Transcript alma işleminde birden fazla yöntem kullanılması
- Whisper başarısız olduğunda YouTube transcript fallback mekanizmasının devreye girmesi
- Metnin konu bloklarına ayrılarak daha kontrollü özetlenmesi
- Gemini API ile yapılandırılmış ve daha anlamlı özet üretilmesi
- Gemini başarısız olduğunda bazı analizlerde fallback yöntemlerinin kullanılması
- Anahtar kelime, duygu / ton ve argo analizinin aynı sistemde sunulması
- Kullanıcı bazlı analiz geçmişi tutulması
- Analiz sonuçlarının PDF raporu olarak indirilebilmesi
- Türkçe odaklı kullanıcı deneyimi sunulması

---

## Kullanılan Teknolojiler

Projede kullanılan temel teknolojiler şunlardır:

| Teknoloji / Kütüphane | Kullanım Amacı |
|---|---|
| Python | Ana programlama dili |
| Streamlit | Web arayüzü geliştirme |
| Gemini API | Özetleme, duygu / ton analizi ve bazı NLP işlemleri |
| faster-whisper | Video sesinden transcript çıkarma |
| yt-dlp | YouTube video verilerine erişme |
| youtube-transcript-api | Transcript alma işlemi için fallback yöntem |
| regex | Metin temizleme ve ön işleme |
| YAKE | Anahtar kelime çıkarımı için fallback yöntem |
| deep-translator | Çeviri işlemleri |
| SQLite | Kullanıcı ve analiz geçmişi saklama |
| reportlab | PDF raporu oluşturma |
| Git / GitHub | Versiyon kontrolü ve proje paylaşımı |

---

## Kullanılan Yöntemler

### 1. Transcript Alma

Uygulama, YouTube videosuna ait metin verisini elde etmek için öncelikle `faster-whisper` ve `yt-dlp` yöntemlerini kullanır. Eğer bu yöntem başarısız olursa `youtube-transcript-api` fallback yöntemi devreye girer.

Bu yapı sayesinde uygulama farklı video türlerinde daha esnek çalışabilir.

### 2. Metin Ön İşleme

Transcript verisi doğrudan analiz için uygun olmayabilir. Bu nedenle metin üzerinde ön işleme uygulanır.

Ön işleme adımları:

- Gereksiz boşlukların temizlenmesi
- Segmentlerin düzenlenmesi
- Metnin daha okunabilir hale getirilmesi
- Konu bloklarının oluşturulması
- Analiz için daha uygun metin yapısının hazırlanması

### 3. Özetleme

Özetleme işlemi Gemini API ile yapılmaktadır. Metin önce konu bloklarına ayrılır. Ardından her blok için ara özetler oluşturulur. Son aşamada bu ara özetler birleştirilerek final yapılandırılmış özet üretilir.

Bu yöntem, uzun video metinlerinin daha düzenli ve anlamlı şekilde özetlenmesini sağlar.

### 4. Anahtar Kelime Çıkarımı

Anahtar kelime çıkarımı için öncelikli olarak Gemini API kullanılır. Gemini API’den sonuç alınamadığı durumlarda YAKE fallback yöntemi devreye girer.

Bu sayede video içeriğinde öne çıkan kavramlar kullanıcıya sunulur.

### 5. Argo / Uygunsuz İfade Analizi

Argo analizi sözlük tabanlı bir yaklaşımla yapılmaktadır. Metin içinde belirli argo veya uygunsuz ifadeler tespit edilerek kullanıcıya raporlanır.

### 6. Duygu ve Ton Analizi

Duygu ve ton analizi Gemini API ile yapılmaktadır. Bu analiz sayesinde video içeriğinin genel tonu, anlatım yapısı ve duygusal yönü hakkında bilgi verilir.

### 7. Çeviri

Kullanıcı isterse analiz sonuçlarını farklı dillere çevirebilir. Çeviri işlemleri için `deep-translator` kullanılmaktadır.

### 8. Kullanıcı Yönetimi ve Geçmiş Kayıt

Uygulamada kullanıcı kayıt ve giriş sistemi bulunmaktadır. Kullanıcıların yaptığı analizler SQLite veritabanında saklanır. Böylece kullanıcı daha önce yaptığı analizleri tekrar görüntüleyebilir.

### 9. Raporlama

Analiz sonuçları metin ve PDF olarak indirilebilir. PDF çıktıları `reportlab` kütüphanesi ile oluşturulmaktadır.

---

## Klasör Yapısı

```text
proje-dogaldilisleme/
├── app.py
├── README.md
├── requirements.txt
├── youtube_uygulamasi.command
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

