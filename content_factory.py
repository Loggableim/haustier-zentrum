#!/usr/bin/env python3
"""
Haustierzentrum Content Factory
===============================
Generiert SEO-optimierte Blog-Artikel für haustierzentrum.com.

Provider-Strategie:
  1. MiniMax-M3 (Primär) – via api.minimax.io/v1/chat/completions
  2. OpenRouter Owl Alpha (Fallback) – via openrouter.ai/api/v1/chat/completions

Jeder Durchlauf generiert 1 Artikel + 1 Hero-Bild (MiniMax image-01).
Läuft als Cron-Job alle 180 Minuten.
"""

import json, os, re, sys, time, urllib.request, urllib.error, ssl, hashlib, textwrap
from datetime import datetime
from PIL import Image

# ── Paths ──
REPO = "C:/sidekick/home/spaces/haustier-zentrum"
IMG_DIR = os.path.join(REPO, "images")
os.chdir(REPO)
os.makedirs(IMG_DIR, exist_ok=True)

# ── MiniMax Config ──
try:
    from _minimax_key import API_KEY as MM_KEY
except ImportError:
    MM_KEY = ""
MM_BASE = "https://api.minimax.io/v1/chat/completions"
MM_MODEL = "MiniMax-M3"

# ── OpenRouter Config ──
try:
    with open("C:/HermesPortable/home/auth.json", encoding="utf-8") as f:
        auth = json.load(f)
    OR_KEY = auth["credential_pool"]["openrouter"][0]["access_token"]
except Exception:
    OR_KEY = ""
OR_BASE = "https://openrouter.ai/api/v1/chat/completions"
OR_MODEL = "openrouter/auto"

NEGATIVE_STYLE = "text, watermark, signature, blurry, low quality, distorted, photograph, realistic, 3d render"
IMG_STYLE = "furry pop-art, anthropomorphic animal characters, editorial illustration, bold black contour lines, clean vector art, kawaii, cute, vibrant orange/violet color palette, halftone comic textures, graphic novel aesthetic, modern advertising illustration, dynamic composition, highly detailed, professional magazine artwork, sharp linework, colorful background"

# ── Article Topics ──
TOPICS = [
    {
        "slug": "whippet-rasseguide",
        "title": "Whippet Rasseguide \u2013 Der schnelle Windhund f\u00fcr die Familie",
        "category_tags": ["Hunde", "Hunderassen"],
        "description": "Whippet Rasseguide: Charakter, Haltung, Erziehung und Gesundheit des eleganten Rennhundes. Ideal f\u00fcr Wohnung? Alle Infos zum sanften Windhund.",
        "subject": "anthropomorphic Whippet dog character, elegant slender body with short smooth coat, big dark eyes, gentle expression, running gracefully"
    },
    {
        "slug": "dog-sitting-hundesitter-finden",
        "title": "Dog-Sitting & Hundesitter finden \u2013 Der komplette Ratgeber 2026",
        "category_tags": ["Hunde", "Betreuung"],
        "description": "Hundesitter oder Dog-Sitting finden: Kosten, Tipps, worauf du achten musst. Inkl. Checkliste und Vergleich Hundepension vs. Sitter.",
        "subject": "anthropomorphic dog character with a friendly pet sitter holding a leash, trusty and happy scene"
    },
    {
        "slug": "katzen-zimmerpflanzen-giftig",
        "title": "Giftige Zimmerpflanzen f\u00fcr Katzen \u2013 Diese 15 Pflanzen sind tabu",
        "category_tags": ["Katzen", "Gesundheit"],
        "description": "Giftige Zimmerpflanzen f\u00fcr Katzen: Die 15 gef\u00e4hrlichsten Pflanzen mit Bildern. Inkl. ungiftige Alternativen und was im Notfall zu tun ist.",
        "subject": "anthropomorphic cat character sniffing a potted plant curiously, surrounded by both safe and dangerous plants"
    },
    {
        "slug": "hundefutter-vergleich-2026",
        "title": "Hundefutter Vergleich 2026 \u2013 Trockenfutter, Nassfutter & BARF im Test",
        "category_tags": ["Hunde", "Ern\u00e4hrung"],
        "description": "Hundefutter Vergleich 2026: Trockenfutter, Nassfutter, BARF und Frischfutter im Test. Die besten Marken, Preisvergleich und F\u00fctterungsempfehlungen.",
        "subject": "anthropomorphic dog character comparing different food bowls with kibble, meat and fresh ingredients"
    },
    {
        "slug": "katzenfreundliche-wohnung-gestalten",
        "title": "Katzenfreundliche Wohnung gestalten \u2013 12 Tipps f\u00fcr gl\u00fcckliche Wohnungskatzen",
        "category_tags": ["Katzen", "Wohnungshaltung"],
        "description": "So gestaltest du deine Wohnung katzenfreundlich: Kletterm\u00f6glichkeiten, R\u00fcckzugsorte, Balkonsicherung und artgerechte Besch\u00e4ftigung f\u00fcr Wohnungskatzen.",
        "subject": "anthropomorphic cat character in a cozy colorful apartment with cat tree, scratching post and window hammock"
    },
    {
        "slug": "chinchilla-ernaehrung-futter",
        "title": "Chinchilla Ern\u00e4hrung \u2013 Was fressen Chinchillas wirklich? Futterplan & Tipps",
        "category_tags": ["Kleintiere", "Chinchilla"],
        "description": "Chinchilla Ern\u00e4hrung komplett erkl\u00e4rt: Heu, Pellets, Leckerlis und verbotene Lebensmittel. Mit Futterplan f\u00fcr eine gesunde, artgerechte Chinchilla-Haltung.",
        "subject": "anthropomorphic Chinchilla character surrounded by hay, pellets and fresh herbs, cute eating scene"
    },
    {
        "slug": "welpenschule-finden-kosten",
        "title": "Welpenschule finden \u2013 Kosten, Kursarten und worauf du achten musst",
        "category_tags": ["Hunde", "Welpen"],
        "description": "Die richtige Welpenschule finden: Kosten 2026, Kursarten, Qualit\u00e4tskriterien und Tipps f\u00fcr die Auswahl. Inklusive Checkliste f\u00fcr den ersten Besuch.",
        "subject": "anthropomorphic puppy character in a dog school with a cap and diploma certificate, proud graduate"
    },
    {
        "slug": "katzen-kratzmoebel-test",
        "title": "Kratzm\u00f6bel f\u00fcr Katzen \u2013 Kratzbaum, Kratzbrett & Kratzpappe im Test",
        "category_tags": ["Katzen", "Kratzbaum"],
        "description": "Kratzm\u00f6bel f\u00fcr Katzen im Vergleich: Kratzbaum, Kratzbrett, Kratzpappe und Kratztonne. Welches M\u00f6belst\u00fcck f\u00fcr welche Katze? Inkl. Kauftipps mit Amazon-Links.",
        "subject": "anthropomorphic cat character testing different scratching furniture: tall cat tree, cardboard scratcher, sisal post"
    },
    {
        "slug": "hamster-ernaehrung-futterplan",
        "title": "Hamster Ern\u00e4hrung \u2013 Der komplette Futterplan f\u00fcr gesunde Hamster",
        "category_tags": ["Kleintiere", "Hamster"],
        "description": "Hamster Ern\u00e4hrung richtig gemacht: Was d\u00fcrfen Hamster fressen? Futterplan, verbotene Lebensmittel, Leckerlis und die richtige Menge f\u00fcr Zwerghamster und Goldhamster.",
        "subject": "anthropomorphic hamster character with chubby cheeks surrounded by seeds, grains, vegetables and herbs"
    },
    {
        "slug": "hundeangst-training-tipps",
        "title": "Hundeangst \u00fcberwinden \u2013 Training bei Angst, Stress & Unsicherheit",
        "category_tags": ["Hunde", "Erziehung"],
        "description": "Hilfe bei Hundeangst: Ursachen erkennen, Training bei Angst vor Ger\u00e4uschen, Menschen oder Artgenossen. Mit \u00dcbungen, Desensibilisierung und Tipps f\u00fcr \u00e4ngstliche Hunde.",
        "subject": "anthropomorphic dog character hiding behind a person\u2019s legs nervously, being comforted gently"
    },
    {
        "slug": "aquarium-pflanzen-einsteiger",
        "title": "Aquarium Pflanzen f\u00fcr Einsteiger \u2013 10 pflegeleichte Arten",
        "category_tags": ["Aquarium", "Einrichtung"],
        "description": "Aquarium Pflanzen f\u00fcr Einsteiger: Die 10 pflegeleichtesten Wasserpflanzen. Mit Pflanzanleitung, Lichtbedarf und D\u00fcngungstipps f\u00fcr dein erstes Aquarium.",
        "subject": "anthropomorphic tropical fish swimming among lush green aquarium plants, colorful underwater garden scene"
    },
    {
        "slug": "vogelvoliere-kaufen-checkliste",
        "title": "Vogelvoliere kaufen \u2013 Die ultimative Checkliste f\u00fcr die richtige Wahl",
        "category_tags": ["V\u00f6gel", "Vogelhaltung"],
        "description": "Vogelvoliere kaufen: Checkliste mit Gr\u00f6\u00dfe, Material, Gitterabstand und Standort. Innen- und Au\u00dfenvoliere im Vergleich. Inklusive Modell-Empfehlungen mit Amazon-Links.",
        "subject": "anthropomorphic budgie character in a large colorful aviary with toys, happy bird in a great home"
    },
]

SYSTEM_PROMPT = """Du bist ein deutscher SEO-Content-Autor für haustierzentrum.com. 
Schreibe direkt, persönlich (Du-Form), bodenständig und warmherzig.
Verwende echte Umlaute (ä/ö/ü/ß) — NIEMALS ae/oe/ue/ss.
Kein BWL-Geschwafel. Praxisorientierte Ratgeber.
KEINE <think>-Tags oder Gedankenprozesse. Gib NUR den fertigen Text aus."""

ARTICLE_STRUCTURE = """
Schreibe einen ausführlichen SEO-optimierten Artikel für haustierzentrum.com.
Der Artikel sollte 1500-2500 Wörter haben.

STRUKTUR (als HTML-Body-Fragment, in dieser Reihenfolge):
1. **Key-Takeaways Box** (3-5 Punkte in <div class="key-takeaways"><h3>📌 Das Wichtigste auf einen Blick</h3><ul>...</ul></div>)
2. **Einleitung** – Warum dieses Thema wichtig ist
3. **H2 Abschnitte** (4-6 Stück) mit H3-Unterabschnitten, gefüllt mit wertvollen Inhalten
4. **AdSense Platzhalter** nach Abschnitt 2 und 4: <div class="ad-placeholder"><p><strong>📢 Anzeige</strong></p></div>
5. **Amazon Affiliate Block** nach Abschnitt 3: <div class="amazon-affiliate"><p>🛍️ <strong>Produkt-Empfehlung:</strong></p><a href="https://www.amazon.de/s?k=THEMA+HAUSTIER&tag=nova079-20" target="_blank" rel="nofollow">👉 Beste Produkte bei Amazon entdecken</a><p style="font-size:.85rem;color:#666;margin-top:6px;">* Als Amazon-Partner verdienen wir an qualifizierten Verkäufen.</p></div>
6. **FAQ** (3-5 Fragen in <div class="faq-item"><h3>Frage?</h3><p>Antwort.</p></div>)
7. **Fazit** mit Zusammenfassung
8. **Amazon Affiliate Block** (nochmal, breiteres Thema)
9. **Disclaimer** als letzter Satz

WICHTIGE REGELN:
- Nur HTML-Body-Fragment (KEIN <html><head><body>, KEIN <h1>)
- Amazon-Links IMMER mit tag=nova079-20
- 5+ H2-Überschriften
- Echte Umlaute ä/ö/ü/ß (NIEMALS ae/oe/ue/ss)
- Mindestens 1500 Wörter
- Interne Links zu anderen haustierzentrum.com Artikeln
- KEINE <think>-Tags"""


# ── API Helpers ──

def call_minimax(prompt_text, system=SYSTEM_PROMPT, retries=3):
    """Call MiniMax-M3 via OpenAI-compatible endpoint."""
    if not MM_KEY:
        return None
    payload = json.dumps({
        "model": MM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 8192,
        "temperature": 0.7,
    }).encode()
    headers = {"Authorization": f"Bearer {MM_KEY}", "Content-Type": "application/json"}
    ctx = ssl.create_default_context()
    req = urllib.request.Request(MM_BASE, data=payload, headers=headers, method="POST")
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
                result = json.loads(resp.read())
            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                # Strip <think> tags
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                return content if content else None
            return None
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            if "2056" in body:
                print("  ⛔ MiniMax Token Limit. Fallback nötig.")
                return "TOKEN_LIMIT"
            if "1002" in body or "rate" in body.lower():
                print(f"  ⏸ MiniMax RPM. Warte 30s...")
                time.sleep(30)
                continue
            print(f"  ⚠️  MiniMax HTTP {e.code}")
            if attempt < retries - 1:
                time.sleep(10 * (attempt + 1))
        except Exception as e:
            print(f"  ⚠️  MiniMax Fehler: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return None


def call_openrouter(prompt_text, system=SYSTEM_PROMPT, retries=3):
    """Fallback to OpenRouter Owl Alpha."""
    if not OR_KEY:
        return None
    payload = json.dumps({
        "model": OR_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 8192,
        "temperature": 0.7,
    }).encode()
    headers = {
        "Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json",
        "HTTP-Referer": "https://haustierzentrum.com",
        "X-Title": "Haustierzentrum Content Factory",
    }
    req = urllib.request.Request(OR_BASE, data=payload, headers=headers, method="POST")
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠️  OpenRouter {attempt+1}: {e}")
            if attempt == retries - 1:
                return None
            time.sleep(10 * (attempt + 1))
    return None


def generate_text(topic):
    """Generate article text. MiniMax -> OpenRouter fallback."""
    print(f"\n📝 Generiere Text für: {topic['title']}")
    print(f"  Provider: MiniMax-M3...", end=" ", flush=True)
    
    result = call_minimax(ARTICLE_STRUCTURE)
    
    if result == "TOKEN_LIMIT":
        print("⛔ Fallback zu OpenRouter...", end=" ", flush=True)
        result = call_openrouter(ARTICLE_STRUCTURE)
    
    if result:
        print(f"✅ {len(result)} Zeichen")
        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
        result = result.replace('\u00a0', ' ').replace('\u202f', ' ')
        result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)
        return result
    else:
        print("❌ Fehlgeschlagen")
        return None


def generate_image(topic):
    """Generate hero image via MiniMax image-01."""
    slug = topic["slug"]
    subject = topic.get("subject", "a cute pet animal, furry pop-art style")
    prompt = f"{subject}, {IMG_STYLE}"
    
    print(f"  🖼️  Generiere Bild: {slug}...", end=" ", flush=True)
    
    payload = json.dumps({
        "model": "image-01",
        "prompt": prompt,
        "negative_prompt": NEGATIVE_STYLE,
    }).encode()
    
    headers = {"Authorization": f"Bearer {MM_KEY}", "Content-Type": "application/json"}
    ctx = ssl.create_default_context()
    
    try:
        req = urllib.request.Request("https://api.minimax.io/v1/image_generation", data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
            result = json.loads(resp.read())
        
        if result.get("base_resp", {}).get("status_code") != 0:
            print(f"❌ API Error: {result.get('base_resp',{}).get('status_msg','?')}")
            return False
        
        urls = result.get("data", {}).get("image_urls", [])
        if not urls:
            print("❌ Keine URL")
            return False
        
        ctx2 = ssl.create_default_context()
        with urllib.request.urlopen(urllib.request.Request(urls[0]), context=ctx2, timeout=60) as resp:
            img_data = resp.read()
        
        temp = os.path.join(IMG_DIR, slug + ".tmp")
        with open(temp, 'wb') as f:
            f.write(img_data)
        
        img = Image.open(temp)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        img = img.resize((1216, 832), Image.LANCZOS)
        dst = os.path.join(IMG_DIR, f"{slug}_00001_.webp")
        img.save(dst, "WEBP", quality=92)
        kb = os.path.getsize(dst) // 1024
        os.remove(temp)
        print(f"✅ {kb}KB")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def build_html(topic, body, today_str, today_iso):
    """Build complete article HTML."""
    slug = topic["slug"]
    title = topic["title"]
    category_tags = topic["category_tags"]
    description = topic["description"]
    canonical = f"https://haustierzentrum.com/artikel/{slug}.html"
    og_image_url = f"https://haustierzentrum.com/images/{slug}_00001_.webp"
    cat_spans = "".join(f'<span>{c}</span>' for c in category_tags)
    
    # Category link for breadcrumb
    cat_lower = [c.lower() for c in category_tags]
    if "hunde" in " ".join(cat_lower):
        cat_link = "/artikel/hunderassen-anfaenger.html"
        cat_name = "Hunde"
    elif "katzen" in " ".join(cat_lower):
        cat_link = "/artikel/katzenhaltung-wohnung.html"
        cat_name = "Katzen"
    elif "kleintiere" in " ".join(cat_lower) or "nager" in " ".join(cat_lower) or "hamster" in " ".join(cat_lower):
        cat_link = "/artikel/kleintiere-hamster-meerschweinchen.html"
        cat_name = "Kleintiere"
    elif "vogel" in " ".join(cat_lower):
        cat_link = "/artikel/voegel-haustier-beste-vogelarten-einsteiger.html"
        cat_name = "Vögel"
    elif "aquarium" in " ".join(cat_lower):
        cat_link = "/artikel/aquarium-einrichtung.html"
        cat_name = "Aquarium"
    else:
        cat_link = "/artikel/haustier-anschaffung.html"
        cat_name = "Ratgeber"
    
    # Apply escaping
    title_esc = title.replace('&', '&amp;').replace('"', '&quot;')
    body_safe = body.replace('{', '{{').replace('}', '}}')
    cat_spans_safe = cat_spans
    
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_esc} | Haustierzentrum</title>
<meta name="description" content="{description[:155]}">
<meta property="og:title" content="{title_esc} | Haustierzentrum">
<meta property="og:description" content="{description[:155]}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:image" content="{og_image_url}">
<meta property="og:site_name" content="Haustierzentrum">
<meta property="og:locale" content="de_DE">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#FF9800">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="Haustierzentrum RSS Feed" href="https://haustierzentrum.com/rss.xml">
<link rel="stylesheet" href="../css/style.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title_esc}",
  "description": "{description[:155]}",
  "author": {{"@type":"Person","name":"Haustierzentrum Redaktion"}},
  "datePublished": "{today_iso}",
  "dateModified": "{today_iso}",
  "image": "{og_image_url}",
  "publisher": {{"@type":"Organization","name":"Haustierzentrum","url":"https://haustierzentrum.com"}},
  "mainEntityOfPage": {{"@type":"WebPage","@id":"{canonical}"}},
  "articleSection": ["{cat_name}"]
}}
</script>
<style>
.breadcrumb{{padding:.5rem 0;margin-bottom:1rem;font-size:.88rem;color:var(--text-muted)}}
.breadcrumb a{{color:var(--primary)}}
.breadcrumb a:hover{{text-decoration:underline}}
</style>
</head>
<body>
<header class="site-header">
  <div class="nav-wrap">
    <a href="/" class="logo">🐾 Haustier<span>zentrum</span></a>
    <button class="nav-toggle" aria-label="Menü" onclick="document.querySelector('.main-nav').classList.toggle('open');this.textContent=this.textContent=='☰'?'✕':'☰'">☰</button>
    <nav class="main-nav">
      <ul class="nav-links">
        <li><a href="/artikel/hunderassen-anfaenger.html">Hunde <span class="arrow">▾</span></a>
          <div class="mega-panel"><div class="mega-grid cols-4">
            <div class="mega-col"><h4>🐕 Rassen</h4><a href="/artikel/hunderassen-anfaenger.html">🐕 Hunderassen für Anfänger</a><a href="/artikel/labrador-retriever.html">🐕 Labrador Retriever</a></div>
            <div class="mega-col"><h4>🎓 Erziehung</h4><a href="/artikel/hundeerziehung-grundlagen.html">🎓 Hundeerziehung Grundlagen</a><a href="/artikel/leinenfuehrigkeit.html">🦮 Leinenführigkeit</a></div>
            <div class="mega-col"><h4>🏥 Gesundheit</h4><a href="/artikel/hunde-gesundheit.html">🏥 Hundegesundheit</a><a href="/artikel/hunde-zahnpflege.html">🪥 Zahnpflege</a></div>
            <div class="mega-col"><h4>🥩 Ernährung</h4><a href="/artikel/hundeernaehrung.html">🥩 Hundeernährung</a><a href="/artikel/hundefutter-vergleich-2026.html">🥩 Hundefutter Vergleich</a></div>
          </div></div>
        </li>
        <li><a href="/artikel/katzenhaltung-wohnung.html">Katzen <span class="arrow">▾</span></a>
          <div class="mega-panel"><div class="mega-grid cols-3">
            <div class="mega-col"><h4>🏠 Haltung</h4><a href="/artikel/katzenhaltung-wohnung.html">🏠 Wohnungshaltung</a><a href="/artikel/katzen-freigaenger.html">🌳 Freigänger</a></div>
            <div class="mega-col"><h4>🥫 Ernährung & Gesundheit</h4><a href="/artikel/katzen-ernaehrung.html">🥫 Katzenernährung</a><a href="/artikel/katzenkrankheiten-erkennen.html">🏥 Katzenkrankheiten</a></div>
            <div class="mega-col"><h4>🎾 Beschäftigung</h4><a href="/artikel/katzenbeschaeftigung.html">🎾 Beschäftigungsideen</a><a href="/artikel/katzen-kratzbaum.html">🌲 Kratzbäume</a></div>
          </div></div>
        </li>
        <li><a href="/artikel/kleintiere-hamster-meerschweinchen.html">Kleintiere <span class="arrow">▾</span></a>
          <div class="mega-panel"><div class="mega-grid cols-3">
            <div class="mega-col"><h4>🐹 Nagetiere</h4><a href="/artikel/hamster-haltung.html">🐹 Hamster</a><a href="/artikel/meerschweinchen-haltung.html">🐹 Meerschweinchen</a><a href="/artikel/kaninchenhaltung.html">🐰 Kaninchen</a></div>
            <div class="mega-col"><h4>🥗 Ernährung</h4><a href="/artikel/meerschweinchen-ernaehrung-vitamin-c.html">🥗 Meerschweinchen Ernährung</a></div>
            <div class="mega-col"><h4>🐦 Vögel & Aquarium</h4><a href="/artikel/voegel-haustier-beste-vogelarten-einsteiger.html">🐦 Vögel</a><a href="/artikel/aquarium-einrichtung.html">🐟 Aquarium</a></div>
          </div></div>
        </li>
        <li><a href="/artikel/haustier-anschaffung.html">Ratgeber <span class="arrow">▾</span></a>
          <div class="mega-panel" style="min-width:450px;"><div class="mega-grid cols-2">
            <div class="mega-col"><h4>📋 Allgemein</h4><a href="/artikel/haustier-anschaffung.html">📋 Haustier Anschaffung</a><a href="/artikel/haustiere-kinder.html">👨‍👩‍👧‍👦 Haustiere & Kinder</a></div>
            <div class="mega-col"><h4>💰 Gesundheit & Kosten</h4><a href="/artikel/tierarztkosten.html">💰 Tierarztkosten</a><a href="/artikel/allergiker-haustiere.html">🤧 Allergiker</a></div>
          </div></div>
        </li>
        <li class="simple-link"><a href="/">Start</a></li>
      </ul>
    </nav>
    <button class="search-btn" onclick="window.location.href='/?s='" aria-label="Suche">🔍</button>
  </div>
</header>
<main>
  <nav class="breadcrumb" aria-label="Brotkrümelnavigation">
    <a href="/">Startseite</a> › 
    <a href="{cat_link}">{cat_name}</a> › 
    <span>{title_esc}</span>
  </nav>
  <div class="featured-img">
    <img src="../images/{slug}_00001_.webp" alt="{title_esc}" style="width:100%;height:auto;border-radius:12px;">
  </div>
  <article>
    <div class="article-header">
      <div class="article-meta">
        <div class="cats">{cat_spans_safe}</div>
        <span>{today_str}</span>
        <span>· Lesezeit: {max(len(body)//1500, 5)} Min</span>
      </div>
      <h1>{title_esc}</h1>
    </div>
    <div class="article-content">
{body_safe}
    </div>
  </article>
</main>
<footer class="site-footer">
  <div class="footer-wrap">
    <div><strong style="color:#fff;">🐾 Haustierzentrum</strong><p style="margin-top:.3rem;">Dein Blog für artgerechte Haustierhaltung</p></div>
    <div><a href="/about.html">Über uns</a> &middot; <a href="/impressum.html">Impressum</a> &middot; <a href="/sitemap.xml">Sitemap</a></div>
    <div class="footer-copy"><p>&copy; 2026 Haustierzentrum. Alle Rechte vorbehalten.</p><p style="margin-top:.3rem;font-size:.8rem;">Als Amazon-Partner verdienen wir an qualifizierten Verkäufen.</p></div>
  </div>
</footer>
</body>
</html>"""


def update_sitemap(slug, today_iso):
    """Add new article to sitemap.xml."""
    sitemap_path = os.path.join(REPO, "sitemap.xml")
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entry = f"""  <url>
    <loc>https://haustierzentrum.com/artikel/{slug}/</loc>
    <lastmod>{today_iso}T00:00:00+00:00</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""
    
    if slug not in content:
        content = content.replace('</urlset>', entry + '\n</urlset>')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  📍 Sitemap aktualisiert")
        return True
    return False


def update_homepage_count():
    """Update the stat counter on the homepage."""
    index_path = os.path.join(REPO, "index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count actual articles
    articles_dir = os.path.join(REPO, "artikel")
    count = len([f for f in os.listdir(articles_dir) if f.endswith('.html')])
    
    pattern = r'(class="stat-num">)(\d+)(</div>\s*<div class="stat-label">Ratgeber)'
    import re
    m = re.search(pattern, content)
    if m:
        content = content[:m.start(1)] + m.group(1) + str(count) + m.group(3) + content[m.end(3):]
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  📊 Stat auf {count} aktualisiert")


def git_commit_push(slug):
    """Git add, commit and push."""
    import subprocess
    repo = REPO
    
    try:
        subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True, timeout=30)
        subprocess.run(
            ["git", "commit", "-m", f"Content Factory: {slug}"],
            cwd=repo, capture_output=True, timeout=30
        )
        result = subprocess.run(
            ["git", "pull", "--rebase"], cwd=repo, capture_output=True, timeout=30
        )
        result = subprocess.run(
            ["git", "push"], cwd=repo, capture_output=True, timeout=60
        )
        if result.returncode == 0:
            print(f"  🚀 Gepusht nach GitHub Pages")
            return True
        else:
            print(f"  ⚠️  Push: {result.stderr.decode()[:200]}")
            return False
    except Exception as e:
        print(f"  ⚠️  Git: {e}")
        return False


# ── Main ──
def main():
    print(f"\n{'='*50}")
    print(f"🐾 HAUSTIERZENTRUM CONTENT FACTORY")
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print(f"{'='*50}")
    
    # Pick next ungenerated topic
    existing = set(f.replace('.html','') for f in os.listdir(
        os.path.join(REPO, "artikel")
    ) if f.endswith('.html'))
    
    available = [t for t in TOPICS if t['slug'] not in existing]
    
    if not available:
        print("\n✅ Alle Themen bereits generiert! Keine neuen Artikel nötig.")
        return 0
    
    topic = available[0]
    today_str = datetime.now().strftime('%d. %B %Y').lstrip('0')
    today_iso = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📌 Thema: {topic['title']}")
    print(f"   Kategorien: {', '.join(topic['category_tags'])}")
    print(f"   Noch verfügbar: {len(available)-1} Themen")
    
    # Step 1: Generate text
    body = generate_text(topic)
    if not body:
        print("\n❌ Textgenerierung fehlgeschlagen. Abbruch.")
        return 1
    
    # Step 2: Generate image
    image_ok = generate_image(topic)
    
    # Step 3: Build HTML
    html = build_html(topic, body, today_str, today_iso)
    art_path = os.path.join(REPO, "artikel", f"{topic['slug']}.html")
    os.makedirs(os.path.dirname(art_path), exist_ok=True)
    with open(art_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  📄 Artikel geschrieben: {topic['slug']}.html ({len(html)//1024}KB)")
    
    # Step 4: Update sitemap
    update_sitemap(topic['slug'], today_iso)
    
    # Step 5: Update homepage stat
    update_homepage_count()
    
    # Step 6: Git commit + push
    print(f"  📤 Deploye...", end=" ", flush=True)
    if git_commit_push(topic['slug']):
        print(f"  ✅ Fertig! {topic['title']}")
        return 0
    else:
        print(f"  ⚠️  Git Push fehlgeschlagen, Artikel lokal gespeichert")
        return 1


if __name__ == "__main__":
    sys.exit(main())
