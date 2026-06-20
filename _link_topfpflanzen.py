#!/usr/bin/env python3
"""
_link_topfpflanzen.py — Fügt 12 Artikeln einen Crosslink auf
/artikel/katzen-zimmerpflanzen-giftig hinzu.

Strategie:
  - 12 thematisch passende Artikel auswählen (Katzen, Aquarium, Ernährung/BARF,
    Haushalt-Sicherheit)
  - Pro Artikel:
    1. Suche nach kontextuell passender Stelle (Pflanzen/Wohnung/Sicherheit)
    2. Existiert ein solcher Absatz, füge inline <a href> ein (max 1 pro Artikel)
    3. Sonst: füge vor related-posts einen kleinen "Sicherheits-Hinweis" ein
"""
from pathlib import Path
import re

BASE = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART = BASE / "artikel"
TARGET = "katzen-zimmerpflanzen-giftig"
TARGET_URL = "/artikel/katzen-zimmerpflanzen-giftig"
TARGET_TITLE = "Giftige Zimmerpflanzen für Katzen"

# 12 thematisch passende Quell-Artikel
SOURCES = [
    "perserkatze-rasseguide",
    "katzenhaltung-wohnung",
    "britisch-kurzhaar-rasseguide",
    "katzen-freigaenger",
    "katzen-kratzbaum",
    "aquarium-fische-einsteiger",
    "hunde-ernaehrung-barf-trocken-nass",
    "katzen-ernaehrung",
    "hundeernaehrung",
    "haustier-anschaffung",
    "haustiere-kinder",
    "allergiker-haustiere",
]

# Kontext-Phrasen, die wir suchen (priorisiert)
CONTEXT_PHRASES = [
    # cat-related
    (r"\b(Wohnungskatze|Wohnungskatzen)\b", "Für Wohnungskatzen ist auch die Auswahl der {ziel} entscheidend"),
    (r"\b(Sicherheit|sicher|Gefahr|gefährlich)\b", "Was die {ziel} betrifft, solltest du ebenfalls vorsichtig sein"),
    (r"\b(Pflanze|Pflanzen|Topfpflanze)\b", "Auch bei {ziel} ist Vorsicht geboten"),
    (r"\b(Einrichtung|einrichten|eingerichtet)\b", "Wie bei der Ausstattung gehört auch das Thema {ziel} dazu"),
    (r"\b(Anfänger|Einsteiger|erst)\b", "Gerade für Einsteiger ist das Thema {ziel} wichtig"),
    (r"\b(Ernährung|füttern|Futter)\b", "Neben der Ernährung spielt auch das Thema {ziel} eine Rolle"),
]

def has_topfpflanzen_link(html: str) -> bool:
    return TARGET in html

def find_paragraph_with_phrase(html: str) -> str | None:
    """Finde einen <p>-Tag der eine der Kontext-Phrasen enthält."""
    for pattern, _ in CONTEXT_PHRASES:
        # Find all paragraphs
        for m in re.finditer(r'<p>(.*?)</p>', html, re.DOTALL):
            para = m.group(1)
            # Skip if already has a link
            if '<a href' in para: continue
            if re.search(pattern, para, re.IGNORECASE):
                return m.group(0)
    return None

def inject_link_into_paragraph(para: str) -> str:
    """Füge einen Link in den ersten passenden Satz ein."""
    # Suche erstes Vorkommen einer Kontext-Phrase
    for pattern, _ in CONTEXT_PHRASES:
        m = re.search(pattern, para, re.IGNORECASE)
        if m:
            # Finde das Wort und umschließe es mit einem <a>-Tag
            # Original-Wort beibehalten
            start, end = m.span()
            # Finde Wortgrenzen
            before = para[:start]
            match_text = para[start:end]
            after = para[end:]
            # Wenn das Wort mehrfach in der Phrase ist, nimm nur das erste Token
            word_match = re.search(r'\S+', match_text)
            if word_match:
                word = word_match.group(0)
                # Link nur auf das gefundene Wort
                link = f'<a href="{TARGET_URL}" title="{TARGET_TITLE}">{word}</a>'
                new_para = before + link + match_text[len(word):] + after
                return new_para
    return para  # fallback, sollte nicht passieren

def make_callout() -> str:
    """Generiere einen Callout-Block für Artikel ohne passenden Kontext."""
    return (
        f'\n  <aside class="related-note" style="margin:1.5rem 0;padding:1rem 1.2rem;'
        f'background:var(--bg-alt);border-left:4px solid var(--primary);border-radius:0 8px 8px 0;">'
        f'<p style="margin:0"><strong>🌿 Sicherheits-Hinweis:</strong> '
        f'Auch bei der <a href="{TARGET_URL}" title="{TARGET_TITLE}">Wahl der Zimmerpflanzen</a> '
        f'ist Vorsicht geboten — viele beliebte Pflanzen sind für Katzen giftig. '
        f'<a href="{TARGET_URL}" title="{TARGET_TITLE}">Hier findest du eine Liste der 15 gefährlichsten Arten</a>.</p>'
        f'</aside>\n'
    )

def main():
    fixed = 0
    skipped = []
    for slug in SOURCES:
        art = ART / f"{slug}.html"
        if not art.exists():
            skipped.append((slug, "file not found"))
            continue
        with open(art, encoding="utf-8") as f:
            html = f.read()

        if has_topfpflanzen_link(html):
            skipped.append((slug, "already linked"))
            continue

        # Try contextual inline link
        para_match = find_paragraph_with_phrase(html)
        if para_match:
            # Find and inject
            new_para = inject_link_into_paragraph(para_match)
            new_html = html.replace(para_match, new_para, 1)
            if new_html != html:
                with open(art, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                fixed += 1
                print(f"  ✓ {slug}  → inline link injected")
                continue

        # Fallback: callout before related-posts
        if 'class="related-posts"' in html:
            callout = make_callout()
            new_html = html.replace('<section class="related-posts">', callout + '  <section class="related-posts">', 1)
            if new_html != html:
                with open(art, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                fixed += 1
                print(f"  ✓ {slug}  → callout block added")
                continue

        skipped.append((slug, "no insertion point"))
        print(f"  SKIP: {slug}")

    print(f"\n=== Result: {fixed} fixed, {len(skipped)} skipped ===")
    for s, r in skipped:
        print(f"  {s}: {r}")

if __name__ == '__main__':
    main()
