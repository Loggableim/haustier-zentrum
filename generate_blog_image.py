#!/usr/bin/env python3
"""Generate colored pencil sketch style hero images for Haustierzentrum articles.
Uses ComfyUI API if available, otherwise Pillow fallback with sketch aesthetic."""
from pathlib import Path
import sys, hashlib, textwrap, json, time, uuid, requests
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow is required: pip install pillow")

API_BASE = "http://127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

WORKFLOW_TEMPLATE = {
    "3": {"class_type": "KSampler", "inputs": {"seed": 42, "steps": 25, "cfg": 7, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
    "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 768, "batch_size": 1}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["4", 1]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "photorealistic, 3d render, photograph, realistic texture", "clip": ["4", 1]}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "comfy", "images": ["8", 0]}}
}

SKETCH_PROMPT = "Colored pencil sketch drawing on cream paper of {s}, hand-drawn illustration style, soft pastel colors, warm tones, gentle artistic strokes, children's book illustration, cute and charming, high quality colored pencil artwork"

def font(size, bold=False):
    candidates = [
        "/c/Windows/Fonts/segoeuib.ttf" if bold else "/c/Windows/Fonts/segoeui.ttf",
        "/c/Windows/Fonts/arialbd.ttf" if bold else "/c/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def generate_via_comfyui(slug, subject, outdir):
    """Generate image via ComfyUI API with colored pencil sketch style."""
    try:
        w = json.loads(json.dumps(WORKFLOW_TEMPLATE))
        w["3"]["inputs"]["seed"] = abs(hash(slug)) % (2**31)
        w["6"]["inputs"]["text"] = SKETCH_PROMPT.format(s=subject)
        r = requests.post(f"{API_BASE}/prompt", json={"prompt": w, "client_id": CLIENT_ID}, timeout=15)
        pid = r.json()["prompt_id"]
        for _ in range(60):
            r2 = requests.get(f"{API_BASE}/history/{pid}", timeout=10)
            if r2.status_code == 200 and pid in r2.json():
                for nid, no in r2.json()[pid].get("outputs", {}).items():
                    for img in no.get("images", []):
                        src = Path(f"C:/HermesPortable/ComfyUI/output/{img['filename']}")
                        dst = outdir / f"{slug}_00001_.png"
                        if src.exists():
                            import shutil
                            shutil.copy2(src, dst)
                            return True
            time.sleep(2)
    except Exception as e:
        print(f"ComfyUI failed: {e}", file=sys.stderr)
    return False

def generate_fallback(slug, title, outdir):
    """Pillow fallback: sketch-style colored pencil aesthetic placeholder."""
    digest = hashlib.md5(slug.encode()).hexdigest()
    palettes = [('#fff3e0','#ff9800','#5d4037'),('#e8f5e9','#43a047','#263238'),('#e3f2fd','#1e88e5','#263238'),('#fce4ec','#d81b60','#3e2723'),('#f3e5f5','#8e24aa','#263238')]
    bg, accent, text_c = palettes[int(digest[:2],16) % len(palettes)]
    img = Image.new('RGB',(1200,630),bg)
    d = ImageDraw.Draw(img)
    for i in range(12):
        x = int(digest[(i*2)%30:(i*2)%30+2],16) * 1200 // 255
        y = int(digest[(i*2+1)%30:(i*2+1)%30+2],16) * 630 // 255
        r = 35 + int(digest[(i*2+2)%30:(i*2+2)%30+2],16) % 70
        d.ellipse((x-r,y-r,x+r,y+r), fill=accent if i%3==0 else '#ffffff', outline=None)
    d.rounded_rectangle((60,60,1140,570), radius=30, fill=(255,255,255), outline=accent, width=4)
    d.text((95,95), "✎ Haustierzentrum", fill=accent, font=font(38, True))
    lines = []
    for part in textwrap.wrap(title, width=26):
        lines.append(part)
    y = 200
    for line in lines[:4]:
        d.text((95,y), line, fill=text_c, font=font(52, True))
        y += 64
    d.text((95,485), "Buntstift-Skizze · Handgezeichnet", fill='#999999', font=font(24))
    path = outdir / f"{slug}_00001_.png"
    img.save(path, quality=92)
    print(f"  Fallback: {path.name}")
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: generate_blog_image.py <slug> <title>", file=sys.stderr)
        return 2
    slug = sys.argv[1].strip().replace('/', '-')
    title = " ".join(sys.argv[2:]).strip()
    outdir = Path('images'); outdir.mkdir(exist_ok=True)
    
    if not generate_via_comfyui(slug, title, outdir):
        generate_fallback(slug, title, outdir)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
