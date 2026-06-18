#!/usr/bin/env python3
"""Restructure homepage: category filters, load-more, external CSS."""
import re, os

INDEX = r'C:\hermesportable\home\spaces\haustier-zentrum\index.html'

with open(INDEX, 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Extract CSS into external file ──
css_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
inline_css = css_match.group(1) if css_match else ''

# Write the CSS file
css_dir = r'C:\hermesportable\home\spaces\haustier-zentrum\css'
os.makedirs(css_dir, exist_ok=True)
css_path = os.path.join(css_dir, 'style.css')
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(inline_css)
print(f"✅ CSS ausgelagert: css/style.css ({len(inline_css)//1024}KB)")

# ── 2. Replace inline <style> with <link> ──
html = html.replace(
    '<style>' + inline_css + '</style>',
    '<link rel="stylesheet" href="css/style.css">'
)

# ── 3. Add theme-color meta tag (already there from earlier fix, ensure it's present) ──
if 'theme-color' not in html:
    html = html.replace(
        '<meta name="robots" content="index, follow">',
        '<meta name="robots" content="index, follow">\n<meta name="theme-color" content="#FF9800">'
    )

# ── 4. Replace the "Alle Beiträge" section header with category tabs ──
old_header = '''  <div class="section-header">
    <div class="sketch-divider"></div>
    <h2>📖 Alle Beiträge</h2>
    <p>42+ Ratgeber, ständig wachsend. Für jedes Haustier und jede Frage die richtige Antwort.</p>
  </div>
  <div class="articles-grid">'''

new_header = '''  <div class="section-header">
    <div class="sketch-divider"></div>
    <h2>📖 Alle Beiträge</h2>
    <p>98+ Ratgeber, ständig wachsend. Für jedes Haustier und jede Frage die richtige Antwort.</p>
  </div>
  <div class="filter-tabs">
    <button class="filter-btn active" data-filter="all">🐾 Alle</button>
    <button class="filter-btn" data-filter="hunde">🐕 Hunde</button>
    <button class="filter-btn" data-filter="katzen">🐈 Katzen</button>
    <button class="filter-btn" data-filter="kleintiere">🐹 Kleintiere</button>
    <button class="filter-btn" data-filter="voegel">🐦 Vögel</button>
    <button class="filter-btn" data-filter="aquarium">🐟 Aquarium</button>
    <button class="filter-btn" data-filter="allgemein">📋 Allgemein</button>
  </div>
  <div class="articles-grid" id="article-grid">'''

html = html.replace(old_header, new_header)

# ── 5. Inject data-cat attribute into each article card based on its <span> categories ──
# Find all article cards and add data-cat based on the first category span
def add_data_cat(match):
    full = match.group(0)
    # Extract the category from <span> tags inside card-cats
    cats_match = re.search(r'<div class="card-cats">(.*?)</div>', full, re.DOTALL)
    if cats_match:
        spans = re.findall(r'<span>([^<]+)</span>', cats_match.group(1))
        primary = spans[0].lower() if spans else 'allgemein'
        # Map to filter categories
        cat_map = {
            'hunde': 'hunde', 'hunderassen': 'hunde', 'welpen': 'hunde',
            'erziehung': 'hunde', 'gesundheit': 'hunde', 'betreuung': 'hunde',
            'pension': 'hunde', 'hundeschule': 'hunde', 'ernährung': 'hunde',
            'fellpflege': 'hunde', 'versicherung': 'hunde', 'reisen': 'hunde',
            'spielzeug': 'hunde', 'übergewicht': 'hunde', 'zahnpflege': 'hunde',
            'allergien': 'hunde', 'erstausstattung': 'hunde', 'rasseporträt': 'hunde',
            'haustierratgeber': 'hunde', 'hunderasse': 'hunde',
            'katzen': 'katzen', 'katzenrassen': 'katzen', 'katzenerziehung': 'katzen',
            'training': 'katzen', 'beschäftigung': 'katzen', 'vorsorge': 'katzen',
            'senioren': 'katzen', 'wohnungshaltung': 'katzen', 'sicherheit': 'katzen',
            'freigänger': 'katzen', 'kratzbaum': 'katzen', 'katzentoilette': 'katzen',
            'katzenfutter': 'katzen',
            'kleintiere': 'kleintiere', 'nager': 'kleintiere', 'nagetiere': 'kleintiere',
            'meerschweinchen': 'kleintiere', 'kaninchen': 'kleintiere', 'hamster': 'kleintiere',
            'degus': 'kleintiere', 'chinchilla': 'kleintiere', 'frettchen': 'kleintiere',
            'gehege': 'kleintiere', 'pferde': 'allgemein', 'pferdehaltung': 'allgemein',
            'voegel': 'voegel', 'vögel': 'voegel', 'vogelhaltung': 'voegel',
            'wellensittich': 'voegel', 'sittiche': 'voegel',
            'aquarium': 'aquarium', 'aquaristik': 'aquarium', 'fische': 'aquarium',
            'reptilien': 'allgemein', 'terrarium': 'allgemein',
        }
        data_cat = cat_map.get(primary, 'allgemein')
        # Insert data-cat into <article
        full = full.replace('<article class="blog-card">', f'<article class="blog-card" data-cat="{data_cat}">')
    return full

html = re.sub(r'<article class="blog-card">.*?</article>', add_data_cat, html, flags=re.DOTALL)

# ── 6. Replace closing </div></section> with load-more button ──
old_close = '''  </div>
</section>

<!-- ============ NEWSLETTER ============ -->'''

new_close = '''  </div>
  <div class="load-more-wrap">
    <button id="loadMoreBtn" class="btn btn-outline" onclick="loadMore()">📚 Weitere Artikel laden</button>
  </div>
</section>

<!-- ============ NEWSLETTER ============ -->'''

html = html.replace(old_close, new_close)

# ── 7. Add filter + load-more CSS to external stylesheet ──
extra_css = '''
/* ── Filter Tabs ── */
.filter-tabs{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center;margin-bottom:2rem}
.filter-btn{background:var(--bg-alt);border:2px solid var(--border);border-radius:50px;padding:.5rem 1.2rem;font-weight:600;font-size:.85rem;cursor:pointer;transition:.2s;font-family:var(--font);color:var(--text);min-height:44px}
.filter-btn:hover{border-color:var(--primary);background:var(--primary-light);color:var(--primary-dark)}
.filter-btn.active{background:var(--primary);color:#fff;border-color:var(--primary)}
/* ── Load More ── */
.load-more-wrap{text-align:center;margin-top:2rem}
.load-more-wrap .btn{font-size:1rem;padding:.8rem 2rem}
#loadMoreBtn.hidden{display:none}
/* ── Hide filtered cards ── */
.blog-card.hidden-by-filter{display:none}
'''

# Append to existing CSS file
with open(css_path, 'a', encoding='utf-8') as f:
    f.write(extra_css)
print(f"✅ Filter/Load-More CSS hinzugefügt")

# ── Mark article grid items with data-index for pagination ──
# Add data-index to each article card in the grid
article_count = [0]
def add_index(match):
    article_count[0] += 1
    art = match.group(0)
    if 'data-index' not in art:
        art = art.replace('<article ', f'<article data-index="{article_count[0]}" ', 1)
    return art

html = re.sub(r'<article class="blog-card" data-cat="[^"]*">', add_index, html, flags=0)

print(f"✅ {article_count} Artikel mit data-index markiert")

# ── 8. Add JS for filter + load-more before </body> ──
filter_js = '''
<script>
// ── Category Filter ──
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    const filter = this.dataset.filter;
    const cards = document.querySelectorAll('#article-grid .blog-card');
    let visibleCount = 0;
    cards.forEach(card => {
      if (filter === 'all' || card.dataset.cat === filter) {
        card.classList.remove('hidden-by-filter');
        visibleCount++;
      } else {
        card.classList.add('hidden-by-filter');
      }
    });
    // Reset load-more visibility
    const loadBtn = document.getElementById('loadMoreBtn');
    if (loadBtn) {
      loadBtn.dataset.page = '1';
      showPage(1, filter);
    }
  });
});

// ── Load More ──
const CARDS_PER_PAGE = 12;
let currentPage = 1;

function showPage(page, filter) {
  const cards = document.querySelectorAll('#article-grid .blog-card');
  const filtered = [];
  cards.forEach(card => {
    if (!card.classList.contains('hidden-by-filter')) {
      filtered.push(card);
    }
  });
  const totalVisible = filtered.length;
  const start = 0;
  const end = page * CARDS_PER_PAGE;
  
  filtered.forEach((card, i) => {
    if (i < end) {
      card.classList.remove('hidden-by-pagination');
    } else {
      card.classList.add('hidden-by-pagination');
    }
  });
  
  const loadBtn = document.getElementById('loadMoreBtn');
  if (loadBtn) {
    if (end >= totalVisible) {
      loadBtn.classList.add('hidden');
    } else {
      loadBtn.classList.remove('hidden');
    }
  }
}

function loadMore() {
  currentPage++;
  const activeFilter = document.querySelector('.filter-btn.active');
  showPage(currentPage, activeFilter ? activeFilter.dataset.filter : 'all');
}

// Init: hide pagination-hidden on load
document.addEventListener('DOMContentLoaded', function() {
  showPage(1, 'all');
});
</script>'''

html = html.replace('</body>', filter_js + '\n</body>')

# ── Add .hidden-by-pagination CSS ──
with open(css_path, 'a', encoding='utf-8') as f:
    f.write('\n.blog-card.hidden-by-pagination{display:none}\n')

# ── Write back ──
with open(INDEX, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ JS Filter + Load More eingebaut")
print(f"✅ index.html geschrieben ({len(html)//1024}KB)")
print(f"\n📊 Zusammenfassung:")
print(f"  {article_count} Artikel-Karten")
print(f"  Filter: Alle, Hunde, Katzen, Kleintiere, Vögel, Aquarium, Allgemein")
print(f"  Load More: {CARDS_PER_PAGE} pro Seite")
print(f"  CSS: ausgelagert nach css/style.css")
