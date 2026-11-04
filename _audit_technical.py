#!/usr/bin/env python3
"""Read-only local technical audit; JSON to stdout, no third-party packages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
from collections import Counter
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SITE = "https://haustierzentrum.com"
HOSTS = {"haustierzentrum.com", "www.haustierzentrum.com", "haustier-zentrum.com", "www.haustier-zentrum.com"}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.canonicals, self.schemas, self.schema_errors = [], [], [], []
        self.hreflang = self.h1 = self.direct_ads = 0
        self.ld = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href"))
        self.hreflang += int("hreflang" in a)
        self.h1 += int(tag == "h1")
        if tag == "script":
            self.direct_ads += int("adsbygoogle" in a.get("src", ""))
            if a.get("type") == "application/ld+json":
                self.ld = ""

    def handle_data(self, data):
        if self.ld is not None:
            self.ld += data

    def handle_endtag(self, tag):
        if tag == "script" and self.ld is not None:
            try:
                self.schemas.append(json.loads(self.ld))
            except ValueError as error:
                self.schema_errors.append(str(error))
            self.ld = None


def types(obj):
    found = set()
    if isinstance(obj, dict):
        value = obj.get("@type", [])
        found.update([value] if isinstance(value, str) else value)
        for value in obj.values():
            found.update(types(value))
    elif isinstance(obj, list):
        for value in obj:
            found.update(types(value))
    return found


def exists(urlpath):
    path = unquote(urlpath).strip("/") or "index.html"
    return any(p.is_file() for p in (ROOT / path, ROOT / (path + ".html"), ROOT / path / "index.html"))


def audit():
    result = dict(articles=0, internal_links_checked=0, broken_links=[], canonical_errors=[],
                  jsonld_errors=[], schema_pages=Counter(), missing_article_schema=[],
                  h1_errors=[], hreflang_pages=[], direct_ads_pages=[])
    for source in sorted((ROOT / "artikel").glob("*.html")):
        result["articles"] += 1
        name = str(source.relative_to(ROOT))
        page = Page(source.read_text(encoding="utf-8"))
        url = f"{SITE}/artikel/{source.stem}"
        if page.canonicals != [url]:
            result["canonical_errors"].append(name)
        if page.h1 != 1:
            result["h1_errors"].append(name)
        if page.hreflang:
            result["hreflang_pages"].append(name)
        if page.direct_ads:
            result["direct_ads_pages"].append(name)
        if page.schema_errors:
            result["jsonld_errors"].append(name)
        found = types(page.schemas)
        result["schema_pages"].update(found)
        if not found.intersection({"Article", "BlogPosting", "NewsArticle"}):
            result["missing_article_schema"].append(name)
        for href in page.links:
            target = urlsplit(urljoin(url, href))
            if target.hostname not in HOSTS:
                continue
            result["internal_links_checked"] += 1
            if not exists(target.path):
                result["broken_links"].append(dict(source=name, href=href, path=unquote(target.path)))
    result["sitemaps"] = {}
    for name in ("sitemap.xml", "sitemap-articles.xml", "sitemap-static.xml"):
        root = ET.parse(ROOT / name).getroot()
        locs = [e.text for e in root.iter() if e.tag.endswith("}loc")]
        result["sitemaps"][name] = dict(root=root.tag.split("}")[-1], locs=len(locs), unique=len(set(locs)))
    result["rss_items"] = len(ET.parse(ROOT / "rss.xml").getroot().findall("channel/item"))
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
