---
name: video-montaj
description: FFmpeg ile video montaj, format donusturme, altyazi yakma
triggers:
  - video montaj
  - video birleştir
  - mp4 olustur
  - reels olustur
  - ffmpeg
  - video format
  - altyazi yak
---

# Video Montaj Skill

FFmpeg tabanli video montaj, format donusturme ve altyazi yakma islemleri icin kullanilir.

## Gereksinimler

- Python 3.8+
- FFmpeg sistemde yuklu ve PATH'te erisilebildiyor olmali

## Scriptler

### 1. montaj.py -- Ana Video Montaj Motoru

Ses dosyasi ve gorsel(ler)den MP4 video uretir.

**Kullanim:**

```bash
# Tek gorsel + ses -> MP4
python montaj.py image --audio ses.mp3 --image foto.jpg --output video.mp4 --resolution 1080x1920

# Coklu gorsel + ses -> Slideshow MP4 (fade gecisler)
python montaj.py slideshow --audio ses.mp3 --images-dir slides/ --output video.mp4 --slide-duration 5

# 9:16 Reels formati
python montaj.py reels --audio ses.mp3 --images foto1.jpg foto2.jpg --output reels.mp4
```

**Ozellikler:**

- libx264 + AAC kodlama
- Slideshow modunda fade gecisler (crossfade)
- Reels modu: 1080x1920, 9:16 dikey format
- Otomatik cozunurluk ayarlama

### 2. format_convert.py -- Instagram Format Donusturme

Mevcut videoyu farkli sosyal medya formatlarina donusturur.

**Kullanim:**

```bash
# 9:16 Reels (1080x1920, max 90sn)
python format_convert.py reels --input video.mp4 --output reels.mp4

# 1:1 Kare (1080x1080)
python format_convert.py square --input video.mp4 --output square.mp4 --mode crop

# 4:5 Portre (1080x1350)
python format_convert.py portrait --input video.mp4 --output portrait.mp4 --mode pad
```

**Modlar:**

- `pad`: Siyah kenarlik ekleyerek boyutlandirir (icerik kaybi yok)
- `crop`: Ortadan keserek boyutlandirir (tam dolum)

### 3. add_subtitles.py -- SRT Altyazi Yakma

SRT formatindaki altyazilari videoya hard-sub olarak yakar.

**Kullanim:**

```bash
# Varsayilan ayarlarla altyazi yak
python add_subtitles.py --video video.mp4 --srt altyazi.srt --output final.mp4

# Ozel stil ile
python add_subtitles.py --video video.mp4 --srt altyazi.srt --output final.mp4 \
  --font-size 48 --font-color yellow --position center
```

**Ozellikler:**

- Turkce karakter destegi (UTF-8)
- Ayarlanabilir font boyutu, renk ve konum
- Yari saydam arka plan

## Tipik Is Akisi

1. `montaj.py` ile ses + gorsellerden ham video olustur
2. `format_convert.py` ile hedef platforma uygun formata donustur
3. `add_subtitles.py` ile gerekirse altyazi yak

## Notlar

- Tum scriptler `--help` ile kullanim bilgisi verir
- FFmpeg bulunamazsa anlasilir hata mesaji gosterir
- Cikti dosyasi zaten varsa uzerine yazar
