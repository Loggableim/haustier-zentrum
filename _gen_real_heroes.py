#!/usr/bin/env python3
"""Generate all hero images for Haustierzentrum via local gen queue (SDXL Lightning)."""
import json, os, sys, time, urllib.request, re
from PIL import Image

QUEUE = "http://127.0.0.1:8283"
IMG_DIR = r"C:\HermesPortable\home\scripts\blog-automation\haustier-zentrum\images"
os.makedirs(IMG_DIR, exist_ok=True)

STYLE = ", POP ART COMIC STYLE, WARHOL STYLE, bold thick black outlines, halftone dots, Ben-Day dots effect, vibrant flat colors, high contrast, white background, simple centered composition, cute expressive cartoon animal style"

# Priority 1: < 5KB (broken/placeholder)
# Priority 2: "hero-*" prefixed
# Priority 3: Other small images

IMAGES = [
    # Priority 1: CRAZY small (1-2KB - pure blank placeholders)
    ("westie-west-highland-white-terrier-rasseguide_00001_", "Niedlicher West Highland White Terrier (Westie) mit weißem Fell, schwarzen Knopfaugen, kleinen aufrechten Ohren, freundlicher Ausdruck, sitzt stolz"),
    ("beagle-rasseguide_00001_", "Fröhlicher Beagle mit dreifarbigem Fell (black/tan/white), braunen Schlappohren, großen braunen Augen, neugieriger Gesichtsausdruck"),
    ("malteser-rasseguide_00001_", "Süßer Malteser Hund mit reinweißem seidigem Langhaarfell, dunklen Knopfaugen, kleiner schwarzer Nase, edler Ausdruck"),
    ("havaneser-rasseguide_00001_", "Havaneser Hund mit langem seidigem Fell in Cremefarbe, großen dunklen Augen, Schlappohren, verspielter Ausdruck"),
    ("dalmatiner-rasseguide_00001_", "Dalmatiner mit weißem Fell und schwarzen Tupfen, aufmerksamen braunen Augen, elegantem Körperbau, freundlich"),
    ("zwergspitz-pomeranian-rasseguide_00001_", "Süßer Zwergspitz (Pomeranian) mit flauschigem orange-braunem Fell, kleinen spitzen Ohren, fuchsähnlichem Gesicht"),
    ("cocker-spaniel-rasseguide_00001_", "Cocker Spaniel mit langen Schlappohren, seidigem Fell in goldener Farbe, großen dunklen Augen, sanftem Ausdruck"),
    ("berner-sennenhund-rasseguide_00001_", "Berner Sennenhund mit dreifarbigem Fell (black/white/tan), kräftigem Körperbau, freundlichem Ausdruck"),

    # Priority 2: Hero images 
    ("hero-mops-rasseguide", "Süßer Mops (Pug) in beiger Farbe mit brauner/schwarzer Maske, kurze Stupsnase, große runde braune Augen, tiefe Gesichtsfalten, hängende Ohren, freundlich"),
    ("hero-ragdoll-katze-rasseguide", "Wunderschöne Ragdoll-Katze mit großen leuchtend blauen Augen, seidigem mittellangem Fell in Seal Point Farbe, entspannt liegend"),
    ("hero-sibirischer-husky-rasseguide", "Charismatischer Sibirischer Husky mit auffällig blauen Augen, grau-weiß-schwarzem Fell, aufrechtstehenden dreieckigen Ohren"),
    ("katzen-krankheiten_hero", "Verschmuste Hauskatze mit charakteristischen, aufmerksamen Augen, beim Tierarzt mit Stethoskop, Gesundheits-Check"),
]

def submit(prompt):
    data = json.dumps({
        "model": "sdxl-lightning",
        "prompt": prompt,
        "steps": 8,
        "width": 1216,
        "height": 832,
    }).encode()
    req = urllib.request.Request(f"{QUEUE}/generate", data=data,
        headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp.get("job_id")

def wait_for(job_id, timeout=300):
    start = time.time()
    for i in range(timeout // 3):
        time.sleep(3)
        try:
            resp = json.loads(
                urllib.request.urlopen(f"{QUEUE}/status/{job_id}", timeout=10).read()
            )
            st = resp.get("status")
            if st == "done" and resp.get("output_path"):
                return resp["output_path"]
            if st == "failed":
                print(f"  ❌ Job failed: {resp.get('error','')[:200]}", file=sys.stderr)
                return None
        except: pass
        if i % 20 == 0 and i > 0:
            elapsed = int(time.time() - start)
            print(f"  ⏳ {elapsed}s waiting...")
    print("  ⏰ Timed out", file=sys.stderr)
    return None

def process(slug, src_path):
    if not src_path:
        return False
    src_path = src_path.replace("\\", "/")
    dst = os.path.join(IMG_DIR, f"{slug}.webp")
    try:
        img = Image.open(src_path)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        img = img.resize((1216, 832), Image.LANCZOS)
        img.save(dst, "WEBP", quality=92)
        kb = os.path.getsize(dst) // 1024
        print(f"  ✅ {slug}.webp ({kb}KB)")
        return True
    except Exception as e:
        print(f"  ❌ Processing error: {e}")
        return False

total = len(IMAGES)
print(f"🎯 Generating {total} hero images via SDXL Lightning Queue...\n")

for idx, (slug, subject) in enumerate(IMAGES, 1):
    webp_path = os.path.join(IMG_DIR, f"{slug}.webp")
    existing_kb = os.path.getsize(webp_path) // 1024 if os.path.exists(webp_path) else 0
    
    print(f"[{idx}/{total}] {slug} ({existing_kb}KB currently)...")
    
    try:
        prompt = f"{subject}{STYLE}"
        job_id = submit(prompt)
        if not job_id:
            print(f"  ❌ Submit failed")
            continue
        print(f"  → job_id={job_id}")
        out_path = wait_for(job_id)
        if out_path:
            process(slug, out_path)
        else:
            print(f"  ❌ No output")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    time.sleep(1)

print(f"\n✅ Done! Generated {sum(1 for slug,_ in IMAGES if os.path.exists(os.path.join(IMG_DIR, f'{slug}.webp')) and os.path.getsize(os.path.join(IMG_DIR, f'{slug}.webp')) > 50000)}/{total} proper images")
