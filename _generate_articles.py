#!/usr/bin/env python3
"""Generate 3 SEO-optimized blog articles for haustierzentrum.com via OpenRouter API."""

import json
import os
import re
import sys
import time
import urllib.request

REPO = "C:/HermesPortable/home/scripts/blog-automation/haustier-zentrum"
IMAGES = os.path.join(REPO, "images")
os.chdir(REPO)

# Load OpenRouter key from auth.json
with open("C:/HermesPortable/home/auth.json", encoding="utf-8") as f:
    auth = json.load(f)
or_key = auth["credential_pool"]["openrouter"][0]["access_token"]

HEADERS = {
    "Authorization": f"Bearer {or_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://haustierzentrum.com",
    "X-Title": "Haustierzentrum Content Factory",
}

OR_BASE = "https://openrouter.ai/api/v1/chat/completions"

def or_chat(system, user, model="openrouter/auto", max_tokens=8192, temp=0.7):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temp,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(OR_BASE, data=data, headers=HEADERS, method="POST")
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=300)
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠ Attempt {attempt+1} failed: {e}")
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
    return ""

def build_html(title, slug, body, category_tags, description, today_str, related_links):
    """Build a complete HTML article matching haustierzentrum breed guide template."""
    
    # Determine primary category for nav active state
    cats_lower = [c.lower() for c in category_tags]
    nav_active = ""
    if "hunde" in cats_lower:
        nav_active = """<li><a href="/artikel/hunderassen-anfaenger.html" class="active">Hunde</a></li>"""
    elif "katzen" in cats_lower:
        nav_active = """<li><a href="/artikel/katzenhaltung-wohnung.html" class="active">Katzen</a></li>"""
    else:
        nav_active = """<li><a href="/">Start</a></li>"""
    
    img_path = f"../images/hero-{slug}.webp"
    og_image_url = f"https://haustierzentrum.com/images/{slug}_00001_.webp"
    canonical = f"https://haustierzentrum.com/artikel/{slug}.html"
    
    # Build category labels for the blog card
    cat_spans = "".join(f'<span>{c}</span>' for c in category_tags)
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Haustierzentrum</title>
<meta name="description" content="{description[:155]}">
<meta property="og:title" content="{title} | Haustierzentrum">
<meta property="og:description" content="{description[:155]}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:image" content="{og_image_url}">
<meta property="og:site_name" content="Haustierzentrum">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title}",
  "description": "{description[:155]}",
  "author": {{"@type":"Person","name":"Haustierzentrum Redaktion"}},
  "datePublished": "{today_str}",
  "dateModified": "{today_str}",
  "image": "{og_image_url}",
  "publisher": {{"@type":"Organization","name":"Haustierzentrum","url":"https://haustierzentrum.com"}},
  "mainEntityOfPage": {{"@type":"WebPage","@id":"{canonical}"}}
}}
</script>
<style>
:root {{
  --primary: #FF9800;
  --primary-dark: #e68900;
  --primary-light: #fff3e0;
  --border-light: #f0ece1;
  --bg: #ffffff;
  --bg-alt: #f7f7f7;
  --text: #1a1a1a;
  --text-muted: #666;
  --border: #e0e0e0;
  --card-shadow: 0 2px 12px rgba(0,0,0,.08);
  --font: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--font);color:var(--text);background:var(--bg);line-height:1.7;display:flex;flex-direction:column;min-height:100vh}}
a{{color:var(--primary);text-decoration:none}}a:hover{{text-decoration:underline}}img{{max-width:100%;height:auto;display:block}}
.site-header{{background:rgba(255,255,255,.92);backdrop-filter:blur(16px) saturate(1.2);border-bottom:3px solid var(--primary);padding:0 1rem;position:sticky;top:0;z-index:1000;}}
.nav-wrap{{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px;}}
.logo{{font-size:1.4rem;font-weight:900;letter-spacing:-1px;background:linear-gradient(135deg,var(--primary-dark),var(--primary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;flex-shrink:0;}}
.logo span{{font-weight:400;color:var(--text-muted);-webkit-text-fill-color:var(--text-muted);}}
.main-nav{{display:flex;align-items:center}}
.nav-links{{display:flex;gap:0;list-style:none;align-items:center;margin:0;padding:0}}
.nav-links>li{{position:relative}}
.nav-links>li>a{{color:var(--text);font-weight:600;font-size:.85rem;padding:.4rem 1rem;border-radius:50px;transition:.2s;letter-spacing:.2px;display:flex;align-items:center;gap:.3rem;white-space:nowrap;}}
.nav-links>li>a.active{{background:var(--primary);color:#fff;}}
.nav-links>li>a:hover{{background:var(--primary-light);}}
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:8px;}}
.hamburger span{{width:24px;height:2.5px;background:var(--text);border-radius:4px;transition:.25s;}}
.article-hero{{width:100%;max-height:480px;object-fit:cover;display:block;}}
.post-header{{background:linear-gradient(135deg,#FF9800,#FFB74D);padding:40px 20px;text-align:center;color:#fff;}}
.post-header h1{{font-size:1.8rem;margin-top:0;max-width:800px;margin:0 auto;}}
.post-meta{{margin-top:10px;font-size:.85rem;opacity:.85;}}
.article-content{{max-width:780px;margin:30px auto;padding:0 20px;flex:1;}}
.article-content h2{{color:var(--primary-dark);margin:30px 0 15px;padding-bottom:8px;border-bottom:2px solid var(--primary-light);font-size:1.4em;}}
.article-content h3{{color:var(--text);margin:20px 0 10px;font-size:1.1em;}}
.article-content p{{margin-bottom:15px;}}
.article-content ul,.article-content ol{{margin:10px 0 15px 25px;}}
.article-content li{{margin-bottom:6px;}}
.article-content table{{width:100%;border-collapse:collapse;margin:20px 0;font-size:.9em;}}
.article-content th,.article-content td{{border:1px solid var(--border);padding:10px 12px;text-align:left;}}
.article-content th{{background:var(--primary-light);font-weight:700;color:var(--primary-dark);}}
.article-content tr:nth-child(even) td{{background:var(--bg-alt);}}
.key-takeaways{{background:var(--primary-light);border:2px solid var(--primary);border-radius:12px;padding:20px 25px;margin:25px 0;}}
.key-takeaways h3{{color:var(--primary-dark);margin-top:0;}}
.key-takeaways ul{{margin:10px 0 0 20px;}}
.amazon-affiliate{{margin:30px 0;padding:20px;background:var(--primary-light);border:1px solid var(--primary);border-radius:8px;text-align:center;}}
.amazon-affiliate a{{color:var(--primary-dark);font-weight:bold;font-size:1.05em;}}
.ad-placeholder{{margin:25px 0;padding:20px;background:var(--bg-alt);border:2px dashed var(--border);border-radius:8px;text-align:center;color:var(--text-muted);font-size:.9em;}}
.faq-item{{margin:20px 0;padding:18px;background:var(--bg-alt);border-radius:8px;border-left:4px solid var(--primary);}}
.faq-item h3{{margin-top:0;color:var(--primary-dark);font-size:1.05em;}}
.faq-item p{{margin-bottom:0;}}
.related-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px;margin:30px 0;}}
.related-card{{border:1px solid var(--border);border-radius:10px;overflow:hidden;transition:.2s;}}
.related-card:hover{{box-shadow:var(--card-shadow);transform:translateY(-2px);}}
.related-card img{{width:100%;height:150px;object-fit:cover;}}
.related-card-body{{padding:12px 15px;}}
.related-card-body h4{{font-size:.95em;margin-bottom:5px;}}
.related-card-body p{{font-size:.8em;color:var(--text-muted);margin:0;}}
.site-footer{{background:#1a1a2e;color:#ccc;padding:40px 20px 20px;margin-top:50px;}}
.footer-wrap{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:30px;}}
.footer-brand p{{font-size:.85em;margin-top:10px;color:#999;}}
.footer-col h4{{color:#fff;margin-bottom:12px;font-size:.95em;}}
.footer-col ul{{list-style:none;padding:0;}}
.footer-col li{{margin-bottom:6px;}}
.footer-col a{{color:#aaa;font-size:.85em;}}
.footer-col a:hover{{color:var(--primary);}}
.footer-bottom{{border-top:1px solid #333;text-align:center;padding-top:20px;margin-top:30px;font-size:.8em;color:#777;}}
@media(max-width:768px){{
  .nav-links{{display:none;position:absolute;top:72px;left:0;right:0;background:#fff;flex-direction:column;padding:15px 20px;box-shadow:0 4px 12px rgba(0,0,0,.1);z-index:999;}}
  .nav-links.open{{display:flex;}}
  .hamburger{{display:flex;}}
  .footer-wrap{{grid-template-columns:1fr;}}
  .post-header h1{{font-size:1.4rem;}}
}}
</style>
<meta property="og:locale" content="de_DE" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title} | Haustierzentrum" />
<meta name="twitter:description" content="{description[:155]}" />
<meta name="twitter:image" content="{og_image_url}" />
</head>
<body>

<header class="site-header">
  <div class="nav-wrap">
    <a href="/" class="logo">🐾 Haustier<span>zentrum</span></a>
    <button class="hamburger" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Menü">
      <span></span><span></span><span></span>
    </button>
    <nav class="main-nav">
      <ul class="nav-links">
        <li><a href="/">Start</a></li>
        {nav_active}
        <li><a href="/about.html">Über uns</a></li>
        <li><a href="/sitemap.xml">Sitemap</a></li>
      </ul>
    </nav>
  </div>
</header>

<img src="../images/hero-{slug}.webp" alt="{title}" class="article-hero" />

<div class="post-header">
  <h1>{title}</h1>
  <div class="post-meta">📅 {today_str} · {cat_spans}</div>
</div>

<div class="article-content">
{body}
</div>

<footer class="site-footer">
  <div class="footer-wrap">
    <div class="footer-brand">
      <a href="/" class="logo">🐾 Haustier<span>zentrum</span></a>
      <p>Dein Blog für artgerechte Haustierhaltung. Praktische Ratgeber, ehrliche Produktvergleiche und jede Menge Liebe zu Tieren.</p>
    </div>
    <div class="footer-col">
      <h4>Themen</h4>
      <ul>
        <li><a href="/artikel/hunderassen-anfaenger.html">Hunde</a></li>
        <li><a href="/artikel/katzenhaltung-wohnung.html">Katzen</a></li>
        <li><a href="/artikel/kleintiere-hamster-meerschweinchen.html">Kleintiere</a></li>
        <li><a href="/sitemap.xml">Sitemap</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Rechtliches</h4>
      <ul>
        <li><a href="/about.html">Über uns</a></li>
        <li><a href="/impressum.html">Impressum</a></li>
        <li><a href="/impressum.html">Datenschutz</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>&copy; 2026 Haustierzentrum. Alle Rechte vorbehalten.</p>
    <p>Als Amazon-Partner verdienen wir an qualifizierten Verkäufen.</p>
  </div>
</footer>

<script>
document.querySelectorAll('.nav-links a').forEach(l=>l.addEventListener('click',()=>{{
  document.querySelector('.nav-links').classList.remove('open')
}}))
</script>
</body>
</html>"""
    return html

def sanitize_body(body):
    """Sanitize body text: fix unicode issues and ensure valid HTML."""
    body = body.replace('\u00a0', ' ').replace('\u202f', ' ').replace('\u2009', ' ')
    body = body.replace('\u2014', '--').replace('\u2013', '-')
    body = body.replace('\u2018', "'").replace('\u2019', "'")
    body = body.replace('\u201c', '"').replace('\u201d', '"')
    body = body.replace('\u2011', '-')
    # Fix any ** markdown bold markers - convert to <strong>
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    return body

# ---- ARTICLE DEFINITIONS ----
today = "7. Juni 2026"
today_iso = "2026-06-07"

articles = [
    {
        "slug": "mops-rasseguide",
        "title": "Mops (Pug) Rasseguide – Charakter, Haltung, Gesundheit & Pflege",
        "category_tags": ["Hunde", "Hunderassen"],
        "description": "Der komplette Mops Rasseguide: Herkunft, Charakter, Haltung in der Wohnung, typische Gesundheitsprobleme, Ernährung, Fellpflege und Erziehung des beliebten Begleiters.",
        "scene": "Ein süßer Mops (Pug) in Fellfarben beige/schwarz mit großen Kulleraugen, kurzer Schnauze, typischen Hautfalten, freundlichem Gesichtsausdruck, sitzt auf einem Kissen",
        "system_prompt": "Du bist ein deutscher SEO-Content-Autor für eine hundefreundliche Website. Schreibe direkt, persönlich (Du-Form), bodenständig. Verwende echte Umlaute (ä/ö/ü/ß). Kein BWL-Geschwafel.",
        "prompt": """Schreibe einen ausführlichen Mops (Pug) Rasseguide für haustierzentrum.com. 
Der Artikel sollte 1500-2500 Wörter haben.

STRUKTUR (in dieser Reihenfolge):
1. Eine **Key-Takeaways** Box (3-5 Punkte in einer div.key-takeaways)
2. **Herkunft & Geschichte** – Der Mops stammt aus China, über 2000 Jahre alt, kam über Holland nach Europa. Berühmte Besitzer (William III., Josephine Bonaparte)
3. **Charakter & Wesen** – Verspielt, freundlich, eigensinnig, menschenbezogen, charmant, aber auch stur. Gut für Anfänger? Vergleich mit anderen Rassen
4. **AdSense Platzhalter** (div.ad-placeholder)
5. **Erziehung & Training** – Positive Verstärkung, Geduld, Sozialisation wichtig. Futterorientiert, aber schnell abgelenkt
6. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Mops+Hund+Zubehör&tag=nova079-20)
7. **Haltung & Wohnung** – Ideal für Wohnungen, wenig Auslauf nötig, aber hitzeempfindlich (brachycephales Syndrom). Treppen vermeiden
8. **Ernährung** – Neigt stark zu Übergewicht! Portionskontrolle, hochwertiges Futter, Leckerlis sparsam. Fütterungsplan
9. **Pflege** – Gesichtsfalten täglich reinigen! Fellpflege, Ohren, Augen, Zahnpflege. Tränenfluss beachten
10. **Gesundheit** – Brachycephales Syndrom (Atemnot), Hautfalten-Dermatitis, Augenprobleme (Exophthalmus, Hornhautgeschwüre), Patellaluxation, Hüftdysplasie, Übergewicht. Lebenserwartung 12-15 Jahre
11. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Mops+Pflege+Gesundheit&tag=nova079-20)
12. **Vergleichstabelle** – Mops vs. Französische Bulldogge vs. Boston Terrier (Größe, Gewicht, Charakter, Wohnung, Familienfreundlich, Gesundheit, Pflegeaufwand, Lebenserwartung)
13. **FAQ** (5-6 Fragen in div.faq-item Blöcken)
14. **Fazit** mit Zusammenfassung
15. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Mops+Welpe&tag=nova079-20)
16. **Disclaimer** als letzter Satz

WICHTIGE REGELN:
- Nur HTML-Body-Fragment (kein <html><head><body>, kein <h1>) 
- Amazon-Links IMMER mit tag=nova079-20 (NICHT nova03e-21!)
- 5+ H2-Überschriften
- Echte Umlaute ä/ö/ü/ß (NIEMALS ae/oe/ue/ss)
- Mindestens 1500 Wörter
- Vergleichstabelle mit <table>
- Interne Links zu anderen haustierzentrum.com Artikeln (z.B. /artikel/franzoesische-bulldogge-rasseguide.html, /artikel/hunderassen-anfaenger.html)"""
    },
    {
        "slug": "sibirischer-husky-rasseguide",
        "title": "Sibirischer Husky Rasseguide – Aussehen, Charakter, Haltung & Erziehung",
        "category_tags": ["Hunde", "Hunderassen"],
        "description": "Alles über den Sibirischen Husky: Herkunft als Schlittenhund, charakterliche Eigenschaften, Bewegungsbedarf, Erziehung, Ernährung, Fellpflege und typische Gesundheitsaspekte.",
        "scene": "Ein Sibirischer Husky mit blauen Augen, grau-weißem Fell, aufrechtstehenden Ohren, kraftvoller Statur, steht im Schnee",
        "system_prompt": "Du bist ein deutscher SEO-Content-Autor für eine hundefreundliche Website. Schreibe direkt, persönlich (Du-Form), bodenständig. Verwende echte Umlaute (ä/ö/ü/ß). Kein BWL-Geschwafel.",
        "prompt": """Schreibe einen ausführlichen Sibirischer Husky Rasseguide für haustierzentrum.com.
Der Artikel sollte 1500-2500 Wörter haben.

STRUKTUR (in dieser Reihenfolge):
1. **Key-Takeaways** Box (3-5 Punkte in div.key-takeaways)
2. **Herkunft & Geschichte** – Tschuktschen-Volk in Sibirien, Schlittenhunde, 1925 Serum Run nach Nome (Balto, Togo), Berühmtheit durch Filme und Serien
3. **Charakter & Wesen** – Freundlich, sanft, aber auch stur, unabhängig, verspielt, kein Wachhund (freundlich zu Fremden). Starkes Rudelverhalten. Fluchttendenz! Vergleich zu anderen nordischen Rassen
4. **AdSense Platzhalter** (div.ad-placeholder)
5. **Erziehung & Training** – Nur für erfahrene Hundehalter! Konsequenz, Geduld, positive Verstärkung. Rückruf trainieren, Leinenführigkeit. Gehorsamkeit ist nicht selbstverständlich
6. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Sibirischer+Husky+Hund&tag=nova079-20)
7. **Haltung & Auslauf** – SEHR hoher Bewegungsbedarf (2+ Stunden täglich). Nicht für Wohnung ohne Ausgleich! Braucht Aufgabe (Zughundesport, Canicross, Bikejöring). Kein Freilauf ohne sicheren Zaun!
8. **Ernährung** – Aktivitätsangepasst, hochwertiges Protein, moderate Fette. Im Winter (Schlittenarbeit) höherer Kalorienbedarf. Fütterungsplan
9. **Fellpflege** – Dichtes Doppelfell, 2x jährlich Fellwechsel. Regelmäßiges Bürsten, besonders im Frühjahr. Nicht scheren! Baden selten nötig
10. **Gesundheit** – Hüftdysplasie, Augenprobleme (Katarakt, PRA), Hypothyreose. Relative gesunde Rasse. Lebenserwartung 12-15 Jahre
11. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Husky+Zughund+Zubehör&tag=nova079-20)
12. **Vergleichstabelle** – Siberian Husky vs. Alaskan Malamute vs. Samojede (Größe, Gewicht, Charakter, Bewegungsbedarf, Familienfreundlich, Pflegeaufwand, Bellverhalten, Lebenserwartung)
13. **FAQ** (5-6 Fragen in div.faq-item Blöcken)
14. **Fazit** – Für wen geeignet? (aktive Menschen, Haus mit Garten, erfahrene Halter, keine Allergiker)
15. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Hunde+Zughund+Canicross&tag=nova079-20)
16. **Disclaimer**

WICHTIGE REGELN:
- Nur HTML-Body-Fragment
- Amazon-Links IMMER mit tag=nova079-20 (NICHT nova03e-21!)
- 5+ H2-Überschriften
- Echte Umlaute ä/ö/ü/ß
- Mindestens 1500 Wörter
- Vergleichstabelle mit <table>
- Interne Links zu /artikel/zwergspitz-pomeranian-rasseguide.html, /artikel/hunderassen-anfaenger.html, /artikel/hundeerziehung-grundlagen.html"""
    },
    {
        "slug": "ragdoll-katze-rasseguide",
        "title": "Ragdoll Katze Rasseguide – Sanfter Riese mit blauen Augen",
        "category_tags": ["Katzen", "Katzenrassen"],
        "description": "Ragdoll Rasseguide: Herkunft, Charakter, Haltung in der Wohnung, Fellpflege, Ernährung, Gesundheit und Preise der beliebten Halblanghaarkatze aus den USA.",
        "scene": "Eine Ragdoll-Katze mit blauen Augen, mittellangem seidigem Fell, farblich Seal Point oder Blue Point, entspannt auf weichem Teppich liegend",
        "system_prompt": "Du bist ein deutscher SEO-Content-Autor für eine hundefreundliche Website. Schreibe direkt, persönlich (Du-Form), bodenständig. Verwende echte Umlaute (ä/ö/ü/ß). Kein BWL-Geschwafel.",
        "prompt": """Schreibe einen ausführlichen Ragdoll Katzen Rasseguide für haustierzentrum.com.
Der Artikel sollte 1500-2500 Wörter haben.

STRUKTUR (in dieser Reihenfolge):
1. **Key-Takeaways** Box (3-5 Punkte in div.key-takeaways)
2. **Herkunft & Geschichte** – Ann Baker, 1960er Jahre, Kalifornien. Josephine (die Mutterkatze), Zuchtstart mit Persian-ähnlichen und Burmese-Einflüssen. Name "Ragdoll" wegen der Neigung, beim Hochnehmen schlaff wie eine Stoffpuppe zu werden
3. **Charakter & Wesen** – Sehr ruhig, sanft, menschenbezogen, "hundähnlich" (folgt Besitzern, apportiert). Kein typisches "Katzen-Verhalten". Sehr verschmust, sozial. Vergleich zu anderen Katzenrassen
4. **AdSense Platzhalter** (div.ad-placeholder)
5. **Haltung in der Wohnung** – Ideal für Wohnungshaltung! Braucht Gesellschaft (besser nicht allein). Kratzbaum, Spielzeug, erhöhte Schlafplätze. Kein Freigänger – zu zutraulich und wertvoll
6. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Ragdoll+Katze+Zubehör&tag=nova079-20)
7. **Fellpflege** – Mittellanges seidiges Fell ohne starke Unterwolle. Weniger Verfilzungsgefahr als Perser. Regelmäßiges Bürsten (2-3x/Woche). Das Fell verfilzt seltener als bei Persern
8. **Ernährung** – Hochwertiges Katzenfutter mit viel Fleisch. Neigt zu Übergewicht. Nasses Futter bevorzugen. Portionsgrößen und Fütterungsrhythmus
9. **Gesundheit & typische Krankheiten** – HCM (Hypertrophe Kardiomyopathie) häufigste Erkrankung! PKD (Polyzystische Nierenerkrankung). Hüftdysplasie. Regelmäßige Vorsorge. Lebenserwartung 12-17 Jahre
10. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Ragdoll+Katzenfutter+Gesundheit&tag=nova079-20)
11. **Aussehen & Farbvarianten** – Colourpoint-Muster (Seal Point, Blue Point, Chocolate Point, Lilac Point). Mitted, Bicolor, Van. Blaue Augen sind Pflicht. 4-9 kg (Kater deutlich größer als Katzen)
12. **Vergleichstabelle** – Ragdoll vs. Maine Coon vs. Perserkatze (Größe, Gewicht, Charakter, Fellpflege, Wohnungstauglich, Familienfreundlich, Gesundheitsrisiken, Lebenserwartung)
13. **FAQ** (5-6 Fragen in div.faq-item Blöcken)
14. **Kosten** – Welpe von Züchter: 800-1500 EUR. Wichtige Züchterkriterien (HCM-Testung, PKD-Test, Freigang der Elterntiere)
15. **Fazit** – Ideale Katze für ruhige Haushalte, Familien, Wohnungshaltung. Keine Katze für Vielreisende
16. **Amazon Affiliate Block** (div.amazon-affiliate mit Link zu https://www.amazon.de/s?k=Ragdoll+Katze+Züchter&tag=nova079-20)

WICHTIGE REGELN:
- Nur HTML-Body-Fragment
- Amazon-Links IMMER mit tag=nova079-20 (NICHT nova03e-21!)
- 5+ H2-Überschriften
- Echte Umlaute ä/ö/ü/ß
- Mindestens 1500 Wörter
- Vergleichstabelle mit <table>
- Interne Links zu /artikel/perserkatze-rasseguide.html, /artikel/maine-coon-katze-rasseguide.html, /artikel/katzenrassen-vergleich.html"""
    }
]

print("=" * 60)
print("HAUSTIERZENTRUM CONTENT FACTORY — 3 Articles")
print(f"Date: {today} ({today_iso})")
print("=" * 60)

results = []

for art in articles:
    slug = art["slug"]
    out_path = os.path.join(REPO, "artikel", f"{slug}.html")
    
    if os.path.exists(out_path):
        print(f"\n⚠ {slug}.html existiert bereits — überspringe")
        results.append({"slug": slug, "status": "skipped", "path": out_path})
        continue
    
    print(f"\n{'─'*40}")
    print(f"📝 Generiere: {art['title']} ({slug})")
    print(f"{'─'*40}")
    
    try:
        body = or_chat(art["system_prompt"], art["prompt"])
        body = sanitize_body(body)
        
        # Split body into rough word count
        text_only = re.sub(r'<[^>]+>', ' ', body)
        wc = len(text_only.split())
        print(f"  📊 Body: ~{wc} Wörter")
        
        html = build_html(
            title=art["title"],
            slug=slug,
            body=body,
            category_tags=art["category_tags"],
            description=art["description"],
            today_str=today_iso,
            related_links=[]
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        file_bytes = os.path.getsize(out_path)
        print(f"  ✅ Geschrieben: {out_path} ({file_bytes:,} Bytes)")
        
        # Count affiliate tags
        aff_count = html.count("tag=nova079-20")
        print(f"  🔗 Amazon-Links mit nova079-20: {aff_count}")
        
        # Verify OG tags
        has_og = "og:image" in html and "og:url" in html and "og:title" in html
        has_jsonld = "application/ld+json" in html
        has_canonical = "rel=\"canonical\"" in html
        has_close = html.rstrip().endswith("</html>")
        
        print(f"  ✅ OG-Tags: {'✓' if has_og else '✗'}")
        print(f"  ✅ JSON-LD: {'✓' if has_jsonld else '✗'}")
        print(f"  ✅ Canonical: {'✓' if has_canonical else '✗'}")
        print(f"  ✅ HTML geschlossen: {'✓' if has_close else '✗'}")
        print(f"  ✅ Tag nova03e-21 (alt): {'⚠ FOUND!' if html.count('nova03e-21') > 0 else '✓ none'}")
        
        results.append({"slug": slug, "status": "created", "path": out_path, "words": wc, "bytes": file_bytes, "aff_links": aff_count})
        
        # Cooldown between articles
        if art != articles[-1]:
            print("  ⏳ 10s pause...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        results.append({"slug": slug, "status": "error", "error": str(e)})

print(f"\n{'='*60}")
print("ZUSAMMENFASSUNG")
print(f"{'='*60}")
for r in results:
    if r["status"] == "created":
        print(f"  ✅ {r['slug']}: {r['words']} Wörter, {r['bytes']:,} Bytes, {r['aff_links']} Amazon-Links")
    elif r["status"] == "skipped":
        print(f"  ⏭ {r['slug']}: Bereits vorhanden")
    else:
        print(f"  ❌ {r['slug']}: {r.get('error', 'Unbekannter Fehler')}")

print(f"\nJetzt: Hero-Bilder generieren mit generate_blog_image.py")
print("Done!")
