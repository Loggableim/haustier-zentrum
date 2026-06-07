#!/usr/bin/env python3
"""Submit hero image jobs for all 3 articles and wait for completion."""

import json
import os
import sys
import time
import urllib.request
from PIL import Image

QUEUE = "http://127.0.0.1:8283"
IMG_DIR = "C:/HermesPortable/home/scripts/blog-automation/haustier-zentrum/images"
os.makedirs(IMG_DIR, exist_ok=True)

STYLE = ", POP ART COMIC STYLE, WARHOL STYLE, bold thick black outlines, halftone dots, Ben-Day dots effect, vibrant flat colors, high contrast, white background, simple centered composition, cute expressive cartoon animal style"

images = [
    {
        "slug": "mops-rasseguide",
        "prompt": "Ein süßer Mops (Pug) in beiger Farbe mit brauner/roter Maske, kurze Stupsnase, große runde braune Augen, tiefe Gesichtsfalten, hängende Ohren, freundlicher Ausdruck, sitzt auf einem gemütlichen Kissen" + STYLE
    },
    {
        "slug": "sibirischer-husky-rasseguide",
        "prompt": "Ein Sibirischer Husky mit auffällig blauen Augen, grau-weiß-schwarzem Fell, aufrechtstehenden dreieckigen Ohren, buschiger Ringelschwanz, kraftvolle elegante Statur, steht im Schnee" + STYLE
    },
    {
        "slug": "ragdoll-katze-rasseguide",
        "prompt": "Eine Ragdoll-Katze mit großen leuchtend blauen Augen, seidigem mittellangem Fell in Seal Point Farbe (hellbeige mit dunkelbraunen Ohren/Gesicht/Pfoten/Schwanz), entspannt liegend auf weichem Teppich" + STYLE
    }
]

def submit(prompt):
    data = json.dumps({
        "model": "sdxl-realvis",
        "prompt": prompt,
        "steps": 25,
        "width": 1216,
        "height": 832,
    }).encode()
    req = urllib.request.Request(
        f"{QUEUE}/generate", data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp.get("job_id")

def wait_for(job_id, timeout=400):
    start = time.time()
    for i in range(timeout):
        time.sleep(3)
        try:
            resp = json.loads(
                urllib.request.urlopen(f"{QUEUE}/status/{job_id}", timeout=10).read()
            )
            st = resp.get("status")
            if st == "done" and resp.get("output_path"):
                return resp["output_path"]
            if st == "failed":
                err = resp.get("error", "")
                import re
                m = re.search(r'"output_path": "([^"]+)"', err)
                if m:
                    return m.group(1)
                print(f"  ❌ Job failed: {err[:200]}", file=sys.stderr)
                return None
        except Exception as e:
            pass
        if i % 10 == 0 and i > 0:
            elapsed = int(time.time() - start)
            print(f"  ⏳ {elapsed}s waiting for job {job_id[:12]}...")
    print("  ⏰ Timed out", file=sys.stderr)
    return None

def process(slug, src_path):
    if not src_path:
        return False
    src_path = src_path.replace("\\", "/")
    dst_png = os.path.join(IMG_DIR, f"{slug}.png")
    dst_webp = os.path.join(IMG_DIR, f"{slug}.webp")
    try:
        img = Image.open(src_path)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        img = img.resize((1216, 832), Image.LANCZOS)
        img.save(dst_png, "PNG")
        img.save(dst_webp, "WEBP", quality=85)
        kb_png = os.path.getsize(dst_png) // 1024
        kb_webp = os.path.getsize(dst_webp) // 1024
        print(f"  ✅ {slug}: {kb_png}KB PNG / {kb_webp}KB WEBP")
        return True
    except Exception as e:
        print(f"  ❌ Image processing error for {slug}: {e}")
        return False

print("=" * 50)
print("HAUSTIERZENTRUM HERO IMAGE GENERATION")
print("=" * 50)

# Check if images already exist
to_generate = []
for img in images:
    slug = img["slug"]
    webp_path = os.path.join(IMG_DIR, f"{slug}.webp")
    if os.path.exists(webp_path):
        print(f"  ⏭ {slug}.webp existiert bereits")
    else:
        to_generate.append(img)

print(f"\nGeneriere {len(to_generate)} Bilder...\n")

for img in to_generate:
    slug = img["slug"]
    print(f"  📤 Submitting {slug}...")
    try:
        job_id = submit(img["prompt"])
        if not job_id:
            print(f"  ❌ Job submission failed for {slug}")
            continue
        print(f"     → job_id={job_id}")
        out_path = wait_for(job_id)
        if out_path:
            process(slug, out_path)
        else:
            print(f"  ❌ No output for {slug}")
    except Exception as e:
        print(f"  ❌ Error for {slug}: {e}")
    time.sleep(2)

print("\n✅ Done!")
