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

    def test_repaired_article_schema_uses_the_same_working_visible_image(self):
        for slug in (
            'allergiker-haustiere',
            'franzoesische-bulldogge-rasseguide',
            'hamster-haltung',
            'haustier-anschaffung',
            'haustiere-kinder',
            'hunde-fellpflege-buersten-baden-krallen',
            'hunde-gesundheit',
            'hunde-uebergewicht',
            'hunde-zahnpflege',
            'kaninchenhaltung',
            'katzen-impfungen-vorsorge',
            'katzenbeschaeftigung',
            'katzenrassen-vergleich',
            'katzentoilette-geruch-vermeiden',
            'kleintier-gehege',
            'labrador-retriever',
            'meerschweinchen-ernaehrung-vitamin-c',
            'meerschweinchen-haltung',
            'seniorkatzen-pflege-ernaehrung-gesundheit',
            'siamkatze-rasseguide',
            'tierarztkosten',
            'voegel-haustier-beste-vogelarten-einsteiger',
            'wellensittich-haltung',
            'zeckenschutz-flohschutz-hund',
        ):
            with self.subTest(page=slug):
                html = (ROOT / 'artikel' / (slug + '.html')).read_text()
                article = SITE + '/artikel/' + slug
                parsed = ImageRefs(html)
                previews = parsed.preview
                self.assertEqual(previews['og:image'], previews['twitter:image'])
                self.assertEqual(len(previews['og:image']), 1)
                expected = previews['og:image'][0]
                # Ignore other featured-image wrappers used for illustrations in the body.
                lead = html.split('<div class="article-content">', 1)[0]
                featured = re.findall(
                    r'<div class="featured-img"[^>]*>(?:\s|<!--.*?-->)*<img\b[^>]*?\bsrc="([^"]+)"',
                    lead, re.S)
                self.assertEqual([urljoin(article, ref) for ref in featured], [expected])
                self.assertTrue((ROOT / urlsplit(expected).path.lstrip('/')).is_file())
                schemas = [json.loads(block) for block in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
                articles = [data for data in schemas if data.get('@type') in {'Article', 'BlogPosting'}]
                self.assertEqual([data.get('image') for data in articles], [expected])

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

class ErrorPageNavigationTest(unittest.TestCase):
    def test_nested_missing_route_resolves_public_assets_at_root(self):
        page = (ROOT / '404.html').read_text()
        stylesheet = re.search(r'<link rel="stylesheet" href="([^"]+)"', page)[1]
        for route in ['/artikel/fehlt/tief', '/artikel/fehlt/tief/']:
            self.assertEqual(urljoin(SITE + route, stylesheet), SITE + '/css/style.css')
        self.assertIn('src="/images/htz-404-v1.webp"', page)
        self.assertEqual(page.count('src="/js/consent.js" defer'), 1)
        self.assertIn('content="noindex, follow"', page)

    def test_early_error_page_policy_blocks_third_party_styles_and_fonts(self):
        page = (ROOT / '404.html').read_text()
        policy = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', page)
        self.assertIsNotNone(policy)
        self.assertEqual(policy[1], "style-src 'self' 'unsafe-inline'; font-src 'self'")
        self.assertLess(policy.start(), page.index('<link rel="stylesheet"'))
        self.assertLess(policy.start(), page.index('<style>'))

    def test_error_menu_needs_no_script_or_hamburger(self):
        page = (ROOT / '404.html').read_text()
        self.assertNotIn('class="nav-toggle"', page)
        self.assertIn('id="error-navigation"', page)
        self.assertRegex(page, r'(?s)@media\(max-width:900px\).*?#error-navigation > \.nav-links\{[^}]*display:flex')
        self.assertIn('href="/#alle-artikel"', page)


class InlineArticleNavigationTest(unittest.TestCase):
    PAGES = (
        'allergiker-haustiere', 'haustier-anschaffung', 'haustiere-kinder',
        'katzentoilette-geruch-vermeiden', 'kleintier-gehege',
        'meerschweinchen-ernaehrung-vitamin-c', 'tierarztkosten',
        'wellensittich-haltung',
    )

    def test_homogeneous_inline_articles_expose_direct_mobile_category_links(self):
        asset = ROOT / 'css/inline-article-navigation.css'
        self.assertTrue(asset.is_file())
        css = asset.read_text()
        self.assertIn('@media (max-width: 768px)', css)
        self.assertRegex(css, r'#article-navigation:not\(\.open\)\s*\{\s*display: none')
        self.assertRegex(css, r'#article-navigation\.open > \.nav-links\s*\{[^}]*display: flex')
        self.assertNotRegex(css, r'@import|url\(')
        for name in self.PAGES:
            with self.subTest(article=name):
                page = (ROOT / 'artikel' / (name + '.html')).read_text()
                self.assertIn('href="/css/inline-article-navigation.css"', page)
                self.assertIn('aria-controls="article-navigation" aria-expanded="false"', page)
                self.assertIn('id="article-navigation"', page)
                self.assertNotIn("this.parentElement.classList.toggle('open')", page)
                self.assertIn('href="/artikel/hunderassen-anfaenger"', page)
                self.assertEqual(page.count('src="/js/consent.js" defer'), 1)


class RemainingInlineArticleNavigationTest(unittest.TestCase):
    PAGES = {
        'katzen': 'fixed',
        'mops-rasseguide': 'list',
        'ragdoll-katze-rasseguide': 'list',
        'sibirischer-husky-rasseguide': 'list',
    }

    def test_remaining_templates_keep_category_and_guide_destinations(self):
        asset = ROOT / 'css/inline-article-navigation-compat.css'
        self.assertTrue(asset.is_file())
        css = asset.read_text()
        self.assertNotRegex(css, r'@import|url\(')
        self.assertRegex(css, r'#legacy-article-navigation\.open > \.nav-links\s*\{\s*display: flex')
        self.assertRegex(css, r'(?s)\[data-layout="fixed"\]\.open\s*\{[^}]*'
                              r'position: absolute;[^}]*top: 100%;[^}]*bottom: auto;[^}]*overflow: auto;')
        self.assertIn('li:not(.open) .mega-panel', css)
        for name, layout in self.PAGES.items():
            with self.subTest(article=name):
                page = (ROOT / 'artikel' / (name + '.html')).read_text()
                self.assertIn('href="/css/inline-article-navigation-compat.css"', page)
                self.assertIn('aria-controls="legacy-article-navigation" aria-expanded="false"', page)
                self.assertIn(f'id="legacy-article-navigation" data-layout="{layout}"', page)
                self.assertIn('href="/artikel/hunderassen-anfaenger"', page)
                self.assertIn('href="/artikel/hunde-zahnpflege"', page)
                self.assertEqual(page.count('src="/js/consent.js" defer'), 1)
                self.assertNotIn("querySelector('.nav-links').classList.remove('open')", page)


if __name__ == '__main__':
    unittest.main()
