#!/usr/bin/env python3
"""
_inject_feed_link.py — Add <link rel="alternate" type="application/rss+xml">
to every article that doesn't have it yet.

Also adds it to index.html, about.html, impressum.html.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
FEED_LINK = '<link rel="alternate" type="application/rss+xml" title="Haustierzentrum RSS Feed" href="https://haustierzentrum.com/rss.xml">'

# Files to patch
TARGETS = list(ART_DIR.glob("*.html")) + [ROOT / "index.html", ROOT / "about.html", ROOT / "impressum.html", ROOT / "datenschutz.html"]

# Insert the link after <meta name="viewport" ...> if found, else after <head>
INJECT_AFTER = re.compile(r'(<meta name="viewport"[^>]+>)', re.IGNORECASE)
ALREADY_PRESENT = re.compile(r'<link[^>]+rel="alternate"[^>]+type="application/rss\+xml"')

patched = 0
already = 0
missing_files = []
for p in TARGETS:
    if not p.exists():
        missing_files.append(p.name)
        continue
    text = p.read_text(encoding='utf-8')
    if ALREADY_PRESENT.search(text):
        already += 1
        continue
    if INJECT_AFTER.search(text):
        new_text, n = INJECT_AFTER.subn(r'\1\n  ' + FEED_LINK, text, count=1)
    else:
        # Fallback: insert right after <head>
        new_text, n = re.subn(r'(<head[^>]*>)', r'\1\n  ' + FEED_LINK, text, count=1)
    if n:
        p.write_text(new_text, encoding='utf-8')
        patched += 1

print(f"Patched: {patched}")
print(f"Already had feed link: {already}")
print(f"Files missing: {missing_files}")
