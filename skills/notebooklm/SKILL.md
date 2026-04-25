---
name: notebooklm
description: "Google NotebookLM ile araştırma ve içerik üretim entegrasyonu. Notebook oluşturma, YouTube/web/PDF kaynak ekleme, soru-cevap analizi, podcast/infografik/mind-map/flashcard/quiz üretimi için kullan. Kullanıcı notebooklm, podcast oluştur, infografik, mind map, flashcard, araştırma analizi gibi ifadeler kullandığında tetikle."
version: "1.1.0"
category: "research"
tags: [notebooklm, google, ai-analiz]
model: "sonnet"
tools: "Bash, Read, Write"
mcp_tools: ""
triggers:
  [
    "notebooklm",
    "notebook lm",
    "notebooklm olustur",
    "podcast olustur",
    "infografik olustur",
    "mind map",
    "flashcard",
  ]
---

# NotebookLM Skill

Google NotebookLM ile tam entegrasyon. Notebook olusturma, kaynak ekleme, analiz yapma ve icerik uretimi.

## Yetenekler

- **Notebook Yönetimi**: Oluşturma, listeleme, silme, aktif notebook seçimi
- **Kaynak Ekleme**: YouTube video, web sayfası, yerel PDF/dosya, web araştırma otomatik import
- **Soru-Cevap**: Tek soru veya interaktif sohbet modu
- **İçerik Üretimi**: Ses (podcast), video, infografik, mind-map, flashcard, quiz, slayt, rapor, veri tablosu
- **İndirme**: Üretilen tüm içerikleri yerel dosyaya kaydetme

## Ne Zaman Kullan

- Araştırma konusu için kaynak toplama ve analiz yapılacağında
- YouTube videolarından veya web sayfalarından bilgi çıkarılacağında
- Podcast, infografik, mind-map gibi içerik üretimi istendiğinde
- Flashcard veya quiz ile öğrenme materyali hazırlanacağında
- Birden fazla kaynağı sentezleyip rapor yazılacağında

## İş Akışı

1. **Notebook Oluştur**: Konu bazlı notebook oluştur
2. **Kaynak Ekle**: YouTube videolari, web sayfalari veya dosyalari kaynak olarak ekle
3. **Analiz Yap**: NotebookLM soru sorarak analiz yaptir
4. **Icerik Uret**: Infografik, podcast, mind map vb. uret
5. **Indir**: Uretilen icerikleri yerel dosyalara indir

## Onkosul

```bash
# Ilk kullanim icin login gerekli
notebooklm login
```

## CLI Komutlari

### Notebook Yonetimi

```bash
notebooklm create "Notebook Adi"       # Yeni notebook olustur
notebooklm list                         # Tum notebooklari listele
notebooklm use <notebook_id>            # Aktif notebook sec
notebooklm delete <notebook_id>         # Notebook sil
```

### Kaynak Ekleme

```bash
notebooklm source add "https://youtube.com/watch?v=..."   # YouTube videosu
notebooklm source add "https://example.com"                # Web sayfasi
notebooklm source add "./dosya.pdf"                        # Yerel dosya
notebooklm source add-research "arama terimi"              # Web arastirma + otomatik import
notebooklm source list                                     # Kaynaklari listele
```

### Soru-Cevap

```bash
notebooklm ask "Sorunuz"               # Tek soru sor
notebooklm chat                         # Interaktif sohbet
```

### Icerik Uretimi

```bash
# Ses (Podcast)
notebooklm generate audio "talimatlar" --format deep-dive --language tr --wait

# Video
notebooklm generate video "talimatlar" --style whiteboard --wait

# Infografik
notebooklm generate infographic --orientation portrait --detail detailed --wait

# Mind Map
notebooklm generate mind-map --wait

# Flashcard
notebooklm generate flashcards --quantity more --difficulty medium --wait

# Quiz
notebooklm generate quiz --quantity more --difficulty hard --wait

# Slayt Sunumu
notebooklm generate slide-deck --format detailed --length 12 --wait

# Rapor
notebooklm generate report --template study-guide --wait

# Veri Tablosu
notebooklm generate data-table "aciklama" --wait
```

### Indirme

```bash
notebooklm download audio ./podcast.mp3
notebooklm download video ./video.mp4
notebooklm download infographic ./infografik.png
notebooklm download mind-map ./zihinharitasi.json
notebooklm download flashcards ./kartlar.md --format markdown
notebooklm download quiz ./sinav.md --format markdown
notebooklm download slide-deck ./slaytlar.pptx --format pptx
notebooklm download report ./rapor.md
notebooklm download data-table ./veri.csv
```

## Python API Kullanimi

```python
import asyncio
from notebooklm import NotebookLMClient

async def main():
    async with await NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create("Arastirma")
        await client.sources.add_url(nb.id, "https://youtube.com/watch?v=xxx", wait=True)
        result = await client.chat.ask(nb.id, "Anahtar temalar nelerdir?")
        print(result.answer)
        status = await client.artifacts.generate_infographic(nb.id, orientation="portrait", detail="detailed")
        await client.artifacts.wait_for_completion(nb.id, status.task_id)
        await client.artifacts.download_infographic(nb.id, "infografik.png")

asyncio.run(main())
```

## Kurallar ve Kısıtlamalar

- Her işlemden önce notebooklm login ile oturum açık olduğundan emin ol
- Büyük dosyalar için --wait parametresini kullan; üretim zaman alabilir
- Aynı anda birden fazla üretim işlemi başlatma — sıralı çalıştır

## En İyi Uygulamalar

- Konu odaklı notebooklar oluştur; hepsini tek notebooka koyma
- YouTube videoları en iyi kaynak kalitesini sunar; öncelik ver
- Mind-map ve flashcardı birlikte üret — öğrenme materyali tamamlanır
- Rapor üretmeden önce en az 3-5 kaynak ekle
