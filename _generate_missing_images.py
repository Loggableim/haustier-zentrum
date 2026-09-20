#!/usr/bin/env python3
"""
_generate_missing_images.py — Generate missing hero images via local SDXL queue.

Uses the haustier-zentrum furry pop-art style (per prompt-templates.md).
Falls back gracefully if the queue is unavailable.

Usage: python _generate_missing_images.py
"""
import json
import os
import sys
import time
import urllib.request
from io import BytesIO

from PIL import Image

sys.path.insert(0, "C:/sidekick/home/spaces/haustier-zentrum")
from content_factory import TOPICS

QUEUE = "http://127.0.0.1:8283"
IMG_DIR = "C:/sidekick/home/spaces/haustier-zentrum/images"

# haustier-zentrum style (from references/prompt-templates.md)
POSITIVE = ("furry pop-art, anthropomorphic animal characters, editorial illustration, "
            "bold black contour lines, clean vector art, kawaii, cute, vibrant orange/violet "
            "color palette, halftone comic textures, graphic novel aesthetic, modern advertising "
            "illustration, dynamic composition, highly detailed, professional magazine artwork, "
            "sharp linework, colorful background")
NEGATIVE = ("text, watermark, signature, blurry, low quality, distorted, photograph, realistic, "
            "3d render, photorealistic, hyperrealistic, cinematic lighting, shadows, gradient, "
            "oil painting, digital art, smooth shading")

MISSING = [
    "aquarium-pflanzen-einsteiger",
    "chinchilla-ernaehrung-futter",
    "hamster-ernaehrung-futterplan",
    "hundeangst-training-tipps",
    "katzen-kratzmoebel-test",
    "vogelvoliere-kaufen-checkliste",
    "welpenschule-finden-kosten",
]


def get_subject(slug):
    for t in TOPICS:
        if t["slug"] == slug:
            return t["subject"]
    return None


def submit(prompt, negative):
    data = json.dumps({
        "model": "sdxl-lightning",
        "prompt": prompt,
        "negative": negative,
        "steps": 8,
        "cfg": 2.0,
        "width": 1216,
        "height": 832,
    }).encode()
    req = urllib.request.Request(f"{QUEUE}/generate", data=data,
                                 headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp.get("job_id")


def wait_for(job_id, timeout=300):
    for _ in range(timeout // 3):
        time.sleep(3)
        try:
            resp = json.loads(
                urllib.request.urlopen(f"{QUEUE}/status/{job_id}", timeout=10).read())
        except Exception as e:
            print(f"    poll error: {e}")
            continue
        st = resp.get("status")
        if st == "done" and resp.get("output_path"):
            return resp["output_path"]
        if st == "failed":
            print(f"    job failed: {resp.get('error')}")
            return None
    return None


def process(slug, src_path):
    img = Image.open(src_path)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    img = img.resize((1216, 832), Image.LANCZOS)
    dst = os.path.join(IMG_DIR, f"{slug}_00001_.webp")
    img.save(dst, "WEBP", quality=92)
    kb = os.path.getsize(dst) // 1024
    return dst, kb


def main():
    results = []
    for slug in MISSING:
        subject = get_subject(slug)
        if not subject:
            print(f"❌ No subject for {slug}")
            results.append((slug, False))
            continue

        prompt = f"{POSITIVE}, {subject}"
        print(f"\n🎨 {slug}")
        print(f"   subject: {subject[:70]}")

        try:
            job_id = submit(prompt, NEGATIVE)
            print(f"   job: {job_id}")
        except Exception as e:
            print(f"   ❌ submit failed: {e}")
            results.append((slug, False))
            continue

        out = wait_for(job_id)
        if not out:
            print(f"   ❌ generation failed/timeout")
            results.append((slug, False))
            continue

        try:
            dst, kb = process(slug, out)
            print(f"   ✅ {dst} ({kb}KB)")
            results.append((slug, True))
        except Exception as e:
            print(f"   ❌ processing failed: {e}")
            results.append((slug, False))

    print(f"\n{'='*60}")
    print("SUMMARY:")
    for slug, ok in results:
        print(f"  {'✅' if ok else '❌'} {slug}")
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
