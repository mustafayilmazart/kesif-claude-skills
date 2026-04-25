#!/usr/bin/env python3
"""
Udemy Ders Scripti Uretici
NotebookLM analizinden veya konudan Turkce ders scripti olusturur.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_analysis(analysis_path):
    """NotebookLM analiz dosyasini oku."""
    if not os.path.exists(analysis_path):
        print(f"HATA: Analiz dosyasi bulunamadi: {analysis_path}")
        return None

    with open(analysis_path, "r", encoding="utf-8") as f:
        return f.read()


def load_mindmap(mindmap_path):
    """Mind map JSON'dan konu yapisi cikar."""
    if not os.path.exists(mindmap_path):
        return None

    with open(mindmap_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def generate_section_script(section_title, section_content, section_num, total_sections, topic):
    """Bir bolum icin anlatim scripti olustur."""
    # Bu fonksiyon temel bir sablon kullanir.
    # Gercek uygulamada Claude API ile zenginlestirilir.

    intro = ""
    if section_num == 1:
        intro = (
            f"Merhaba, ben Keşif Akademi'den. "
            f"Bu kurs serisinde '{topic}' konusunu derinlemesine inceleyeceğiz. "
            f"Toplam {total_sections} bölümden oluşan bu serinin ilk bölümünde "
            f"'{section_title}' konusunu ele alacağız.\n\n"
        )
    else:
        intro = (
            f"Serimizin {section_num}. bölümüne hoş geldiniz. "
            f"Bu bölümde '{section_title}' konusunu inceleyeceğiz.\n\n"
        )

    # Alt basliklardan icerik olustur
    body = ""
    if isinstance(section_content, list):
        for item in section_content:
            if isinstance(item, dict):
                name = item.get("name", "")
                children = item.get("children", [])
                body += f"{name}. "
                if children:
                    child_names = [c.get("name", "") for c in children if isinstance(c, dict)]
                    if child_names:
                        body += "Bu konu altında " + ", ".join(child_names) + " konularını inceleyeceğiz. "
                body += "\n\n"
            elif isinstance(item, str):
                body += f"{item}. \n\n"

    outro = ""
    if section_num == total_sections:
        outro = (
            f"\nBu bölümle birlikte '{topic}' konusundaki serimizi tamamlamış olduk. "
            f"Umarım faydalı olmuştur. Sorularınız için yorum bölümünü kullanabilirsiniz. "
            f"Keşif Akademi'den sevgilerle.\n"
        )
    else:
        outro = (
            f"\nBu bölümün sonuna geldik. "
            f"Bir sonraki bölümde konumuza devam edeceğiz. "
            f"Görüşmek üzere.\n"
        )

    narration = intro + body + outro
    return narration.strip()


def create_script_from_mindmap(mindmap_data, topic, max_sections=None):
    """Mind map verisinden ders scripti olustur."""
    sections = []
    children = mindmap_data.get("children", [])

    if max_sections and len(children) > max_sections:
        children = children[:max_sections]

    total = len(children)

    for i, child in enumerate(children):
        section_title = child.get("name", f"Bolum {i+1}")
        section_children = child.get("children", [])

        narration = generate_section_script(
            section_title, section_children, i + 1, total, topic
        )

        # Slayt icerikleri
        slides = [{"type": "title", "content": section_title}]
        for sub in section_children:
            if isinstance(sub, dict):
                sub_name = sub.get("name", "")
                sub_children = sub.get("children", [])
                if sub_children:
                    bullet_items = [c.get("name", "") for c in sub_children if isinstance(c, dict)]
                    slides.append({"type": "bullet", "title": sub_name, "content": bullet_items})
                else:
                    slides.append({"type": "text", "content": sub_name})

        # Tahmini sure (kelime sayisindan)
        word_count = len(narration.split())
        duration_min = max(1, round(word_count / 130))  # ~130 kelime/dk konusma hizi

        sections.append({
            "id": i + 1,
            "title": section_title,
            "duration_estimate": f"{duration_min} min",
            "narration": narration,
            "char_count": len(narration),
            "slides": slides,
            "notes": ""
        })

    script = {
        "title": topic,
        "language": "tr",
        "total_sections": len(sections),
        "total_chars": sum(s["char_count"] for s in sections),
        "sections": sections
    }

    return script


def create_script_from_analysis(analysis_text, topic, num_sections=5):
    """Analiz metninden ders scripti olustur."""
    # Basit paragraf bolme
    paragraphs = [p.strip() for p in analysis_text.split("\n\n") if p.strip()]

    # Bolumlere ayir
    chunk_size = max(1, len(paragraphs) // num_sections)
    sections = []

    for i in range(num_sections):
        start = i * chunk_size
        end = start + chunk_size if i < num_sections - 1 else len(paragraphs)
        section_paragraphs = paragraphs[start:end]

        if not section_paragraphs:
            continue

        section_title = f"Bolum {i+1}: {topic}"
        narration = "\n\n".join(section_paragraphs)

        # Giris/cikis ekle
        if i == 0:
            narration = (
                f"Merhaba, ben Keşif Akademi'den. "
                f"Bu derste '{topic}' konusunu inceleyeceğiz.\n\n" + narration
            )

        if i == num_sections - 1:
            narration += (
                f"\n\nBu dersin sonuna geldik. "
                f"Umarım faydalı olmuştur. Keşif Akademi'den sevgilerle."
            )

        word_count = len(narration.split())
        duration_min = max(1, round(word_count / 130))

        sections.append({
            "id": i + 1,
            "title": section_title,
            "duration_estimate": f"{duration_min} min",
            "narration": narration,
            "char_count": len(narration),
            "slides": [{"type": "title", "content": section_title}],
            "notes": ""
        })

    script = {
        "title": topic,
        "language": "tr",
        "total_sections": len(sections),
        "total_chars": sum(s["char_count"] for s in sections),
        "sections": sections
    }

    return script


def main():
    parser = argparse.ArgumentParser(description="Udemy ders scripti uret")
    parser.add_argument("--topic", "-t", required=True, help="Konu basligi")
    parser.add_argument("--analysis", "-a", help="NotebookLM analiz dosyasi (.md)")
    parser.add_argument("--mindmap", "-mm", help="Mind map JSON dosyasi")
    parser.add_argument("--sections", "-s", type=int, default=None, help="Maksimum bolum sayisi")
    parser.add_argument("--output", "-o", required=True, help="Cikti JSON dosyasi")

    args = parser.parse_args()

    script = None

    # Mind map varsa oncelikli kullan
    if args.mindmap:
        print(f"Mind map'ten script uretiliyor: {args.mindmap}")
        mindmap = load_mindmap(args.mindmap)
        if mindmap:
            script = create_script_from_mindmap(mindmap, args.topic, args.sections)

    # Yoksa analiz dosyasindan uret
    if not script and args.analysis:
        print(f"Analiz dosyasindan script uretiliyor: {args.analysis}")
        analysis = load_analysis(args.analysis)
        if analysis:
            num_sections = args.sections or 5
            script = create_script_from_analysis(analysis, args.topic, num_sections)

    if not script:
        print("HATA: --mindmap veya --analysis parametrelerinden biri gerekli!")
        sys.exit(1)

    # Kaydet
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    print(f"\nScript olusturuldu: {args.output}")
    print(f"Konu: {script['title']}")
    print(f"Bolum sayisi: {script['total_sections']}")
    print(f"Toplam karakter: {script['total_chars']:,}")
    print(f"\nBolumler:")
    for s in script["sections"]:
        print(f"  {s['id']}. {s['title']} (~{s['duration_estimate']}, {s['char_count']} kar)")


if __name__ == "__main__":
    main()
