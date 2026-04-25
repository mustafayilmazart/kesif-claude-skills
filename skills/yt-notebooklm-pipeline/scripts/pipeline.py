#!/usr/bin/env python3
"""
YouTube + NotebookLM Tam Otomasyon Pipeline
Tek komutla: YouTube'da ara -> NotebookLM'e yukle -> Analiz yap -> Icerik uret
"""

import subprocess
import sys
import os
import json
import time
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="YouTube + NotebookLM Tam Pipeline")
    parser.add_argument("query", help="Arama terimi / konu")
    parser.add_argument("--output-type", default="infographic",
                        choices=["infographic", "audio", "video", "mind-map",
                                 "slide-deck", "flashcards", "quiz", "report", "all"],
                        help="Cikti turu (varsayilan: infographic)")
    parser.add_argument("--max-videos", type=int, default=20, help="Maks video sayisi")
    parser.add_argument("--period", default="6m", help="Zaman filtresi")
    parser.add_argument("--output-dir", default=".output", help="Cikti klasoru")
    parser.add_argument("--notebook-name", default=None, help="Notebook adi (varsayilan: '<query> Research')")
    return parser.parse_args()


def run_cmd(cmd, description="", timeout=120):
    """Komutu calistir ve sonucu dondur."""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"UYARI: {result.stderr}", file=sys.stderr)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"HATA: Komut zaman asimina ugradi ({timeout}s)")
        return False, "", "timeout"
    except FileNotFoundError:
        print(f"HATA: Komut bulunamadi: {cmd[0]}")
        return False, "", "not found"


def step1_search(query, max_videos, period, output_dir):
    """Faz 1: YouTube'da arama yap."""
    search_script = os.path.expanduser("~/.claude/skills/yt-search/scripts/search.py")
    output_file = os.path.join(output_dir, "yt-search-results.json")

    ok, stdout, _ = run_cmd(
        ["python", search_script, query,
         "--max-results", str(max_videos),
         "--period", period,
         "--output", output_file],
        description=f"FAZ 1: YouTube'da '{query}' araniyor...",
        timeout=90
    )

    if not ok:
        print("HATA: YouTube arama basarisiz!")
        return None

    # URL dosyasini oku
    urls_file = os.path.join(output_dir, "yt-urls.txt")
    if os.path.exists(urls_file):
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"\n{len(urls)} video URL'si bulundu.")
        return urls
    return None


def step2_create_notebook(notebook_name):
    """Faz 2: NotebookLM notebook olustur."""
    ok, stdout, _ = run_cmd(
        ["notebooklm", "create", notebook_name],
        description=f"FAZ 2: NotebookLM notebook olusturuluyor: '{notebook_name}'"
    )

    if not ok:
        print("HATA: Notebook olusturulamadi!")
        return None

    # Notebook ID'yi stdout'tan cikart
    # notebooklm create genelde notebook_id doner
    notebook_id = stdout.strip().split("\n")[-1].strip() if stdout else None

    # Olusturulan notebook'u aktif yap
    if notebook_id:
        run_cmd(["notebooklm", "use", notebook_id])

    return notebook_id


def step3_load_sources(urls, delay=2.0):
    """Faz 3: Video URL'lerini NotebookLM'e kaynak olarak yukle."""
    print(f"\n{'='*60}")
    print(f"  FAZ 3: {len(urls)} kaynak NotebookLM'e yukleniyor...")
    print(f"{'='*60}")

    success = 0
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url[:55]}...", end=" ")
        ok, _, _ = run_cmd(
            ["notebooklm", "source", "add", url],
            timeout=60
        )
        if ok:
            success += 1
            print("OK")
        else:
            print("HATA")

        if i < len(urls):
            time.sleep(delay)

    print(f"\n  {success}/{len(urls)} kaynak basariyla yuklendi.")
    return success > 0


def step4_analyze(query):
    """Faz 4: NotebookLM'de analiz yap."""
    questions = [
        f"Based on all the sources, what are the most important insights about {query}?",
        f"What are the top recommended strategies, tools, or approaches mentioned across the videos?",
    ]

    print(f"\n{'='*60}")
    print(f"  FAZ 4: NotebookLM analiz yapiliyor...")
    print(f"{'='*60}")

    for q in questions:
        print(f"\n  Soru: {q}")
        ok, stdout, _ = run_cmd(
            ["notebooklm", "ask", q],
            timeout=120
        )
        if ok and stdout:
            print(f"  Cevap: {stdout[:500]}")


def step5_generate(output_type, output_dir):
    """Faz 5: Icerik uret ve indir."""
    generators = {
        "infographic": {
            "generate": ["notebooklm", "generate", "infographic", "--orientation", "portrait", "--detail", "detailed", "--wait"],
            "download": ["notebooklm", "download", "infographic", os.path.join(output_dir, "infographic.png")],
        },
        "audio": {
            "generate": ["notebooklm", "generate", "audio", "make it engaging and insightful", "--format", "deep-dive", "--wait"],
            "download": ["notebooklm", "download", "audio", os.path.join(output_dir, "podcast.mp3")],
        },
        "video": {
            "generate": ["notebooklm", "generate", "video", "overview", "--style", "whiteboard", "--wait"],
            "download": ["notebooklm", "download", "video", os.path.join(output_dir, "video.mp4")],
        },
        "mind-map": {
            "generate": ["notebooklm", "generate", "mind-map", "--wait"],
            "download": ["notebooklm", "download", "mind-map", os.path.join(output_dir, "mindmap.json")],
        },
        "slide-deck": {
            "generate": ["notebooklm", "generate", "slide-deck", "--format", "detailed", "--length", "12", "--wait"],
            "download": ["notebooklm", "download", "slide-deck", os.path.join(output_dir, "slides.pptx"), "--format", "pptx"],
        },
        "flashcards": {
            "generate": ["notebooklm", "generate", "flashcards", "--quantity", "more", "--wait"],
            "download": ["notebooklm", "download", "flashcards", os.path.join(output_dir, "flashcards.md"), "--format", "markdown"],
        },
        "quiz": {
            "generate": ["notebooklm", "generate", "quiz", "--quantity", "more", "--difficulty", "hard", "--wait"],
            "download": ["notebooklm", "download", "quiz", os.path.join(output_dir, "quiz.md"), "--format", "markdown"],
        },
        "report": {
            "generate": ["notebooklm", "generate", "report", "--template", "study-guide", "--wait"],
            "download": ["notebooklm", "download", "report", os.path.join(output_dir, "report.md")],
        },
    }

    if output_type == "all":
        types_to_generate = list(generators.keys())
    else:
        types_to_generate = [output_type]

    print(f"\n{'='*60}")
    print(f"  FAZ 5: Icerik uretiliyor: {', '.join(types_to_generate)}")
    print(f"{'='*60}")

    os.makedirs(output_dir, exist_ok=True)

    for t in types_to_generate:
        gen = generators[t]
        print(f"\n  >> {t} uretiliyor...")
        ok, _, _ = run_cmd(gen["generate"], timeout=300)
        if ok:
            print(f"  >> {t} indiriliyor...")
            run_cmd(gen["download"], timeout=120)
        else:
            print(f"  >> {t} uretimi basarisiz, devam ediliyor...")


def main():
    args = parse_args()
    notebook_name = args.notebook_name or f"{args.query} Research"
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'#'*60}")
    print(f"  YouTube + NotebookLM Pipeline")
    print(f"  Konu: {args.query}")
    print(f"  Cikti: {args.output_type}")
    print(f"{'#'*60}")

    # Faz 1: YouTube Arama
    urls = step1_search(args.query, args.max_videos, args.period, output_dir)
    if not urls:
        print("\nPipeline durdu: Video bulunamadi.")
        sys.exit(1)

    # Faz 2: Notebook Olustur
    notebook_id = step2_create_notebook(notebook_name)

    # Faz 3: Kaynaklari Yukle
    step3_load_sources(urls)

    # Faz 4: Analiz
    step4_analyze(args.query)

    # Faz 5: Icerik Uret
    step5_generate(args.output_type, output_dir)

    print(f"\n{'#'*60}")
    print(f"  Pipeline tamamlandi!")
    print(f"  Ciktilar: {output_dir}/")
    print(f"{'#'*60}")


if __name__ == "__main__":
    main()
