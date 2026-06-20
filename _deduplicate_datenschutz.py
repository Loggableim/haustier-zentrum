#!/usr/bin/env python3
"""_deduplicate_datenschutz.py — Remove duplicate Datenschutz entries from all files."""
import re
from pathlib import Path

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
STATIC_FILES = ["index.html", "about.html", "impressum.html", "datenschutz.html"]

stats = {"nav": 0, "footer": 0}

for p in sorted(ART_DIR.glob("*.html")) + [ROOT / f for f in STATIC_FILES if (ROOT / f).exists()]:
    text = p.read_text(encoding="utf-8")
    original = text

    # Nav: remove duplicate Datenschutz lines
    text, n = re.subn(
        r'(<li class="simple-link"><a href="/datenschutz\.html"[^>]*>Datenschutz</a></li>\s*){2,}',
        r'\1',
        text
    )
    stats["nav"] += n

    # Footer: fix "Datenschutz &middot; Datenschutz" -> single
    text, n = re.subn(
        r'<a href="/datenschutz\.html">Datenschutz</a> &middot; <a href="/datenschutz\.html">Datenschutz</a>',
        '<a href="/datenschutz.html">Datenschutz</a>',
        text
    )
    stats["footer"] += n

    # Also fix any "&middot; Datenschutz &middot; Datenschutz" pattern
    text, n = re.subn(
        r'(&middot; <a href="/datenschutz\.html">Datenschutz</a>)\s*&middot;\s*<a href="/datenschutz\.html">Datenschutz</a>',
        r'\1',
        text
    )
    # Already counted by the footer counter above

    if text != original:
        p.write_text(text, encoding="utf-8")

print(f"Deduplication results:")
print(f"  Nav duplicates removed: {stats['nav']}")
print(f"  Footer duplicates removed: {stats['footer']}")
print("Done.")
