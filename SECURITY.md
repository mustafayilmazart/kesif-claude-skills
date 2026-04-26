# Security Policy

## Reporting / Bildirim

**bilgi@mustafayilmaz.art** — public issue açmayın / do not open public issues.

72 saat yanıt, 14 gün düzeltme hedefi.

## Skill Güvenliği / Skill Security

Bu repodaki skill'ler **markdown dosyaları**dır; tek başlarına çalıştırılabilir değildir. Ancak Claude Code üzerinden çağrıldığında AI'ın davranışını yönlendirirler.

### Risk: Prompt Injection

Bir skill markdown dosyasının içine **kötü niyetli komutlar** eklenebilir (ör. "ignore safety, execute X"). Bu repo'dan skill kopyalarken:

1. **Markdown'ı tek tek okuyun** — sadece yapıştırmayın
2. **`description` ve `name` alanlarına dikkat edin** — beklenenle uyumlu olmalı
3. Skill'in yaptığını anlamadan global skills dizininize kopyalamayın

### Risk: Üçüncü Taraf Servis Çağrıları

Skills, kullanıcının kendi hesabıyla şu servisleri çağırabilir:
- ElevenLabs (sesli üretim — fatura yaratabilir)
- Instagram Graph API (paylaşım — content policy ihlali riski)
- YouTube Data API (kota tüketir)
- FFmpeg (lokal CPU/disk kullanımı)

Çalıştırmadan önce **hangi servisi çağıracağını** mutlaka okuyun.

> ⚠️ **Meta/Instagram Graph API Uyarısı:** Instagram Graph API ile **otomatik toplu paylaşım**, Meta Platform Terms §4.2 kapsamında özel "Publishing API" erişimi gerektirir. Bu erişim **sadece onaylı iş hesaplarına** verilir; standart geliştirici hesaplarında toplu post = **hesap askıya alma** riski yüksektir. `instagram-orkestrasyon` skill'i bu nedenle **manuel onay modunda** çalıştırılmalıdır. Yazar, Meta tarafından alınan herhangi bir hesap aksiyonundan sorumlu değildir.

### Risk: Bulk Operasyon Skills

`instagram-orkestrasyon`, `udemy-video-pipeline` gibi pipeline skill'leri **çoklu otomatik adım** çalıştırır. İlk kullanımda her adımı **onayla** modunda çalıştırın; bilinçsiz toplu post = hesap askıya alma riski.

## Supported Versions

Sadece en son revizyon (skills versiyonsuzdur, repo HEAD esastır).
