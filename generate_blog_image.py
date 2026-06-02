#!/usr/bin/env python3
"""Deterministic fallback hero image generator for Haustierzentrum articles."""
from pathlib import Path
import sys, hashlib, textwrap
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow is required: pip install pillow")

def font(size, bold=False):
    candidates = [
        "/c/Windows/Fonts/segoeuib.ttf" if bold else "/c/Windows/Fonts/segoeui.ttf",
        "/c/Windows/Fonts/arialbd.ttf" if bold else "/c/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def main():
    if len(sys.argv) < 3:
        print("Usage: generate_blog_image.py <slug> <title>", file=sys.stderr)
        return 2
    slug = sys.argv[1].strip().replace('/', '-')
    title = " ".join(sys.argv[2:]).strip()
    outdir = Path('images'); outdir.mkdir(exist_ok=True)
    digest = hashlib.md5(slug.encode()).hexdigest()
    palettes = [('#fff3e0','#ff9800','#5d4037'),('#e8f5e9','#43a047','#263238'),('#e3f2fd','#1e88e5','#263238'),('#fce4ec','#d81b60','#3e2723'),('#f3e5f5','#8e24aa','#263238')]
    bg, accent, text = palettes[int(digest[:2],16) % len(palettes)]
    img = Image.new('RGB',(1200,630),bg)
    d = ImageDraw.Draw(img)
    # decorative soft blobs
    for i in range(18):
        x = int(digest[(i*2)%30:(i*2)%30+2],16) * 1200 // 255
        y = int(digest[(i*2+1)%30:(i*2+1)%30+2],16) * 630 // 255
        r = 45 + int(digest[(i*2+2)%30:(i*2+2)%30+2],16) % 90
        d.ellipse((x-r,y-r,x+r,y+r), fill=accent if i%3==0 else '#ffffff', outline=None)
    d.rectangle((0,0,1200,630), outline=accent, width=18)
    d.rounded_rectangle((70,70,1130,560), radius=34, fill=(255,255,255), outline=accent, width=4)
    d.text((105,105), "🐾 Haustierzentrum", fill=accent, font=font(42, True))
    lines=[]
    for part in textwrap.wrap(title, width=28):
        lines.append(part)
    y=210
    for line in lines[:4]:
        d.text((105,y), line, fill=text, font=font(58, True))
        y += 70
    d.text((105,505), "Ratgeber • Haltung • Gesundheit • Ernährung", fill='#666666', font=font(28))
    path = outdir / f"{slug}_00001_.png"
    img.save(path, quality=92)
    print(path.as_posix())
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
