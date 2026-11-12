"""Regression checks for unsupported editorial/testing claims removed in Nov 2026."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent

class EditorialClaimsTests(unittest.TestCase):
    def test_public_pages_do_not_claim_unverified_credentials_or_tests(self):
        banned = ['Lerne das Team hinter', 'Tests aus 2026 zeigen', 'aktuelle Tests, verhaltensbiologische Erkenntnisse und Praxiserfahrungen zusammengetragen', 'in Tests und Erfahrungsberichten regelmäßig schlecht', 'im Test', 'Tierhalter mit langjähriger Erfahrung', 'Wir sind ein Team von leidenschaftlichen Tierfreunden', 'Wir testen Produkte', 'unsere Erfahrungen aus erster Hand', 'Stunden Recherche', 'Artgerecht & Praxiserprobt', 'Testsieger', 'Wir haben 5 Nass- und Trockenfutter getestet', 'testen 5 Top-Produkte', 'in mehreren Praxistests verglichen']
        failures = []
        for path in [ROOT / 'index.html', ROOT / 'about.html', ROOT / 'rss.xml', *sorted((ROOT / 'artikel').glob('*.html'))]:
            text = path.read_text(encoding='utf-8')
            failures.extend(f'{path.relative_to(ROOT)}: {claim}' for claim in banned if claim in text)
        self.assertEqual(failures, [])

    def test_cage_comparison_has_no_unsourced_ratings(self):
        source = (ROOT / 'artikel/vogelkaefig-voliere-kaufen-vergleich-2026.html').read_text(encoding='utf-8')
        self.assertNotIn('class="prod-rating"', source)
        self.assertNotIn('empfehlen wir den <strong>Savic', source)
        self.assertNotIn('empfehlen wir allerdings das größere Modell von Savic', source)

    def test_generator_does_not_restore_experience_claim(self):
        source = (ROOT / '_fix_eeat.py').read_text(encoding='utf-8')
        self.assertNotIn('Tierhalter mit langjähriger Erfahrung', source)

if __name__ == '__main__':
    unittest.main()
