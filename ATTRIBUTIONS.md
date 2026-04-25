# Atıflar & Yararlanılan Kaynaklar

## Standart & Spesifikasyon

- **Claude Code Skills** — © Anthropic PBC, açık dokümantasyon: [docs.anthropic.com](https://docs.anthropic.com)
- **Markdown frontmatter** — YAML 1.2 standardı

## Skill'lerin Çağırdığı Üçüncü Taraf Servisler

Her skill, kullanıcının kendi hesabıyla aşağıdaki servislere bağlanır:

| Servis | Sahibi | Skill |
|---|---|---|
| ElevenLabs | ElevenLabs Inc. | `elevenlabs` |
| Google NotebookLM | Google LLC | `notebooklm`, `yt-notebooklm-pipeline` |
| Suno AI | Suno Inc. | (`udemy-video-pipeline` opsiyonel) |
| Instagram Graph API | Meta Platforms Inc. | `instagram-manager`, `instagram-orkestrasyon` |
| YouTube Data API | Google LLC | `yt-search`, `yt-notebooklm-pipeline` |
| FFmpeg | FFmpeg topluluğu (LGPL/GPL) | `video-montaj` |
| yt-dlp | yt-dlp topluluğu (Unlicense) | `yt-search` |

> Her servisin kendi ToS'una tabisiniz. Skill'ler yalnızca **kullanıcının kendi kimliğiyle** çağrı yapar; üçüncü taraf veri toplamaz.

## İlham Alınan / Referans Alınan Çalışmalar

- [**Awesome Claude Code**](https://github.com/hesreallyhim/awesome-claude-code) (MIT, topluluk listesi) — skill dizilim referansı
- [**Anthropic Cookbook**](https://github.com/anthropics/anthropic-cookbook) (MIT) — prompt mühendisliği örüntüleri
- [**Cursor Rules ekosistemi**](https://cursor.directory) — markdown-tabanlı kural dağıtım modeli (yapı ilhamı)

> Yazarın özel olarak yönettiği başka skill koleksiyonları da var; ancak bu repoda yer alan skill'ler **bu koleksiyondan bağımsız olarak**, sıfırdan veya `skill-creator` ile yeniden yazılmıştır. Hiçbiri başka bir koleksiyondan kopyalanmamıştır.

> Bu repo, yukarıdaki kaynaklardan **kod kopyalamamış**; "tek dosya markdown skill" formatını standartlaştırmıştır.

## Açık Kaynak Yardımcı Araçlar

Bazı skill'ler aşağıdaki açık kaynak araçları çalıştırır (her biri kullanıcının makinesinde lokal kurulmuş olmalı):

| Araç | Lisans |
|---|---|
| FFmpeg | LGPL / GPL |
| yt-dlp | Unlicense |
| ImageMagick | Apache 2.0 (varyant) |
| pandoc | GPL-2.0 |

## Markalar

"Claude" Anthropic'e, "Instagram" Meta'ya, "YouTube" / "NotebookLM" Google'a, "Udemy" Udemy LLC'ye, "Suno" Suno Inc.'e aittir. Bu projede yalnızca tanımlama amaçlı (nominative fair use) anılmıştır.

## Dağıtım Notu

Bu koleksiyondaki skill'lerin **bazıları KEŞİF Ekosistemi'nin özel pipeline'ları için yazıldı** ve burada **sadeleştirilmiş, genelleştirilmiş halleri** yayınlanıyor. **Yayın öncesi içerik denetimi** yapılarak şu bilgiler kaldırılmıştır:

- Müşteri verisi, hasta/danışan referansı (yazarın iç sağlık projelerinden hiçbir veri veya kod referansı bu repoda yer almaz)
- Özel hesap ID'leri (`@kesiforg` gibi public handle'lar dışında)
- Özel API endpoint URL'leri, dahili sunucu adresleri
- Müşteri brief'leri, müşteri-spesifik prompt şablonları
- Hassas iş akışı sırrı

> Skill'in bir kullanıcının kendi platformunda ürettiği sonuç **AS IS / NO WARRANTY** çerçevesinde değerlendirilmelidir. Yazar, üçüncü tarafın skill'i kullanırken kendi hesabında yaşayacağı yaptırım, content policy ihlali veya iş kaybından sorumlu değildir.
