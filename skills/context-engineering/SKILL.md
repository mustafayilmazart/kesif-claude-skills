---
name: context-engineering
description: Context Engineering ve PRP (Plan-Research-Plan) sistemi. Feature geliştirme öncesi kapsamlı bağlam hazırlığı yapar. INITIAL.md ile feature spec, PRP ile implementation blueprint, examples ile pattern referansı sağlar. Büyük özelliklerde ve yeni projelerde kullan.
---

# Context Engineering — KEŞİF PRP Sistemi

Yapay zeka destekli geliştirmede bağlam mühendisliği sistemi. "Prompt engineering değil, context engineering."

## Felsefe
AI kodlama hatalarının %90'ı model hatası değil, bağlam eksikliğidir. Bu skill doğru bağlamı sistematik olarak sağlar.

## Bileşenler

### 1. INITIAL.md — Feature Spesifikasyonu
Her yeni özellik için oluşturulacak yapılandırılmış spec dosyası:

```markdown
# [Feature Adı]

## FEATURE
- Spesifik gereksinimler (ne yapılacak)
- Kabul kriterleri
- Kapsam sınırları (ne YAPILMAYACAK)

## EXAMPLES
- Takip edilecek kod pattern'leri
- Mevcut benzer implementasyonlar
- Referans dosyalar ve satır numaraları

## DOCUMENTATION
- İlgili API dokümantasyonları
- Framework/kütüphane referansları
- Mimari karar kayıtları (ADR)

## CONSIDERATIONS
- Bilinen kısıtlamalar ve gotcha'lar
- Performans gereksinimleri
- Güvenlik gereksinimleri
- Geriye uyumluluk
```

### 2. PRP — Plan-Research-Plan Döngüsü

#### Faz 1: Plan (İlk Tasarım)
1. Codebase'i analiz et (yapı, pattern'ler, konvansiyonlar)
2. İlgili dosyaları ve bağımlılıkları belirle
3. İlk uygulama planını oluştur
4. Güven skoru ver (1-10)

#### Faz 2: Research (Araştırma)
1. Mevcut pattern'leri araştır (grep, glob ile)
2. Benzer implementasyonları incele
3. Dokümantasyonu kontrol et
4. Edge case'leri belirle
5. Eksik bilgileri tespit et

#### Faz 3: Plan (Revize Tasarım)
1. Araştırma bulgularıyla planı güncelle
2. Spesifik dosya:satır değişikliklerini listele
3. Test stratejisini belirle
4. Final güven skoru ver

### 3. Examples Klasörü
Proje kökünde `.claude/examples/` dizini:
- Tercih edilen kod pattern'leri
- Test yazım örnekleri
- API tasarım örnekleri
- Hata yönetim pattern'leri

## Kullanım

### PRP Oluşturma
```
"Bu feature için PRP oluştur: [feature açıklaması]"
```

### PRP Uygulama
```
"Bu PRP'yi uygula: [PRP dosya yolu]"
```

### INITIAL.md Oluşturma
```
"Bu feature için INITIAL.md hazırla: [feature açıklaması]"
```

## PRP Çıktı Formatı
```markdown
# PRP: [Feature Adı]
Tarih: YYYY-MM-DD
Güven Skoru: X/10

## Analiz
- Etkilenen dosyalar: [liste]
- Bağımlılıklar: [liste]
- Risk seviyesi: Düşük/Orta/Yüksek

## Uygulama Adımları
1. [dosya:satır] — [değişiklik açıklaması]
2. [dosya:satır] — [değişiklik açıklaması]

## Test Stratejisi
- [ ] Unit test: [açıklama]
- [ ] Integration test: [açıklama]

## Kontrol Listesi
- [ ] Mevcut testler geçiyor
- [ ] Yeni testler yazıldı
- [ ] Dokümantasyon güncellendi
- [ ] Güvenlik kontrolü yapıldı
```

## En İyi Uygulamalar
- Her büyük feature'dan önce PRP oluştur
- Güven skoru 7'nin altındaysa daha fazla araştırma yap
- Examples klasörünü güncel tut
- INITIAL.md'yi paydaşlarla paylaş ve onay al
