#!/usr/bin/env python3
"""
YouTube Video Arama Araci
yt-dlp kullanarak YouTube'da video arar ve metadata ceker.
"""

import subprocess
import json
import sys
import argparse
import os
from datetime import datetime, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description="YouTube video arama araci")
    parser.add_argument("query", help="Arama terimi")
    parser.add_argument("--max-results", type=int, default=20, help="Maksimum sonuc sayisi (varsayilan: 20)")
    parser.add_argument("--period", default="6m", choices=["1m", "3m", "6m", "1y", "all"], help="Zaman filtresi (varsayilan: 6m)")
    parser.add_argument("--sort", default="relevance", choices=["views", "date", "relevance"], help="Siralama (varsayilan: relevance)")
    parser.add_argument("--output", default=None, help="Cikti dosyasi yolu (JSON)")
    return parser.parse_args()


def get_cutoff_date(period):
    """Zaman filtresine gore kesme tarihini hesapla."""
    now = datetime.now()
    period_map = {
        "1m": timedelta(days=30),
        "3m": timedelta(days=90),
        "6m": timedelta(days=180),
        "1y": timedelta(days=365),
    }
    if period == "all":
        return None
    return now - period_map.get(period, timedelta(days=180))


def format_views(views):
    """Goruntulenme sayisini formatla."""
    if views is None:
        return "N/A"
    if views >= 1_000_000:
        return f"{views/1_000_000:.1f}M"
    if views >= 1_000:
        return f"{views/1_000:.1f}K"
    return str(views)


def format_duration(seconds):
    """Sureyi mm:ss formatina cevir."""
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def search_youtube(query, max_results=20, period="6m", sort="relevance"):
    """YouTube'da arama yap ve sonuclari dondur."""
    # yt-dlp ile arama
    search_count = max_results * 3  # Filtreleme sonrasi yeterli sonuc icin fazla cek

    cmd = [
        sys.executable, "-m", "yt_dlp",
        f"ytsearch{search_count}:{query}",
        "--dump-json",
        "--flat-playlist",
        "--no-warnings",
        "--quiet",
    ]

    print(f"Searching YouTube for: \"{query}\" (top {max_results} results, last {period})...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
    except subprocess.TimeoutExpired:
        print("Error: Arama zaman asimina ugradi.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: yt-dlp bulunamadi. 'pip install yt-dlp' ile kurun.")
        sys.exit(1)

    if result.returncode != 0 and not result.stdout:
        print(f"Error: yt-dlp hatasi: {result.stderr}")
        sys.exit(1)

    # JSON satirlarini parse et
    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            videos.append(data)
        except json.JSONDecodeError:
            continue

    # Zaman filtreleme
    cutoff = get_cutoff_date(period)
    filtered_videos = []
    filtered_count = 0

    for v in videos:
        upload_date = v.get("upload_date")
        if cutoff and upload_date:
            try:
                vid_date = datetime.strptime(upload_date, "%Y%m%d")
                if vid_date < cutoff:
                    filtered_count += 1
                    continue
            except ValueError:
                pass
        filtered_videos.append(v)

    if filtered_count > 0:
        print(f"(Filtered out {filtered_count} video(s) older than {period})")

    # Siralama
    if sort == "views":
        filtered_videos.sort(key=lambda x: x.get("view_count", 0) or 0, reverse=True)
    elif sort == "date":
        filtered_videos.sort(key=lambda x: x.get("upload_date", ""), reverse=True)

    # Limitle
    return filtered_videos[:max_results]


def print_results(videos):
    """Sonuclari tablo formatinda yazdir."""
    if not videos:
        print("\nHicbir sonuc bulunamadi.")
        return

    # Tablo basliklari
    print(f"\n{'#':<4} {'URL':<48} {'Channel':<25} {'Views':<8} {'Length':<8} {'Date':<10}")
    print("-" * 103)

    for i, v in enumerate(videos, 1):
        vid_id = v.get("id", v.get("url", ""))
        if not vid_id.startswith("http"):
            url = f"https://youtube.com/watch?v={vid_id}"
        else:
            url = vid_id

        channel = v.get("channel", v.get("uploader", "Unknown"))
        if channel and len(channel) > 22:
            channel = channel[:22] + "..."

        views = format_views(v.get("view_count"))
        duration = format_duration(v.get("duration"))

        upload_date = v.get("upload_date", "")
        if upload_date and len(upload_date) == 8:
            try:
                dt = datetime.strptime(upload_date, "%Y%m%d")
                upload_date = dt.strftime("%b %d")
            except ValueError:
                pass

        print(f"{i:<4} {url:<48} {channel:<25} {views:<8} {duration:<8} {upload_date:<10}")


def save_results(videos, output_path):
    """Sonuclari JSON dosyasina kaydet."""
    results = []
    for v in videos:
        vid_id = v.get("id", v.get("url", ""))
        if not vid_id.startswith("http"):
            url = f"https://youtube.com/watch?v={vid_id}"
        else:
            url = vid_id

        results.append({
            "url": url,
            "title": v.get("title", ""),
            "channel": v.get("channel", v.get("uploader", "")),
            "views": v.get("view_count", 0),
            "duration": v.get("duration", 0),
            "upload_date": v.get("upload_date", ""),
            "description": v.get("description", "")[:200] if v.get("description") else "",
        })

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSonuclar kaydedildi: {output_path}")
    return results


def main():
    args = parse_args()

    videos = search_youtube(
        query=args.query,
        max_results=args.max_results,
        period=args.period,
        sort=args.sort,
    )

    print(f"\n* Here are the top {len(videos)} YouTube results for \"{args.query}\" from the last {args.period}:")
    print_results(videos)

    # JSON ciktisi kaydet
    output_path = args.output or ".output/yt-search-results.json"
    results = save_results(videos, output_path)

    # URL listesini de ayri kaydet (notebooklm entegrasyonu icin)
    urls_path = os.path.join(os.path.dirname(output_path), "yt-urls.txt")
    with open(urls_path, "w") as f:
        for r in results:
            f.write(r["url"] + "\n")
    print(f"URL listesi kaydedildi: {urls_path}")


if __name__ == "__main__":
    main()
