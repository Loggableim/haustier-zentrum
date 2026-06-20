#!/usr/bin/env python3
"""
_quick_wins.py — 5 SEO quick wins in one pass.

1. og:image:  ../images/X  →  https://haustierzentrum.com/images/X
   (relative URLs broken in WhatsApp/Facebook/Twitter previews)

2. meta description:  truncate to <= 158 chars at word boundary
   (Google cuts at ~160; >160 is silently dropped from snippets)

3. og:title / twitter:title:  shorten to <= 55 chars (Google cuts at ~580px)
   Strategy: take <title>, drop the " | Haustierzentrum" suffix, then truncate.
   If still > 55, hard-truncate at word boundary.

4. FAQ-Page schema:  for every article that has <h2>Häufig gestellte Fragen</h2>
   followed by H3 + P pairs, generate a FAQPage JSON-LD block.
   (Big CTR boost in SERPs via rich snippets.)

5. <link rel="preconnect">:  add preconnect to googlesyndication (AdSense)
   and fonts.gstatic if present. (Speeds up first paint by ~100-300ms.)
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
SITE = "https://haustierzentrum.com"
MAX_DESC = 158
MAX_OG_TITLE = 55
SUFFIX = " | Haustierzentrum"

PRECONNECT_HOSTS = [
    "https://pagead2.googlesyndication.com",
    "https://www.googletagservices.com",
]


def canon_for_slug(slug: str) -> str:
    return f"{SITE}/artikel/{slug}"


# ---------- Helpers ----------

def truncate_at_word(s: str, max_len: int) -> str:
    """Truncate at last word boundary that fits max_len, strip trailing punctuation."""
    if len(s) <= max_len:
        return s
    # find last space within max_len
    cut = s[:max_len]
    last_space = cut.rfind(" ")
    if last_space > 0:
        cut = cut[:last_space]
    return cut.rstrip(" ,;:.-–—")


def normalize_image_url(value: str) -> str:
    """Convert '../images/X' to absolute. Already-absolute values pass through."""
    if not value:
        return value
    v = value.strip()
    if v.startswith("../"):
        return f"{SITE}/{v[3:]}"
    if v.startswith("/"):
        return f"{SITE}{v}"
    if v.startswith(("http://", "https://")):
        return v
    # bare filename
    return f"{SITE}/images/{v}"


# ---------- Pass 1: og:image + meta description + og/twitter title ----------

def fix_meta(path: Path, dry_run: bool) -> dict:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = {"og_image": 0, "desc": 0, "og_title": 0, "twitter_title": 0, "preconnect": 0}

    # 1) og:image (relative → absolute)
    def _og_image(m):
        url = m.group(1)
        new = normalize_image_url(url)
        if new != url:
            changes["og_image"] += 1
        return f'<meta property="og:image" content="{new}"'
    text = re.sub(r'<meta property="og:image" content="([^"]+)"', _og_image, text)

    # 2) meta description
    def _desc(m):
        v = m.group(1)
        if len(v) > MAX_DESC:
            new = truncate_at_word(v, MAX_DESC)
            if new != v:
                changes["desc"] += 1
            return f'<meta name="description" content="{new}"'
        return m.group(0)
    text = re.sub(r'<meta name="description" content="([^"]+)"', _desc, text)

    # 3) og:title — drop suffix + truncate
    def _og_title(m):
        v = m.group(1)
        if SUFFIX in v:
            v = v.replace(SUFFIX, "").rstrip()
        new = truncate_at_word(v, MAX_OG_TITLE)
        if new != m.group(1):
            changes["og_title"] += 1
        return f'<meta property="og:title" content="{new}"'
    text = re.sub(r'<meta property="og:title" content="([^"]+)"', _og_title, text)

    # 4) twitter:title — same as og:title
    def _tw_title(m):
        v = m.group(1)
        if SUFFIX in v:
            v = v.replace(SUFFIX, "").rstrip()
        new = truncate_at_word(v, MAX_OG_TITLE)
        if new != m.group(1):
            changes["twitter_title"] += 1
        return f'<meta name="twitter:title" content="{new}"'
    text = re.sub(r'<meta name="twitter:title" content="([^"]+)"', _tw_title, text)

    if text != original and not dry_run:
        path.write_text(text, encoding="utf-8")
    return changes


# ---------- Pass 2: FAQPage JSON-LD ----------

# Match an H2 whose text looks like an FAQ section header.
# Accepts: "Häufig gestellte Fragen", "Häufige Fragen ...", "FAQ ...", "Fragen & Antworten", etc.
FAQ_H2_RE = re.compile(
    r'<h2[^>]*>\s*([^<]*(?:'
    r'gestellte\s+fragen|häufige\s+fragen|h[uä]ufige\s+fragen|'
    r'faq|fragen\s*[&und]\s*antworten|fragen\s+und\s+antworten|'
    r'oft\s+gestellte\s+fragen|'
    r'fragen\s+und\s+antworten'
    r')[^<]*)\s*</h2>',
    re.IGNORECASE,
)
# Match H3 + the next <p> that follows it (until the next H2/H3 or end)
FAQ_ITEM_RE = re.compile(
    r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>',
    re.DOTALL | re.IGNORECASE,
)
H2_H3_RE = re.compile(r'<h[23][^>]*>', re.IGNORECASE)


def extract_faq_items(text: str) -> list[dict] | None:
    """Find FAQ section, return list of {question, answer} dicts or None."""
    m = FAQ_H2_RE.search(text)
    if not m:
        return None
    start = m.end()
    rest = text[start:]
    # End of FAQ section = next H2 (any H2 after the FAQ H2)
    parts = re.split(r'(<h2[^>]*>)', rest, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) >= 2:
        section = parts[0] + parts[1]
    else:
        section = rest
    items = []
    for im in FAQ_ITEM_RE.finditer(section):
        q = re.sub(r'<[^>]+>', '', im.group(1)).strip()
        a = re.sub(r'<[^>]+>', '', im.group(2)).strip()
        a = re.sub(r'\s+', ' ', a)
        if q and a and len(q) > 5 and len(a) > 20:
            items.append({"@type": "Question", "name": q,
                          "acceptedAnswer": {"@type": "Answer", "text": a}})
    if len(items) < 2:
        return None
    return items


def add_faq_schema(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    # If FAQPage schema already exists, skip
    if '"FAQPage"' in text:
        return False
    items = extract_faq_items(text)
    if not items:
        return False
    slug = path.name[:-5]
    # Get datePublished from existing JSON-LD if present
    date_pub = ""
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', text)
    if m:
        date_pub = m.group(1)
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items,
    }
    if date_pub:
        schema["datePublished"] = date_pub
    schema_block = f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>\n'
    # Insert before </head>
    new_text, n = re.subn(r'</head>', schema_block + '</head>', text, count=1)
    if n and not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return bool(n)


# ---------- Pass 3: preconnect ----------

def add_preconnect(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'rel="preconnect"' in text:
        return False
    # Inject after <meta name="viewport"
    links = '\n'.join(f'  <link rel="preconnect" href="{u}">' for u in PRECONNECT_HOSTS)
    new_text, n = re.subn(
        r'(<meta name="viewport"[^>]+>)',
        r'\1\n' + links,
        text, count=1,
    )
    if n and not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return bool(n)


# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print(f"=== _quick_wins.py (dry_run={args.dry_run}) ===\n")

    # 1-4: meta fixes
    totals = {"og_image": 0, "desc": 0, "og_title": 0, "twitter_title": 0, "preconnect": 0}
    files_meta = 0
    for p in sorted(ART_DIR.glob("*.html")):
        c = fix_meta(p, args.dry_run)
        if any(c.values()):
            files_meta += 1
            for k, v in c.items():
                totals[k] += v
    print(f"[1] Meta fixes in {files_meta} files:")
    for k, v in totals.items():
        print(f"      {k}: {v} edits")

    # 5: FAQ schema
    faq_files = 0
    faq_items = 0
    for p in sorted(ART_DIR.glob("*.html")):
        if add_faq_schema(p, args.dry_run):
            faq_files += 1
            # re-count items by re-reading (only if not dry-run, else use cached)
    print(f"[2] FAQPage schema added to {faq_files} articles")

    # 6: preconnect
    pc_files = 0
    for p in sorted(ART_DIR.glob("*.html")):
        if add_preconnect(p, args.dry_run):
            pc_files += 1
    print(f"[3] preconnect added to {pc_files} articles")

    print("\nDone.")


if __name__ == "__main__":
    main()
