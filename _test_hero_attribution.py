"""Keep the unverified old title graphic out of public references."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SLUG = 'ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-fruehzeitig-erkennen-und-'
OLD = 'hero-ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-frühzeitig-erkennen-und-vorbeugen.webp'
NEW = 'hundegesundheit-vorsorge-hz-v1.webp'

class HeroAttributionTests(unittest.TestCase):
    def test_public_pages_do_not_display_old_graphic(self):
        for page in (ROOT / 'index.html', ROOT / 'artikel' / (SLUG + '.html')):
            content = page.read_text()
            self.assertNotIn(OLD, content)
            self.assertIn('/images/' + NEW, content)
        self.assertNotIn(OLD, (ROOT / 'rss.xml').read_text())

    def test_original_hero_and_preview(self):
        svg = ET.parse(ROOT / 'artwork/hundegesundheit-vorsorge.svg').getroot()
        self.assertEqual(svg.attrib['viewBox'], '0 0 1200 630')
        image = (ROOT / 'images' / NEW).read_bytes()
        self.assertEqual(image[:4] + image[8:12], b'RIFFWEBP')
        article = (ROOT / 'artikel' / (SLUG + '.html')).read_text()
        self.assertEqual(article.count('https://haustierzentrum.com/images/' + NEW), 3)

if __name__ == '__main__':
    unittest.main()
