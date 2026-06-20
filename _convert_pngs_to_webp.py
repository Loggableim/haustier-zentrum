#!/usr/bin/env python3
"""
_convert_pngs_to_webp.py — Konvertiert alle PNG-Bilder in images/ zu WebP.

Quality 92 (siehe haustier-image-style Skill) für furry pop-art Halbton-Stil.

Vorgehen:
  1. Lade PNG via PIL
  2. Konvertiere zu RGB (WebP unterstützt RGBA, aber RGB ist kleiner)
  3. Speichere als .webp (quality 92, method 6)
  4. Verifiziere Größen-Reduktion
  5. Lösche Original-PNG
  6. Falls WebP-Konvertierung fehlschlägt, behalte PNG

Idempotent: Wenn WebP bereits existiert, wird PNG direkt gelöscht.
"""
from pathlib import Path
from PIL import Image
import os, sys, json

IMG_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\images")

png_files = sorted(IMG_DIR.glob("*.png"))
print(f"Gefunden: {len(png_files)} PNG-Dateien\n")

results = []
total_orig = 0
total_new = 0
errors = []

for png in png_files:
    webp = png.with_suffix(".webp")
    orig_size = png.stat().st_size
    total_orig += orig_size

    if webp.exists():
        # WebP already there, just delete the orphan PNG
        png.unlink()
        new_size = webp.stat().st_size
        total_new += new_size
        results.append((png.name, orig_size, new_size, "deleted (webp existed)"))
        continue

    try:
        img = Image.open(png)
        # Convert palette/RGBA to RGB for smaller WebP
        if img.mode in ('P', 'RGBA', 'LA'):
            img = img.convert('RGB')
        # Save as WebP quality 92
        img.save(webp, 'WEBP', quality=92, method=6)
        new_size = webp.stat().st_size
        total_new += new_size
        # Verify image is valid
        with Image.open(webp) as test:
            test.verify()
        # Delete the PNG
        png.unlink()
        results.append((png.name, orig_size, new_size, "converted"))
    except Exception as e:
        errors.append((png.name, str(e)))
        results.append((png.name, orig_size, -1, f"ERROR: {e}"))

# Summary
print("=" * 75)
print(f"{'File':<70} {'PNG→WebP':>12} {'Savings':>8}")
print("-" * 75)
for name, orig, new, status in results:
    if new < 0:
        print(f"{name[:70]:<70} {'ERR':>12}")
    else:
        savings = (1 - new/orig) * 100
        orig_kb = orig / 1024
        new_kb = new / 1024
        print(f"{name[:70]:<70} {orig_kb:6.0f}→{new_kb:5.0f}KB {savings:6.1f}%")

print("-" * 75)
print(f"Total:  {(total_orig/1024/1024):6.2f} MB → {(total_new/1024/1024):6.2f} MB  ({(1-total_new/total_orig)*100:.1f}% smaller)")

if errors:
    print(f"\nERRORS: {len(errors)}")
    for n, e in errors:
        print(f"  {n}: {e}")

# Final check
remaining_pngs = list(IMG_DIR.glob("*.png"))
print(f"\nRemaining PNGs: {len(remaining_pngs)}")
for p in remaining_pngs:
    print(f"  {p.name}")
