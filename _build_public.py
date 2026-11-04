#!/usr/bin/env python3
"""Stage only public web assets, never the repository or Python helpers."""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"


def build():
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    site = "https://haustierzentrum.com"
    index = ET.parse(ROOT / "sitemap.xml").getroot()
    expected = [f"{site}/sitemap-articles.xml", f"{site}/sitemap-static.xml"]
    if index.tag != f"{{{namespace['sm']}}}sitemapindex" or [e.text for e in index.findall("sm:sitemap/sm:loc", namespace)] != expected:
        raise ValueError("Sitemap index must contain exactly the two sub-sitemaps")
    articles = {f"{site}/artikel/{p.stem}" for p in (ROOT / "artikel").glob("*.html")}
    locs = [e.text for e in ET.parse(ROOT / "sitemap-articles.xml").findall("sm:url/sm:loc", namespace)]
    if not articles or len(locs) != len(set(locs)) or set(locs) != articles:
        raise ValueError("Article sitemap does not match article files")
    static = [e.text for e in ET.parse(ROOT / "sitemap-static.xml").findall("sm:url/sm:loc", namespace)]
    if len(static) != 4 or set(static) != {f"{site}/", f"{site}/about", f"{site}/impressum", f"{site}/datenschutz"}:
        raise ValueError("Static sitemap does not match the four public pages")
    feed = ET.parse(ROOT / "rss.xml").getroot()
    items = feed.findall("channel/item")
    links = [item.findtext("link") for item in items]
    if not items or len(links) != len(set(links)) or not set(links) <= articles:
        raise ValueError("RSS must contain unique existing article URLs")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in ("index.html", "404.html", "about.html", "impressum.html",
                 "datenschutz.html", "affiliate-hinweis.html", "robots.txt",
                 "ads.txt", "rss.xml", "sitemap.xml", "sitemap-articles.xml",
                 "sitemap-static.xml", "favicon.ico", "_headers", "_redirects"):
        shutil.copy2(ROOT / name, OUT / name)
    # IndexNow verification is public by design; do not copy arbitrary TXT files.
    for source in ROOT.glob("*.txt"):
        if len(source.stem) == 32 and all(c in "0123456789abcdef" for c in source.stem):
            shutil.copy2(source, OUT / source.name)
    extensions = {"artikel": {".html"}, "css": {".css"},
                  "images": {".png", ".webp", ".jpg", ".jpeg", ".svg", ".gif", ".ico", ".avif"}}
    for folder, allowed in extensions.items():
        for source in (ROOT / folder).rglob("*"):
            if source.is_symlink():
                raise ValueError(f"Symlink is not a public asset: {source.relative_to(ROOT)}")
            if source.is_file() and source.suffix.lower() in allowed:
                target = OUT / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    print(f"Indexing verified: {len(articles)} articles, 4 static pages, {len(items)} RSS items")
    print(f"Public build: {len(list(OUT.rglob('*')))} entries in dist/")


if __name__ == "__main__":
    build()
