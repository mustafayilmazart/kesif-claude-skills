---
name: elevenlabs
description: ElevenLabs TTS entegrasyonu - metin okuma, ses klonlama, Turkce seslendirme
triggers:
  - elevenlabs
  - ses olustur
  - seslendirme yap
  - tts
  - text to speech
  - seslendir
  - voice clone
  - ses klonla
---

# ElevenLabs TTS Skill

ElevenLabs API ile metin-ses donusumu (TTS) yapan skill.

## Ozellikler

- Turkce dahil 29+ dilde TTS
- Kullanicinin klonlanmis sesi ile seslendirme
- Uzun metin parcalama ve birlestirme
- SRT/VTT altyazi uretimi
- Ses parametreleri (stability, similarity, style) ayarlama

## Kullanim

### Hizli TTS

```bash
python ~/.claude/skills/elevenlabs/scripts/tts.py "Merhaba dunya" --voice "Kesif -TR"
```

### Dosyadan TTS

```bash
python ~/.claude/skills/elevenlabs/scripts/tts.py --file script.txt --voice "Kesif -TR" --output narration.mp3
```

### Sesleri Listele

```bash
python ~/.claude/skills/elevenlabs/scripts/tts.py --list-voices --lang tr
```

## Turkce Sesler

| Voice ID             | Isim           | Tip                    |
| -------------------- | -------------- | ---------------------- |
| KBG3AdJeZGfwgERL7bFX | Kesif -TR      | Klonlanmis (kullanici) |
| 75SIZa3vvET95PHhf1yD | Ahmet          | Erkek, anlatici        |
| Y2T2O1csKPgWgyuKcU0a | Cavit Pancar   | Erkek, egitim          |
| fg8pljYEn5ahwjyOQaro | Mustafa Silici | Erkek, profesyonel     |
| mBUB5zYuPwfVE6DTcEjf | Eda Atlas      | Kadin, Istanbul        |

## API Anahtari

- WordPress DB: `klms_settings` -> `elevenlabs_api_key`
- Env: `ELEVENLABS_API_KEY`
- Varsayilan konum: `~/.elevenlabs_api_key`

## Parametreler

| Parametre    | Varsayilan             | Aciklama              |
| ------------ | ---------------------- | --------------------- |
| --voice      | Kesif -TR              | Ses ismi veya ID      |
| --model      | eleven_multilingual_v2 | TTS modeli            |
| --stability  | 0.5                    | Ses kararliligi (0-1) |
| --similarity | 0.75                   | Ses benzerlik (0-1)   |
| --style      | 0.0                    | Stil vurgusu (0-1)    |
| --output     | output.mp3             | Cikti dosyasi         |
| --format     | mp3_44100_128          | Ses formati           |

## Limitler

- Free plan: 10,000 karakter/ay
- Starter: 30,000 karakter/ay
- Uzun metinler otomatik parcalanir (max 5000 karakter/istek)
