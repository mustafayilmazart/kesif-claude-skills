#!/usr/bin/env python3
"""
NotebookLM Login Script
Tarayici acar, Google girisini bekler, storage state'i kaydeder.
"""

import os
import json
import time
from playwright.sync_api import sync_playwright


def main():
    nlm_dir = os.path.join(os.path.expanduser("~"), ".notebooklm")
    os.makedirs(nlm_dir, exist_ok=True)
    storage_path = os.path.join(nlm_dir, "storage_state.json")

    print("Tarayici aciliyor...")
    print("Google hesabinla giris yap.")
    print("NotebookLM ana sayfasi gorunene kadar beklenecek...\n")

    with sync_playwright() as p:
        # Mevcut Edge/Chrome profilini kullan (Google girisini tekrar yapmaya gerek kalmasin)
        import shutil
        edge_path = shutil.which("msedge") or "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
        chrome_path = shutil.which("chrome") or "C:/Program Files/Google/Chrome/Application/chrome.exe"

        # Oncelikle Edge, yoksa Chrome, yoksa Chromium kullan
        if os.path.exists(edge_path):
            browser = p.chromium.launch(headless=False, slow_mo=100, channel="msedge")
            print("Edge tarayicisi kullaniliyor...")
        elif os.path.exists(chrome_path):
            browser = p.chromium.launch(headless=False, slow_mo=100, channel="chrome")
            print("Chrome tarayicisi kullaniliyor...")
        else:
            browser = p.chromium.launch(headless=False, slow_mo=100)
            print("Chromium tarayicisi kullaniliyor...")

        context = browser.new_context()
        page = context.new_page()

        # NotebookLM'e git
        page.set_default_timeout(120000)  # 2 dakika timeout
        page.goto("https://notebooklm.google.com", wait_until="domcontentloaded", timeout=120000)
        print(f"Sayfa yuklendi: {page.url}")

        # Giris tamamlanana kadar bekle (max 5 dakika)
        max_wait = 300  # 5 dakika
        start = time.time()
        logged_in = False

        while time.time() - start < max_wait:
            current_url = page.url
            # Giris basarili oldugunda URL notebooklm.google.com icersin ve login/accounts sayfasindan cikmis olsun
            if "notebooklm.google.com" in current_url and "accounts.google.com" not in current_url:
                # Sayfada notebook listesi veya olusturma butonu var mi kontrol et
                try:
                    # Ana sayfa yuklendiginde genelde "Create notebook" veya notebook listesi gorunur
                    page.wait_for_selector('text=Create', timeout=5000)
                    logged_in = True
                    break
                except Exception:
                    pass

                try:
                    page.wait_for_selector('text=New notebook', timeout=3000)
                    logged_in = True
                    break
                except Exception:
                    pass

                try:
                    # Turkce arayuz icin
                    page.wait_for_selector('text=Not defteri', timeout=3000)
                    logged_in = True
                    break
                except Exception:
                    pass

                # URL dogru ama element bulunamadi, yine de kaydedelim
                if "notebooklm.google.com/notebook" in current_url or current_url == "https://notebooklm.google.com/":
                    logged_in = True
                    break

            time.sleep(2)
            elapsed = int(time.time() - start)
            if elapsed % 10 == 0:
                print(f"  Bekleniyor... ({elapsed}s) - {current_url[:60]}")

        if logged_in:
            # Storage state'i kaydet
            state = context.storage_state()
            with open(storage_path, "w") as f:
                json.dump(state, f, indent=2)
            print(f"\nGiris basarili!")
            print(f"Storage kaydedildi: {storage_path}")

            # notebooklm-py'nin beklediyi yere de kopyala
            alt_dirs = [
                os.path.join(os.path.expanduser("~"), ".config", "notebooklm"),
                os.path.join(os.environ.get("APPDATA", ""), "notebooklm") if os.environ.get("APPDATA") else None,
            ]
            for d in alt_dirs:
                if d:
                    os.makedirs(d, exist_ok=True)
                    alt_path = os.path.join(d, "storage_state.json")
                    with open(alt_path, "w") as f:
                        json.dump(state, f, indent=2)
                    print(f"Yedek kaydedildi: {alt_path}")
        else:
            print("\nZaman asimi: 5 dakika icinde giris yapilamadi.")
            print("Tekrar denemek icin: python ~/.claude/skills/notebooklm/scripts/login.py")

        browser.close()


if __name__ == "__main__":
    main()
