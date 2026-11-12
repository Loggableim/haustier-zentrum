#!/usr/bin/env python3
"""
_fix_eeat.py — Remove harmful E-E-A-T signals from all articles.

Problems fixed:
1. Visible "(noch nicht geprüft)" reviewer text — actively tells Google the
   content is unreviewed. Replace the whole author box with a clean
   editorial attribution.
2. Empty JSON-LD fields: "reviewer": {"name": ""} and "sources": [] —
   empty structured-data values are worse than absent ones.
3. "Alle Preise und Angaben ohne Gewaehr" → proper umlaut "Gewähr".

JSON-LD edits are applied ONLY inside <script type="application/ld+json">
blocks to avoid touching page JS.

Usage: python _fix_eeat.py [--dry-run]
"""
import argparse
import json
import re
from pathlib import Path

ART_DIR = Path(r"C:\sidekick\home\spaces\haustier-zentrum\artikel")

OLD_BOX_RE = re.compile(
    r'<div class="author-reviewer-box"[^>]*>'
    r'<p><strong>Autor:</strong> Haustierzentrum Redaktion</p>'
    r'<p><strong>Reviewer:</strong> \(noch nicht geprüft\)</p>'
    r'<p><strong>Letztes Review:</strong> ([0-9-]+)</p>'
    r'</div>',
    re.DOTALL,
)

NEW_BOX = (
    '<div class="author-reviewer-box" style="border-top:1px solid #ccc;'
    'padding-top:1rem;margin-top:1rem;">'
    '<p><strong>Autor:</strong> Haustierzentrum Redaktion</p>'
    '<p><strong>Stand:</strong> {date}</p>'
    '</div>'
)

JSONLD_RE = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)',
    re.DOTALL,
)


def clean_jsonld(blob: str) -> tuple[str, int]:
    """Remove empty reviewer/sources fields from a JSON-LD blob."""
    changes = 0
    try:
        data = json.loads(blob)
    except Exception:
        # Fall back to regex if not parseable
        new, n = re.subn(r',?\s*"reviewer":\s*\{\s*"@type":\s*"Person",\s*"name":\s*""\s*\}', '', blob)
        new, n2 = re.subn(r',?\s*"sources":\s*\[\s*\]', '', new)
        return new, n + n2

    def strip_empty(o):
        nonlocal changes
        if isinstance(o, dict):
            if o.get("reviewer") == {"@type": "Person", "name": ""}:
                del o["reviewer"]
                changes += 1
            if o.get("sources") == []:
                del o["sources"]
                changes += 1
            for v in list(o.values()):
                strip_empty(v)
        elif isinstance(o, list):
            for v in o:
                strip_empty(v)

    strip_empty(data)
    if changes:
        return json.dumps(data, ensure_ascii=False, indent=2), changes
    return blob, 0


def fix_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    changes = 0

    # 1. Replace the harmful author box
    m = OLD_BOX_RE.search(text)
    if m:
        date = m.group(1)
        text = text[:m.start()] + NEW_BOX.format(date=date) + text[m.end():]
        changes += 1

    # 2. Clean JSON-LD blocks (only inside script tags)
    def _sub(m):
        nonlocal changes
        new_blob, n = clean_jsonld(m.group(2))
        changes += n
        return m.group(1) + new_blob + m.group(3)

    text = JSONLD_RE.sub(_sub, text)

    # 3. Fix "Gewaehr" → "Gewähr" (visible text)
    text, n = re.subn(r'ohne Gewaehr', 'ohne Gewähr', text)
    changes += n

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
