# YouTube Video Ozetleme ve NLP Analiz Uygulamasi

## Proje Hakkinda

Bu proje, YouTube videolarinin transcript metinlerini dogal dil isleme
yontemleriyle analiz eden Streamlit tabanli bir web uygulamasidir. Sistem;
transcript metnini temizler, konu bloklarina ayirir ve Gemini API kullanarak
yapilandirilmis bir ozet olusturur. Ayrica anahtar kelime, argo, duygu, ton ve
hedef kitle analizleri sunar.

Uygulama konusma dilinden gelen daginik transcript verileriyle calisabilecek
sekilde tasarlanmistir.

## Baglantilar

Asagidaki alanlari projeyi GitHub'a pushladiktan ve Streamlit Community Cloud
uzerinde deploy ettikten sonra guncelleyin:

| Baglanti | Adres |
| --- | --- |
| Canli uygulama | `https://proje-dogaldilisleme-9vmezzcl4ryrqtc76krjx7.streamlit.app/` |
| Proje tanitim videosu | `https://drive.google.com/file/d/1l1p9DkiURk-Kj4oHPqQZmq89lMIdBXhG/view?usp=sharing` |

> Not: Paylasilan baglantilarin herkese acik oldugunu gizli sekmede kontrol edin.

## Temel Ozellikler

- YouTube videosundan otomatik transcript alma
- Dosya hazirlamadan sistemi deneyebilmek icin hazir ornek transcript
- Regex tabanli metin temizleme ve segment normalizasyonu
- Gemini API ile blok bazli ara ozet ve final yapilandirilmis ozet
- Ozetin secilen hedef dile cevrilmesi
- Gemini ve YAKE tabanli anahtar kelime cikarimi
- Sozluk tabanli argo analizi
- Duygu, ton ve hedef kitle analizi
- Duygu skorlarini tablo, renkli kartlar ve cizgi grafik ile gosterme
- Kullanici kaydi, giris yapma ve analiz gecmisini goruntuleme
- Sonuclari PDF raporu olarak indirme
- PDF dosyalarinda Turkce karakter destegi

## Uygulama Akisi

1. Kullanici hesap olusturur veya mevcut hesabiyla giris yapar.
2. Cikti dilini ve ozet uzunlugunu secer.
3. Transcript kaynagini belirler:
   - `YouTube'dan Otomatik Al`
   - `Hazir Ornek Kullan`
4. `Analizi Baslat` dugmesine basar.
5. Sistem metni temizler, konu bloklari olusturur ve analizleri calistirir.
6. Ozet, ceviri, anahtar kelimeler, argo analizi, duygu analizi ve hedef kitle
   tahmini ekranda gosterilir.
7. Kullanici isterse PDF raporunu indirebilir.

## Transcript Kaynaklari

### YouTube'dan Otomatik Al

Kullanici bir YouTube video baglantisi girer. Uygulama
`youtube-transcript-api` ile videonun transcript metnini almaya calisir.

Ornek:

```text
Bugun dogal dil isleme yontemlerini inceleyecegiz.
Transcript verileri analizden once temizlenmelidir.
Buyuk dil modelleri daginik metinleri ozetlemek icin kullanilabilir.
```

## Kullanilan Teknolojiler

| Alan | Teknoloji |
| --- | --- |
| Arayuz | Streamlit |
| Ozetleme ve analiz | Gemini API |
| Transcript alma | youtube-transcript-api |
| Anahtar kelime cikarimi | YAKE ve Gemini |
| Ceviri | deep-translator |
| Veri isleme | pandas |
| Kullanici ve analiz kayitlari | SQLite |
| PDF raporlama | ReportLab |

## Klasor Yapisi

```text
youtube_video_summarizer/
|-- app.py
|-- README.md
|-- requirements.txt
|-- examples/
|   `-- ornek_transcript.txt
`-- utils/
    |-- __init__.py
    |-- audience.py
    |-- keywords.py
    |-- preprocess.py
    |-- report.py
    |-- sentiment.py
    |-- slang.py
    |-- storage.py
    |-- summarizer.py
    |-- transcript.py
    `-- translator.py
```

`app_data.db` uygulama ilk kez calistirildiginda otomatik olarak olusturulur.
Bu dosya kullanici ve analiz kayitlarini tuttugu icin GitHub reposuna
eklenmemelidir.

## Yerel Kurulum

### Gereksinimler

- Python 3.11 veya daha yeni bir surum
- Gemini API anahtari

### Adimlar

```bash
git clone REPO_BAGLANTISI
cd REPO_KLASORU
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="API_ANAHTARINIZ"
streamlit run app.py
```

Windows PowerShell kullaniyorsaniz sanal ortami su komutla etkinlestirin:

```powershell
.venv\Scripts\Activate.ps1
```

Uygulama varsayilan olarak `http://localhost:8501` adresinde acilir.

## Streamlit Community Cloud Kurulumu

1. Projeyi public bir GitHub reposuna pushlayin.
2. Streamlit Community Cloud uzerinden yeni bir uygulama olusturun.
3. Ana dosya olarak `app.py` secin.
4. Uygulamanin `Settings > Secrets` bolumune Gemini API anahtarini ekleyin:

```toml
GEMINI_API_KEY = "API_ANAHTARINIZ"
```

API anahtarini GitHub reposuna, README dosyasina veya kaynak kodlara yazmayin.

## Bilinen Kisitlar ve Yedek Akis

YouTube, bazi bulut sunucularinin IP adreslerinden gelen transcript isteklerini
sinirlandirabilir. Bu nedenle yerel ortamda calisan otomatik transcript islemi
Streamlit Community Cloud uzerinde bazi videolarda basarisiz olabilir.

Bu yedek akislarda ozetleme, ceviri, anahtar kelime, argo, duygu ve hedef kitle
analizleri ayni sekilde calismaya devam eder.

## Gelistirme Notlari

Projenin gelistirme surecinde transcript kalitesi, dis servis kotalari, bulut
IP kisitlari, API istemci hatalari ve arayuz sadeligi temel teknik konular
olmustur. Sistem bu sorunlara karsi on isleme, hata yonetimi, farkli transcript
kaynaklari, kismi sonuc gosterimi ve moduler yardimci dosyalar kullanilarak
gelistirilmistir.

