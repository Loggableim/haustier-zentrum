"""Keep the unverified old title graphic out of public references."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from _build_public import OUT

ROOT = Path(__file__).resolve().parent
SLUG = 'ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-fruehzeitig-erkennen-und-'
OLD = 'hero-ganzheitliche-hundegesundheit-2026-wie-sie-krankheiten-frühzeitig-erkennen-und-vorbeugen.webp'
ORIGINAL_REPLACEMENT = 'hundegesundheit-vorsorge-hz-v1.webp'

class HeroAttributionTests(unittest.TestCase):
    def test_public_pages_do_not_display_old_graphic(self):
        for page in (ROOT / 'index.html', ROOT / 'artikel' / (SLUG + '.html')):
            content = page.read_text()
            self.assertNotIn(OLD, content)
        self.assertNotIn(OLD, (ROOT / 'rss.xml').read_text())

    def test_legacy_batch_is_never_referenced_or_staged(self):
        old = (ROOT / 'artwork/retired-hero-images.txt').read_text().splitlines()
        self.assertEqual(len(set(old)), 18)
        pages = [*ROOT.glob('*.html'), *(ROOT / 'artikel').glob('*.html'), ROOT / 'rss.xml']
        public = '\n'.join(unquote(page.read_text()) for page in pages)
        for path in old:
            with self.subTest(image=path):
                self.assertNotIn(path, public)
                if OUT.is_dir():
                    self.assertFalse((OUT / path).exists())

    def test_original_replacement_source_and_raster_are_intact(self):
        svg = ET.parse(ROOT / 'artwork/hundegesundheit-vorsorge.svg').getroot()
        self.assertEqual(svg.attrib['viewBox'], '0 0 1200 630')
        image = (ROOT / 'images' / ORIGINAL_REPLACEMENT).read_bytes()
        self.assertEqual(image[:4] + image[8:12], b'RIFFWEBP')

if __name__ == '__main__':
    unittest.main()
