#!/usr/bin/env python3
"""_bulk_fix_articles.py — Mass fixes for all article pages (minified HTML)."""
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

stats = {"nav": 0, "footer": 0, "cookie_banner_link": 0, "cookie_banner_btn": 0, "cookie_script": 0, "health": 0, "emergency": 0, "adsense": 0}

for p in sorted(ART_DIR.glob("*.html")):
    text = p.read_text(encoding="utf-8")
    original = text
    slug = p.name[:-5]

    # FIX 1: Nav — add Datenschutz after Impressum
    text, n = re.subn(
        r'(<li class="simple-link"><a href="/impressum\.html"[^>]*>Impressum</a></li>)',
        r'\1\n        <li class="simple-link"><a href="/datenschutz.html">Datenschutz</a></li>',
        text, count=1
    )
    stats["nav"] += n

    # FIX 2: Footer — add Datenschutz between Impressum and Sitemap  
    text, n = re.subn(
        r'(<a href="/about\.html">Über uns</a> &middot; <a href="/impressum\.html">Impressum</a>)( &middot; <a href="/sitemap\.xml">Sitemap</a>)?',
        lambda m: m.group(1) + ' &middot; <a href="/datenschutz.html">Datenschutz</a>' + (m.group(2) if m.group(2) else ''),
        text, count=1
    )
    stats["footer"] += n

    # FIX 3: Cookie banner link /impressum → /datenschutz
    text, n = re.subn(
        r'<a href="/impressum\.html" style="color:#FFB74D;">Mehr Infos</a>',
        '<a href="/datenschutz.html" style="color:#FFB74D;">Mehr Infos</a>',
        text
    )
    stats["cookie_banner_link"] += n

    # FIX 4: Cookie banner — one-line Akzeptieren button → two buttons
    text, n = re.subn(
        r'<button onclick="localStorage\.setItem\(\'cookieConsent\',\'1\'\);document\.getElementById\(\'cookieBanner\'\)\.classList\.remove\(\'show\'\)">Akzeptieren</button>',
        '<button onclick="window.acceptCookies()">Akzeptieren</button><button onclick="window.declineCookies()" style="background:#555;">Ablehnen</button>',
        text, count=1
    )
    stats["cookie_banner_btn"] += n

    # FIX 5: Cookie script block (multi-line, handle \r\n)
    text, n = re.subn(
        r'<script>\r?\n// Cookie-Consent: Banner nur anzeigen wenn nicht bereits akzeptiert\r?\nif\(!localStorage\.getItem\(\'cookieConsent\'\)\){\r?\n  document\.getElementById\(\'cookieBanner\'\)\?\.classList\.add\(\'show\'\);\r?\n}\r?\n</script>',
        '<script>\n// Cookie-Consent-Management\nwindow.cookieState = localStorage.getItem(\'cookieConsent\');\n\nwindow.acceptCookies = function() {\n  localStorage.setItem(\'cookieConsent\', \'accepted\');\n  document.getElementById(\'cookieBanner\').classList.remove(\'show\');\n};\n\nwindow.declineCookies = function() {\n  localStorage.setItem(\'cookieConsent\', \'declined\');\n  document.getElementById(\'cookieBanner\').classList.remove(\'show\');\n};\n\nif (!window.cookieState) {\n  document.addEventListener(\'DOMContentLoaded\', function() {\n    document.getElementById(\'cookieBanner\')?.classList.add(\'show\');\n  });\n}\n</script>',
        text, count=1
    )
    stats["cookie_script"] += n

    # FIX 6: Health disclaimer
    if slug in HEALTH_ARTICLES and HEALTH_DISCLAIMER not in text:
        text, n = re.subn(
            r'(<main>)\r?\n\s*(<)',
            r'\1\n' + HEALTH_DISCLAIMER + r'\n\2',
            text, count=1
        )
        stats["health"] += n

    # FIX 7: Emergency notice
    if slug in EMERGENCY_ARTICLES and EMERGENCY_NOTICE not in text:
        text, n = re.subn(
            r'(<main>)\r?\n\s*(<)',
            r'\1\n' + EMERGENCY_NOTICE + r'\n\2',
            text, count=1
        )
        stats["emergency"] += n

    # FIX 8: Make AdSense conditional
    text, n = re.subn(
        r'<script async src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=ca-pub-9094916118868532"[^>]*></script>',
        '<script>if(localStorage.getItem(\'cookieConsent\')===\'accepted\'){var s=document.createElement(\'script\');s.async=true;s.src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9094916118868532";s.crossOrigin="anonymous";document.head.appendChild(s);}</script>',
        text, count=1
    )
    stats["adsense"] += n

    if text != original:
        p.write_text(text, encoding="utf-8")

print(f"=== Bulk Fix Results ===")
for k, v in stats.items():
    print(f"  {k}: {v}")
print("Done.")
