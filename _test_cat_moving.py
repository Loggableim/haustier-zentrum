"""Regression checks for the sourced moving guide and its discovery links."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent
SLUG = 'umzug-mit-katze-checkliste'
class CatMovingTests(unittest.TestCase):
    def test_guide_sources_and_no_advertising_claims(self):
        s=(ROOT/'artikel'/f'{SLUG}.html').read_text()
        for source in ['cats.org.uk', 'tasso.net']:
            self.assertIn(source,s)
        self.assertIn('@media print',s)
        self.assertNotIn('min-width:450px',s)
        self.assertIn('.article-content a{color:#8a4800;text-decoration:underline}',s)
        self.assertIn('@media print{#hz-consent,#hz-consent-settings',s)
        self.assertNotIn('tierärztlich geprüft',s.lower())
        self.assertNotIn('garantiert stressfrei',s.lower())
    def test_discovery(self):
        s=(ROOT/'index.html').read_text()
        self.assertIn('/artikel/'+SLUG,s)
        for name in ['katzen-freigaenger','katzen-verhalten-koerpersprache-kommunikation','katzenfreundliche-wohnung-gestalten']:
            self.assertIn('/artikel/'+SLUG,(ROOT/'artikel'/f'{name}.html').read_text())
    def test_feed_and_sitemap(self):
        rss=ET.parse(ROOT/'rss.xml')
        links=[x.text for x in rss.findall('./channel/item/link')]
        self.assertEqual(links.count('https://haustierzentrum.com/artikel/'+SLUG),1)
        maps=''.join(p.read_text() for p in ROOT.glob('sitemap*.xml'))
        self.assertIn('https://haustierzentrum.com/artikel/'+SLUG,maps)
if __name__=='__main__': unittest.main()
