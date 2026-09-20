#!/usr/bin/env python3
"""
_fix_urls.py — Normalize all URL forms to the canonical extensionless form.

Cloudflare Pages 308-redirects:
  /artikel/foo.html  → /artikel/foo
  /artikel/foo/      → /artikel/foo

So the canonical URL must be https://haustierzentrum.com/artikel/<slug>
(no .html, no trailing slash) — otherwise every canonical points at a
redirect, which wastes crawl budget and confuses Google.

Fixes:
1. <link rel="canonical"> with .html → extensionless
2. <meta property="og:url"> with .html → extensionless
3. Internal href="/artikel/foo.html" → href="/artikel/foo" (only for real slugs)
4. JSON-LD mainEntityOfPage @id with .html → extensionless

Usage: python _fix_urls.py [--dry-run]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
SITE = "https://haustierzentrum.com"

ARTICLE_SLUGS = {p.name[:-5] for p in ART_DIR.glob("*.html")}

JSONLD_RE = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)',
    re.DOTALL,
)


def normalize_href(href: str) -> str:
    """Collapse /artikel/foo.html and /artikel/foo/ to /artikel/foo."""
    h = href
    if h.startswith(SITE):
        h = h[len(SITE):]
    m = re.match(r"^(/artikel/[A-Za-z0-9_\-]+)\.html$", h)
    if m:
        return m.group(1)
    m = re.match(r"^(/artikel/[A-Za-z0-9_\-]+)/$", h)
    if m:
        return m.group(1)
    return href


def fix_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0
    slug = path.name[:-5]
    canon = f"{SITE}/artikel/{slug}"

    # 1. canonical
    text, n = re.subn(
        r'<link rel="canonical" href="[^"]+"\s*/?>',
        f'<link rel="canonical" href="{canon}">',
        text, count=1,
    )
    changes += n

    # 2. og:url
    text, n = re.subn(
        r'<meta property="og:url" content="[^"]+"\s*/?>',
        f'<meta property="og:url" content="{canon}">',
        text, count=1,
    )
    changes += n

    # 3. internal hrefs
    href_changes = 0

    def _href_sub(m):
        nonlocal href_changes
        attr, href = m.group(1), m.group(2)
        new_href = normalize_href(href)
        if new_href != href:
            mm = re.match(r"^/artikel/([A-Za-z0-9_\-]+)$", new_href)
            if mm and mm.group(1) in ARTICLE_SLUGS:
                href_changes += 1
                return f'{attr}="{new_href}"'
        return m.group(0)

    text = re.sub(r'(href)="([^"]+)"', _href_sub, text)
    changes += href_changes

    # 4. JSON-LD @id / url fields (keep absolute URL form)
    def _jsonld_sub(m):
        nonlocal changes
        blob = m.group(2)
        try:
            data = json.loads(blob)
        except Exception:
            return m.group(0)

        local_changes = 0

        def fix_obj(o):
            nonlocal local_changes
            if isinstance(o, dict):
                for k, v in list(o.items()):
                    if k in ("@id", "url", "mainEntityOfPage") and isinstance(v, str):
                        new_v = normalize_href(v)
                        if new_v != v:
                            # JSON-LD needs absolute URLs
                            if new_v.startswith("/"):
                                new_v = SITE + new_v
                            o[k] = new_v
                            local_changes += 1
                    else:
                        fix_obj(v)
            elif isinstance(o, list):
                for v in o:
                    fix_obj(v)

        fix_obj(data)
        if local_changes == 0:
            return m.group(0)  # nothing changed — keep original formatting
        changes += local_changes
        return m.group(1) + json.dumps(data, ensure_ascii=False, indent=2) + m.group(3)

    text = JSONLD_RE.sub(_jsonld_sub, text)

    if text != original and not dry_run:
        path.write_text(text, encoding="utf-8")
    return changes


def fix_static(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changed = 0

    # Fix canonical for static pages (must be extensionless — CF 308-redirects .html)
    slug = path.stem  # e.g. "about"
    canon = f"{SITE}/{slug}" if slug != "index" else f"{SITE}/"
    m = re.search(r'<link rel="canonical" href="([^"]+)"\s*/?>', text)
    if m and m.group(1) != canon:
        text = text[:m.start()] + f'<link rel="canonical" href="{canon}">' + text[m.end():]
        changed += 1

    # Fix og:url for static pages
    m = re.search(r'<meta property="og:url" content="([^"]+)"\s*/?>', text)
    if m and m.group(1) != canon:
        text = text[:m.start()] + f'<meta property="og:url" content="{canon}">' + text[m.end():]
        changed += 1

    def _href_sub(m):
        nonlocal changed
        attr, href = m.group(1), m.group(2)
        new_href = normalize_href(href)
        if new_href != href:
            mm = re.match(r"^/artikel/([A-Za-z0-9_\-]+)$", new_href)
            if mm and mm.group(1) in ARTICLE_SLUGS:
                changed += 1
                return f'{attr}="{new_href}"'
        return m.group(0)

    text = re.sub(r'(href)="([^"]+)"', _href_sub, text)
    if text != original and not dry_run:
        path.write_text(text, encoding="utf-8")
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total_files = 0
    total_changes = 0
    for f in sorted(ART_DIR.glob("*.html")):
        c = fix_file(f, args.dry_run)
        if c:
            total_files += 1
            total_changes += c

    for fn in ["index.html", "about.html", "impressum.html", "datenschutz.html",
               "affiliate-hinweis.html", "404.html"]:
        p = ROOT / fn
        if p.exists():
            c = fix_static(p, args.dry_run)
            if c:
                total_files += 1
                total_changes += c

    print(f"{'[dry-run] ' if args.dry_run else ''}Fixed {total_files} files, {total_changes} edits")


if __name__ == "__main__":
    main()
