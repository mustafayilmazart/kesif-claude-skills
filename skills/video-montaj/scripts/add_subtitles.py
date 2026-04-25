#!/usr/bin/env python3
"""
SRT Altyazi Yakma Araci
Video uzerine SRT formatindaki altyazilari hard-sub olarak yakar.
Turkce karakter destegi mevcuttur.
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


# Renk haritasi: kullanici dostu isimlerden ASS/SSA renk kodlarina
RENK_HARITASI = {
    "white": "&H00FFFFFF",
    "black": "&H00000000",
    "red": "&H000000FF",
    "green": "&H0000FF00",
    "blue": "&H00FF0000",
    "yellow": "&H0000FFFF",
    "cyan": "&H00FFFF00",
    "magenta": "&H00FF00FF",
    "orange": "&H000080FF",
}

# Konum haritasi: kullanici dostu isimlerden ASS/SSA Alignment degerlerine
KONUM_HARITASI = {
    "bottom": 2,      # Alt orta
    "center": 5,      # Tam orta
    "top": 8,         # Ust orta
}


def renk_kodu_al(renk_adi):
    """Renk adini ASS/SSA formatindaki renk koduna donusturur."""
    renk = renk_adi.lower()
    if renk in RENK_HARITASI:
        return RENK_HARITASI[renk]
    # Dogrudan hex kod girilmisse onu kullan
    if renk.startswith("&H"):
        return renk
    print(f"UYARI: Bilinmeyen renk '{renk_adi}', varsayilan beyaz kullaniliyor.")
    return "&H00FFFFFF"


def konum_degeri_al(konum_adi):
    """Konum adini ASS/SSA Alignment degerine donusturur."""
    konum = konum_adi.lower()
    if konum in KONUM_HARITASI:
        return KONUM_HARITASI[konum]
    print(f"UYARI: Bilinmeyen konum '{konum_adi}', varsayilan alt kullaniliyor.")
    return 2


def margin_degeri_al(konum_adi):
    """Konuma gore alt/ust margin degerini belirler."""
    konum = konum_adi.lower()
    if konum == "bottom":
        return 50   # Alttan 50px yukari
    elif konum == "top":
        return 50   # Ustten 50px asagi
    elif konum == "center":
        return 0    # Ortada, margin gereksiz
    return 50


def srt_yolu_hazirla(srt_path):
    """
    SRT dosya yolunu FFmpeg subtitles filtresi icin hazirlar.
    Windows'ta ters slash ve ozel karakterleri escape eder.
    """
    # Windows yol ayiraclarini duz slash yap
    hazir_yol = srt_path.replace("\\", "/")
    # FFmpeg subtitles filtresi icin : ve \ karakterlerini escape et
    hazir_yol = hazir_yol.replace(":", "\\:")
    return hazir_yol


def burn_subtitles(video_path, srt_path, output_path,
                   font_size=42, font_color="white",
                   bg_color="black@0.6", position="bottom"):
    """
    Video uzerine SRT altyazilari hard-sub olarak yakar.

    Args:
        video_path: Girdi video dosyasi
        srt_path: SRT altyazi dosyasi
        output_path: Cikti video dosyasi
        font_size: Yazi boyutu (varsayilan: 42)
        font_color: Yazi rengi (varsayilan: white)
        bg_color: Arka plan rengi ve saydamlik (varsayilan: black@0.6)
        position: Konum -- bottom, center, top (varsayilan: bottom)
    """
    ffmpeg_kontrol()

    if not os.path.exists(video_path):
        print(f"HATA: Video dosyasi bulunamadi: {video_path}")
        sys.exit(1)
    if not os.path.exists(srt_path):
        print(f"HATA: Altyazi dosyasi bulunamadi: {srt_path}")
        sys.exit(1)

    # Renk ve konum degerlerini al
    birincil_renk = renk_kodu_al(font_color)
    alignment = konum_degeri_al(position)
    margin_v = margin_degeri_al(position)

    # Arka plan rengi (ASS/SSA BackColour formati)
    # black@0.6 -> %60 opak siyah arka plan
    bg_opacity = "80"  # Varsayilan ~50% opaklik (hex)
    if "@" in bg_color:
        bg_parts = bg_color.split("@")
        opacity_float = float(bg_parts[1])
        # ASS/SSA'da 00=tamamen opak, FF=tamamen saydam (ters mantik)
        bg_opacity = format(int((1 - opacity_float) * 255), "02X")

    arka_plan_renk = f"&H{bg_opacity}000000"

    # SRT yolunu hazirla
    srt_hazir = srt_yolu_hazirla(os.path.abspath(srt_path))

    # Force style dizesi
    force_style = (
        f"FontSize={font_size},"
        f"PrimaryColour={birincil_renk},"
        f"BackColour={arka_plan_renk},"
        f"BorderStyle=4,"
        f"Alignment={alignment},"
        f"MarginV={margin_v},"
        f"Encoding=1"
    )

    # Video filtresi
    video_filtre = f"subtitles={srt_hazir}:force_style='{force_style}'"

    komut = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", video_filtre,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    print(f"Altyazi yakiliyor: {output_path}")
    print(f"  Video: {video_path}")
    print(f"  Altyazi: {srt_path}")
    print(f"  Font boyutu: {font_size}")
    print(f"  Yazi rengi: {font_color}")
    print(f"  Konum: {position}")

    sonuc = subprocess.run(komut, capture_output=True, text=True)

    if sonuc.returncode != 0:
        print(f"HATA: FFmpeg hatasi:\n{sonuc.stderr}")
        sys.exit(1)

    print(f"Altyazili video basariyla olusturuldu: {output_path}")


def main():
    """Ana giris noktasi. Komut satiri argumanlari ile calistirilir."""
    parser = argparse.ArgumentParser(
        description="SRT Altyazi Yakma -- Video uzerine hard-sub altyazi yakar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  %(prog)s --video video.mp4 --srt altyazi.srt --output final.mp4
  %(prog)s --video video.mp4 --srt altyazi.srt --output final.mp4 --font-size 48
  %(prog)s --video video.mp4 --srt altyazi.srt --output final.mp4 --font-color yellow --position center

Desteklenen renkler:
  white, black, red, green, blue, yellow, cyan, magenta, orange

Konum secenekleri:
  bottom  - Alt kisim (varsayilan)
  center  - Orta kisim
  top     - Ust kisim
        """,
    )

    parser.add_argument("--video", required=True, help="Girdi video dosyasi")
    parser.add_argument("--srt", required=True, help="SRT altyazi dosyasi")
    parser.add_argument("--output", required=True, help="Cikti video dosyasi")
    parser.add_argument(
        "--font-size", type=int, default=42,
        help="Yazi boyutu (varsayilan: 42)",
    )
    parser.add_argument(
        "--font-color", default="white",
        help="Yazi rengi (varsayilan: white)",
    )
    parser.add_argument(
        "--bg-color", default="black@0.6",
        help="Arka plan rengi ve saydamlik (varsayilan: black@0.6)",
    )
    parser.add_argument(
        "--position", choices=["bottom", "center", "top"], default="bottom",
        help="Altyazi konumu (varsayilan: bottom)",
    )

    args = parser.parse_args()

    burn_subtitles(
        video_path=args.video,
        srt_path=args.srt,
        output_path=args.output,
        font_size=args.font_size,
        font_color=args.font_color,
        bg_color=args.bg_color,
        position=args.position,
    )


if __name__ == "__main__":
    main()
