#!/usr/bin/env python3
"""Batch-update all article HTML files to use the mega menu header."""
import os, glob, re

ARTIKEL_DIR = "C:/HermesPortable/home/scripts/blog-automation/haustier-zentrum/artikel"
LABRADOR_FILE = os.path.join(ARTIKEL_DIR, "labrador-retriever.html")

# --- Replacement: --border-light variable ---
OLD_BORDER = """  --border: #e0e0e0;
  --card-shadow: 0 2px 12px rgba(0,0,0,.08);"""
NEW_BORDER = """  --border: #e0e0e0;
  --border-light: #f0ece1;
  --card-shadow: 0 2px 12px rgba(0,0,0,.08);"""

# --- Replacement: site-header + nav CSS (lines 56-93 in original) ---
OLD_HEADER_CSS = """.site-header{
  background:var(--bg);
  border-bottom:2px solid var(--primary);
  padding:0 1rem;
  position:sticky;
  top:0;
  z-index:100;
}
.nav-wrap{
  max-width:1100px;
  margin:0 auto;
  display:flex;
  align-items:center;
  justify-content:space-between;
  height:64px;
}
.logo{
  font-size:1.4rem;
  font-weight:800;
  color:var(--primary);
  letter-spacing:-.5px;
}
.logo:hover{text-decoration:none}
.nav-links{display:flex;gap:1.5rem;list-style:none}
.nav-links a{
  color:var(--text);
  font-weight:500;
  font-size:.95rem;
  padding:.3rem 0;
  border-bottom:2px solid transparent;
  transition:.2s;
}
.nav-links a:hover,.nav-links a.active{
  color:var(--primary);
  border-bottom-color:var(--primary);
  text-decoration:none;
}
.nav-toggle{display:none;background:none;border:none;font-size:1.6rem;cursor:pointer;color:var(--text);padding:.25rem;}
main{flex:1;max-width:1100px;margin:0 auto;padding:2rem 1rem;width:100%}"""

NEW_HEADER_CSS = """.site-header{
  background:rgba(255,255,255,.92);
  backdrop-filter:blur(16px) saturate(1.2);
  border-bottom:3px solid var(--primary);
  padding:0 1rem;
  position:sticky;
  top:0;
  z-index:1000;
}
.nav-wrap{
  max-width:1200px;
  margin:0 auto;
  display:flex;
  align-items:center;
  justify-content:space-between;
  height:72px;
}
.logo{
  font-size:1.4rem;
  font-weight:900;
  letter-spacing:-1px;
  background:linear-gradient(135deg,var(--primary-dark),var(--primary));
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
  flex-shrink:0;
}
.logo span{font-weight:400;color:var(--text-muted);-webkit-text-fill-color:var(--text-muted);}
.logo:hover{text-decoration:none}
.main-nav{display:flex;align-items:center}
.nav-links{display:flex;gap:0;list-style:none;align-items:center;margin:0;padding:0}
.nav-links > li{position:relative}
.nav-links > li > a{
  color:var(--text);
  font-weight:600;
  font-size:.85rem;
  padding:.4rem 1rem;
  border-radius:50px;
  transition:.2s;
  letter-spacing:.2px;
  display:flex;
  align-items:center;
  gap:.3rem;
  white-space:nowrap;
}
.nav-links > li > a .arrow{
  font-size:.6rem;
  transition:transform .25s;
  display:inline-block;
}
.nav-links > li:hover > a .arrow{
  transform:rotate(180deg);
}
.nav-links > li > a:hover,
.nav-links > li > a.active{
  color:#fff;
  background:var(--primary);
  text-decoration:none;
}
.nav-links > li.simple-link > a{
  color:var(--text-muted);
  font-weight:500;
  font-size:.8rem;
}
.nav-links > li.simple-link > a:hover{
  color:#fff;
}
.mega-panel{
  position:absolute;
  top:100%;
  left:50%;
  transform:translateX(-50%) translateY(12px);
  background:#fff;
  border-radius:16px;
  box-shadow:0 20px 60px rgba(0,0,0,.15), 0 4px 20px rgba(0,0,0,.06);
  min-width:680px;
  max-width:900px;
  padding:0;
  opacity:0;
  visibility:hidden;
  transition:all .25s cubic-bezier(.16,1,.3,1);
  border:1px solid var(--border-light);
  overflow:hidden;
  pointer-events:none;
}
.nav-links > li:hover .mega-panel{
  opacity:1;
  visibility:visible;
  transform:translateX(-50%) translateY(8px);
  pointer-events:auto;
}
.mega-grid{
  display:grid;
  gap:0;
  padding:1.5rem;
}
.mega-grid.cols-2{grid-template-columns:1fr 1fr}
.mega-grid.cols-3{grid-template-columns:1fr 1fr 1fr}
.mega-grid.cols-4{grid-template-columns:1fr 1fr 1fr 1fr}
.mega-col{
  padding:0 .8rem;
  border-right:1px solid var(--border-light);
}
.mega-col:last-child{border-right:none}
.mega-col h4{
  font-size:.7rem;
  text-transform:uppercase;
  letter-spacing:1px;
  color:var(--primary);
  font-weight:700;
  margin:0 0 .6rem 0;
  padding-bottom:.4rem;
  border-bottom:2px solid var(--primary-light);
}
.mega-col a{
  display:flex;
  align-items:center;
  gap:.4rem;
  padding:.35rem .5rem;
  border-radius:8px;
  color:var(--text);
  font-size:.82rem;
  font-weight:500;
  transition:all .15s;
  text-decoration:none;
  line-height:1.3;
}
.mega-col a:hover{
  background:var(--primary-light);
  color:var(--primary-dark);
  text-decoration:none;
}
.mega-col a .badge{
  font-size:.6rem;
  background:var(--primary);
  color:#fff;
  padding:.1rem .4rem;
  border-radius:20px;
  font-weight:700;
  margin-left:auto;
  animation:pulse-badge 2s infinite;
}
@keyframes pulse-badge{
  0%,100%{opacity:1}
  50%{opacity:.6}
}
.mega-col a .desc{
  font-size:.68rem;
  color:var(--text-muted);
  font-weight:400;
  display:block;
  margin-left:1.6rem;
  margin-top:-.1rem;
}
.mega-featured{
  background:linear-gradient(135deg,var(--primary-light),#fff8e1);
  border-radius:12px;
  padding:.8rem 1rem;
  margin-top:.6rem;
  display:flex;
  align-items:center;
  gap:.8rem;
}
.mega-featured img{
  width:52px;
  height:52px;
  border-radius:8px;
  object-fit:cover;
  flex-shrink:0;
}
.mega-featured .meta{flex:1}
.mega-featured .meta strong{display:block;font-size:.82rem;color:var(--text)}
.mega-featured .meta span{font-size:.7rem;color:var(--text-muted)}
.search-btn{
  background:none;
  border:none;
  font-size:1.1rem;
  cursor:pointer;
  color:var(--text-muted);
  padding:.4rem .6rem;
  border-radius:50px;
  transition:.2s;
  display:flex;
  align-items:center;
  flex-shrink:0;
}
.search-btn:hover{
  background:var(--primary-light);
  color:var(--primary);
}
.nav-toggle{
  display:none;
  background:none;
  border:none;
  font-size:1.6rem;
  cursor:pointer;
  color:var(--text);
  padding:.25rem;
}
main{flex:1;max-width:1100px;margin:0 auto;padding:2rem 1rem;width:100%}"""

# --- Replacement: old mobile responsive CSS ---
OLD_MOBILE_CSS = """@media(max-width:768px){
  .nav-links{
    display:none;
    position:absolute;
    top:64px;
    left:0;
    right:0;
    background:var(--bg);
    flex-direction:column;
    padding:1rem;
    border-bottom:2px solid var(--primary);
    box-shadow:0 4px 12px rgba(0,0,0,.1);
    gap:.25rem;
  }
  .nav-links.open{display:flex}
  .nav-toggle{display:block}
  .article-header h1{font-size:1.5rem}
  .article-content table{font-size:.82rem}
  .article-content table th,.article-content table td{padding:.5rem}
  .related-grid{grid-template-columns:1fr}
  .cookie-banner{flex-direction:column;text-align:center}
}"""

NEW_MOBILE_CSS = """@media(max-width:900px){
  .main-nav{
    position:fixed;
    top:72px;
    left:0;
    right:0;
    bottom:0;
    background:rgba(255,255,255,.98);
    backdrop-filter:blur(20px);
    flex-direction:column;
    padding:1rem;
    overflow-y:auto;
    transform:translateX(100%);
    transition:transform .35s cubic-bezier(.16,1,.3,1);
    z-index:999;
  }
  .main-nav.open{transform:translateX(0)}
  .nav-links{flex-direction:column;width:100%;gap:0}
  .nav-links > li{width:100%}
  .nav-links > li > a{
    padding:.8rem 1rem;
    border-radius:12px;
    font-size:.95rem;
    justify-content:space-between;
  }
  .nav-links > li > a .arrow{font-size:.8rem}
  .mega-panel{
    position:static;
    transform:none;
    opacity:1;
    visibility:visible;
    box-shadow:none;
    border:none;
    border-radius:0;
    min-width:auto;
    max-width:100%;
    padding:0;
    max-height:0;
    overflow:hidden;
    transition:max-height .35s cubic-bezier(.16,1,.3,1),padding .35s;
    pointer-events:auto;
    background:var(--bg-alt);
    margin:0;
    border-radius:12px;
  }
  .nav-links > li.open .mega-panel{
    max-height:800px;
    padding:.8rem;
    margin-bottom:.5rem;
  }
  .mega-grid{
    grid-template-columns:1fr 1fr !important;
    padding:.5rem;
    gap:.5rem;
  }
  .mega-col{
    border-right:none;
    padding:0;
  }
  .mega-col h4{font-size:.75rem;margin-bottom:.4rem}
  .mega-col a{padding:.3rem .5rem;font-size:.85rem}
  .search-btn{display:none}
  .nav-toggle{display:block}
  .nav-links > li.simple-link{
    border-top:1px solid var(--border-light);
    padding-top:.5rem;
    margin-top:.3rem;
  }
}
@media(max-width:500px){
  .mega-grid{grid-template-columns:1fr !important}
}
@media(max-width:768px){
  .article-header h1{font-size:1.5rem}
  .article-content table{font-size:.82rem}
  .article-content table th,.article-content table td{padding:.5rem}
  .related-grid{grid-template-columns:1fr}
  .cookie-banner{flex-direction:column;text-align:center}
}"""

# --- Replacement: old header HTML ---
OLD_HEADER_HTML = """<header class=\"site-header\">
  <div class=\"nav-wrap\">
    <a href=\"/\" class=\"logo\">🐾 Haustierzentrum</a>
    <button class=\"nav-toggle\" aria-label=\"Menü\" onclick=\"document.querySelector('.nav-links').classList.toggle('open')\">☰</button>
    <ul class=\"nav-links\">
      <li><a href=\"/\">Start</a></li>
      <li><a href=\"/artikel/hunderassen-anfaenger.html\">Hunde</a></li>
      <li><a href=\"/artikel/katzenhaltung-wohnung.html\">Katzen</a></li>
      <li><a href=\"/artikel/kleintiere-hamster-meerschweinchen.html\">Kleintiere</a></li>
      <li><a href=\"/about.html\">Über uns</a></li>
      <li><a href=\"/impressum.html\">Impressum</a></li>
    </ul>
  </div>
</header>"""

NEW_HEADER_HTML = """<!-- ============ HEADER ============ -->
<header class=\"site-header\">
  <div class=\"nav-wrap\">
    <a href=\"/\" class=\"logo\">🐾 Haustier<span>zentrum</span></a>
    <button class=\"nav-toggle\" aria-label=\"Menü\" onclick=\"document.querySelector('.main-nav').classList.toggle('open');this.textContent=this.textContent=='☰'?'✕':'☰'\">☰</button>
    <nav class=\"main-nav\">
      <ul class=\"nav-links\">
        <!-- HUNDE -->
        <li>
          <a href=\"/artikel/hunderassen-anfaenger.html\">Hunde <span class=\"arrow\">▾</span></a>
          <div class=\"mega-panel\">
            <div class=\"mega-grid cols-4\">
              <div class=\"mega-col\">
                <h4>🐕 Rassen</h4>
                <a href=\"/artikel/hunderassen-anfaenger.html\">🐕 Hunderassen für Anfänger <span class=\"badge\">Top</span></a>
                <a href=\"/artikel/labrador-retriever.html\">🐕 Labrador Retriever <span class=\"badge\">Neu</span></a>
                <a href=\"/artikel/franzoesische-bulldogge-rasseguide.html\">🐕 Französische Bulldogge</a>
              </div>
              <div class=\"mega-col\">
                <h4>🎓 Erziehung</h4>
                <a href=\"/artikel/hundeerziehung-grundlagen.html\">🎓 Hundeerziehung Grundlagen</a>
                <a href=\"/artikel/leinenfuehrigkeit.html\">🦮 Leinenführigkeit & Ziehen</a>
                <a href=\"/artikel/welpen-eingewoehnung.html\">🐾 Welpeneingewöhnung</a>
              </div>
              <div class=\"mega-col\">
                <h4>🏥 Gesundheit & Pflege</h4>
                <a href=\"/artikel/hunde-gesundheit.html\">🏥 Hundegesundheit & Vorsorge</a>
                <a href=\"/artikel/hunde-fellpflege-buersten-baden-krallen.html\">🧴 Fellpflege & Baden</a>
                <a href=\"/artikel/hunde-zahnpflege.html\">🪥 Zahnpflege für Hunde</a>
                <a href=\"/artikel/zeckenschutz-flohschutz-hund.html\">🌿 Zecken- & Flohschutz</a>
                <a href=\"/artikel/hunde-hausmittel.html\">🏡 Hausmittel für Hunde</a>
              </div>
              <div class=\"mega-col\">
                <h4>🥩 Ernährung & Mehr</h4>
                <a href=\"/artikel/hundeernaehrung.html\">🥩 Hundeernährung</a>
                <a href=\"/artikel/hunde-uebergewicht.html\">⚖️ Übergewicht bei Hunden</a>
                <a href=\"/artikel/hundespielzeuge-2026.html\">🎾 Hundespielzeug 2026</a>
                <a href=\"/artikel/hundeversicherung.html\">🛡️ Hundeversicherung</a>
                <a href=\"/artikel/hunde-reisen.html\">✈️ Reisen mit Hund</a>
              </div>
            </div>
          </div>
        </li>
        <!-- KATZEN -->
        <li>
          <a href=\"/artikel/katzenhaltung-wohnung.html\">Katzen <span class=\"arrow\">▾</span></a>
          <div class=\"mega-panel\">
            <div class=\"mega-grid cols-3\">
              <div class=\"mega-col\">
                <h4>🏠 Haltung</h4>
                <a href=\"/artikel/katzenhaltung-wohnung.html\">🏠 Wohnungshaltung</a>
                <a href=\"/artikel/katzen-freigaenger.html\">🌳 Freigänger</a>
                <a href=\"/artikel/seniorkatzen-pflege-ernaehrung-gesundheit.html\">👵 Seniorkatzen</a>
              </div>
              <div class=\"mega-col\">
                <h4>🥫 Ernährung & Gesundheit</h4>
                <a href=\"/artikel/katzen-ernaehrung.html\">🥫 Katzenernährung</a>
                <a href=\"/artikel/katzenfutter-vergleich-2026.html\">🥩 Katzenfutter Vergleich</a>
                <a href=\"/artikel/katzenkrankheiten-erkennen.html\">🏥 Katzenkrankheiten</a>
                <a href=\"/artikel/katzen-impfungen-vorsorge.html\">💉 Impfungen & Vorsorge</a>
                <a href=\"/artikel/katzen-zahnpflege.html\">🪥 Zahnpflege</a>
              </div>
              <div class=\"mega-col\">
                <h4>🎾 Beschäftigung & Rassen</h4>
                <a href=\"/artikel/katzenbeschaeftigung.html\">🎾 Beschäftigungsideen</a>
                <a href=\"/artikel/katzen-kratzbaum.html\">🌲 Kratzbäume</a>
                <a href=\"/artikel/katzentoilette-geruch-vermeiden.html\">🚽 Katzentoilette</a>
                <a href=\"/artikel/katzenrassen-vergleich.html\">🐱 Katzenrassen Vergleich</a>
              </div>
            </div>
          </div>
        </li>
        <!-- KLEINTIERE -->
        <li>
          <a href=\"/artikel/kleintiere-hamster-meerschweinchen.html\">Kleintiere <span class=\"arrow\">▾</span></a>
          <div class=\"mega-panel\">
            <div class=\"mega-grid cols-3\">
              <div class=\"mega-col\">
                <h4>🐹 Nagetiere</h4>
                <a href=\"/artikel/hamster-haltung.html\">🐹 Hamster Haltung</a>
                <a href=\"/artikel/meerschweinchen-haltung.html\">🐹 Meerschweinchen Haltung</a>
                <a href=\"/artikel/kaninchenhaltung.html\">🐰 Kaninchenhaltung</a>
              </div>
              <div class=\"mega-col\">
                <h4>🥗 Ernährung & Gehege</h4>
                <a href=\"/artikel/meerschweinchen-ernaehrung-vitamin-c.html\">🥗 Meerschweinchen Ernährung</a>
                <a href=\"/artikel/kleintier-gehege.html\">🏠 Kleintiergehege</a>
                <a href=\"/artikel/kleintiere-hamster-meerschweinchen.html\">🐹 Hamster & Meerschweinchen</a>
              </div>
              <div class=\"mega-col\">
                <h4>🐦 Vögel & Aquarien</h4>
                <a href=\"/artikel/voegel-haustier-beste-vogelarten-einsteiger.html\">🐦 Vögel als Haustiere</a>
                <a href=\"/artikel/wellensittich-haltung.html\">🐦 Wellensittich Haltung</a>
                <a href=\"/artikel/aquarium-einrichtung.html\">🐟 Aquarium Einrichtung</a>
              </div>
            </div>
          </div>
        </li>
        <!-- RATGEBER -->
        <li>
          <a href=\"/artikel/haustier-anschaffung.html\">Ratgeber <span class=\"arrow\">▾</span></a>
          <div class=\"mega-panel\" style=\"min-width:450px;\">
            <div class=\"mega-grid cols-2\">
              <div class=\"mega-col\">
                <h4>📋 Allgemein</h4>
                <a href=\"/artikel/haustier-anschaffung.html\">📋 Haustier Anschaffung</a>
                <a href=\"/artikel/haustiere-kinder.html\">👨‍👩‍👧‍👦 Haustiere & Kinder</a>
              </div>
              <div class=\"mega-col\">
                <h4>💰 Gesundheit & Kosten</h4>
                <a href=\"/artikel/tierarztkosten.html\">💰 Tierarztkosten</a>
                <a href=\"/artikel/allergiker-haustiere.html\">🤧 Allergiker & Haustiere</a>
                <div class=\"mega-featured\">
                  <img src=\"../images/labrador-retriever_00001_.png\" alt=\"Labrador\" loading=\"lazy\">
                  <div class=\"meta\">
                    <strong>📖 Neuer Artikel</strong>
                    <span>Labrador Retriever Rasseguide</span>
                    <a href=\"/artikel/labrador-retriever.html\" style=\"font-size:.7rem;\">Jetzt lesen →</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </li>
        <!-- Simple Links -->
        <li class=\"simple-link\"><a href=\"/\">Start</a></li>
        <li class=\"simple-link\"><a href=\"/about.html\">Über uns</a></li>
        <li class=\"simple-link\"><a href=\"/impressum.html\">Impressum</a></li>
      </ul>
    </nav>
    <button class=\"search-btn\" onclick=\"window.location.href='/?s='\" aria-label=\"Suche\">🔍</button>
  </div>
</header>"""

# --- Replacement: old script ---
OLD_SCRIPT = """document.querySelectorAll('.nav-links a').forEach(l=>l.addEventListener('click',()=>{
  document.querySelector('.nav-links').classList.remove('open')
}))"""

NEW_SCRIPT = """// Mobile: close nav when simple links are clicked
document.querySelectorAll('.simple-link a').forEach(l=>l.addEventListener('click',()=>{
  document.querySelector('.main-nav').classList.remove('open');
  document.querySelector('.nav-toggle').textContent='☰';
}))
// Mobile: tap mega-menu items to toggle panels
document.querySelectorAll('.nav-links > li:not(.simple-link) > a').forEach(l=>l.addEventListener('click',function(e){
  if(document.querySelector('.main-nav').classList.contains('open')){
    e.preventDefault();
    this.parentElement.classList.toggle('open');
  }
}))"""


def apply_replacements(filepath):
    """Apply all replacements to a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # 1. Add --border-light
    if OLD_BORDER in content:
        content = content.replace(OLD_BORDER, NEW_BORDER)
        changes.append("border-light var")
    else:
        # Check if already has border-light
        if '--border-light' in content:
            changes.append("border-light already present")
        else:
            changes.append("border-light NOT FOUND!")
    
    # 2. Replace header CSS
    if OLD_HEADER_CSS in content:
        content = content.replace(OLD_HEADER_CSS, NEW_HEADER_CSS)
        changes.append("header CSS")
    else:
        # Maybe already updated?
        if '.mega-panel' in content:
            changes.append("header CSS already mega")
        else:
            changes.append("header CSS NOT FOUND!")
    
    # 3. Replace mobile CSS
    if OLD_MOBILE_CSS in content:
        content = content.replace(OLD_MOBILE_CSS, NEW_MOBILE_CSS)
        changes.append("mobile CSS")
    else:
        if 'max-width:900px' in content:
            changes.append("mobile CSS already mega")
        else:
            changes.append("mobile CSS NOT FOUND!")
    
    # 4. Replace header HTML
    if OLD_HEADER_HTML in content:
        content = content.replace(OLD_HEADER_HTML, NEW_HEADER_HTML)
        changes.append("header HTML")
    else:
        if 'mega-panel' in content:
            changes.append("header HTML already mega")
        else:
            changes.append("header HTML NOT FOUND!")
    
    # 5. Replace script
    if OLD_SCRIPT in content:
        content = content.replace(OLD_SCRIPT, NEW_SCRIPT)
        changes.append("script")
    else:
        if 'simple-link' in content and 'main-nav' in content:
            changes.append("script already mega")
        else:
            changes.append("script NOT FOUND!")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ UPDATED: {', '.join(changes)}")
        return True, changes
    else:
        print(f"  ⏭️  SKIPPED: {', '.join(changes)}")
        return False, changes


def main():
    files = sorted(glob.glob(os.path.join(ARTIKEL_DIR, "*.html")))
    # Exclude labrador-retriever (already done)
    files = [f for f in files if 'labrador-retriever' not in f]
    
    print(f"Found {len(files)} article files to update\n")
    
    ok = 0
    skipped = 0
    errors = 0
    
    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            updated, changes = apply_replacements(fpath)
            if updated:
                ok += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ ERROR {fname}: {e}")
            errors += 1
    
    print(f"\n--- Done: {ok} updated, {skipped} skipped, {errors} errors ---")


if __name__ == '__main__':
    main()
