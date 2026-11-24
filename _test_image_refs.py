"""Verify public image references point to files Cloudflare can actually serve."""
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
SITE = 'https://haustierzentrum.com'

class ImageRefs(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.refs = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'img' and attr.get('src'):
            self.refs.append(attr['src'])

class ImageTests(unittest.TestCase):
    def test_public_html_has_no_missing_site_images(self):
        pages = [*ROOT.glob('*.html'), *(ROOT / 'artikel').glob('*.html')]
        for page in pages:
            name = page.relative_to(ROOT).as_posix()
            # Cloudflare serves the custom 404 at the original missing path.
            requested = '/artikel/nicht-vorhanden/tief/' if name == '404.html' else '/' + name.removesuffix('.html')
            html = page.read_text()
            refs = ImageRefs(html).refs
            for ref in refs:
                url = urlsplit(urljoin(SITE + requested, ref))
                if url.netloc == 'haustierzentrum.com':
                    with self.subTest(page=name, image=ref):
                        target = ROOT / unquote(url.path.lstrip('/'))
                        self.assertTrue(target.is_file())
                        self.assertIn(target.suffix.lower(), {'.png', '.webp', '.jpg', '.jpeg', '.svg', '.gif', '.ico', '.avif'})

if __name__ == '__main__':
    unittest.main()
