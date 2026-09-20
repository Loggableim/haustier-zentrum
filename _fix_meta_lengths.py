#!/usr/bin/env python3
"""
_fix_meta_lengths.py — Truncate <title> and meta description to SERP limits.

Google truncates:
  - <title> at ~60 chars
  - meta description at ~160 chars

Only touches the SERP-facing <title> and <meta name="description">.
og:title / twitter:title / JSON-LD headline keep their full length
(social previews have more room).

Usage: python _fix_meta_lengths.py [--dry-run]
"""
import argparse
import html as htmllib
import re
from pathlib import Path

ART_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\artikel")
MAX_TITLE = 60
MAX_DESC = 160


def truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    cut = s[:max_len - 1]
    last_space = cut.rfind(' ')
    if last_space > max_len * 0.6:
        cut = cut[:last_space]
    return cut.rstrip(' –-·|') + '…'


def fix_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0

    # 1. <title>
    m = re.search(r'<title>([^<]*)</title>', text)
    if m:
        raw = m.group(1)
        decoded = htmllib.unescape(raw)
        if len(decoded) > MAX_TITLE:
            new_title = truncate(decoded, MAX_TITLE)
            # Re-escape for HTML
            new_title_esc = new_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text = text[:m.start()] + f'<title>{new_title_esc}</title>' + text[m.end():]
            changes += 1

    # 2. meta description
    m = re.search(r'<meta name="description" content="([^"]*)"', text)
    if m:
        raw = m.group(1)
        decoded = htmllib.unescape(raw)
        if len(decoded) > MAX_DESC:
            new_desc = truncate(decoded, MAX_DESC)
            new_desc_esc = new_desc.replace('&', '&amp;').replace('"', '&quot;')
            text = text[:m.start()] + f'<meta name="description" content="{new_desc_esc}"' + text[m.end():]
            changes += 1

    if changes and not dry_run:
        path.write_text(text, encoding="utf-8")
    return changes


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

    print(f"{'[dry-run] ' if args.dry_run else ''}Fixed {total_files} files, {total_changes} edits")


if __name__ == "__main__":
    main()
