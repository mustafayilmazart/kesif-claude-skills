#!/usr/bin/env python3
"""
NotebookLM Login - Edge profilini kopyalayarak kullanan versiyon.
Edge acik kalabilir, profil kopyalanir.
"""

import os
import json
import time
import shutil
import tempfile
import sys
from playwright.sync_api import sync_playwright


def copy_edge_profile():
    """Edge profilinin cookie ve storage verilerini gecici dizine kopyala."""
    edge_data = os.path.join(
        os.path.expanduser("~"),
        "AppData", "Local", "Microsoft", "Edge", "User Data"
    )

    if not os.path.exists(edge_data):
        return None

    # Gecici dizin olustur
    tmp_dir = os.path.join(tempfile.gettempdir(), "nlm_edge_profile")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)

    os.makedirs(tmp_dir, exist_ok=True)
    default_src = os.path.join(edge_data, "Default")
    default_dst = os.path.join(tmp_dir, "Default")
    os.makedirs(default_dst, exist_ok=True)

    # Sadece gerekli dosyalari kopyala
    files_to_copy = [
        "Cookies", "Cookies-journal",
        "Login Data", "Login Data-journal",
        "Web Data", "Web Data-journal",
        "Preferences", "Secure Preferences",
        "Local State",
    ]

    for f in files_to_copy:
        src = os.path.join(default_src, f)
        if os.path.exists(src):
            try:
                shutil.copy2(src, os.path.join(default_dst, f))
            except (PermissionError, OSError):
                pass

    # Local State ust dizinde
    ls_src = os.path.join(edge_data, "Local State")
    if os.path.exists(ls_src):
        try:
            shutil.copy2(ls_src, os.path.join(tmp_dir, "Local State"))
        except (PermissionError, OSError):
            pass

    return tmp_dir


def main():
    nlm_dir = os.path.join(os.path.expanduser("~"), ".notebooklm")
    os.makedirs(nlm_dir, exist_ok=True)
    storage_path = os.path.join(nlm_dir, "storage_state.json")

    print("Edge profili kopyalaniyor...")
    tmp_profile = copy_edge_profile()

    if not tmp_profile:
        print("HATA: Edge profili bulunamadi!")
        sys.exit(1)

    print(f"Profil kopyalandi: {tmp_profile}")
    print("Tarayici aciliyor...\n")
    print("Google hesabini sec ve NotebookLM'e giris yap.")
    print("Script otomatik algilayacak.\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=tmp_profile,
            channel="msedge",
            headless=False,
            slow_mo=50,
            args=["--profile-directory=Default"],
            timeout=120000,
        )

        page = context.new_page()
        page.set_default_timeout(120000)

        print("NotebookLM'e gidiliyor...")
        page.goto("https://notebooklm.google.com", wait_until="domcontentloaded", timeout=120000)
        print(f"URL: {page.url}")

        # Giris kontrolu - 5 dakika bekle
        max_wait = 300
        start = time.time()
        logged_in = False

        while time.time() - start < max_wait:
            url = page.url
            if "notebooklm.google.com" in url and "accounts.google.com" not in url:
                time.sleep(5)
                logged_in = True
                break
            time.sleep(2)
            elapsed = int(time.time() - start)
            if elapsed % 15 == 0:
                print(f"  Bekleniyor... ({elapsed}s) - Giris yap!")

        if logged_in:
            print(f"\nGiris basarili! URL: {page.url}")

            state = context.storage_state()
            with open(storage_path, "w") as f:
                json.dump(state, f, indent=2)
            print(f"Storage kaydedildi: {storage_path}")

            # Diger lokasyonlara da kaydet
            for d in [
                os.path.join(os.environ.get("APPDATA", ""), "notebooklm"),
                os.path.join(os.path.expanduser("~"), ".config", "notebooklm"),
            ]:
                if d:
                    os.makedirs(d, exist_ok=True)
                    p2 = os.path.join(d, "storage_state.json")
                    with open(p2, "w") as f:
                        json.dump(state, f, indent=2)
                    print(f"Yedek: {p2}")
        else:
            print("\nZaman asimi. Tekrar dene.")

        context.close()

    # Gecici profili temizle
    if tmp_profile and os.path.exists(tmp_profile):
        shutil.rmtree(tmp_profile, ignore_errors=True)


if __name__ == "__main__":
    main()
