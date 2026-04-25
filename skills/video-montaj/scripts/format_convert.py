#!/usr/bin/env python3
"""
Instagram Format Donusturme Araci
Videolari farkli sosyal medya formatlarina donusturur.
Desteklenen formatlar: reels (9:16), square (1:1), portrait (4:5)
"""

import argparse
import os
import subprocess
import sys


def ffmpeg_kontrol():
    """FFmpeg'in sistemde yuklu olup olmadigini kontrol eder."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        print("HATA: FFmpeg bulunamadi. Lutfen FFmpeg'i yukleyin ve PATH'e ekleyin.")
        sys.exit(1)


def video_suresi_al(video_path):
    """Video dosyasinin suresini saniye olarak dondurur."""
    sonuc = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True,
        text=True,
    )
    return float(sonuc.stdout.strip())


def format_donustur(input_path, output_path, genislik, yukseklik, mode="pad", max_sure=None):
    """
    Videoyu belirtilen boyutlara donusturur.

    Args:
        input_path: Girdi video dosyasi
        output_path: Cikti video dosyasi
        genislik: Hedef genislik (piksel)
        yukseklik: Hedef yukseklik (piksel)
        mode: 'pad' (siyah kenar) veya 'crop' (ortadan kes)
        max_sure: Maksimum sure (saniye), None ise sinir yok
    """
    ffmpeg_kontrol()

    if not os.path.exists(input_path):
        print(f"HATA: Video dosyasi bulunamadi: {input_path}")
        sys.exit(1)

    if mode == "pad":
        # Padding modu: video oranini koru, siyah kenarlik ekle
        video_filtre = (
            f"scale={genislik}:{yukseklik}:force_original_aspect_ratio=decrease,"
            f"pad={genislik}:{yukseklik}:(ow-iw)/2:(oh-ih)/2:color=black"
        )
    elif mode == "crop":
        # Crop modu: ortadan keserek tam dolum
        video_filtre = (
            f"scale={genislik}:{yukseklik}:force_original_aspect_ratio=increase,"
            f"crop={genislik}:{yukseklik}"
        )
    else:
        print(f"HATA: Gecersiz mod: {mode}. 'pad' veya 'crop' kullanin.")
        sys.exit(1)

    komut = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", video_filtre,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
    ]

    if max_sure is not None:
        komut.extend(["-t", str(max_sure)])

    komut.append(output_path)

    return komut


def to_reels(input_path, output_path, mode="pad"):
    """
    Videoyu Instagram Reels formatina (9:16, 1080x1920) donusturur.
    Maksimum 90 saniye siniri uygulanir.
    """
    sure = video_suresi_al(input_path)
    max_sure = min(sure, 90)

    if sure > 90:
        print("UYARI: Video 90 saniyeden uzun, Reels sinirinda kesilecek.")

    komut = format_donustur(input_path, output_path, 1080, 1920, mode, max_sure)

    print(f"Reels formatina donusturuluyor: {output_path}")
    print(f"  Boyut: 1080x1920 (9:16)")
    print(f"  Mod: {mode}")
    print(f"  Sure: {max_sure:.1f} saniye")

    sonuc = subprocess.run(komut, capture_output=True, text=True)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Reels videosu basariyla olusturuldu: {output_path}")


def to_square(input_path, output_path, mode="pad"):
    """
    Videoyu kare formata (1:1, 1080x1080) donusturur.
    Instagram feed postlari icin idealdir.
    """
    komut = format_donustur(input_path, output_path, 1080, 1080, mode)

    print(f"Kare formata donusturuluyor: {output_path}")
    print(f"  Boyut: 1080x1080 (1:1)")
    print(f"  Mod: {mode}")

    sonuc = subprocess.run(komut, capture_output=True, text=True)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Kare video basariyla olusturuldu: {output_path}")


def to_portrait(input_path, output_path, mode="pad"):
    """
    Videoyu portre formata (4:5, 1080x1350) donusturur.
    Instagram feed'de maksimum alan kaplar.
    """
    komut = format_donustur(input_path, output_path, 1080, 1350, mode)

    print(f"Portre formata donusturuluyor: {output_path}")
    print(f"  Boyut: 1080x1350 (4:5)")
    print(f"  Mod: {mode}")

    sonuc = subprocess.run(komut, capture_output=True, text=True)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Portre video basariyla olusturuldu: {output_path}")


def main():
    """Ana giris noktasi. Komut satiri argumanlari ile calistirilir."""
    parser = argparse.ArgumentParser(
        description="Instagram Format Donusturme -- Videolari sosyal medya formatlarina donusturur",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  %(prog)s reels --input video.mp4 --output reels.mp4
  %(prog)s square --input video.mp4 --output square.mp4 --mode crop
  %(prog)s portrait --input video.mp4 --output portrait.mp4 --mode pad

Modlar:
  pad   - Siyah kenarlik ekler, icerik kaybi olmaz (varsayilan)
  crop  - Ortadan keserek tam dolum saglar
        """,
    )

    alt_komutlar = parser.add_subparsers(dest="format", help="Hedef format")

    # Reels formati
    reels_parser = alt_komutlar.add_parser("reels", help="9:16 Reels (1080x1920, max 90sn)")
    reels_parser.add_argument("--input", required=True, help="Girdi video dosyasi")
    reels_parser.add_argument("--output", required=True, help="Cikti video dosyasi")
    reels_parser.add_argument(
        "--mode", choices=["pad", "crop"], default="pad",
        help="Boyutlandirma modu (varsayilan: pad)",
    )

    # Kare format
    square_parser = alt_komutlar.add_parser("square", help="1:1 Kare (1080x1080)")
    square_parser.add_argument("--input", required=True, help="Girdi video dosyasi")
    square_parser.add_argument("--output", required=True, help="Cikti video dosyasi")
    square_parser.add_argument(
        "--mode", choices=["pad", "crop"], default="pad",
        help="Boyutlandirma modu (varsayilan: pad)",
    )

    # Portre format
    portrait_parser = alt_komutlar.add_parser("portrait", help="4:5 Portre (1080x1350)")
    portrait_parser.add_argument("--input", required=True, help="Girdi video dosyasi")
    portrait_parser.add_argument("--output", required=True, help="Cikti video dosyasi")
    portrait_parser.add_argument(
        "--mode", choices=["pad", "crop"], default="pad",
        help="Boyutlandirma modu (varsayilan: pad)",
    )

    args = parser.parse_args()

    if args.format is None:
        parser.print_help()
        sys.exit(1)

    if args.format == "reels":
        to_reels(args.input, args.output, args.mode)
    elif args.format == "square":
        to_square(args.input, args.output, args.mode)
    elif args.format == "portrait":
        to_portrait(args.input, args.output, args.mode)


if __name__ == "__main__":
    main()
