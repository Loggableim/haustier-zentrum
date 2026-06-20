#!/usr/bin/env python3
"""
_extend_thin_articles.py — Verlängert dünne haustierzentrum-Artikel auf 1500+ Wörter
via MiniMax-M3 (mit OpenRouter-Fallback).

State-File: C:\\sidekick\\home\\spaces\\haustier-zentrum\\extend_state.json
  {
    "completed": ["slug1", "slug2", ...],
    "last_run": "2026-06-20T00:00:00"
  }

Pro Run wird EIN Artikel verarbeitet (cron-freundlich, ~60s pro Artikel).
Bei 'katzen' (Hub-Page ohne Body) wird komplett neuer Content generiert.

Author: Haustierzentrum CEO
"""
import json, os, re, sys, time, urllib.request, urllib.error, ssl
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
ART_DIR = BASE / "artikel"
STATE_FILE = BASE / "extend_state.json"

# ── API Config ──
# Try workspace key first, then C:\sidekick\home\auth.json
try:
    sys.path.insert(0, str(BASE))
    from _minimax_key import API_KEY as MM_KEY
except ImportError:
    MM_KEY = ""

try:
    with open(r"C:\sidekick\home\auth.json", encoding="utf-8") as f:
        auth = json.load(f)
    OR_KEY = auth["credential_pool"]["openrouter"][0]["access_token"]
except Exception:
    OR_KEY = ""

MM_BASE = "https://api.minimax.io/v1/chat/completions"
OR_BASE = "https://openrouter.ai/api/v1/chat/completions"

# Die 6 dünnsten Artikel (380-700 Wörter) — Ziel: 1500+
THIN_ARTICLES = [
    "katzen",                          # 381w — Hub-Page, full body needed
    "britisch-kurzhaar-rasseguide",    # 502w
    "katzenhaltung-wohnung",           # 575w
    "hundeerziehung-grundlagen",       # 592w
    "kleintiere-hamster-meerschweinchen", # 626w
    "wellensittich-haltung",           # 641w
]

# ── System Prompt ──
SYSTEM_PROMPT = """Du bist ein deutscher SEO-Content-Autor für haustierzentrum.com.
Schreibe direkt, persönlich (Du-Form), bodenständig und warmherzig.
Verwende echte Umlaute (ä/ö/ü/ß) — NIEMALS ae/oe/ue/ss.
Kein BWL-Geschwafel. Praxisorientierte Ratgeber.
KEINE <think>-Tags oder Gedankenprozesse. Gib NUR den fertigen Text aus."""


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"completed": [], "last_run": None}


def save_state(state: dict):
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def call_minimax(prompt: str, system: str = SYSTEM_PROMPT, max_tokens: int = 6000) -> str | None:
    if not MM_KEY: return None
    payload = json.dumps({
        "model": "MiniMax-M3",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    headers = {"Authorization": f"Bearer {MM_KEY}", "Content-Type": "application/json"}
    ctx = ssl.create_default_context()
    req = urllib.request.Request(MM_BASE, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
            result = json.loads(resp.read())
        if "choices" in result:
            content = result["choices"][0]["message"]["content"]
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
            return content if content else None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        if "2056" in body: return "TOKEN_LIMIT"
        print(f"  [MiniMax] HTTP {e.code}: {body[:200]}")
    except Exception as e:
        print(f"  [MiniMax] {e}")
    return None


def call_openrouter(prompt: str, system: str = SYSTEM_PROMPT, max_tokens: int = 6000) -> str | None:
    if not OR_KEY: return None
    payload = json.dumps({
        "model": "openrouter/auto",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://haustierzentrum.com",
        "X-Title": "Haustierzentrum Article Extender",
    }
    req = urllib.request.Request(OR_BASE, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [OpenRouter] {e}")
    return None


def generate(prompt: str) -> str | None:
    print("  [LLM] MiniMax-M3...", end=" ", flush=True)
    result = call_minimax(prompt)
    if result == "TOKEN_LIMIT":
        print("⛔ fallback to OpenRouter...", end=" ", flush=True)
        result = call_openrouter(prompt)
    if result:
        # Cleanup
        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
        result = result.replace('\u00a0', ' ').replace('\u202f', ' ')
        print(f"✅ {len(result)} chars")
        return result
    print("❌")
    return None


def get_existing_h2s(html: str) -> list:
    return re.findall(r'<h2>(.*?)</h2>', html, re.DOTALL)


def get_body(html: str) -> tuple:
    """Return (body_start_idx, body_end_idx) for the article content body."""
    # Try article-content div first
    m = re.search(r'class="article-content"[^>]*>', html)
    if m:
        start = m.end()
        # Find matching </div></article> or just </div>
        # The article-content div is closed by the FIRST </div> after it that doesn't have a nested div
        # Simpler: find first </div> at the same nesting level
        # Look for either </div></article> pattern
        end_pat = re.search(r'</div>\s*</article>', html[start:])
        if end_pat:
            return start, start + end_pat.start()
        end_pat = re.search(r'</div>\s*</main>', html[start:])
        if end_pat:
            return start, start + end_pat.start()
        end_pat = re.search(r'</div>\s*<footer', html[start:])
        if end_pat:
            return start, start + end_pat.start()
    return None, None


def extend_article(slug: str) -> bool:
    """Verlängere einen Artikel auf 1500+ Wörter."""
    art = ART_DIR / f"{slug}.html"
    if not art.exists():
        print(f"  ❌ File not found: {slug}")
        return False
    html = art.read_text(encoding="utf-8")

    # Get title
    h1 = re.search(r'<h1>(.*?)</h1>', html, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else slug

    # Get current H2s and word count
    existing_h2s = get_existing_h2s(html)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    current_words = len(text.split())

    print(f"\n📝 {slug}  |  Title: {title}")
    print(f"   Current: {current_words}w, {len(existing_h2s)} H2s")

    body_start, body_end = get_body(html)
    if body_start is None:
        # Hub page like 'katzen' — need to inject before related-posts
        if 'class="related-posts"' in html:
            body_start = html.find('<section class="related-posts">')
            body_end = body_start
        else:
            # Find <footer
            m = re.search(r'<footer', html)
            if m:
                body_start = m.start()
                body_end = m.start()
            else:
                # Find </body>
                m = re.search(r'</body>', html)
                body_start = m.start() if m else len(html) - 10
                body_end = body_start
        is_hub = True
    else:
        is_hub = False

    if is_hub or current_words < 700:
        # Generate full body
        prompt = f"""Schreibe einen ausführlichen einleitenden Hauptteil (ohne <h1>) für folgenden Artikel auf haustierzentrum.com:

TITEL: {title}

AUFGABE: Der Artikel hat aktuell KEINEN echten Content-Body (nur Header, Meta, Related-Posts). 
Generiere 1200-1500 Wörter SEO-optimierten Content in folgendem Format:

1. Einleitung (2-3 Absätze, ca. 200 Wörter) — was den Leser erwartet
2. 4-5 H2-Hauptabschnitte (je 200-300 Wörter) zu diesen Themen:
   - Grundlagen / Was man wissen muss
   - Praktische Tipps / Haltung / Pflege
   - Häufige Fehler vermeiden
   - Kosten / Zeitaufwand
   - Fazit / Empfehlung
3. KEIN abschließendes Fazit (das wird separat gemacht)

WICHTIG:
- Nur HTML-Body-Fragment (KEIN <html><head><body>, KEIN <h1>, KEIN <footer>)
- Echte Umlaute ä/ö/ü/ß
- Praxisorientiert, Du-Form, warmherzig
- Mindestens 1200 Wörter
- KEINE <think>-Tags
- 4-5 <h2>Überschriften</h2>
- Absätze als <p>...</p>
- Bullet-Points als <ul><li>...</li></ul>"""
    else:
        # Generate extension
        h2_list = "\n".join(f"  - {h[:80]}" for h in existing_h2s)
        prompt = f"""Verlängere folgenden haustierzentrum.com-Artikel um zusätzliche 1000-1500 Wörter.

TITEL: {title}

BESTEHENDE H2-ABSCHNITTE (NICHT wiederholen!):
{h2_list}

AUFGABE: Generiere 2-3 NEUE H2-Abschnitte, die das Thema sinnvoll ergänzen — z.B.:
  - Häufige Fehler / Mythen
  - Praxisbeispiele / Erfahrungsberichte
  - Spezielle Tipps für Fortgeschrittene
  - Wissenschaftliche Hintergründe / Studien
  - Saisonale Aspekte

FORMAT:
- Nur HTML-Body-Fragment (KEIN <html><head><body>, KEIN <h1>)
- 2-3 <h2>Überschriften</h2>
- Jeder Abschnitt: 300-500 Wörter, mehrere <p>-Tags, ggf. <ul>-Listen
- Echte Umlaute ä/ö/ü/ß
- Du-Form, warmherzig, praxisorientiert
- KEINE <think>-Tags
- KEIN Fazit, KEIN Disclaimer (das ist schon im Original)"""

    new_content = generate(prompt)
    if not new_content:
        print(f"  ❌ Generation failed")
        return False

    # Strip any H1 / DOCTYPE / html tags that may have leaked
    new_content = re.sub(r'<!DOCTYPE[^>]*>', '', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'</?html[^>]*>', '', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'</?head[^>]*>', '', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'</?body[^>]*>', '', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'<h1[^>]*>.*?</h1>', '', new_content, flags=re.DOTALL|re.IGNORECASE)

    # Insert
    if is_hub or body_start is None or body_start == body_end:
        # Hub: wrap in article-content div if missing
        if 'class="article-content"' not in html:
            # Find <h1> and add article-content div after the article-meta
            m = re.search(r'</h1>.*?(<div class="article-meta">.*?</div>)', html, re.DOTALL)
            if m:
                # Find the end of article-meta
                meta_end = m.end()
                wrapped = f'\n        <div class="article-content">\n{new_content}\n        </div>'
                html = html[:meta_end] + wrapped + html[meta_end:]
            else:
                # Just inject before related-posts
                html = html.replace('<section class="related-posts">', f'\n  {new_content}\n\n  <section class="related-posts">', 1)
        else:
            html = html[:body_start] + new_content + '\n' + html[body_end:]
    else:
        # Normal: insert at end of body (before closing </div>)
        html = html[:body_end] + '\n' + new_content + '\n' + html[body_end:]

    art.write_text(html, encoding="utf-8")

    # Verify new word count
    new_text = re.sub(r'<[^>]+>', ' ', html)
    new_text = re.sub(r'\s+', ' ', new_text).strip()
    new_words = len(new_text.split())
    print(f"   New: {new_words}w  (Δ +{new_words - current_words})")

    return True


def main():
    state = load_state()
    completed = set(state.get("completed", []))

    # Find next unprocessed article
    next_slug = None
    for slug in THIN_ARTICLES:
        if slug not in completed:
            next_slug = slug
            break

    if not next_slug:
        print(f"✅ All {len(THIN_ARTICLES)} articles already extended!")
        return

    print(f"Processing: {next_slug}  ({len(completed)}/{len(THIN_ARTICLES)} done)")

    success = extend_article(next_slug)
    if success:
        completed.add(next_slug)
        state["completed"] = sorted(completed)
        save_state(state)
        print(f"  ✅ State updated: {next_slug} marked done")
    else:
        print(f"  ❌ Failed, will retry next run")


if __name__ == '__main__':
    main()
