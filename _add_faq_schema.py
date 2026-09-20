#!/usr/bin/env python3
"""
_add_faq_schema.py — Inject FAQPage JSON-LD into articles that have FAQ
sections (class="faq-item") but no FAQPage schema.

Google shows FAQ rich snippets only when FAQPage structured data is present.
The FAQ content already exists in the HTML — this just makes it machine-readable.

Usage: python _add_faq_schema.py [--dry-run]
"""
import argparse
import json
import re
from pathlib import Path

ART_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\artikel")

FAQ_ITEM_RE = re.compile(
    r'<div class="faq-item">\s*<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>',
    re.DOTALL,
)


def strip_tags(s: str) -> str:
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def build_faq_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in items
        ],
    }


def fix_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")

    if '"FAQPage"' in text:
        return 0  # already has FAQ schema

    items = FAQ_ITEM_RE.findall(text)
    if not items:
        return 0

    cleaned = [(strip_tags(q), strip_tags(a)) for q, a in items]
    cleaned = [(q, a) for q, a in cleaned if q and a]
    if len(cleaned) < 2:
        return 0

    schema = build_faq_schema(cleaned)
    script = ('<script type="application/ld+json">\n'
              + json.dumps(schema, ensure_ascii=False, indent=2)
              + '\n</script>')

    # Insert right before </head>
    if '</head>' in text:
        text = text.replace('</head>', script + '\n</head>', 1)
    else:
        return 0

    if not dry_run:
        path.write_text(text, encoding="utf-8")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total = 0
    for f in sorted(ART_DIR.glob("*.html")):
        c = fix_file(f, args.dry_run)
        if c:
            total += 1
            print(f"  {'[dry-run] ' if args.dry_run else ''}FAQPage added: {f.name}")

    print(f"{'[dry-run] ' if args.dry_run else ''}Total: {total} articles")


if __name__ == "__main__":
    main()
