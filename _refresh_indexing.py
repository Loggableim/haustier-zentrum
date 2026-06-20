#!/usr/bin/env python3
"""
_refresh_indexing.py — Normalize URLs + refresh sitemap + ping search engines.

Goal: every article has ONE canonical URL = https://haustierzentrum.com/artikel/<slug>
(no .html, no trailing slash, no /artikel/-prefix bugs)

This is what Cloudflare serves after 308 redirects, so picking this as canonical
removes duplicate-URL confusion for Google and saves 2 redirects per inbound link.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
SITEMAP = ROOT / "sitemap.xml"
SITE = "https://haustierzentrum.com"
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "")

# Article slug set (only files actually in /artikel/)
ARTICLE_SLUGS = {p.name[:-5] for p in ART_DIR.glob("*.html")}
# Slug that was historically a buggy og:url (no /artikel/ prefix)
KNOWN_BAD_SLUGS = set(ARTICLE_SLUGS)


def canon_for_slug(slug: str) -> str:
    return f"{SITE}/artikel/{slug}"


def _extract_date_modified(path: Path) -> float | None:
    """Try to find dateModified or datePublished in JSON-LD of an article.
    Returns a unix timestamp or None."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    # Find the first script type=application/ld+json
    m = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.DOTALL)
    if not m:
        return None
    blob = m.group(1).strip()
    # Try direct JSON first
    data = None
    try:
        data = json.loads(blob)
    except Exception:
        # Sometimes HTML-escaped; try a relaxed parse
        try:
            data = json.loads(blob.replace("&quot;", '"').replace("&amp;", "&"))
        except Exception:
            return None
    # Search for dateModified or datePublished recursively
    target = None
    def walk(o):
        nonlocal target
        if isinstance(o, dict):
            if "dateModified" in o:
                target = o["dateModified"]
                return True
            if "datePublished" in o and target is None:
                target = o["datePublished"]
            for v in o.values():
                if walk(v):
                    return True
        elif isinstance(o, list):
            for v in o:
                if walk(v):
                    return True
        return False
    walk(data)
    if not target:
        return None
    # Parse ISO date; if date-only, treat as midnight UTC
    s = str(target)
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            return time.mktime(time.strptime(s, "%Y-%m-%d"))
        return time.mktime(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return None


def normalize_href(href: str) -> str:
    """Collapse .../artikel/foo.html and .../artikel/foo/ to .../artikel/foo."""
    if not href:
        return href
    h = href
    if h.startswith(SITE):
        h = h[len(SITE):]
    elif h.startswith("https://www.haustier-zentrum.com"):
        h = h[len("https://www.haustier-zentrum.com"):]
    m = re.match(r"^(/artikel/[A-Za-z0-9_\-]+)\.html$", h)
    if m:
        return m.group(1)
    m = re.match(r"^(/artikel/[A-Za-z0-9_\-]+)/$", h)
    if m:
        return m.group(1)
    return href


def fix_article_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0
    slug = path.name[:-5]
    canon = canon_for_slug(slug)

    # canonical
    new, n = re.subn(
        r'<link rel="canonical" href="[^"]+"\s*/?>',
        f'<link rel="canonical" href="{canon}">',
        text, count=1,
    )
    if n:
        text = new
        changes += n

    # og:url
    new, n = re.subn(
        r'<meta property="og:url" content="[^"]+"\s*/?>',
        f'<meta property="og:url" content="{canon}">',
        text, count=1,
    )
    if n:
        text = new
        changes += n

    # inter-article hrefs (only inside /artikel/ and pointing to real slugs)
    def _href_sub(m):
        attr, href = m.group(1), m.group(2)
        new_href = normalize_href(href)
        if new_href != href:
            mm = re.match(r"^/artikel/([A-Za-z0-9_\-]+)$", new_href)
            if mm and mm.group(1) in ARTICLE_SLUGS:
                return f'{attr}="{new_href}"'
        return m.group(0)

    new, n = re.subn(r'(href)="([^"]+)"', _href_sub, text)
    if n:
        text = new
        changes += n

    if text != original and not dry_run:
        path.write_text(text, encoding="utf-8")
    return changes


def fix_static_pages(dry_run: bool) -> int:
    total = 0
    for fn in ["index.html", "about.html", "impressum.html", "datenschutz.html"]:
        p = ROOT / fn
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        original = text

        def _href_sub(m):
            attr, href = m.group(1), m.group(2)
            new_href = normalize_href(href)
            if new_href != href:
                mm = re.match(r"^/artikel/([A-Za-z0-9_\-]+)$", new_href)
                if mm and mm.group(1) in ARTICLE_SLUGS:
                    return f'{attr}="{new_href}"'
            return m.group(0)

        text, n = re.subn(r'(href)="([^"]+)"', _href_sub, text)
        if text != original:
            total += n
            if not dry_run:
                p.write_text(text, encoding="utf-8")
    return total


def rebuild_sitemap(dry_run: bool, mtime_cache: dict[str, float] | None = None) -> tuple[int, int]:
    # Build sitemap directly from article files — no longer parses old sitemap.xml
    static_map = {
        f"{SITE}/": ROOT / "index.html",
        f"{SITE}/about/": ROOT / "about.html",
        f"{SITE}/impressum/": ROOT / "impressum.html",
        f"{SITE}/datenschutz/": ROOT / "datenschutz.html",
    }

    article_parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    static_parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # Add all articles
    for p in sorted(ART_DIR.glob("*.html")):
        slug = p.name[:-5]
        loc = f"{SITE}/artikel/{slug}"
        mt = _extract_date_modified(p)
        if mt is None:
            mt = (mtime_cache or {}).get(f"{slug}.html")
        if mt is None:
            mt = p.stat().st_mtime
        new_lastmod = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(mt))
        article_parts.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{new_lastmod}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>"
        )

    article_parts.append("</urlset>")
    article_text = "\n".join(article_parts) + "\n"

    # Add static pages
    for loc, src in static_map.items():
        if not src.exists():
            continue
        mt = (mtime_cache or {}).get(src.name)
        if mt is None:
            mt = src.stat().st_mtime
        new_lastmod = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(mt))
        freq = "daily" if loc == f"{SITE}/" else "monthly"
        prio = "1.0" if loc == f"{SITE}/" else "0.5"
        static_parts.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{new_lastmod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        )

    static_parts.append("</urlset>")
    static_text = "\n".join(static_parts) + "\n"

    # Write sub-sitemaps
    article_file = ROOT / "sitemap-articles.xml"
    static_file = ROOT / "sitemap-static.xml"
    if not dry_run:
        article_file.write_text(article_text, encoding="utf-8")
        static_file.write_text(static_text, encoding="utf-8")

    # Write sitemap index
    mt_now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    index_text = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{SITE}/sitemap-articles.xml</loc>
    <lastmod>{mt_now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>{SITE}/sitemap-static.xml</loc>
    <lastmod>{mt_now}</lastmod>
  </sitemap>
</sitemapindex>
"""
    if not dry_run:
        SITEMAP.write_text(index_text, encoding="utf-8")

    article_dates = re.findall(r"<lastmod>([^<]+)</lastmod>", article_text)
    return len(article_parts) - 3, len(article_dates)


def ping_indexnow() -> dict:
    if not INDEXNOW_KEY:
        return {"status": "skipped", "body": "no INDEXNOW_KEY env var set"}
    payload = {
        "host": "haustierzentrum.com",
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://haustierzentrum.com/{INDEXNOW_KEY}.txt",
        "urlList": [f"{SITE}/sitemap.xml"],
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return {"status": r.status, "body": r.read().decode("utf-8", "ignore")[:200]}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode("utf-8", "ignore")[:200]}
    except Exception as e:
        return {"status": "error", "body": str(e)}


def ping_google() -> dict:
    url = f"https://www.google.com/ping?sitemap={SITE}/sitemap.xml"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return {"status": r.status, "url": url}
    except Exception as e:
        return {"status": "error", "body": str(e), "url": url}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ping", action="store_true")
    args = ap.parse_args()
    print(f"=== _refresh_indexing.py (dry_run={args.dry_run}) ===\n")
    # Cache mtimes BEFORE we modify anything (so sitemap reflects real lastmod)
    mtime_cache = {p.name: p.stat().st_mtime for p in ART_DIR.glob("*.html")}
    for fn in ["index.html", "about.html", "impressum.html", "datenschutz.html"]:
        p = ROOT / fn
        if p.exists():
            mtime_cache[fn] = p.stat().st_mtime
    n = 0
    touched = 0
    for p in sorted(ART_DIR.glob("*.html")):
        c = fix_article_file(p, args.dry_run)
        if c:
            n += c
            touched += 1
    print(f"[1/3] Articles patched: {touched} files, {n} edits")
    n = fix_static_pages(args.dry_run)
    print(f"[2/3] Static pages: {n} href edits")
    kept, dates = rebuild_sitemap(args.dry_run, mtime_cache)
    with open(SITEMAP, encoding="utf-8") as f:
        all_dates = re.findall(r"<lastmod>([^<]+)</lastmod>", f.read())
    print(f"[3/3] Sitemap: {kept} URLs, oldest={min(all_dates) if all_dates else 'n/a'}, newest={max(all_dates) if all_dates else 'n/a'}")
    if args.ping and not args.dry_run:
        print("\n[ping] IndexNow:", ping_indexnow())
        print("[ping] Google:  ", ping_google())
    print("\nDone.")


if __name__ == "__main__":
    main()
