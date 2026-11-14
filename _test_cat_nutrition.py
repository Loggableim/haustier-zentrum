"""Regression checks for removal of unvalidated cat-diet prescriptions."""
from pathlib import Path
import html
import json
import re
import unittest

PAGE = Path(__file__).resolve().parent / 'artikel/katzenfutter-selber-machen.html'

class CatNutritionTests(unittest.TestCase):
    def test_no_unvalidated_recipe_or_safety_promises(self):
        text = PAGE.read_text(encoding='utf-8')
        for phrase in ['5 ausgewogene Rezepte', '5 einfache Rezepte', '2 g Calciumcarbonat',
                       '1–2 TL pro kg', '72 Stunden', 'Hunger ist ein starker Motivator',
                       'nicht durchgaren', 'zu 50 % verloren', '50 % des Tagesbedarfs',
                       'Bedarf (pro 1.000 kcal)', '5 g rotes Protein', 'Kochbeutel']:
            self.assertNotIn(phrase, text, phrase)
        self.assertNotRegex(text, r'<h3>Rezept [1-5]:')

    def test_homepage_and_feed_do_not_advertise_removed_recipes(self):
        for path in [PAGE.parents[1] / 'index.html', PAGE.parents[1] / 'rss.xml']:
            text = path.read_text(encoding='utf-8')
            for phrase in ['5 ausgewogene Rezepte', '5 einfache Rezepte', 'Katzenfutter selber machen: Gesunde Rezepte']:
                self.assertNotIn(phrase, text, str(path))
        import xml.etree.ElementTree as ET
        root = ET.parse(PAGE.parents[1] / 'rss.xml').getroot()
        matches = [i for i in root.findall('./channel/item') if i.findtext('link') == 'https://haustierzentrum.com/artikel/katzenfutter-selber-machen']
        self.assertEqual(len(matches), 1)
        self.assertIn('Planung, Risiken und Beratung', matches[0].findtext('title'))
    def test_sources_and_clear_limits_present(self):
        text = PAGE.read_text(encoding='utf-8')
        for phrase in ['keine berechnete Tagesration', 'tierärztliche Ernährungsberatung',
                       'nicht alle Bakterien', 'nicht durch Hunger',
                       'nutrition.vetmed.ucdavis.edu', 'wsava.org',
                       'feline-health-topics/feeding-your-cat', 'feline-health-topics/anorexia']:
            self.assertIn(phrase, text, phrase)

    def test_faq_schema_matches_visible_answers(self):
        text = PAGE.read_text(encoding='utf-8')
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
        faq = next(json.loads(b) for b in blocks if json.loads(b).get('@type') == 'FAQPage')
        visible = re.findall(r'<div class="faq-item"><h3>(.*?)</h3><p>(.*?)</p></div>', text, re.S)
        plain = lambda s: html.unescape(re.sub('<[^>]+>', '', s))
        self.assertEqual([(q['name'], q['acceptedAnswer']['text']) for q in faq['mainEntity']],
                         [(plain(q), plain(a)) for q, a in visible])

class CatSelectionTests(unittest.TestCase):
    def test_raw_feeding_risks_and_correct_link(self):
        text = (PAGE.parent / 'katzen-ernaehrung.html').read_text(encoding='utf-8')
        for phrase in ['Die Vorteile: glänzendes Fell', 'gute Alternative für', 'mindestens 70 % Fleischanteil', 'BARF-Zubehör', 'Nassfutter oder einer ausgewogenen BARF-Ration']:
            self.assertNotIn(phrase, text)
        for phrase in ['keinen belegten gesundheitlichen Vorteil', 'Krankheitserreger', 'Alleinfuttermittel', 'kein Qualitätsnachweis', 'tierärztliche Ernährungsberatung', 'Raw-Meat-Based-Diets-for-Pets', 'Frequently-Asked-Questions-and-Myths', '/artikel/katzenfutter-selber-machen']:
            self.assertIn(phrase, text)
        self.assertNotRegex(text, r'katzen-zimmerpflanzen-giftig[^>]*>Einsteiger')

    def test_revision_metadata_and_schema(self):
        text = (PAGE.parent / 'katzen-ernaehrung.html').read_text(encoding='utf-8')
        blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)]
        post = next(b for b in blocks if b.get('@type') == 'BlogPosting')
        self.assertEqual(post['datePublished'], '2026-06-15')
        self.assertEqual(post['dateModified'], '2026-11-14')
        self.assertIn('Redaktionell aktualisiert: 14. November 2026', text)
        self.assertNotIn('lastReviewed', post)

if __name__ == '__main__': unittest.main()
