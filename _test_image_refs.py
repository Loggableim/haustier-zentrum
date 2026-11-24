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
    def test_pop_art_cover_matches_its_own_article_and_home_card(self):
        home = (ROOT / 'index.html').read_text()
        pilots = (
            (
                'ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-fruehzeitig-erkennen-und-',
                107, 'hunde-gesundheit_00001_.webp',
                'Pop-Art-Illustration: Hund mit roter Brille und Stethoskop', True,
            ),
            (
                'notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte',
                123, 'erste-hilfe-haustiere-notfall-ratgeber_00001_.webp',
                'Pop-Art-Illustration: Hund und Katze neben einem Erste-Hilfe-Koffer', False,
            ),
        )
        for slug, index, filename, alt, schema_image in pilots:
            with self.subTest(article=slug):
                expected = f'/images/{filename}'
                article = (ROOT / 'artikel' / (slug + '.html')).read_text()
                lead = article.split('<div class="article-content">', 1)[0]
                hero = re.findall(r'<img\b[^>]*\bclass="article-hero"[^>]*>', lead)
                self.assertEqual(len(hero), 1)
                for attribute in (f'src="{expected}"', f'alt="{alt}"', 'width="1216"', 'height="832"'):
                    self.assertIn(attribute, hero[0])
                card = re.search(rf'<article data-index="{index}"[^>]*>.*?</article>', home, re.S)
                self.assertIsNotNone(card)
                self.assertIn(f'href="/artikel/{slug}"', card[0])
                self.assertRegex(card[0], rf'<img\b[^>]*src="{re.escape(expected)}"[^>]*alt="{re.escape(alt)}"')
                if index == 123:
                    self.assertRegex(card[0], r'<img\b[^>]*style="object-position: center 35%"')
                self.assertEqual(ImageRefs(article).preview, {
                    'og:image': [SITE + expected], 'twitter:image': [SITE + expected],
                })
                schemas = [json.loads(block) for block in re.findall(
                    r'<script type="application/ld\+json">(.*?)</script>', article, re.S)]
                items = [data for data in schemas if data.get('@type') in {'Article', 'BlogPosting'}]
                self.assertEqual(len(items), 1)
                if schema_image:
                    self.assertEqual(items[0]['image'], SITE + expected)
                    self.assertIn(f'<meta property="og:image:alt" content="{alt}">', article)
                else:
                    self.assertNotIn('image', items[0])

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

class HomeCatalog(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.cards = []
        self.load_more = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'article' and 'blog-card' in attr.get('class', '').split():
            self.cards.append((attr['data-index'], [elem_id for _, elem_id in self.stack]))
        if attr.get('id') == 'loadMoreBtn':
            self.load_more.append([elem_id for _, elem_id in self.stack])
        if tag not in self.VOID:
            self.stack.append((tag, attr.get('id')))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


class HomeCatalogTest(unittest.TestCase):
    def test_all_catalog_cards_share_the_filter_grid(self):
        home = HomeCatalog((ROOT / 'index.html').read_text())
        featured = {'1', '2', '3', '4', '5'}
        indices = [index for index, _ in home.cards]
        self.assertEqual(len(indices), len(set(indices)))
        self.assertTrue({str(i) for i in range(1, 132)}.issubset(indices))
        detached = []
        for index, parents in home.cards:
            if index in featured:
                self.assertNotIn('alle-artikel', parents)
                self.assertNotIn('article-grid', parents)
            elif parents[-2:] != ['alle-artikel', 'article-grid']:
                detached.append(index)
        self.assertEqual(detached, [], f'Catalogue cards outside filter grid: {detached}')
        self.assertEqual(len(home.load_more), 1)
        self.assertEqual(home.load_more[0][-1], 'alle-artikel')


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


class RestoredArticleTemplateTest(unittest.TestCase):
    def test_no_public_article_has_an_unstyled_document(self):
        for path in (ROOT / 'artikel').glob('*.html'):
            with self.subTest(article=path.name):
                self.assertRegex(path.read_text(), r'<style(?:\s|>)|<link[^>]+rel="stylesheet"')

    def test_restored_guides_print_without_navigation_or_consent_overlay(self):
        css = (ROOT / 'css/article-template.css').read_text()
        printed = css.split('@media print {', 1)[1]
        self.assertRegex(printed, r'(?s)#hz-consent,[^{}]*#hz-consent-settings\s*\{\s*display: none !important;')
        self.assertRegex(css, r'(?s)\.restored-guide\s*\{[^}]*scroll-margin-top:')

    def test_restored_template_wraps_twelve_raw_articles(self):
        pages = [(p.name, p.read_text()) for p in (ROOT / 'artikel').glob('*.html')]
        pages = [(name, html) for name, html in pages if 'class="restored-guide-page"' in html]
        self.assertEqual(len(pages), 12)
        stylesheet = (ROOT / 'css/article-template.css').read_text()
        self.assertNotRegex(stylesheet, r'@import|url\(')
        for name, html in pages:
            with self.subTest(article=name):
                self.assertIn('<header class="site-header">', html)
                self.assertIn('<main id="artikel" class="restored-guide" tabindex="-1">', html)
                self.assertIn('<footer class="site-footer">', html)
                self.assertIn('href="/css/style.css"', html)
                self.assertIn('href="/css/article-template.css"', html)
                self.assertLess(html.index('Content-Security-Policy'), html.index('rel="stylesheet"'))
                self.assertEqual(html.count('src="/js/consent.js" defer'), 1)
                self.assertRegex(html, r'<img [^>]+class="article-hero" width="[1-9]\d*" height="[1-9]\d*"')
                self.assertEqual(len(re.findall(r'<h1(?=\s|>)', html)), 1)


if __name__ == '__main__':
    unittest.main()
