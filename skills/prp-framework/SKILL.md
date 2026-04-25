---
name: prp-framework
description: "Feature geliştirme için Plan-Research-Plan framework'ü. Codebase analizi, pattern araştırma, güven skoru, blueprint oluşturma ve uygulama döngüsü. /generate-prp ve /execute-prp komutlarıyla çalışır."
version: "1.0.0"
category: engineering
model: sonnet
tools: Read, Write, Edit, Bash, Grep, Glob, Agent
tags: ["context-engineering", "planning", "architecture", "prp"]
author: kesif
---

# PRP Framework — Plan-Research-Plan

PRP (Product Requirements Prompt), geleneksel PRD'nin (Product Requirements Document) AI kodlama asistanları için optimize edilmiş versiyonudur. Bağlam eksikliğini giderir, tutarlı implementasyonu sağlar.

## Felsefe

> "Bağlam mühendisliği, prompt mühendisliğinden 10x, vibe kodlamadan 100x daha etkilidir."

AI kodlama hatalarının büyük çoğunluğu model hatası değil, bağlam eksikliğidir. PRP sistemi şunları sağlar:
- Codebase pattern'lerinin sistematik araştırılması
- Validasyon döngüleriyle öz-düzeltme kapasitesi
- Adım adım uygulama planı
- Ölçülebilir başarı kriterleri

---

## `/generate-prp` Komutu

**Kullanım:** `"[feature açıklaması] için PRP oluştur"` veya bir INITIAL.md dosyası vererek

### Süreç

#### Faz 1: İlk Plan
1. INITIAL.md veya feature açıklamasını oku
2. Codebase yapısını tarama (Glob ile)
3. İlgili dosyaları ve bağımlılıkları belirle
4. İlk tasarım kararlarını yap

#### Faz 2: Araştırma
1. Benzer implementasyonları bul (Grep ile pattern ara)
2. Mevcut konvansiyonları çıkar (isimlendirme, yapı, stil)
3. Entegrasyon noktalarını tespit et
4. Edge case'leri ve gotcha'ları belirle
5. Eksik bilgileri listele

#### Faz 3: Revize Plan (Blueprint)
1. Araştırma bulgularını plana entegre et
2. Spesifik görevleri sırala (Task 1, Task 2...)
3. Her görev için pseudocode ekle
4. Validasyon komutları ekle
5. Final güven skoru ver (1-10)

### Çıktı Formatı: PRP Dosyası

PRP dosyaları `PRPs/` klasörüne kaydedilir: `PRPs/[feature-adi].md`

```markdown
---
name: "[Feature Adı]"
description: |
  [Feature açıklaması ve amacı]

## Temel Prensipler
1. Bağlam Her Şeydir: Tüm dokümantasyon, örnekler ve uyarıları dahil et
2. Validasyon Döngüleri: AI'ın çalıştırıp düzeltebileceği testler ekle
3. Bilgi Yoğunluğu: Codebase'den keyword ve pattern'leri kullan
4. Aşamalı Başarı: Önce basit başla, doğrula, sonra geliştir
---

## Hedef

[Ne inşa edilecek — son durumu ve istekleri spesifik olarak belirt]

## Neden

- [İş değeri ve kullanıcı etkisi]
- [Mevcut özelliklerle entegrasyon]
- [Çözülen problemler ve kime faydası var]

## Ne

[Kullanıcıya görünür davranış ve teknik gereksinimler]

### Başarı Kriterleri

- [ ] [Spesifik ölçülebilir sonuçlar]

## Tüm Gerekli Bağlam

### Dokümantasyon ve Referanslar

```yaml
# MUTLAKA OKU — Bunları bağlam penceresine ekle
- url: [Resmi API docs URL]
  neden: [Kullanılacak spesifik bölümler/metodlar]

- dosya: [path/to/example.py]
  neden: [Takip edilecek pattern, kaçınılacak gotcha'lar]

- doc: [Kütüphane dokümantasyon URL]
  bölüm: [Yaygın tuzaklar hakkında spesifik bölüm]
  kritik: [Yaygın hataları önleyen temel bilgi]
```

### Mevcut Codebase Ağacı

```bash
[tree komutu çıktısı]
```

### Eklenecek Dosyalarla İstenen Codebase Ağacı

```bash
[Yeni dosyalar dahil hedef yapı]
```

### Bilinen Tuzaklar ve Kütüphane Özellikleri

```python
# KRİTİK: [Kütüphane adı] [spesifik kurulum] gerektirir
# KRİTİK: Bu ORM 1000'den fazla kayıt için toplu insert desteklemiyor
```

## Uygulama Planı

### Veri Modelleri ve Yapı

```python
# Temel veri yapıları — tip güvenliği ve tutarlılık
```

### Tamamlanacak Görevler Listesi

```yaml
Görev 1:
OLUŞTUR src/yeni_ozellik.py:
  - PATTERN: src/benzer_ozellik.py'dan kopyala
  - DEĞIŞTIR: sınıf adı ve temel mantık
  - KORU: hata yönetim pattern'i

Görev 2:
DÜZENLE src/mevcut_modul.py:
  - BUL: "class MevcutImpl"
  - EKLE: "__init__" içeren satırdan sonra
  - KORU: mevcut metod imzaları

...

Görev N:
...
```

### Görev Başına Pseudocode

```python
# Görev 1
# PATTERN: Her zaman önce girdi doğrula (bkz. src/validators.py)
validated = validate_input(param)

# KRİTİK: Bu API saniyede 10'dan fazla istek için 429 döndürür
await rate_limiter.acquire()
result = await external_api.call(validated)
```

### Entegrasyon Noktaları

```yaml
VERİTABANI:
  - migration: "users tablosuna 'feature_enabled' sütunu ekle"

CONFIG:
  - ekle: config/settings.py
  - pattern: "TIMEOUT = int(os.getenv('TIMEOUT', '30'))"

ROTALAR:
  - ekle: src/api/routes.py
```

## Validasyon Döngüsü

### Seviye 1: Sözdizimi ve Stil

```bash
# ÖNCE BUNLARI ÇALIŞTIR — Devam etmeden önce hataları düzelt
ruff check src/ --fix
mypy src/
```

### Seviye 2: Unit Testler

```python
# test_yeni_ozellik.py içinde bu test durumlarını oluştur:
def test_mutlu_yol():
    """Temel işlevsellik çalışıyor"""
    result = yeni_ozellik("gecerli_girdi")
    assert result.status == "success"

def test_dogrulama_hatasi():
    """Geçersiz girdi ValidationError fırlatıyor"""
    with pytest.raises(ValidationError):
        yeni_ozellik("")
```

```bash
# Geçene kadar çalıştır ve iterate et:
pytest tests/ -v
# Başarısızsa: Hatayı oku, kök nedeni anla, kodu düzelt, tekrar çalıştır
```

### Seviye 3: Entegrasyon Testi

```bash
python -m src.main --dev
curl -X POST http://localhost:8000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'
```

## Final Validasyon Kontrol Listesi

- [ ] Tüm testler geçiyor: `pytest tests/ -v`
- [ ] Lint hatası yok: `ruff check src/`
- [ ] Tip hatası yok: `mypy src/`
- [ ] Manuel test başarılı
- [ ] Hata durumları zarif şekilde ele alınıyor
- [ ] Loglar bilgilendirici ama aşırı değil
- [ ] Gerekirse dokümantasyon güncellendi

---

## Kaçınılacak Anti-Pattern'ler

- Mevcut pattern'ler işe yararken yenilerini oluşturma
- "Çalışmalı" diye validasyonu atlama
- Başarısız testleri görmezden gelme
- Async bağlamda sync fonksiyon kullanma
- Config olması gereken değerleri hardcode etme
- Tüm exception'ları yakalama — spesifik ol

## Güven Skoru: X/10

[Güven seviyesinin nedenleri]
[Kalan belirsizlikler]
```

---

## `/execute-prp` Komutu

**Kullanım:** `"Bu PRP'yi uygula: PRPs/feature-adi.md"`

### Süreç

1. **Bağlamı Yükle**: Tüm PRP'yi oku, tüm referans dosyaları ve dokümantasyonu incele
2. **Plan Yap**: TodoWrite ile detaylı görev listesi oluştur
3. **Uygula**: Her bileşeni sırayla implement et
4. **Doğrula**: Her görev sonrası lint ve testleri çalıştır
5. **İtera Et**: Bulunan sorunları düzelt, tekrar doğrula
6. **Tamamla**: Tüm başarı kriterlerinin karşılandığını teyit et

### Uygulama Kuralları

- Güven skoru 7'nin altındaysa, uygulamadan önce daha fazla araştırma yap
- Her görev tamamlandıktan sonra çalışma durumunu doğrula
- Validasyon döngüsü yeşile dönene kadar iterate et
- Tüm anti-pattern'lerden kaçın
- Değişiklikleri atomik tutun — kısmen çalışan sistem bırakma

---

## PRP Şablonu Nasıl Doldurulur

### INITIAL.md'den PRP'ye

INITIAL.md dosyasındaki bilgileri alarak PRP oluşturulur:

| INITIAL.md Bölümü | PRP'de Karşılığı |
|---|---|
| FEATURE | Hedef + Ne bölümü |
| EXAMPLES | Referans dosyalar + Pattern'ler |
| DOCUMENTATION | Dokümantasyon ve Referanslar |
| CONSIDERATIONS | Bilinen Tuzaklar bölümü |

### Güven Skoru Rehberi

| Skor | Anlam | Eylem |
|---|---|---|
| 9-10 | Çok yüksek güven | Direkt uygula |
| 7-8 | Yüksek güven | Küçük belirsizlikler var, uygula |
| 5-6 | Orta güven | Daha fazla araştırma gerekebilir |
| 1-4 | Düşük güven | Araştırmayı tamamla, sonra uygula |

---

## Örnek Kullanım Senaryoları

### Senaryo 1: Yeni API Endpoint'i

```
"KEŞİF Portal'a kullanıcı profil güncelleme endpoint'i eklemek için PRP oluştur"
```

Sistem:
1. Mevcut endpoint pattern'lerini tarar
2. Auth middleware'ini inceler
3. Veritabanı modellerini analiz eder
4. Blueprint oluşturur (güven: 8/10)

### Senaryo 2: Yeni MCP Entegrasyonu

```
"Yeni bir MCP sunucusu eklemek için PRP oluştur: INITIAL.md"
```

Sistem:
1. Mevcut MCP yapılandırmalarını araştırır
2. kesif-mcp-registry.json formatını analiz eder
3. Entegrasyon adımlarını listeler

### Senaryo 3: Refactoring

```
"D:/0/000Portal/src/api/ klasörünü async'e geçirmek için PRP oluştur"
```

Sistem:
1. Tüm sync fonksiyonları tespit eder
2. Bağımlılık zincirini haritar
3. Sıralı migrasyon planı oluşturur
