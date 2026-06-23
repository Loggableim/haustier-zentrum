#!/usr/bin/env python3
"""Generate sitemap index structure for haustierzentrum.com."""
import re, json, time, os
from pathlib import Path

ROOT = Path(r"C:\sidekick\home\spaces\haustier-zentrum")
ART_DIR = ROOT / "artikel"
SITE = "https://haustierzentrum.com"

def extract_date(path, slug):
    """Extract dateModified or datePublished from article JSON-LD."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(1).strip())
    except Exception:
        return None
    for key in ("dateModified", "datePublished"):
        val = data.get(key)
        if val:
            s = str(val)
            try:
                if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
                    return time.mktime(time.strptime(s, "%Y-%m-%d"))
                return time.mktime(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))
            except Exception:
                pass
    return None

# Generate sitemap-articles.xml
articles = sorted(ART_DIR.glob("*.html"))
parts = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in articles:
    slug = p.name[:-5]
    loc = f"{SITE}/artikel/{slug}"
    mt = extract_date(p, slug)
    if mt is None:
        mt = p.stat().st_mtime
    lastmod = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(mt))
    parts.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")
parts.append("</urlset>")
text = "\n".join(parts) + "\n"
(ROOT / "sitemap-articles.xml").write_text(text, encoding="utf-8")
print(f"Articles sitemap: {len(articles)} URLs")

# Generate sitemap-static.xml
static_urls = [
    (f"{SITE}/", ROOT / "index.html", "daily", "1.0"),
    (f"{SITE}/about/", ROOT / "about.html", "monthly", "0.6"),
    (f"{SITE}/impressum/", ROOT / "impressum.html", "monthly", "0.5"),
    (f"{SITE}/datenschutz/", ROOT / "datenschutz.html", "monthly", "0.5"),
]
parts = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, fpath, freq, prio in static_urls:
    if fpath.exists():
        mt = fpath.stat().st_mtime
        lastmod = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(mt))
        parts.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""")
parts.append("</urlset>")
text = "\n".join(parts) + "\n"
(ROOT / "sitemap-static.xml").write_text(text, encoding="utf-8")
print(f"Static sitemap: {len(static_urls)} URLs")

# Also update sitemap.xml index
mt_now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
sitemap_index = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{SITE}/sitemap-articles.xml</loc>
    <lastmod>{mt_now}</lastmod>
  </sitemap>
  <sitemap>
    <loc>{SITE}/sitemap-static.xml</loc>
    <lastmod>{mt_now}</lastmod>
  </sitemap>
</sitemapindex>
"""
(ROOT / "sitemap.xml").write_text(sitemap_index, encoding="utf-8")
print("Sitemap index updated")
print("Done.")
