"""Verify pet-appropriate emergency routing on the printable checklist."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
CHECKLIST = ROOT / 'artikel/notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte.html'

class PoisonContactTests(unittest.TestCase):
    def test_no_human_poison_number_or_alternative(self):
        html = CHECKLIST.read_text()
        self.assertNotIn('19240', html)
        self.assertNotRegex(html, r'(?i)oder (?:die |der )?Giftnotruf')
        self.assertIn('Für Tiervergiftungen ist der tierärztliche Notdienst', html)
        self.assertIn('giftnotruf.charite.de/fuer_patienten/', html)
        self.assertIn('tiho-hannover.de/', html)

    def test_emergency_faq_matches_structured_and_printable_copy(self):
        html = CHECKLIST.read_text()
        for answer in ('Bei möglicher Aufnahme sofort die Tierarztpraxis oder den tierärztlichen Notdienst kontaktieren.',
                       'Bei Vergiftungsverdacht sofort dort anrufen, auch wenn noch keine Symptome sichtbar sind.'):
            self.assertEqual(html.count(answer), 2)
        self.assertIn('Tierärztlicher Notdienst für Deine Tierart', html)

if __name__ == '__main__':
    unittest.main()
