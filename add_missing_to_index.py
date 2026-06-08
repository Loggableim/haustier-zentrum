#!/usr/bin/env python3
"""
Add missing article cards to haustierzentrum.com index.html.
Reads each missing article HTML to extract title + excerpt, then generates
compact blog-card entries and appends them to the articles-grid section.
"""
import os, re, glob

INDEX = r"C:\HermesPortable\home\scripts\blog-automation\haustier-zentrum\index.html"
ARTIKEL_DIR = r"C:\HermesPortable\home\scripts\blog-automation\haustier-zentrum\artikel"

def extract_title_and_desc(html_path):
    """Extract title and meta description from article HTML."""
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Title
    title_m = re.search(r'<title>(.*?)</title>', content, re.DOTALL | re.IGNORECASE)
    title = title_m.group(1).strip() if title_m else os.path.basename(html_path)
    # Remove site name suffix
    title = re.sub(r'\s*[|–-]\s*haustierzentrum\.com.*$', '', title).strip()
    
    # Meta description
    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content, re.IGNORECASE)
    desc = desc_m.group(1).strip() if desc_m else ""
    
    # Category hint from filename
    slug = os.path.splitext(os.path.basename(html_path))[0]
    
    return title, desc, slug

def guess_category(slug):
    """Guess article category from slug."""
    if "rasseguide" in slug or slug in ["golden-retriever-rasseguide"]:
        return ("Hunde", "Rasseporträt")
    if "-katze-" in slug or "-katzen-" in slug or slug.startswith("katzen") or slug.startswith("katzer"):
        return ("Katzen",)
    if "katz" in slug:
        return ("Katzen",)
    if "hund" in slug or "welpen" in slug or "leinen" in slug:
        return ("Hunde",)
    if "aquarium" in slug or "fisch" in slug:
        return ("Aquaristik",)
    if "hamster" in slug or "meerschwein" in slug or "kaninchen" in slug or "kleintier" in slug or "degus" in slug or "chinchilla" in slug or "frettchen" in slug:
        return ("Kleintiere",)
    if "vogel" in slug or "wellensittich" in slug:
        return ("Vögel",)
    if "pferd" in slug:
        return ("Pferde",)
    if "reptil" in slug:
        return ("Reptilien",)
    if "erste-hilfe" in slug or "notfall" in slug:
        return ("Notfall", "Erste Hilfe")
    if "tierarzt" in slug or "kosten" in slug or "versicherung" in slug:
        return ("Ratgeber",)
    return ("Allgemein",)

def build_card(slug, title, desc):
    """Build a compact blog-card HTML for missing articles."""
    # Guess image filename
    img_base = slug.replace('-', '_')
    # Try common image extensions
    img_path = f"images/{img_base}_00001_.webp"
    if not os.path.exists(os.path.join(os.path.dirname(INDEX), img_path)):
        img_path = f"images/{img_base}.webp"
    if not os.path.exists(os.path.join(os.path.dirname(INDEX), img_path)):
        img_path = f"images/{img_base}.png"
    if not os.path.exists(os.path.join(os.path.dirname(INDEX), img_path)):
        img_path = f"images/{slug}.webp"
    if not os.path.exists(os.path.join(os.path.dirname(INDEX), img_path)):
        # Fallback - use a placeholder
        img_path = f"images/{slug}.png"
    
    cats = guess_category(slug)
    cat_spans = "".join(f'<span>{c}</span>' for c in cats)
    
    return f'''    <article class="blog-card">
      <div class="card-img"><img src="{img_path}" alt="{title}" loading="lazy"></div>
      <div class="card-body">
        <div class="card-cats">{cat_spans}<span>Neu</span></div>
        <div class="card-date">Juni 2026</div>
        <h2><a href="/artikel/{slug}.html">{title}</a></h2>
        <p>{desc[:200]}</p>
        <a href="/artikel/{slug}.html" class="read-more">Weiterlesen →</a>
      </div>
    </article>'''

def main():
    # Read existing index
    with open(INDEX, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Existing article links
    existing_links = set(re.findall(r'artikel/([\w-]+)\.html', content))
    print(f"Existing article links in index: {len(existing_links)}")
    
    # All article files
    all_articles = glob.glob(os.path.join(ARTIKEL_DIR, "*.html"))
    article_slugs = set(os.path.splitext(os.path.basename(a))[0] for a in all_articles)
    print(f"Total article files: {len(article_slugs)}")
    
    # Find missing
    missing = sorted(article_slugs - existing_links)
    print(f"Missing from index: {len(missing)}")
    
    if not missing:
        print("✅ No missing articles!")
        return
    
    # Build cards for missing articles
    new_cards = []
    for slug in missing:
        html_path = os.path.join(ARTIKEL_DIR, f"{slug}.html")
        if os.path.exists(html_path):
            title, desc, _ = extract_title_and_desc(html_path)
            card = build_card(slug, title, desc)
            new_cards.append(card)
            print(f"  + {slug}: {title[:50]}...")
        else:
            print(f"  ⚠️ {slug}.html not found!")
    
    # Inject before closing of articles-grid
    insert_point = '\n  </div>\n</section>\n\n<!-- ============ NEWSLETTER ============ -->'
    new_content = '\n\n'.join(new_cards) + '\n' + insert_point
    old_content = insert_point
    new_index = content.replace(old_content, new_content, 1)
    
    if new_index == content:
        print("❌ Could not find insertion point!")
        return
    
    with open(INDEX, 'w', encoding='utf-8') as f:
        f.write(new_index)
    
    # Verify
    final_links = len(re.findall(r'artikel/[\w-]+\.html', open(INDEX, 'r', encoding='utf-8').read()))
    print(f"\n✅ Done! Article links in index: {final_links}")

if __name__ == "__main__":
    main()
