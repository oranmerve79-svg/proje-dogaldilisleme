# YouTube Video Özetleme Uygulaması

## Proje Açıklaması
Bu proje, YouTube videosunun transcript verisini alıp temizleyen, transcripti konu bloklarına ayıran, ardından `Gemini API` ile yapılandırılmış özet üreten, anahtar kelime çıkaran, argo tespiti ve duygu/ton analizi yapan, sonuçları raporlayıp kullanıcı bazlı geçmişte saklayabilen bir NLP uygulamasıdır.

Uygulamanın ana dili Türkçedir. Varsayılan çıktı dili Türkçedir. Kullanıcı isterse farklı dillere de çeviri alabilir.

## Kullanılan Yöntemler
- Transcript alma: `faster-whisper` + `yt-dlp`, fallback olarak `youtube-transcript-api`
- Ön işleme: regex tabanlı metin temizleme, segment normalizasyonu ve konu blokları oluşturma
- Özetleme: `Gemini API` ile blok bazlı ara özet + final yapılandırılmış özet
- Anahtar kelime çıkarımı: `Gemini + YAKE fallback`
- Argo analizi: sözlük tabanlı tespit
- Duygu ve ton analizi: `Gemini API`
- Çeviri: `deep-translator`
- Kullanıcı yönetimi ve geçmiş kayıt: `SQLite`
- Raporlama ve PDF çıktısı: `reportlab`
- Arayüz: `Streamlit`

## Klasör Yapısı
```text
youtube_video_summarizer/
├── app.py
├── README.md
├── app_data.db
├── requirements.txt
└── utils/
    ├── __init__.py
    ├── keywords.py
    ├── preprocess.py
    ├── report.py
    ├── sentiment.py
    ├── slang.py
    ├── storage.py
    ├── summarizer.py
    ├── transcript.py
    └── translator.py
```

## Kurulum Adımları
```bash
cd /Users/mervenazoran/Documents/Playground/youtube_video_summarizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Gemini API Anahtarı
Uygulamanın özetleme modülü için `GEMINI_API_KEY` ortam değişkeni gereklidir.

```bash
export GEMINI_API_KEY="buraya_gemini_api_key"
```

## Çalıştırma Komutu
```bash
streamlit run app.py
```

## Ürün Özellikleri
- Kullanıcı kayıt / giriş sistemi
- Geçmiş analizlerin kullanıcı bazlı kaydedilmesi
- Kayıtlı analizlerin tekrar görüntülenmesi
- Metin raporu indirme
- PDF raporu indirme

## Arayüzde Bulunan Alanlar
- YouTube video linki giriş alanı
- Çıktı dili seçimi
- Özet uzunluğu seçimi
- Transcript kaynağı seçimi
- Kullanıcı giriş / kayıt alanı
- Geçmiş analizler alanı
- `Analizi Başlat` butonu
- Gemini ile oluşturulan yapılandırılmış özet
- Çevrilmiş özet
- Argo analizi
- Duygu analiz tablosu ve grafiği
- Anahtar kelimeler
- Metin/PDF rapor indirme butonları

## Not
Bu sürümde LLM tabanlı özetleme Gemini ile yapılır. Whisper kullanabilmek için sistemde `ffmpeg` bulunması önerilir. Whisper başarısız olursa uygulama otomatik olarak YouTube transcript fallback yoluna geçer. Kullanıcı ve analiz verileri yerel `SQLite` veritabanında saklanır.
