"""Verify public image references and homepage navigation integration."""
import json
import re
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
        self.preview = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'img' and attr.get('src'):
            self.refs.append(attr['src'])
        key = attr.get('property') or attr.get('name')
        if tag == 'meta' and key in {'og:image', 'twitter:image'}:
            self.preview.setdefault(key, []).append(attr.get('content'))

class ImageTests(unittest.TestCase):
    def test_chihuahua_social_and_schema_match_visible_hero(self):
        html = (ROOT / 'artikel/chihuahua-rasseguide.html').read_text()
        article = SITE + '/artikel/chihuahua-rasseguide'
        hero = re.search(r'<div class="featured-img"><img src="([^"]+)"', html)[1]
        expected = urljoin(article, hero)
        self.assertEqual(expected, SITE + '/images/chihuahua-rasseguide_00001_.webp')
        self.assertEqual(ImageRefs(html).preview, {'og:image': [expected], 'twitter:image': [expected]})
        schemas = [json.loads(block) for block in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        article_schema = [data for data in schemas if data.get('@type') in {'Article', 'BlogPosting'}]
        self.assertEqual([data.get('image') for data in article_schema], [expected])

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

class LegacyArticleNavigationTest(unittest.TestCase):
    def test_shared_mobile_styles_follow_legacy_drawer_state_only(self):
        css = (ROOT / 'css/style.css').read_text()
        selector = ('body:not(.home-page) .site-header > .nav-wrap > '
                    '.nav-toggle[onclick*=".main-nav"] + .main-nav')
        start = css.index('@media(max-width:900px)')
        boundary = css.index('@media(max-width:500px)', start)
        self.assertIn(selector + ':not(.open){display:none}', css[start:boundary])
        phone = css.index('@media(max-width:768px)', boundary)
        self.assertIn(selector + '.open > .nav-links{display:flex;position:static}', css[phone:])
        # Some other templates use an open class on the list itself.
        self.assertIn('.nav-links.open{display:flex}', css[phone:])

    def test_shared_legacy_articles_use_the_scoped_header_structure(self):
        tested = []
        for path in (ROOT / 'artikel').glob('*.html'):
            html = path.read_text()
            if 'css/style.css' not in html or "querySelector('.main-nav').classList.toggle('open')" not in html:
                continue
            with self.subTest(article=path.name):
                self.assertRegex(html, r'<header class="site-header">\s*<div class="nav-wrap">')
                self.assertRegex(html, r'<button class="nav-toggle"[^>]+onclick="[^"]*\.main-nav[^"]*"[^>]*>[^<]*</button>\s*'
                                      r'<nav class="main-nav">\s*<ul class="nav-links">')
                self.assertNotIn('class="home-page"', html)
            tested.append(path.stem)
        self.assertIn('hundeangst-training-tipps', tested)
        self.assertIn('chinchilla-ernaehrung-futter', tested)

if __name__ == '__main__':
    unittest.main()
