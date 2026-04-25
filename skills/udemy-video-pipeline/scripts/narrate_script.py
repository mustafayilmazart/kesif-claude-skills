#!/usr/bin/env python3
"""
Script Seslendirici
Ders scriptindeki bolumleri ElevenLabs ile seslendirir.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ElevenLabs TTS modulu - ayni dizindeki tts.py'yi kullan
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "elevenlabs" / "scripts"))

try:
    from tts import get_api_key, get_voice_id, generate_tts, check_quota
except ImportError:
    print("HATA: ElevenLabs TTS modulu bulunamadi!")
    print("Beklenen konum: ~/.claude/skills/elevenlabs/scripts/tts.py")
    sys.exit(1)


def narrate_section(api_key, voice_id, section, output_dir, stability=0.65,
                    similarity=0.80, style=0.15):
    """Tek bir bolumu seslendir."""
    section_id = section["id"]
    title = section["title"]
    narration = section["narration"]

    output_path = os.path.join(output_dir, f"section_{section_id:02d}.mp3")

    print(f"\n{'='*50}")
    print(f"Bolum {section_id}: {title}")
    print(f"Karakter: {len(narration)}")
    print(f"Cikti: {output_path}")

    success = generate_tts(
        api_key=api_key,
        text=narration,
        voice_id=voice_id,
        output_path=output_path,
        model="eleven_multilingual_v2",
        stability=stability,
        similarity=similarity,
        style=style,
        output_format="mp3_44100_128"
    )

    return success, output_path


def create_subtitles(section, output_dir):
    """Basit SRT altyazi dosyasi olustur."""
    section_id = section["id"]
    narration = section["narration"]
    srt_path = os.path.join(output_dir, f"section_{section_id:02d}.srt")

    # Cumlelere bol
    sentences = []
    for sent in narration.replace("\n\n", "\n").split("\n"):
        sent = sent.strip()
        if sent:
            # Uzun cumleleri bol
            if len(sent) > 80:
                words = sent.split()
                mid = len(words) // 2
                sentences.append(" ".join(words[:mid]))
                sentences.append(" ".join(words[mid:]))
            else:
                sentences.append(sent)

    # Tahmini zamanlama (kelime sayisina gore)
    srt_content = ""
    current_time = 0.0

    for i, sent in enumerate(sentences):
        word_count = len(sent.split())
        duration = max(2.0, word_count / 2.5)  # ~2.5 kelime/saniye

        start_h = int(current_time // 3600)
        start_m = int((current_time % 3600) // 60)
        start_s = int(current_time % 60)
        start_ms = int((current_time % 1) * 1000)

        end_time = current_time + duration
        end_h = int(end_time // 3600)
        end_m = int((end_time % 3600) // 60)
        end_s = int(end_time % 60)
        end_ms = int((end_time % 1) * 1000)

        srt_content += f"{i+1}\n"
        srt_content += f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> "
        srt_content += f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n"
        srt_content += f"{sent}\n\n"

        current_time = end_time + 0.3  # Cumleler arasi bosluk

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return srt_path


def main():
    parser = argparse.ArgumentParser(description="Ders scriptini seslendir")
    parser.add_argument("--script", "-s", required=True, help="Script JSON dosyasi")
    parser.add_argument("--voice", "-v", default="Kesif -TR", help="Ses ismi veya ID")
    parser.add_argument("--output-dir", "-o", required=True, help="Cikti dizini")
    parser.add_argument("--sections", nargs="*", type=int, help="Sadece belirli bolumleri seslendir")
    parser.add_argument("--stability", type=float, default=0.65, help="Ses kararliligi")
    parser.add_argument("--similarity", type=float, default=0.80, help="Ses benzerlik")
    parser.add_argument("--style", type=float, default=0.15, help="Stil vurgusu")
    parser.add_argument("--subtitles", action="store_true", help="SRT altyazi olustur")
    parser.add_argument("--dry-run", action="store_true", help="Kota kontrolu yap ama seslendirme")

    args = parser.parse_args()

    # Script yukle
    with open(args.script, "r", encoding="utf-8") as f:
        script = json.load(f)

    sections = script.get("sections", [])

    # Bolum filtresi
    if args.sections:
        sections = [s for s in sections if s["id"] in args.sections]

    if not sections:
        print("HATA: Seslendirilecek bolum bulunamadi!")
        sys.exit(1)

    total_chars = sum(len(s["narration"]) for s in sections)

    # API key ve ses
    api_key = get_api_key()
    voice_id = get_voice_id(api_key, args.voice)

    # Kota kontrolu
    quota = check_quota(api_key)
    print(f"\nKurs: {script.get('title', '?')}")
    print(f"Seslendirilecek bolum: {len(sections)}")
    print(f"Toplam karakter: {total_chars:,}")
    print(f"Kalan kota: {quota['remaining']:,} ({quota['tier']} plan)")

    if total_chars > quota["remaining"]:
        print(f"\nUYARI: Kota yetersiz! {total_chars - quota['remaining']:,} karakter eksik.")
        print("Cozum: ElevenLabs planini yukselt veya bolum sayisini azalt.")

        if args.dry_run:
            return

        # Kota icinde kalan bolumleri bul
        available_chars = quota["remaining"]
        possible_sections = []
        running_total = 0
        for s in sections:
            if running_total + len(s["narration"]) <= available_chars:
                possible_sections.append(s)
                running_total += len(s["narration"])

        if possible_sections:
            print(f"\nKota dahilinde {len(possible_sections)} bolum seslendirebilir.")
        return

    if args.dry_run:
        print("\n[DRY RUN] Seslendirme yapilmadi.")
        return

    # Dizinleri olustur
    audio_dir = os.path.join(args.output_dir, "audio") if "audio" not in args.output_dir else args.output_dir
    os.makedirs(audio_dir, exist_ok=True)

    if args.subtitles:
        srt_dir = os.path.join(args.output_dir, "subtitles")
        os.makedirs(srt_dir, exist_ok=True)

    # Seslendirme
    print(f"\nSes: {args.voice} ({voice_id})")
    print(f"Seslendirme basliyor...\n")

    results = []
    start_time = time.time()

    for i, section in enumerate(sections):
        success, output_path = narrate_section(
            api_key, voice_id, section, audio_dir,
            stability=args.stability,
            similarity=args.similarity,
            style=args.style
        )

        results.append({
            "section_id": section["id"],
            "title": section["title"],
            "success": success,
            "audio_path": output_path if success else None
        })

        # Altyazi
        if args.subtitles and success:
            srt_path = create_subtitles(section, srt_dir)
            results[-1]["srt_path"] = srt_path
            print(f"  Altyazi: {srt_path}")

        # Rate limit
        if i < len(sections) - 1:
            time.sleep(1.5)

    elapsed = time.time() - start_time

    # Ozet
    successful = sum(1 for r in results if r["success"])
    print(f"\n{'='*50}")
    print(f"Seslendirme tamamlandi! ({elapsed:.0f}s)")
    print(f"Basarili: {successful}/{len(results)} bolum")

    # Metadata kaydet
    metadata = {
        "title": script.get("title", ""),
        "voice": args.voice,
        "voice_id": voice_id,
        "sections": results,
        "total_chars_used": total_chars,
        "elapsed_seconds": round(elapsed)
    }

    meta_path = os.path.join(args.output_dir, "narration_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Metadata: {meta_path}")

    # Guncellenmis kota
    new_quota = check_quota(api_key)
    print(f"Kalan kota: {new_quota['remaining']:,} karakter")


if __name__ == "__main__":
    main()
