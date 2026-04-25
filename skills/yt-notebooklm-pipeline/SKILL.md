---
name: yt-notebooklm-pipeline
description: YouTube video arama + NotebookLM analiz pipeline. Tek prompt ile YouTube scrape, NotebookLM'e kaynak yukleme, analiz ve icerik uretimi.
triggers:
  [
    "yt-notebooklm",
    "youtube notebooklm",
    "youtube analiz",
    "video analiz pipeline",
    "arastirma pipeline",
  ]
---

# YouTube + NotebookLM Pipeline

Tek prompt ile calisan tam otomasyon pipeline:

1. YouTube'da arama yap (yt-dlp)
2. Video URL'lerini NotebookLM'e kaynak olarak yukle
3. NotebookLM'de analiz yap
4. Infografik, podcast, mind map vb. uret

## Kullanim

```
/yt-notebooklm-pipeline <konu> [cikti_turu]
```

## Standart Islem Proseduru

### Faz 1: YouTube Arama

```bash
python ~/.claude/skills/yt-search/scripts/search.py "<konu>" --max-results 20 --period 6m
```

### Faz 2: NotebookLM Notebook Olustur

```bash
notebooklm create "<konu> Research"
notebooklm use <notebook_id>
```

### Faz 3: Kaynaklari Yukle

Video URL'lerini `.output/yt-urls.txt` dosyasindan oku ve NotebookLM'e ekle:

```bash
python ~/.claude/skills/yt-notebooklm-pipeline/scripts/load_sources.py .output/yt-urls.txt
```

Veya tek tek:

```bash
notebooklm source add "https://youtube.com/watch?v=VIDEO_ID_1"
notebooklm source add "https://youtube.com/watch?v=VIDEO_ID_2"
# ... (50'ye kadar kaynak)
```

### Faz 4: Analiz

```bash
notebooklm ask "Based on all the sources, what are the key themes and insights?"
notebooklm ask "What are the most recommended strategies/tools mentioned across videos?"
```

### Faz 5: Icerik Uretimi

Kullanicinin istegine gore:

```bash
# Infografik (blueprint/handwritten tarz)
notebooklm generate infographic --orientation portrait --detail detailed --wait
notebooklm download infographic ./.output/infographic.png

# Podcast
notebooklm generate audio "engaging analysis" --format deep-dive --wait
notebooklm download audio ./.output/podcast.mp3

# Mind Map
notebooklm generate mind-map --wait
notebooklm download mind-map ./.output/mindmap.json

# Slayt Sunumu
notebooklm generate slide-deck --format detailed --length 12 --wait
notebooklm download slide-deck ./.output/slides.pptx --format pptx

# Flashcard
notebooklm generate flashcards --quantity more --wait
notebooklm download flashcards ./.output/flashcards.md --format markdown

# Quiz
notebooklm generate quiz --difficulty hard --wait
notebooklm download quiz ./.output/quiz.md --format markdown
```

## Tam Otomasyon Script

Tum pipeline'i tek seferde calistirmak icin:

```bash
python ~/.claude/skills/yt-notebooklm-pipeline/scripts/pipeline.py "<konu>" --output-type infographic
```

## Cikti Turleri

- `infographic` - Blueprint/handwritten tarz infografik
- `audio` - Deep-dive podcast
- `video` - Whiteboard video
- `mind-map` - Zihin haritasi
- `slide-deck` - Slayt sunumu
- `flashcards` - Bilgi kartlari
- `quiz` - Sinav
- `report` - Calisma rehberi
- `all` - Hepsini uret

## Onemli Notlar

- NotebookLM'de analiz Google sunucularinda yapiir, Claude Code neredeyse sifir token harcar
- 50'ye kadar kaynak yuklenebilir
- Ilk kullanimda `notebooklm login` gereklidir
