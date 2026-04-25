---
name: yt-search
description: YouTube'da video arama, metadata cekme ve sonuclari tablo olarak listeleme. yt-dlp tabanli.
triggers:
  ["yt-search", "youtube search", "youtube ara", "video ara", "video bul"]
---

# yt-search Skill

YouTube'da belirli bir konu hakkinda video arar, metadata (baslik, kanal, goruntulenme, sure, tarih) ceker ve sonuclari formatli tablo olarak sunar.

## Kullanim

```
/yt-search <arama_terimi>
```

## Standart Islem Proseduru

1. **Arama**: Kullanicinin verdigi arama terimini `scripts/search.py` ile YouTube'da ara
2. **Filtreleme**: Son 6 ay icindeki videolari filtrele (varsayilan)
3. **Listeleme**: Sonuclari tablo formatinda sun (baslik, kanal, goruntulenme, sure, tarih)
4. **Cikti**: Sonuclari hem terminalde goster hem de `.output/yt-search-results.json` dosyasina kaydet

## Parametreler

- `query` (zorunlu): Arama terimi
- `--max-results` (opsiyonel): Maksimum sonuc sayisi (varsayilan: 20)
- `--period` (opsiyonel): Zaman filtresi - "6m", "1y", "all" (varsayilan: 6m)
- `--sort` (opsiyonel): Siralama - "views", "date", "relevance" (varsayilan: relevance)

## Ornek

```bash
python ~/.claude/skills/yt-search/scripts/search.py "claude code skills" --max-results 20 --period 6m
```
