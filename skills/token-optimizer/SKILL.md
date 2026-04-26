---
name: token-optimizer
description: Uzun prompt veya dosya içeriğini Claude/Gemini/Groq'a göndermeden önce sıkıştırır. Caveman tarzı filler-silme + TR/EN kısa kalıp eşlemeleri ile ortalama %40-60 input token tasarrufu sağlar. Kullanıcı "bu promptu sıkıştır", "token düşür", "maliyet azalt" dediğinde veya 2000+ karakterlik bir metni işlerken devreye gir.
---

# Token Optimizer Skill

## Kullanım

```bash
python <workspace>/mcp-servers/kesif-token-optimizer/src/compressor.py "metin"
# veya
cat uzun.md | python <workspace>/mcp-servers/kesif-token-optimizer/src/compressor.py
```

## Ne zaman otomatik kullan

1. Bir dosya/metni LLM'e göndermeden önce 2000+ karakterse
2. Kullanıcı token maliyetinden şikayet ederse
3. Pipeline'larda batch işlemden önce (her girdi için)

## Sıkıştırma stratejisi

- **Filler silme:** lütfen, aslında, yani, eee, please, kindly, very, really
- **Uzun→kısa kalıp:** "in order to"→"to", "yapabilir misin"→"yap", "approximately"→"≈"
- **Boşluk normalizasyonu:** çoklu ws ve nokta birleşimi
- **Agresif mod:** gereksiz "that" silme, virgül öncesi ws

## Entegrasyon Noktaları

- `instagram-orkestrasyon` pipeline'ında her post taslağı → compress
- `udemy-video-pipeline`'da script üretiminden önce input compress
- `notebooklm` kaynak yüklemeden önce

## Ölçüm

Her çağrıda stats döner:
- `char_saving_pct`, `word_saving_pct` — tasarruf oranı
- Aylık toplam: `<workspace>/scripts/connectome/output/token_stats.json`
