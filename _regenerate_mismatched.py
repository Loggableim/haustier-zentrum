#!/usr/bin/env python3
"""
_regenerate_mismatched.py — Regenerate articles whose body content does not
match their title/slug (root cause: content_factory.py generated text without
passing the topic to the LLM).

Usage:
  python _regenerate_mismatched.py --list          # show mismatched articles
  python _regenerate_mismatched.py --slug <slug>   # regenerate one article
  python _regenerate_mismatched.py --all           # regenerate all mismatched
"""
import argparse
import re
import sys
from datetime import datetime

sys.path.insert(0, "C:/sidekick/home/spaces/haustier-zentrum")
from content_factory import TOPICS, build_html, generate_text, validate_topic_match

REPO = "C:/sidekick/home/spaces/haustier-zentrum"

# Articles whose body content does not match the title (verified 2026-09-20)
MISMATCHED = [
    "aquarium-pflanzen-einsteiger",
    "chinchilla-ernaehrung-futter",
    "dog-sitting-hundesitter-finden",
    "hamster-ernaehrung-futterplan",
    "hundeangst-training-tipps",
    "katzen-kratzmoebel-test",
    "katzen-zimmerpflanzen-giftig",
    "katzenfreundliche-wohnung-gestalten",
    "vogelvoliere-kaufen-checkliste",
    "welpenschule-finden-kosten",
    "whippet-rasseguide",
]


def get_topic(slug):
    for t in TOPICS:
        if t["slug"] == slug:
            return t
    return None


def extract_body(html):
    """Extract the article-content div from existing HTML."""
    start = html.find('<div class="article-content">')
    end = html.find('</article>')
    if start == -1 or end == -1:
        return None
    return html[start:end]


def replace_body(html, new_body):
    """Replace the article-content div in existing HTML."""
    start = html.find('<div class="article-content">')
    end = html.find('</article>')
    if start == -1 or end == -1:
        return None
    return html[:start] + new_body + html[end:]


def regenerate(slug, dry_run=False):
    topic = get_topic(slug)
    if not topic:
        print(f"❌ Kein Topic-Eintrag für {slug}")
        return False

    path = f"{REPO}/artikel/{slug}.html"
    with open(path, encoding="utf-8") as f:
        old_html = f.read()

    print(f"\n{'='*60}")
    print(f"🔄 Regeneriere: {slug}")
    print(f"   Titel: {topic['title']}")

    body = generate_text(topic)
    if not body:
        print(f"❌ Generierung fehlgeschlagen für {slug}")
        return False

    # Wrap in article-content div (generate_text returns inner fragment)
    new_body = f'<div class="article-content">\n{body}\n    '

    new_html = replace_body(old_html, new_body)
    if not new_html:
        print(f"❌ Konnte article-content div nicht ersetzen in {slug}")
        return False

    # Update dateModified in JSON-LD
    today_iso = datetime.now().strftime("%Y-%m-%d")
    new_html = re.sub(
        r'"dateModified":\s*"[^"]*"',
        f'"dateModified": "{today_iso}"',
        new_html, count=1,
    )

    if dry_run:
        print(f"   [dry-run] Würde {len(new_html)} Bytes schreiben")
        return True

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"   ✅ Gespeichert ({len(new_html)//1024}KB)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="Comma-separated slugs to process")
    args = ap.parse_args()

    if args.list:
        for slug in MISMATCHED:
            t = get_topic(slug)
            print(f"  {slug}  →  {t['title'] if t else '(kein Topic!)'}")
        return 0

    if args.slug:
        ok = regenerate(args.slug, args.dry_run)
        return 0 if ok else 1

    if args.all or args.only:
        slugs = args.only.split(",") if args.only else MISMATCHED
        results = []
        for slug in slugs:
            slug = slug.strip()
            # Skip articles already regenerated (dateModified = today)
            path = f"{REPO}/artikel/{slug}.html"
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                if '"dateModified": "2026-09-20"' in content or '"dateModified":"2026-09-20"' in content:
                    print(f"⏭  {slug} bereits regeneriert — übersprungen")
                    results.append((slug, True))
                    continue
            except FileNotFoundError:
                pass
            ok = regenerate(slug, args.dry_run)
            results.append((slug, ok))
        print(f"\n{'='*60}")
        print("ZUSAMMENFASSUNG:")
        for slug, ok in results:
            print(f"  {'✅' if ok else '❌'} {slug}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
