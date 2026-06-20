#!/usr/bin/env python3
"""
_generate_related_posts.py — Fügt <section class="related-posts"> in Artikel ein,
denen sie fehlt.

Algorithmus:
  1. Scanne alle artikel/*.html
  2. Markiere Artikel OHNE <section class="related-posts"> als Kandidaten
  3. Für jeden Kandidaten:
     a) Bestimme Kategorie (Hunde/Katzen/Kleintiere/Vögel/Aquarium/Allgemein)
        anhand articleSection im JSON-LD
     b) Wähle 3 verwandte Artikel aus dem Pool:
        - gleiche Kategorie wenn möglich
        - sonst nächste passende Kategorie
        - niemals sich selbst
     c) Baue HTML-Block mit Standard-SVGs
     d) Injiziere vor </main> oder </article>
  4. Update HTML-Datei atomar

Das CSS für .related-posts existiert bereits in allen Artikeln (von golden-retriever
Template geerbt). Wir müssen NUR den HTML-Block einfügen.
"""
from pathlib import Path
import re, json, sys
from collections import defaultdict

BASE = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART = BASE / "artikel"

# SVG-Icons by category (gleich wie golden-retriever Template)
SVG_PAW = '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="1.5"><circle cx="12" cy="7" r="4"/><path d="M4 21c0-4.418 3.582-8 8-8s8 3.582 8 8"/></svg>'

CATEGORY_SVGS = {
    "Hunde":      '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="1.5"><path d="M4 9c0-2 1-4 4-4s4 2 4 4v3l-2 1v6H6v-6l-2-1z"/><circle cx="10" cy="6" r="1" fill="#bbb"/></svg>',
    "Katzen":     '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="1.5"><path d="M5 4l3 5h8l3-5-1 7v6H6v-6z"/><circle cx="9" cy="14" r=".8" fill="#bbb"/><circle cx="15" cy="14" r=".8" fill="#bbb"/></svg>',
    "Kleintiere": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="1.5"><ellipse cx="12" cy="13" rx="6" ry="5"/><circle cx="9" cy="9" r="1.5"/><circle cx="15" cy="9" r="1.5"/></svg>',
    "Vögel":      '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="1.5"><path d="M3 12c2-4 5-6 9-6s7 2 9 6c-2 4-5 6-9 6s-7-2-9-6z"/><circle cx="16" cy="11" r="1" fill="#bbb"/></svg>',
    "Aquarium":   '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="1.5"><path d="M3 8h18v10H3z"/><path d="M7 8v10M12 8v10M17 8v10"/><path d="M5 18l3-2 3 2 3-2 3 2"/></svg>',
    "default":    SVG_PAW,
}

def get_category(html: str, slug: str) -> str:
    """Extrahiere Kategorie aus JSON-LD articleSection."""
    m = re.search(r'"articleSection":\s*\[?\s*"([^"]+)"', html)
    if m:
        cat = m.group(1)
        # Normalize
        cat_lower = cat.lower()
        if "hund" in cat_lower: return "Hunde"
        if "katz" in cat_lower: return "Katzen"
        if "kleintier" in cat_lower or "hamster" in cat_lower or "meerschwein" in cat_lower or "kaninchen" in cat_lower: return "Kleintiere"
        if "vogel" in cat_lower or "wellensittich" in cat_lower: return "Vögel"
        if "aquarium" in cat_lower or "fisch" in cat_lower: return "Aquarium"
        return cat
    # Fallback by slug
    s = slug.lower()
    if "hund" in s or "welpe" in s or "dog" in s or "whippet" in s: return "Hunde"
    if "katz" in s: return "Katzen"
    if "hamster" in s or "meerschwein" in s or "kaninchen" in s or "kleintier" in s: return "Kleintiere"
    if "vogel" in s or "sittich" in s: return "Vögel"
    if "aquarium" in s or "fisch" in s: return "Aquarium"
    return "Allgemein"

def get_title(html: str) -> str:
    """Extrahiere <h1> aus Artikel."""
    m = re.search(r'<h1>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    # Fallback auf <title>
    m = re.search(r'<title>(.*?)</title>', html)
    if m:
        return m.group(1).split('|')[0].strip().rstrip(' -–')
    return "Artikel"

def get_hero(html: str) -> str:
    """Versuche, Hero-Image-Filename zu extrahieren."""
    m = re.search(r'(?:src|href)="(?:\.\./)?images/([^"]+)"', html)
    if m:
        return m.group(1)
    return ""

def build_related_block(slug: str, related: list, category: str) -> str:
    """Baue <section class="related-posts"> HTML."""
    cards = []
    svg = CATEGORY_SVGS.get(category, CATEGORY_SVGS["default"])
    for r_slug, r_title in related:
        r_title_clean = re.sub(r'<[^>]+>', '', r_title).strip()
        cards.append(
            f'<div class="related-card">'
            f'<div class="card-img">{svg}</div>'
            f'<div class="card-body">'
            f'<h4><a href="/artikel/{r_slug}">{r_title_clean}</a></h4>'
            f'</div></div>'
        )
    grid = ''.join(cards)
    return (
        f'\n  <section class="related-posts">'
        f'<h3>Das könnte Dich auch interessieren</h3>'
        f'<div class="related-grid">{grid}</div>'
        f'</section>\n'
    )

def main():
    # 1. Build full article index
    articles = {}  # slug -> (filepath, title, category, hero)
    for art in sorted(ART.glob("*.html")):
        slug = art.stem
        if slug in ('about', 'impressum', '404', 'index'): continue
        with open(art, encoding="utf-8", errors="ignore") as f:
            html = f.read()
        title = get_title(html)
        category = get_category(html, slug)
        hero = get_hero(html)
        articles[slug] = (art, html, title, category, hero)

    print(f"=== Artikel-Index: {len(articles)} ===\n")

    # 2. Group by category
    by_cat = defaultdict(list)
    for slug, (art, html, title, cat, hero) in articles.items():
        by_cat[cat].append((slug, title))

    for c, items in sorted(by_cat.items()):
        print(f"  {c}: {len(items)}")

    # 3. Find articles without related-posts
    needs_related = []
    for slug, (art, html, title, cat, hero) in articles.items():
        if 'class="related-posts"' not in html and 'class=\'related-posts\'' not in html:
            needs_related.append(slug)

    print(f"\n=== Artikel OHNE related-posts: {len(needs_related)} ===")
    for s in needs_related:
        cat = articles[s][3]
        print(f"  {s}  [{cat}]")

    # 4. For each, pick 3 related articles
    # Strategy: same category first, then fill with other categories
    fixed = 0
    skipped = []
    for slug in needs_related:
        art, html, title, cat, hero = articles[slug]

        # Skip truly broken articles (no H2 = no real content)
        if '<h2' not in html and '<h3' not in html:
            skipped.append((slug, "no body (no h2/h3)"))
            continue

        # Same category, excluding self
        same = [(s, t) for s, t in by_cat.get(cat, []) if s != slug]
        related = same[:3]

        # Fallback: add from other categories
        if len(related) < 3:
            other = []
            for other_cat, items in by_cat.items():
                if other_cat == cat: continue
                other.extend(items)
            # Filter: skip if same slug (shouldn't happen)
            for s, t in other:
                if len(related) >= 3: break
                if s != slug and (s, t) not in related:
                    related.append((s, t))

        if len(related) < 3:
            skipped.append((slug, f"not enough related ({len(related)})"))
            continue

        # 5. Build block
        block = build_related_block(slug, related, cat)

        # 6. Inject before </main> (preferred) or </article> (newer) or <footer> (oldest)
        new_html = None
        if '</main>' in html:
            new_html = html.replace('</main>', block + '</main>', 1)
        elif '</article>' in html:
            new_html = html.replace('</article>', block + '</article>', 1)
        elif '<footer' in html:
            new_html = html.replace('<footer', block + '<footer', 1)

        if new_html is None or new_html == html:
            skipped.append((slug, "no insertion point"))
            continue

        # 7. Save
        with open(art, 'w', encoding='utf-8') as f:
            f.write(new_html)
        fixed += 1
        print(f"  ✓ {slug}  ←  {', '.join(s for s,_ in related)}")

    print(f"\n=== Fixes: {fixed} | Skipped: {len(skipped)} ===")
    for s, reason in skipped:
        print(f"  SKIP: {s}  ({reason})")

if __name__ == '__main__':
    main()
