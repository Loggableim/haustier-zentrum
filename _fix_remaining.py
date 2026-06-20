#!/usr/bin/env python3
"""_fix_remaining.py — Fix remaining issues across articles."""
import re
from pathlib import Path

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"

HEALTH_ARTICLES = [
    "erste-hilfe-haustiere-notfall-ratgeber",
    "hunde-krankheiten-symptome-erste-hilfe",
    "hunde-hausmittel",
    "hunde-gesundheit",
    "hundeallergien",
    "hunde-uebergewicht",
    "hunde-zahnpflege",
    "hundeernaehrung",
    "hunde-ernaehrung-barf-trocken-nass",
    "katzenkrankheiten-erkennen",
    "katzen-impfungen-vorsorge",
    "katzen-kastration-sterilisation",
    "katzen-ernaehrung",
    "katzen-zahnpflege",
    "katzenfutter-selber-machen",
    "katzenfutter-vergleich-2026",
    "allergiker-haustiere",
    "allergien-bei-hund-und-katze-2026-umwelt-futter-und-fell-ganzheitliche-strategie",
    "kaninchen-ernaehrung-gesundheit",
    "meerschweinchen-ernaehrung-vitamin-c",
    "seniorkatzen-pflege-ernaehrung-gesundheit",
    "tierarztkosten",
    "zeckenschutz-flohschutz-hund",
    "hundeversicherung",
    "wellensittich-ernaehrung-gesundheit",
    "wellensittich-ernaehrung-futter",
    "ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-fruehzeitig-erkennen-und-",
    "kleintier-gesundheit-2026-warum-meerschweinchen-kaninchen-und-hamster-mehr-tiera",
    "notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte",
    "naehrstoff-kompass-2026-so-waehlen-sie-das-richtige-futter-fuer-hund-katze-und-k",
    "stille-signale-erkennen-wie-hunde-und-katzen-schmerzen-zeigen-und-was-halter-202",
    "altersgerechte-haltung-2026-welche-beduerfnisse-hunde-katzen-und-kleintiere-im-l",
]

EMERGENCY_ARTICLES = [
    "erste-hilfe-haustiere-notfall-ratgeber",
    "hunde-krankheiten-symptome-erste-hilfe",
    "hunde-hausmittel",
    "notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte",
]

HEALTH_DISCLAIMER = (
    '<!-- MEDICAL DISCLAIMER -->'
    '<div class="health-disclaimer" style="background:#fff3e0;border-left:4px solid #FF9800;padding:1rem 1.2rem;margin-bottom:1.5rem;border-radius:0 8px 8px 0;font-size:.9rem;">'
    '<strong>\u26a0\ufe0f Wichtiger Hinweis:</strong> Dieser Artikel dient nur zu Informationszwecken und ersetzt <strong>keine tierärztliche Beratung, Diagnose oder Behandlung</strong>. '
    'Bei gesundheitlichen Problemen Ihres Tieres wenden Sie sich bitte umgehend an einen Tierarzt.'
    '</div>'
)

EMERGENCY_NOTICE = (
    '<!-- EMERGENCY NOTICE -->'
    '<div class="emergency-notice" style="background:#fdecea;border-left:4px solid #d32f2f;padding:1rem 1.2rem;margin-bottom:1.5rem;border-radius:0 8px 8px 0;font-size:.9rem;">'
    '<strong>\U0001f6a8 Notfall?</strong> Bei akuten Symptomen wie Atemnot, Krampfanfällen, starken Blutungen oder Vergiftungsverdacht '
    'zögern Sie nicht \u2013 fahren Sie sofort zum nächsten Tierarzt oder zur Tierklinik!'
    '</div>'
)

stats = {"nav": 0, "footer": 0, "health": 0, "emergency": 0, "adsense": 0, "cookie_banner": 0}

for p in sorted(ART_DIR.glob("*.html")):
    text = p.read_text(encoding="utf-8")
    original = text
    slug = p.name[:-5]

    # Fix 1: Nav — add Datenschutz if Impressum exists but no Datenschutz
    if 'simple-link' in text and 'Impressum' in text and 'Datenschutz' not in text:
        text, n = re.subn(
            r'(<li class="simple-link"><a href="/impressum\.html"[^>]*>Impressum</a></li>)',
            r'\1\n        <li class="simple-link"><a href="/datenschutz.html">Datenschutz</a></li>',
            text, count=1
        )
        stats["nav"] += n

    # Fix 2: Footer — add Datenschutz if missing
    if 'Über uns' in text and 'Impressum' in text and '/datenschutz.html' not in text:
        text, n = re.subn(
            r'(<a href="/about\.html">Über uns</a> &middot; <a href="/impressum\.html">Impressum</a>)( &middot; <a href="/sitemap\.xml">Sitemap</a>)?',
            lambda m: m.group(1) + ' &middot; <a href="/datenschutz.html">Datenschutz</a>' + (m.group(2) if m.group(2) else ''),
            text, count=1
        )
        stats["footer"] += n

    # Fix 3: Health disclaimer for articles that missed it
    if slug in HEALTH_ARTICLES and 'MEDICAL DISCLAIMER' not in text:
        # Try multiple insertion patterns
        patterns = [
            r'(<main>)\r?\n\s*(<)',
            r'(<main>)\s*(<)',
            r'(</header>)\s*\n?\s*(<div class="info-page"|<main)',
            r'(<div class="article-content">)\s*',
            r'(<section[^>]*>)\s*',
        ]
        for pat in patterns:
            text, n = re.subn(pat, lambda m: m.group(1) + '\n' + HEALTH_DISCLAIMER + '\n' + (m.group(2) if len(m.groups()) > 1 else ''), text, count=1)
            if n:
                stats["health"] += 1
                break

    # Fix 4: Emergency notice
    if slug in EMERGENCY_ARTICLES and 'EMERGENCY NOTICE' not in text:
        text, n = re.subn(
            r'(<main>)\r?\n\s*(<)',
            r'\1\n' + EMERGENCY_NOTICE + r'\n\2',
            text, count=1
        )
        stats["emergency"] += n

    # Fix 5: AdSense consent (if still unconditional)
    if 'pagead2.googlesyndication.com' in text and 'cookieConsent' not in text:
        text, n = re.subn(
            r'<script async src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=ca-pub-9094916118868532"[^>]*></script>',
            '<script>if(localStorage.getItem(\'cookieConsent\')===\'accepted\'){var s=document.createElement(\'script\');s.async=true;s.src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9094916118868532";s.crossOrigin="anonymous";document.head.appendChild(s);}</script>',
            text, count=1
        )
        stats["adsense"] += n

    # Fix 6: Add cookie banner if completely missing (for articles with footer)
    if 'cookieBanner' not in text and 'site-footer' in text:
        cookie_btn = '<div class="cookie-banner" id="cookieBanner"><p>🍪 Diese Website verwendet Cookies und technisch notwendige Funktionen. Mit Klick auf "Akzeptieren" stimmen Sie auch der Nutzung von Analyse- und Werbe-Cookies (AdSense, Amazon) zu. <a href="/datenschutz.html" style="color:#FFB74D;">Mehr Infos</a></p><button onclick="window.acceptCookies()">Akzeptieren</button><button onclick="window.declineCookies()" style="background:#555;">Ablehnen</button></div>'
        text, n = re.subn(r'(</footer>)', r'\1' + cookie_btn, text, count=1)
        stats["cookie_banner"] += n

    if text != original:
        p.write_text(text, encoding="utf-8")

print(f"=== Remaining Fixes Results ===")
for k, v in stats.items():
    print(f"  {k}: {v}")
print("Done.")
