#!/usr/bin/env python3
"""
Udemy Kurs Olusturucu - Tam Pipeline
Konu -> Script -> Seslendirme asamalarini otomatik calistirir.
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent
SCRIPTS = {
    "generate_script": SKILLS_DIR / "udemy-video-pipeline" / "scripts" / "generate_script.py",
    "narrate_script": SKILLS_DIR / "udemy-video-pipeline" / "scripts" / "narrate_script.py",
    "tts": SKILLS_DIR / "elevenlabs" / "scripts" / "tts.py",
}


def run_step(name, cmd, env=None):
    """Pipeline asamasini calistir."""
    print(f"\n{'='*60}")
    print(f"  ASAMA: {name}")
    print(f"{'='*60}\n")

    result = subprocess.run(
        cmd,
        capture_output=False,
        text=True,
        env=env or os.environ.copy()
    )

    if result.returncode != 0:
        print(f"\nHATA: {name} basarisiz! (kod: {result.returncode})")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Udemy kurs olusturma pipeline")
    parser.add_argument("topic", help="Kurs konusu")
    parser.add_argument("--mindmap", "-mm", help="Mind map JSON dosyasi")
    parser.add_argument("--analysis", "-a", help="NotebookLM analiz dosyasi")
    parser.add_argument("--sections", "-s", type=int, default=None, help="Maks bolum sayisi")
    parser.add_argument("--voice", "-v", default="Kesif -TR", help="ElevenLabs ses")
    parser.add_argument("--output-dir", "-o", required=True, help="Cikti dizini")
    parser.add_argument("--skip-narration", action="store_true", help="Sadece script uret")
    parser.add_argument("--subtitles", action="store_true", default=True, help="Altyazi olustur")
    parser.add_argument("--dry-run", action="store_true", help="Kota kontrolu")

    args = parser.parse_args()

    # Dizinleri olustur
    os.makedirs(args.output_dir, exist_ok=True)
    script_path = os.path.join(args.output_dir, "script.json")

    print(f"Udemy Kurs Pipeline")
    print(f"Konu: {args.topic}")
    print(f"Cikti: {args.output_dir}")
    print(f"Ses: {args.voice}")

    # Kaynak kontrolu
    if not args.mindmap and not args.analysis:
        # Varsayilan yollara bak
        default_mindmap = f"<workspace>/notebooklm/output/{args.topic.lower().replace(' ', '-')}-mindmap.json"
        default_analysis = f"<workspace>/notebooklm/output/{args.topic.lower().replace(' ', '-')}-analysis.md"

        if os.path.exists(default_mindmap):
            args.mindmap = default_mindmap
            print(f"Mind map bulundu: {default_mindmap}")
        elif os.path.exists(default_analysis):
            args.analysis = default_analysis
            print(f"Analiz bulundu: {default_analysis}")
        else:
            print("HATA: --mindmap veya --analysis parametresi gerekli!")
            print("Veya once NotebookLM pipeline calistir:")
            print(f'  python ~/.claude/skills/yt-notebooklm-pipeline/scripts/pipeline.py "{args.topic}"')
            sys.exit(1)

    # ASAMA 1: Script uretimi
    script_cmd = [
        sys.executable, str(SCRIPTS["generate_script"]),
        "--topic", args.topic,
        "--output", script_path
    ]

    if args.mindmap:
        script_cmd.extend(["--mindmap", args.mindmap])
    if args.analysis:
        script_cmd.extend(["--analysis", args.analysis])
    if args.sections:
        script_cmd.extend(["--sections", str(args.sections)])

    success = run_step("Script Uretimi", script_cmd)
    if not success:
        sys.exit(1)

    # Script'i oku ve ozet goster
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    print(f"\nScript ozeti:")
    print(f"  Bolum: {script['total_sections']}")
    print(f"  Karakter: {script['total_chars']:,}")

    if args.skip_narration:
        print("\nSeslendirme atlandi (--skip-narration).")
        print(f"Script: {script_path}")
        return

    # ASAMA 2: Seslendirme
    narrate_cmd = [
        sys.executable, str(SCRIPTS["narrate_script"]),
        "--script", script_path,
        "--voice", args.voice,
        "--output-dir", args.output_dir,
    ]

    if args.subtitles:
        narrate_cmd.append("--subtitles")
    if args.dry_run:
        narrate_cmd.append("--dry-run")

    success = run_step("Seslendirme", narrate_cmd)

    if success:
        print(f"\n{'='*60}")
        print(f"  PIPELINE TAMAMLANDI!")
        print(f"{'='*60}")
        print(f"\nCikti dizini: {args.output_dir}")
        print(f"  script.json - Ders scripti")
        if not args.dry_run:
            print(f"  audio/ - Seslendirme dosyalari")
            if args.subtitles:
                print(f"  subtitles/ - SRT altyazilar")
            print(f"  narration_metadata.json - Seslendirme bilgileri")


if __name__ == "__main__":
    main()
