#!/usr/bin/env python3
"""Fail closed on technical SEO errors or an HTML-level advertising bypass."""
from pathlib import Path
import re
import sys
import _audit_technical as audit


def check(root):
    audit.ROOT = root
    result = audit.audit()
    for key in ('broken_links', 'canonical_errors', 'jsonld_errors', 'missing_article_schema', 'h1_errors', 'direct_ads_pages'):
        if result[key]:
            raise ValueError(f'{key}: {result[key]}')
    pages = [root / 'index.html', *(root / 'artikel').glob('*.html')]
    for page in pages:
        text = page.read_text(encoding='utf-8')
        scripts = re.findall(r'<script\b([^>]*)>(.*?)</script>', text, re.I | re.S)
        loaders = [a for a, _ in scripts if re.search(r'src=["\']/js/consent.js["\']', a)]
        if len(loaders) != 1 or not re.search(r'\bdefer\b', loaders[0]):
            raise ValueError(f'Missing/duplicate shared consent loader: {page}')
        # No alternate script/slot/inline handler may load advertising from HTML.
        if re.search(r'adsbygoogle|googlesyndication|googletagservices|doubleclick|cookieConsent|acceptCookies|declineCookies', text, re.I):
            raise ValueError(f'Advertising/legacy consent bypass in HTML: {page}')
        for classes in re.findall(r'class=["\']([^"\']*)["\']', text):
            if 'ad-placeholder' in classes.split() and 'amazon' not in classes.split():
                raise ValueError(f'Advertising placeholder before consent: {page}')
        for _, body in scripts:
            if re.search(r'createElement\(["\'](?:script|ins)["\']', body):
                raise ValueError(f'Unexpected inline script/slot injection: {page}')
    if not (root / 'js/consent.js').is_file():
        raise ValueError('Missing shared consent asset')
    print(f'{root.name}: {result["articles"]} articles, {result["internal_links_checked"]} internal links, 0 broken targets')
    print(f'{root.name}: {len(pages)} pages, 0 inline AdSense loaders/slots, exactly 1 shared consent loader/page')
    print(f'{root.name}: 0 missing Article/BlogPosting schemas, 0 JSON-LD/H1/canonical errors')


if __name__ == '__main__':
    check(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent)
