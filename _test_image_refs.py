"""Verify public image references and homepage navigation integration."""
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

class HomeNavigationTest(unittest.TestCase):
    def test_markup_uses_single_drawer_state_and_preserves_links(self):
        html = (ROOT / 'index.html').read_text()
        self.assertIn('aria-controls="home-navigation" aria-expanded="false"', html)
        self.assertIn('id="home-navigation"', html)
        self.assertNotIn("querySelector('.main-nav').classList.toggle('open')", html)
        self.assertIn('/js/home-navigation.js', html)
        self.assertIn('/css/home-navigation.css', html)
        self.assertIn('/artikel/hunderassen-anfaenger', html)
        self.assertIn('/artikel/hunde-zahnpflege', html)
        self.assertIn('/artikel/silvester-hund-katze-checkliste', html)
        self.assertEqual(html.count('/js/consent.js'), 1)

    def test_drawer_visibility_uses_outer_state_and_excludes_hidden_links(self):
        css = (ROOT / 'css/home-navigation.css').read_text()
        self.assertRegex(css, r'\.home-nav-ready \.main-nav\.open > \.nav-links\s*\{\s*display:flex')
        self.assertRegex(css, r'\.home-nav-ready \.main-nav:not\(\.open\),\s*\.home-nav-ready \.main-nav \.mega-panel\[hidden\]\s*\{\s*display:none')
        self.assertRegex(css, r'@media\(max-width:900px\)')

if __name__ == '__main__':
    unittest.main()
