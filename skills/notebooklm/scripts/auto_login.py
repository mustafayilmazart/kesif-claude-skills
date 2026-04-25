#!/usr/bin/env python3
"""
NotebookLM Auto Login
Resmi notebooklm login komutunu sarar, giris tamamlaninca otomatik Enter gonderir.
"""

import subprocess
import time
import os
import json
import sys


def check_login_complete():
    """Storage state dosyasinin varligini ve gecerliligini kontrol et."""
    paths = [
        os.path.join(os.path.expanduser("~"), ".notebooklm", "storage_state.json"),
        os.path.join(os.path.expanduser("~"), ".notebooklm", "browser_profile", "Default", "Cookies"),
    ]
    for p in paths:
        if os.path.exists(p):
            # Dosya son 5 dakika icinde degismis mi?
            mtime = os.path.getmtime(p)
            if time.time() - mtime < 300:
                return True
    return False


def main():
    print("=" * 55)
    print("  NotebookLM Giris")
    print("=" * 55)
    print()
    print("Tarayici acilacak. Google hesabinla giris yap.")
    print("Giris tamamlandiktan sonra script otomatik kaydedecek.")
    print()

    # notebooklm login komutunu baslat (stdin'e ENTER gondermek icin PIPE kullan)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.Popen(
        [sys.executable, "-m", "notebooklm", "login"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
    )

    # Tarayicinin acilmasini bekle
    time.sleep(5)
    print("Tarayici acildi. Google ile giris yap...")
    print("(5 dakika bekleniyor...)\n")

    # Giris tamamlanana kadar bekle
    max_wait = 300
    start = time.time()

    while time.time() - start < max_wait:
        elapsed = int(time.time() - start)

        # Her 10 saniyede durum kontrolu
        if elapsed % 15 == 0 and elapsed > 0:
            print(f"  Bekleniyor... ({elapsed}s)")

            # Browser profil dizininde Cookies varsa giris yapilmis olabilir
            profile_dir = os.path.join(
                os.path.expanduser("~"), ".notebooklm", "browser_profile"
            )
            if os.path.exists(profile_dir):
                # Default dizinindeki dosya sayisina bak
                default_dir = os.path.join(profile_dir, "Default")
                if os.path.exists(default_dir):
                    files = os.listdir(default_dir)
                    # Network dizini olusmussa giris yapilmis demektir
                    if "Network" in files or len(files) > 20:
                        print(f"  Profil verileri algilandi ({len(files)} dosya)")

        time.sleep(2)

        # Process bitmis mi?
        if proc.poll() is not None:
            break

    # ENTER gonder ve kaydet
    print("\nENTER gonderiliyor...")
    try:
        proc.stdin.write("\n")
        proc.stdin.flush()
    except (BrokenPipeError, OSError):
        pass

    # Biraz bekle kaydedsin
    time.sleep(3)

    # Process'i durdur
    try:
        proc.terminate()
    except Exception:
        pass

    # Ciktiyi oku
    try:
        output = proc.stdout.read()
        if output:
            print(f"Cikti: {output[:500]}")
    except Exception:
        pass

    # Storage state kontrol
    storage_path = os.path.join(os.path.expanduser("~"), ".notebooklm", "storage_state.json")
    if os.path.exists(storage_path):
        print(f"\nBasarili! Storage kaydedildi: {storage_path}")

        # Diger konumlara kopyala
        state = json.load(open(storage_path))
        for d in [
            os.path.join(os.environ.get("APPDATA", ""), "notebooklm"),
            os.path.join(os.path.expanduser("~"), ".config", "notebooklm"),
        ]:
            if d:
                os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, "storage_state.json"), "w") as f:
                    json.dump(state, f, indent=2)
        print("Yedekler olusturuldu.")
    else:
        print("\nStorage dosyasi bulunamadi.")
        print("Manuel olarak dene:")
        print("  1. Terminal'de calistir: python -m notebooklm login")
        print("  2. Tarayicide Google'a giris yap")
        print("  3. Terminal'de ENTER bas")


if __name__ == "__main__":
    main()
