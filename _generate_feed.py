#!/usr/bin/env python3
"""
_generate_feed.py — Build /feed.xml (RSS 2.0 + Atom self-link + content module).

Source: artikel/*.html (title, description, JSON-LD, body)
Output: feed.xml

Standards:
- RSS 2.0 (https://validator.w3.org/feed/docs/rss2.0.html)
- atom:link rel="self" (RFC 4287)
- content:encoded (https://www.rssboard.org/rss-specification#ltcontentgt)

Reader compatibility: Feedly, NetNewsWire, Inoreader, Feedbin, etc.
"""
from __future__ import annotations
import argparse
import json
import re
import time
from html import escape
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
FEED = ROOT / "rss.xml"
SITE = "https://haustierzentrum.com"
SITE_TITLE = "Haustierzentrum"
SITE_DESC = "Dein Ratgeber für artgerechte Haustierhaltung – Hunde, Katzen, Kleintiere, Vögel, Aquarium. Rasseporträts, Erziehung, Gesundheit und Produktvergleiche."
SITE_LANG = "de-DE"
SITE_COPYRIGHT = f"© {time.strftime('%Y')} Haustierzentrum"
MAX_ITEMS = 40
MAX_CONTENT_CHARS = 3000  # keep feed size reasonable


def xml_escape(s: str) -> str:
    """Escape text for XML element content (preserves nothing)."""
    if s is None:
        return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))


def cdata(s: str) -> str:
    """Wrap content in CDATA, escaping any embedded ']]>'."""
    if s is None:
        return ""
    return s.replace("]]>", "]]&gt;")


def parse_iso_date(s: str) -> datetime | None:
    """Parse YYYY-MM-DD or full ISO into aware UTC datetime."""
    if not s:
        return None
    s = s.strip()
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
            return datetime(int(s[:4]), int(s[5:7]), int(s[8:10]), tzinfo=timezone.utc)
        # ISO with time
        s2 = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s2)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def to_rfc822(dt: datetime | None) -> str:
    """RSS requires RFC-822 dates."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return format_datetime(dt, usegmt=True)


def extract_main_text(html: str) -> str:
    """Extract main article body, strip nav/aside/footer/script, return HTML subset."""
    # Find <main> or <article>
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL | re.IGNORECASE)
    if not m:
        m = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL | re.IGNORECASE)
    body = m.group(1) if m else html
    # Remove nav, aside, footer, script, style, header
    body = re.sub(r'<(nav|aside|footer|script|style|header)[^>]*>.*?</\1>', '', body, flags=re.DOTALL | re.IGNORECASE)
    # Remove ads/related-posts/comments
    body = re.sub(r'<div[^>]*class="[^"]*(?:ad|related|comment|cookie|consent|nav|mega|hero|footer)[^"]*"[^>]*>.*?</div>', '', body, flags=re.DOTALL | re.IGNORECASE)
    # Remove inline event handlers (for safety in feed readers)
    body = re.sub(r' on[a-z]+="[^"]*"', '', body, flags=re.IGNORECASE)
    body = re.sub(r'\s+on[a-z]+=\'[^\']*\'', '', body, flags=re.IGNORECASE)
    return body.strip()


def article_metadata(p: Path) -> dict | None:
    """Read one article and return dict for feed entry, or None if invalid."""
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return None
    slug = p.name[:-5]

    # Title: <title> tag, drop " | Haustierzentrum" suffix
    m = re.search(r"<title>([^<]+)</title>", text)
    if not m:
        return None
    title = m.group(1).replace(" | Haustierzentrum", "").strip()
    if not title:
        return None

    # Description: meta description
    m = re.search(r'<meta name="description" content="([^"]+)"', text)
    description = m.group(1) if m else ""

    # JSON-LD
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.DOTALL)
    date_pub = None
    date_mod = None
    image = None
    category = None
    if m:
        try:
            d = json.loads(m.group(1))
        except Exception:
            d = {}
        date_pub = parse_iso_date(d.get("datePublished", ""))
        date_mod = parse_iso_date(d.get("dateModified", ""))
        image = d.get("image", "")
        sec = d.get("articleSection")
        if isinstance(sec, list) and sec:
            category = sec[0]
        elif isinstance(sec, str):
            category = sec

    # Fallbacks
    if not date_pub:
        # Try og:article:published_time
        m = re.search(r'<meta property="article:published_time" content="([^"]+)"', text)
        if m:
            date_pub = parse_iso_date(m.group(1))
    if not date_pub:
        return None  # can't sort without a date

    # Body for content:encoded
    body_html = extract_main_text(text)
    # Truncate intelligently
    if len(body_html) > MAX_CONTENT_CHARS:
        # Cut at last </p> before limit
        cut = body_html[:MAX_CONTENT_CHARS]
        last_p = cut.rfind("</p>")
        if last_p > 0:
            body_html = cut[:last_p + 4] + '\n<p><em>[...]</em></p>'
        else:
            body_html = cut + "..."

    # Canonical link
    link = f"{SITE}/artikel/{slug}"

    return {
        "title": title,
        "link": link,
        "guid": link,
        "pub": date_pub,
        "mod": date_mod or date_pub,
        "description": description,
        "category": category,
        "image": image,
        "content_html": body_html,
    }


def build_feed() -> str:
    items = []
    for p in ART_DIR.glob("*.html"):
        m = article_metadata(p)
        if m:
            items.append(m)
    # Sort newest first
    items.sort(key=lambda x: x["pub"], reverse=True)
    items = items[:MAX_ITEMS]

    now = datetime.now(timezone.utc)
    build_date = to_rfc822(now)
    last_article_date = to_rfc822(items[0]["pub"]) if items else build_date

    # Image: use last article's image, or fallback
    image_url = ""
    for it in items:
        if it.get("image"):
            image_url = it["image"]
            break
    if not image_url:
        image_url = f"{SITE}/images/labrador-retriever_00001_.webp"

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">')
    lines.append('  <channel>')
    lines.append(f'    <title>{xml_escape(SITE_TITLE)}</title>')
    lines.append(f'    <link>{SITE}/</link>')
    lines.append(f'    <description>{xml_escape(SITE_DESC)}</description>')
    lines.append(f'    <language>{SITE_LANG}</language>')
    lines.append(f'    <copyright>{xml_escape(SITE_COPYRIGHT)}</copyright>')
    lines.append(f'    <lastBuildDate>{build_date}</lastBuildDate>')
    lines.append(f'    <pubDate>{last_article_date}</pubDate>')
    lines.append(f'    <ttl>180</ttl>')  # 3 hours
    lines.append('    <atom:link href="https://haustierzentrum.com/rss.xml" rel="self" type="application/rss+xml"/>')
    lines.append('    <image>')
    lines.append(f'      <url>{xml_escape(image_url)}</url>')
    lines.append(f'      <title>{xml_escape(SITE_TITLE)}</title>')
    lines.append(f'      <link>{SITE}/</link>')
    lines.append('    </image>')

    for it in items:
        lines.append('    <item>')
        lines.append(f'      <title>{xml_escape(it["title"])}</title>')
        lines.append(f'      <link>{it["link"]}</link>')
        lines.append(f'      <guid isPermaLink="true">{it["guid"]}</guid>')
        lines.append(f'      <pubDate>{to_rfc822(it["pub"])}</pubDate>')
        if it.get("category"):
            lines.append(f'      <category>{xml_escape(it["category"])}</category>')
        if it.get("description"):
            lines.append(f'      <description>{xml_escape(it["description"])}</description>')
        if it.get("image"):
            # media:content (RSS extension) is widely supported
            lines.append(f'      <enclosure url="{xml_escape(it["image"])}" type="image/webp" length="0"/>')
        # content:encoded (HTML)
        if it.get("content_html"):
            lines.append(f'      <content:encoded><![CDATA[{cdata(it["content_html"])}]]></content:encoded>')
        lines.append('    </item>')

    lines.append('  </channel>')
    lines.append('</rss>')
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    print(f"=== _generate_feed.py (dry_run={args.dry_run}) ===")
    xml = build_feed()
    size_kb = len(xml.encode("utf-8")) / 1024
    item_count = xml.count("<item>")
    print(f"  Items: {item_count}")
    print(f"  Size:  {size_kb:.1f} KB")
    if not args.dry_run:
        FEED.write_text(xml, encoding="utf-8")
        print(f"  Wrote: {FEED}")
    print("Done.")


if __name__ == "__main__":
    main()
