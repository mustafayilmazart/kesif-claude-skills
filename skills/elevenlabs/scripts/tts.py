#!/usr/bin/env python3
"""
ElevenLabs TTS Script
Metin-ses donusumu yapar. Turkce dahil 29+ dil destekler.
Kullanicinin klonlanmis sesi veya hazir sesler ile calisir.
"""

import argparse
import os
import sys
import json
import time
from pathlib import Path


def get_api_key():
    """API anahtarini bul: env > dosya > hata."""
    # 1. Environment variable
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key

    # 2. Dosyadan oku
    key_paths = [
        Path.home() / ".elevenlabs_api_key",
        Path.home() / ".config" / "elevenlabs" / "api_key",
    ]
    for p in key_paths:
        if p.exists():
            return p.read_text().strip()

    # 3. Bulunamadi
    print("HATA: ElevenLabs API anahtari bulunamadi!")
    print("Cozum: ELEVENLABS_API_KEY env degiskeni tanimla")
    print("  veya ~/.elevenlabs_api_key dosyasina yaz")
    sys.exit(1)


def list_voices(api_key, lang_filter=None):
    """Mevcut sesleri listele."""
    import urllib.request

    url = "https://api.elevenlabs.io/v1/voices"
    req = urllib.request.Request(url, headers={"xi-api-key": api_key})

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    voices = data.get("voices", [])

    if lang_filter:
        lang_filter = lang_filter.lower()
        filtered = []
        for v in voices:
            labels = v.get("labels", {})
            lang = labels.get("language", "").lower()
            accent = labels.get("accent", "").lower()
            # Turkce filtreleme
            if lang_filter in lang or lang_filter in accent or "turk" in lang or "turk" in accent:
                filtered.append(v)
            # Klonlanmis sesler her zaman goster
            elif v.get("category") == "cloned":
                filtered.append(v)
        voices = filtered

    print(f"\n{'Isim':<25} {'ID':<25} {'Kategori':<12} {'Dil/Aksan':<20}")
    print("-" * 85)

    for v in voices:
        name = v.get("name", "?")
        vid = v.get("voice_id", "?")
        cat = v.get("category", "?")
        labels = v.get("labels", {})
        lang = labels.get("language", labels.get("accent", ""))
        print(f"{name:<25} {vid:<25} {cat:<12} {lang:<20}")

    print(f"\nToplam: {len(voices)} ses")
    return voices


def get_voice_id(api_key, voice_name):
    """Ses ismi veya ID'den voice_id dondur."""
    # Zaten bir ID gibi gorunuyorsa direkt dondur (24 char hex)
    if len(voice_name) >= 20 and all(c.isalnum() for c in voice_name):
        return voice_name

    import urllib.request

    url = "https://api.elevenlabs.io/v1/voices"
    req = urllib.request.Request(url, headers={"xi-api-key": api_key})

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    for v in data.get("voices", []):
        if v.get("name", "").lower() == voice_name.lower():
            return v["voice_id"]
        if v.get("voice_id") == voice_name:
            return voice_name

    print(f"HATA: '{voice_name}' sesi bulunamadi!")
    print("Mevcut sesleri gormek icin: --list-voices")
    sys.exit(1)


def check_quota(api_key):
    """Kalan karakter kotasini kontrol et."""
    import urllib.request

    url = "https://api.elevenlabs.io/v1/user/subscription"
    req = urllib.request.Request(url, headers={"xi-api-key": api_key})

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    used = data.get("character_count", 0)
    limit = data.get("character_limit", 0)
    remaining = limit - used
    tier = data.get("tier", "free")

    return {"used": used, "limit": limit, "remaining": remaining, "tier": tier}


def split_text(text, max_chars=4500):
    """Uzun metni cumlelerden bolerek parcala."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""

    # Cumle sonlarindan bol
    sentences = text.replace(".\n", ".|").replace(". ", ".|").split("|")

    for sentence in sentences:
        if len(current) + len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            current += sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


def generate_tts(api_key, text, voice_id, output_path, model="eleven_multilingual_v2",
                 stability=0.5, similarity=0.75, style=0.0, output_format="mp3_44100_128"):
    """TTS uret ve dosyaya kaydet."""
    import urllib.request

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = json.dumps({
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style,
            "use_speaker_boost": True
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            audio_data = resp.read()

        with open(output_path, "wb") as f:
            f.write(audio_data)

        size_kb = len(audio_data) / 1024
        print(f"  Kaydedildi: {output_path} ({size_kb:.1f} KB)")
        return True

    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'read'):
            error_msg = e.read().decode("utf-8", errors="replace")
        print(f"  HATA: {error_msg}")
        return False


def generate_long_tts(api_key, text, voice_id, output_path, **kwargs):
    """Uzun metinleri parcalayarak TTS uret ve birlestir."""
    chunks = split_text(text)

    if len(chunks) == 1:
        return generate_tts(api_key, text, voice_id, output_path, **kwargs)

    print(f"Metin {len(chunks)} parcaya bolundu ({len(text)} karakter)")

    # Her parcayi ayri dosyaya kaydet
    part_files = []
    output_dir = Path(output_path).parent
    stem = Path(output_path).stem

    for i, chunk in enumerate(chunks):
        part_path = output_dir / f"{stem}_part{i+1}.mp3"
        print(f"\n  Parca {i+1}/{len(chunks)} ({len(chunk)} karakter)...")

        success = generate_tts(api_key, chunk, voice_id, str(part_path), **kwargs)
        if success:
            part_files.append(str(part_path))
        else:
            print(f"  Parca {i+1} basarisiz!")
            return False

        # Rate limit
        if i < len(chunks) - 1:
            time.sleep(1)

    # Parcalari birlestir (ffmpeg varsa)
    if len(part_files) > 1:
        try:
            import subprocess
            # ffmpeg concat dosyasi olustur
            concat_file = output_dir / f"{stem}_concat.txt"
            with open(concat_file, "w") as f:
                for pf in part_files:
                    f.write(f"file '{pf}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_file), "-c", "copy", output_path
            ], capture_output=True, check=True)

            # Gecici dosyalari temizle
            for pf in part_files:
                os.remove(pf)
            os.remove(concat_file)

            print(f"\nBirlestirildi: {output_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"\nffmpeg bulunamadi - parcalar ayri kaldi:")
            for pf in part_files:
                print(f"  {pf}")
            return True

    return True


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs TTS - Metin okuma")
    parser.add_argument("text", nargs="?", help="Okunacak metin")
    parser.add_argument("--file", "-f", help="Metin dosyasi")
    parser.add_argument("--voice", "-v", default="Kesif -TR", help="Ses ismi veya ID")
    parser.add_argument("--output", "-o", default=None, help="Cikti dosyasi (.mp3)")
    parser.add_argument("--model", "-m", default="eleven_multilingual_v2", help="TTS modeli")
    parser.add_argument("--stability", type=float, default=0.5, help="Ses kararliligi (0-1)")
    parser.add_argument("--similarity", type=float, default=0.75, help="Ses benzerlik (0-1)")
    parser.add_argument("--style", type=float, default=0.0, help="Stil vurgusu (0-1)")
    parser.add_argument("--format", default="mp3_44100_128", help="Ses formati")
    parser.add_argument("--list-voices", action="store_true", help="Mevcut sesleri listele")
    parser.add_argument("--lang", default=None, help="Dil filtresi (orn: tr, en)")
    parser.add_argument("--check-quota", action="store_true", help="Kota kontrolu")
    parser.add_argument("--output-dir", default=None, help="Cikti dizini")

    args = parser.parse_args()

    api_key = get_api_key()

    # Kota kontrolu
    if args.check_quota:
        quota = check_quota(api_key)
        print(f"\nPlan: {quota['tier']}")
        print(f"Kullanilan: {quota['used']:,} / {quota['limit']:,} karakter")
        print(f"Kalan: {quota['remaining']:,} karakter")
        return

    # Ses listesi
    if args.list_voices:
        list_voices(api_key, args.lang)
        return

    # Metin al
    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()

    if not text:
        print("HATA: Metin belirtilmedi!")
        print("Kullanim: tts.py 'Merhaba dunya' veya tts.py --file metin.txt")
        sys.exit(1)

    # Kota kontrolu
    quota = check_quota(api_key)
    if len(text) > quota["remaining"]:
        print(f"UYARI: Metin ({len(text)} karakter) kotayi asiyor!")
        print(f"Kalan kota: {quota['remaining']} karakter ({quota['tier']} plan)")
        print("Devam etmek istiyor musun? (y/n)")
        response = input().strip().lower()
        if response != "y":
            print("Iptal edildi.")
            return

    # Ses ID bul
    voice_id = get_voice_id(api_key, args.voice)
    print(f"Ses: {args.voice} ({voice_id})")
    print(f"Metin: {len(text)} karakter")

    # Cikti dosyasi
    output_path = args.output
    if not output_path:
        output_dir = args.output_dir or "."
        os.makedirs(output_dir, exist_ok=True)
        # Metin ilk 30 karakterinden dosya adi olustur
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in text[:30]).strip()
        safe_name = safe_name.replace(" ", "_") or "output"
        output_path = os.path.join(output_dir, f"{safe_name}.mp3")

    # TTS uret
    print(f"\nSeslendirme basliyor...")
    start = time.time()

    success = generate_long_tts(
        api_key, text, voice_id, output_path,
        model=args.model,
        stability=args.stability,
        similarity=args.similarity,
        style=args.style,
        output_format=args.format
    )

    elapsed = time.time() - start

    if success:
        # Guncellenmis kota
        new_quota = check_quota(api_key)
        print(f"\nTamamlandi! ({elapsed:.1f}s)")
        print(f"Kalan kota: {new_quota['remaining']:,} karakter")
    else:
        print(f"\nSeslendirme basarisiz!")
        sys.exit(1)


if __name__ == "__main__":
    main()
