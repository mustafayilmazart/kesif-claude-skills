#!/usr/bin/env python3
"""
Video Montaj Motoru
Ses + gorsel dosyalarindan MP4 video uretir.
Desteklenen modlar: image, slideshow, reels
"""

import argparse
import os
import subprocess
import sys
import glob
import math


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


def ses_suresi_al(audio_path):
    """Ses dosyasinin suresini saniye olarak dondurur."""
    sonuc = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        capture_output=True,
        text=True,
    )
    return float(sonuc.stdout.strip())


def create_video_from_audio_image(audio_path, image_path, output_path, resolution="1080x1920"):
    """
    Tek gorsel + ses dosyasindan MP4 video olusturur.
    Gorsel video boyunca sabit kalir, ses bitince video biter.
    """
    ffmpeg_kontrol()

    if not os.path.exists(audio_path):
        print(f"HATA: Ses dosyasi bulunamadi: {audio_path}")
        sys.exit(1)
    if not os.path.exists(image_path):
        print(f"HATA: Gorsel dosyasi bulunamadi: {image_path}")
        sys.exit(1)

    genislik, yukseklik = resolution.split("x")

    komut = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={genislik}:{yukseklik}:force_original_aspect_ratio=decrease,pad={genislik}:{yukseklik}:(ow-iw)/2:(oh-ih)/2",
        "-shortest",
        output_path,
    ]

    print(f"Video olusturuluyor: {output_path}")
    print(f"  Gorsel: {image_path}")
    print(f"  Ses: {audio_path}")
    print(f"  Cozunurluk: {resolution}")

    sonuc = subprocess.run(komut, capture_output=True, text=True)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Video basariyla olusturuldu: {output_path}")


def create_slideshow(images_dir, audio_path, output_path, duration_per_slide=5):
    """
    Birden fazla gorsel + ses dosyasindan slideshow video olusturur.
    Gorseller arasinda fade gecis efekti uygulanir.
    """
    ffmpeg_kontrol()

    if not os.path.exists(audio_path):
        print(f"HATA: Ses dosyasi bulunamadi: {audio_path}")
        sys.exit(1)
    if not os.path.isdir(images_dir):
        print(f"HATA: Gorsel dizini bulunamadi: {images_dir}")
        sys.exit(1)

    # Gorselleri bul ve sirala
    uzantilar = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp")
    gorseller = []
    for uzanti in uzantilar:
        gorseller.extend(glob.glob(os.path.join(images_dir, uzanti)))
    gorseller.sort()

    if not gorseller:
        print(f"HATA: {images_dir} dizininde gorsel bulunamadi.")
        sys.exit(1)

    print(f"{len(gorseller)} gorsel bulundu, slideshow hazirlaniyor...")

    # Ses suresini al
    ses_suresi = ses_suresi_al(audio_path)

    # Her slayt icin sure hesapla (ses suresine gore ayarla)
    toplam_slayt_suresi = len(gorseller) * duration_per_slide
    if toplam_slayt_suresi < ses_suresi:
        # Ses daha uzunsa, slayt suresini uzat
        duration_per_slide = math.ceil(ses_suresi / len(gorseller))
        print(f"  Slayt suresi ses'e gore ayarlandi: {duration_per_slide} saniye")

    # Concat dosyasi olustur
    concat_dosya = output_path + ".concat.txt"
    with open(concat_dosya, "w", encoding="utf-8") as f:
        for gorsel in gorseller:
            # Yolu normalize et
            gorsel_yol = os.path.abspath(gorsel).replace("\\", "/")
            f.write(f"file '{gorsel_yol}'\n")
            f.write(f"duration {duration_per_slide}\n")
        # Son gorseli tekrar ekle (FFmpeg concat gerekliligi)
        son_gorsel = os.path.abspath(gorseller[-1]).replace("\\", "/")
        f.write(f"file '{son_gorsel}'\n")

    # Fade gecisli slideshow komutlari
    fade_sure = 1  # 1 saniyelik fade gecis
    filter_parts = []

    # Her gorsel icin input ekle
    input_args = []
    for i, gorsel in enumerate(gorseller):
        input_args.extend(["-loop", "1", "-t", str(duration_per_slide), "-i", gorsel])

    # Ses inputu
    input_args.extend(["-i", audio_path])

    # Filter complex olustur
    for i in range(len(gorseller)):
        filter_parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"fade=t=in:st=0:d={fade_sure},fade=t=out:st={duration_per_slide - fade_sure}:d={fade_sure}[v{i}]"
        )

    # Videolari birlestir
    concat_inputs = "".join(f"[v{i}]" for i in range(len(gorseller)))
    filter_parts.append(f"{concat_inputs}concat=n={len(gorseller)}:v=1:a=0[vout]")

    filter_complex = ";".join(filter_parts)

    komut = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{len(gorseller)}:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]

    print(f"Slideshow olusturuluyor: {output_path}")
    sonuc = subprocess.run(komut, capture_output=True, text=True)

    # Gecici concat dosyasini sil
    if os.path.exists(concat_dosya):
        os.remove(concat_dosya)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Slideshow basariyla olusturuldu: {output_path}")


def create_reels(audio_path, images, output_path):
    """
    Instagram Reels formati (9:16, 1080x1920) video olusturur.
    Birden fazla gorsel ile calisir, her gorsel esit sure gosterilir.
    """
    ffmpeg_kontrol()

    if not os.path.exists(audio_path):
        print(f"HATA: Ses dosyasi bulunamadi: {audio_path}")
        sys.exit(1)

    for img in images:
        if not os.path.exists(img):
            print(f"HATA: Gorsel dosyasi bulunamadi: {img}")
            sys.exit(1)

    ses_suresi = ses_suresi_al(audio_path)

    # Max 90 saniye (Reels siniri)
    if ses_suresi > 90:
        print("UYARI: Ses 90 saniyeden uzun, Reels sinirinda kesilecek.")
        ses_suresi = 90

    # Her gorsel icin sure
    sure_per_img = ses_suresi / len(images)

    # Filter complex olustur
    input_args = []
    filter_parts = []

    for i, img in enumerate(images):
        input_args.extend(["-loop", "1", "-t", str(sure_per_img), "-i", img])
        filter_parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}]"
        )

    input_args.extend(["-i", audio_path])

    concat_inputs = "".join(f"[v{i}]" for i in range(len(images)))
    filter_parts.append(f"{concat_inputs}concat=n={len(images)}:v=1:a=0[vout]")

    filter_complex = ";".join(filter_parts)

    komut = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{len(images)}:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(ses_suresi),
        "-shortest",
        output_path,
    ]

    print(f"Reels videosu olusturuluyor: {output_path}")
    print(f"  Gorsel sayisi: {len(images)}")
    print(f"  Ses suresi: {ses_suresi:.1f} saniye")
    print(f"  Format: 1080x1920 (9:16)")

    sonuc = subprocess.run(komut, capture_output=True, text=True)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Reels videosu basariyla olusturuldu: {output_path}")


def main():
    """Ana giris noktasi. Komut satiri argumanlari ile calistirilir."""
    parser = argparse.ArgumentParser(
        description="Video Montaj Motoru -- Ses ve gorsellerden MP4 video uretir",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  %(prog)s image --audio ses.mp3 --image foto.jpg --output video.mp4
  %(prog)s slideshow --audio ses.mp3 --images-dir slides/ --output video.mp4
  %(prog)s reels --audio ses.mp3 --images foto1.jpg foto2.jpg --output reels.mp4
        """,
    )

    alt_komutlar = parser.add_subparsers(dest="mod", help="Video olusturma modu")

    # image modu
    image_parser = alt_komutlar.add_parser("image", help="Tek gorsel + ses -> MP4")
    image_parser.add_argument("--audio", required=True, help="Ses dosyasi yolu")
    image_parser.add_argument("--image", required=True, help="Gorsel dosyasi yolu")
    image_parser.add_argument("--output", required=True, help="Cikti video dosyasi yolu")
    image_parser.add_argument(
        "--resolution", default="1080x1920",
        help="Video cozunurlugu (varsayilan: 1080x1920)",
    )

    # slideshow modu
    slide_parser = alt_komutlar.add_parser("slideshow", help="Coklu gorsel + ses -> Slideshow MP4")
    slide_parser.add_argument("--audio", required=True, help="Ses dosyasi yolu")
    slide_parser.add_argument("--images-dir", required=True, help="Gorsellerin bulundugu dizin")
    slide_parser.add_argument("--output", required=True, help="Cikti video dosyasi yolu")
    slide_parser.add_argument(
        "--slide-duration", type=int, default=5,
        help="Her slaytin gosterim suresi (saniye, varsayilan: 5)",
    )

    # reels modu
    reels_parser = alt_komutlar.add_parser("reels", help="9:16 Reels formatinda video")
    reels_parser.add_argument("--audio", required=True, help="Ses dosyasi yolu")
    reels_parser.add_argument("--images", nargs="+", required=True, help="Gorsel dosyalari")
    reels_parser.add_argument("--output", required=True, help="Cikti video dosyasi yolu")

    args = parser.parse_args()

    if args.mod is None:
        parser.print_help()
        sys.exit(1)

    if args.mod == "image":
        create_video_from_audio_image(args.audio, args.image, args.output, args.resolution)
    elif args.mod == "slideshow":
        create_slideshow(args.images_dir, args.audio, args.output, args.slide_duration)
    elif args.mod == "reels":
        create_reels(args.audio, args.images, args.output)


if __name__ == "__main__":
    main()
