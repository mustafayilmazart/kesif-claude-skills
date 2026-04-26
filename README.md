# Claude Skills Curated

> **Üretkenliği artıran damıtılmış Claude Code skill koleksiyonu — yazarın kendi pipeline'larında dahili olarak kullanılan, sade, tek dosya markdown skill'ler.**
> *A curated collection of Claude Code skills (markdown-based, single-file each) used internally in the author's pipelines — for content creation, video, AI orchestration, and developer ergonomics. Provided AS IS, no warranty.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Awesome Claude](https://img.shields.io/badge/Awesome-Claude-blueviolet)](#)

---

## 🎯 Niçin Curated?

Claude Code skill ekosistemi hızla büyüyor — yüzlerce skill var ama:
- Çoğu **deneme/ders** kalıbında, üretimde test edilmemiş
- Standart yapısı yok → her skill başka format
- Türkçe odaklı pipeline yok
- Hangisi gerçekten zaman kazandırıyor — belirsiz

Bu repo şunu sunar: **15-20 skill, hepsi yazarın kendi pipeline'larında dahili kullanılıyor, her biri sade tek dosya markdown.** Üçüncü taraf garantisi yok — `AS IS`.

---

## 📂 Skill Kategorileri

### 🎨 İçerik Üretim
| Skill | Ne Yapar |
|---|---|
| `instagram-orkestrasyon` | Instagram içerik pipeline master — araştırma + üretim + paylaşım |
| `instagram-manager` | Tek post paylaşma, caption AI, hashtag, zamanlama |
| `islami-video` | Reels/Shorts için İslami eğitim videosu üretim akışı |
| `udemy-video-pipeline` | NotebookLM araştırma + script + ElevenLabs seslendirme |

### 🎥 Video & Ses
| Skill | Ne Yapar |
|---|---|
| `video-montaj` | FFmpeg ile montaj, format dönüşümü, altyazı yakma |
| `elevenlabs` | Türkçe seslendirme, ses klonlama, batch TTS |
| `notebooklm` | Google NotebookLM ile not, audio overview, mind-map üretimi |

### 🔍 Araştırma & Analiz
| Skill | Ne Yapar |
|---|---|
| `yt-search` | YouTube arama + metadata + tablo çıktısı (`yt-dlp` tabanlı) |
| `yt-notebooklm-pipeline` | YouTube → NotebookLM → analiz tek prompt'ta |

### 🛠 Geliştirici Ergonomisi
| Skill | Ne Yapar |
|---|---|
| `skill-creator` | Yeni skill oluştur, mevcut skill iyileştir, eval ile test |
| `simplify` | Değişen kodu kalite/yeniden kullanım için gözden geçir, sadeleştir |

### 🎼 Orkestrasyon
| Skill | Ne Yapar |
|---|---|
| `kesif-orkestrator` | KEŞİF Ekosistem master orkestratör — MCP + skill koordinasyonu |
| `ceo-briefing` / `ceo-decide` / `ceo-status` | CEO ajan komutları (sabah brifing, karar analizi, sistem durumu) |

---

## ⚠️ Önemli Uyarılar

- **Instagram/Meta Graph API:** `instagram-orkestrasyon` toplu otomatik paylaşım Meta ToS §4.2 — Publishing API erişimi gerekir, standart hesapta hesap askıya alma riski. Manuel onay modu zorunlu.
- **3. taraf API maliyetleri:** ElevenLabs, NotebookLM, Suno → kendi hesabınızdan faturalanır.
- **AS IS:** Yazarın kendi pipeline'larında kullanılır; üçüncü tarafta garanti yok.

Detay: bkz. [SECURITY.md](SECURITY.md).

## 🚀 Kurulum

```bash
git clone https://github.com/mustafayilmazart/claude-skills-curated
cd claude-skills-curated

# Kullanmak istediğiniz skill'leri global skills dizininize kopyalayın
# Windows
xcopy skills\* %USERPROFILE%\.claude\skills\ /E /I

# Mac/Linux
cp -r skills/* ~/.claude/skills/
```

Skill'i kullanmak için Claude Code içinde `/skill-name` yazın:

```
/instagram-orkestrasyon haftalik-icerik-uret
```

---

## 📝 Skill Yapısı

Her skill **tek bir markdown dosyası**, frontmatter + talimatlar:

```markdown
---
name: ornek-skill
description: Ne yaptığını 1-2 cümleyle anlatın
---

# Ne Yapar
...

# Nasıl Kullanılır
...

# Komutlar
- /ornek-skill arg1 arg2
```

---

## 🎓 Yeni Skill Oluşturmak

`skill-creator` skill'i ile:

```
/skill-creator yeni-bir-skill-olustur
```

veya manuel olarak `skills/yeni-skill.md` ekleyip frontmatter doldurun.

---

## 📚 Atıflar

[ATTRIBUTIONS.md](ATTRIBUTIONS.md)

---

## 📄 Lisans

MIT — bkz. [LICENSE](LICENSE).

> Skills are markdown — feel free to fork, adapt, and PR back improvements.
