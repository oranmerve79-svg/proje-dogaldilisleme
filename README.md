# YouTube Video Özetleme ve NLP Analiz Uygulaması

## Proje Hakkında

Bu proje, Doğal Dil İşleme dersi kapsamında geliştirilmiş bir YouTube video özetleme ve analiz uygulamasıdır. Projenin amacı, YouTube videolarından alınan metinleri işleyerek kullanıcıya daha kısa, anlaşılır ve analiz edilebilir sonuçlar sunmaktır.

## Kullanılan Teknolojiler

Projede kullanılan temel teknolojiler şunlardır:

- Python
- Streamlit
- Doğal Dil İşleme teknikleri
- YouTube transcript / altyazı verisi işleme
- Metin temizleme ve ön işleme
- Metin özetleme
- Anahtar kelime çıkarımı
- Duygu / ton analizi
- Çeviri işlemleri
- PDF raporlama
- Git ve GitHub

## Projenin Özellikleri

Bu proje yalnızca video özeti çıkaran basit bir uygulama değildir. YouTube videoları üzerinde birden fazla doğal dil işleme analizi yaparak kullanıcıya daha kapsamlı bir içerik değerlendirmesi sunar.

### Temel Özellikler

- YouTube video bağlantısı üzerinden içerik analizi yapma
- Videoya ait transcript / altyazı metnini alma
- Alınan metni doğal dil işleme için temizleme ve düzenleme
- Uzun video metinlerinden kısa ve anlaşılır özet çıkarma
- Video içeriğindeki önemli anahtar kelimeleri belirleme
- Metin içinde argo veya uygunsuz ifadeleri analiz etme
- Video içeriğinin duygu ve ton analizini yapma
- İçeriğin hedef kitlesi hakkında tahmin üretme
- Analiz sonucunu kullanıcıya sade ve anlaşılır şekilde sunma
- Sonuçları farklı dillere çevirebilme
- Yapılan analizleri geçmiş kayıt olarak saklama
- Kullanıcının analiz sonucunu PDF raporu olarak indirebilmesi
- Streamlit tabanlı kullanıcı dostu web arayüzü sunma

### Kullanıcıya Sağladığı Avantajlar

- Uzun videoları tamamen izlemek zorunda kalmadan içerik hakkında fikir edinme
- Eğitim, haber, teknoloji veya sosyal medya videolarını daha hızlı değerlendirme
- Video içeriğinin yalnızca özetini değil, dil yapısını ve tonunu da analiz etme
- İçerik üreticileri için video metninin kalitesini ve hedef kitlesini inceleme
- Akademik olarak doğal dil işleme tekniklerinin gerçek bir uygulama üzerinde gösterilmesi


## Çalışma Mantığı

Uygulama genel olarak aşağıdaki adımlarla çalışır:

1. Kullanıcı Streamlit arayüzü üzerinden YouTube video bağlantısını girer.
2. Sistem, videoya ait transcript / altyazı metnini almaya çalışır.
3. Alınan metin temizlenir ve analiz için uygun hale getirilir.
4. Doğal dil işleme adımları çalıştırılır:
   - Özet çıkarma
   - Anahtar kelime çıkarımı
   - Argo / uygunsuz ifade analizi
   - Duygu ve ton analizi
   - Hedef kitle tahmini
5. Analiz sonuçları kullanıcıya arayüz üzerinde gösterilir.
6. Kullanıcı isterse sonuçları farklı bir dile çevirebilir.
7. Analiz geçmişi sistemde kayıt altında tutulur.
8. Kullanıcı sonuçları PDF raporu olarak indirebilir.

## Kurulum ve Çalıştırma

Projeyi çalıştırmak için:

```bash
chmod +x youtube_video_summarizer_python.command
./youtube_video_summarizer_python.command
