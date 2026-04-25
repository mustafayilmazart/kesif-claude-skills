#!/usr/bin/env python3
"""
NotebookLM Login - Mevcut Edge profilini kullanan versiyon.
Edge'deki mevcut Google oturumunu kullanir, yeniden giris gerekmez.

ONEMLI: Bu script calistirilmadan once Edge tamamen kapatilmali!
"""

import os
import json
import time
import sys
from playwright.sync_api import sync_playwright


def main():
    nlm_dir = os.path.join(os.path.expanduser("~"), ".notebooklm")
    os.makedirs(nlm_dir, exist_ok=True)
    storage_path = os.path.join(nlm_dir, "storage_state.json")

    edge_user_data = os.path.join(
        os.path.expanduser("~"),
        "AppData", "Local", "Microsoft", "Edge", "User Data"
    )

    if not os.path.exists(edge_user_data):
        print("HATA: Edge profil dizini bulunamadi!")
        sys.exit(1)

    print("=" * 50)
    print("  ONEMLI: Edge tarayicisini tamamen kapat!")
    print("  (Sistem tepsisindeki Edge ikonunu da kapat)")
    print("=" * 50)
    print()
    print("Edge profili ile NotebookLM'e baglaniliyor...")

    with sync_playwright() as p:
        # Mevcut Edge profilini persistent context olarak ac
        context = p.chromium.launch_persistent_context(
            user_data_dir=edge_user_data,
            channel="msedge",
            headless=False,
            slow_mo=50,
            args=["--profile-directory=Default"],
        )

        page = context.new_page()
        page.set_default_timeout(120000)

        print("NotebookLM'e gidiliyor...")
        page.goto("https://notebooklm.google.com", wait_until="domcontentloaded", timeout=120000)
        print(f"URL: {page.url}")

        # Giris kontrolu
        max_wait = 120
        start = time.time()
        logged_in = False

        while time.time() - start < max_wait:
            url = page.url
            if "notebooklm.google.com" in url and "accounts.google.com" not in url:
                # Biraz bekle sayfa yuklensin
                time.sleep(3)
                logged_in = True
                break

            time.sleep(2)
            elapsed = int(time.time() - start)
            if elapsed % 10 == 0:
                print(f"  Bekleniyor... ({elapsed}s)")

        if logged_in:
            # Sayfa tam yuklensin
            time.sleep(5)
            print(f"\nGiris basarili! URL: {page.url}")

            # Storage state kaydet
            state = context.storage_state()
            with open(storage_path, "w") as f:
                json.dump(state, f, indent=2)
            print(f"Storage kaydedildi: {storage_path}")

            # notebooklm-py icin APPDATA'ya da kopyala
            appdata_dir = os.path.join(os.environ.get("APPDATA", ""), "notebooklm")
            if appdata_dir:
                os.makedirs(appdata_dir, exist_ok=True)
                alt_path = os.path.join(appdata_dir, "storage_state.json")
                with open(alt_path, "w") as f:
                    json.dump(state, f, indent=2)
                print(f"Yedek kaydedildi: {alt_path}")

            # NOTEBOOKLM_HOME icin de kaydet
            config_dir = os.path.join(os.path.expanduser("~"), ".config", "notebooklm")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "storage_state.json")
            with open(config_path, "w") as f:
                json.dump(state, f, indent=2)
            print(f"Config kaydedildi: {config_path}")

        else:
            print("\nGiris tamamlanamadi. Edge'de Google'a giris yapmis oldugundan emin ol.")
            print("Edge'i tamamen kapatip tekrar dene.")

        context.close()


if __name__ == "__main__":
    main()
