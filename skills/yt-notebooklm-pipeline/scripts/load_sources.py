#!/usr/bin/env python3
"""
NotebookLM'e YouTube URL'lerini toplu kaynak olarak yukle.
.output/yt-urls.txt dosyasindan URL'leri okur ve aktif notebook'a ekler.
"""

import subprocess
import sys
import time
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="NotebookLM'e toplu kaynak yukleme")
    parser.add_argument("urls_file", help="URL listesi dosyasi (her satirda bir URL)")
    parser.add_argument("--max-sources", type=int, default=50, help="Maksimum kaynak sayisi (varsayilan: 50)")
    parser.add_argument("--delay", type=float, default=2.0, help="Her kaynak arasi bekleme suresi (saniye)")
    return parser.parse_args()


def load_urls(file_path):
    """Dosyadan URL'leri oku."""
    urls = []
    with open(file_path, "r") as f:
        for line in f:
            url = line.strip()
            if url and url.startswith("http"):
                urls.append(url)
    return urls


def add_source(url):
    """Tek bir URL'yi NotebookLM'e kaynak olarak ekle."""
    try:
        result = subprocess.run(
            ["notebooklm", "source", "add", url],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Zaman asimi"
    except FileNotFoundError:
        return False, "notebooklm komutu bulunamadi. 'pip install notebooklm-py' ile kurun."


def main():
    args = parse_args()

    urls = load_urls(args.urls_file)
    if not urls:
        print(f"Hata: {args.urls_file} dosyasinda gecerli URL bulunamadi.")
        sys.exit(1)

    # Limitle
    urls = urls[:args.max_sources]
    total = len(urls)

    print(f"\n{total} URL NotebookLM'e kaynak olarak yuklenecek...")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{total}] Ekleniyor: {url[:60]}...")
        ok, msg = add_source(url)

        if ok:
            success_count += 1
            print(f"  -> Basarili")
        else:
            fail_count += 1
            print(f"  -> Hata: {msg}")

        # Rate limiting
        if i < total:
            time.sleep(args.delay)

    print("-" * 60)
    print(f"\nSonuc: {success_count} basarili, {fail_count} hatali (toplam {total})")

    if success_count > 0:
        print("\nKaynaklar yuklendi! Simdi analiz yapabilirsiniz:")
        print('  notebooklm ask "Based on all sources, what are the key insights?"')


if __name__ == "__main__":
    main()
