---
name: udemy-video-pipeline
description: >
  Udemy/eğitim videosu üretim pipeline'i. NotebookLM araştırma → Türkçe ders scripti → ElevenLabs
  seslendirme → video montaj. Udemy, ders videosu, kurs videosu, eğitim videosu, ders/kurs oluştur
  dediğinizde çağrılır. Bölüm-bazlı organizasyon ve altyazı desteği.
version: "1.1.0"
category: education
tags: [udemy, kurs, video, egitim, pipeline, notebooklm]
model: sonnet
tools: "Read, Write, Edit, Bash, Task"
---

# Udemy Video Pipeline

NotebookLM ile arastirma yapip, Turkce ders scripti uretip, ElevenLabs ile seslendiren tam otomasyon pipeline'i.

## Pipeline Asamalari

```
1. Konu Arastirma (NotebookLM)
   - YouTube'dan kaynak videolar bulunur
   - NotebookLM'e kaynak olarak yuklenir
   - Detayli Turkce analiz uretilir

2. Script Uretimi (Claude)
   - NotebookLM analizinden ders scripti yazilir
   - Slayt icerikleri cikarilir
   - Zamanlama ve bolum planlanir

3. Seslendirme (ElevenLabs)
   - Script bolum bolum seslendirilir
   - Kullanicinin "Kesif -TR" sesi kullanilir
   - MP3 dosyalari uretilir

4. Video Birleştirme (opsiyonel)
   - Ses + slayt birlestirilir
   - SRT altyazi eklenir
```

## Kullanim

### Tam Pipeline

```bash
python ~/.claude/skills/udemy-video-pipeline/scripts/create_course.py \
  "Bagimlilik Norobiyolojisi" \
  --sections 5 \
  --voice "Kesif -TR" \
  --output-dir <workspace>/udemy-courses/bagimlilik
```

### Sadece Script Uret

```bash
python ~/.claude/skills/udemy-video-pipeline/scripts/generate_script.py \
  --topic "Bagimlilik Norobiyolojisi" \
  --analysis <workspace>/notebooklm/output/bagimlilik-analysis.md \
  --sections 5 \
  --output <workspace>/udemy-courses/bagimlilik/script.json
```

### Script'ten Seslendirme

```bash
python ~/.claude/skills/udemy-video-pipeline/scripts/narrate_script.py \
  --script <workspace>/udemy-courses/bagimlilik/script.json \
  --voice "Kesif -TR" \
  --output-dir <workspace>/udemy-courses/bagimlilik/audio
```

## Script Formati (JSON)

```json
{
  "title": "Bagimlilik Norobiyolojisi",
  "language": "tr",
  "sections": [
    {
      "id": 1,
      "title": "Giris: Bagimlilik Nedir?",
      "duration_estimate": "5 min",
      "narration": "Merhaba, bu derste bagimlilik norobiyolojisini...",
      "slides": [
        { "type": "title", "content": "Bagimlilik Norobiyolojisi" },
        { "type": "bullet", "content": ["Tanimlama", "Beyin mekanizmalari"] }
      ],
      "notes": "Ogrencilere kendi deneyimlerini dusunmelerini soyle"
    }
  ]
}
```

## Ses Ayarlari (Udemy Optimum)

- **Model**: eleven_multilingual_v2
- **Stability**: 0.65 (dogal ama tutarli)
- **Similarity**: 0.80 (sese sadik)
- **Style**: 0.15 (hafif vurgulu, monoton degil)
- **Format**: mp3_44100_128 (Udemy uyumlu)

## Dizin Yapisi

```
output-dir/
  script.json          # Tam ders scripti
  audio/
    section_01.mp3     # Bolum seslendirmeleri
    section_02.mp3
    ...
  slides/
    section_01.md      # Slayt icerikleri
    section_02.md
  subtitles/
    section_01.srt     # Altyazilar
  metadata.json        # Kurs bilgileri
```
