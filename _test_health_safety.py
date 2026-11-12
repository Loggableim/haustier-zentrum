"""Guard the targeted November 2026 safety corrections, including FAQ data."""
from pathlib import Path
import unittest
R = Path(__file__).resolve().parent / 'artikel'
class HealthSafetyTests(unittest.TestCase):
    def test_first_aid(self):
        s = (R/'erste-hilfe-haustiere-notfall-ratgeber.html').read_text()
        for old in ['Apomorphin', 'Knobi-Vergiftung', 'Schwächen der Blutgefäße', 'vorsichtig ins Maul spritzen', 'Bauchmassage:']:
            self.assertNotIn(old, s)
        for source in ['msdvetmanual.com', 'merckvetmanual.com', 'rspca.org.uk', 'rabbitwelfare.co.uk']:
            self.assertIn(source, s)
        self.assertGreaterEqual(s.count('Nicht selbst Erbrechen auslösen'), 2)
    def test_home_remedies(self):
        s = (R/'hunde-hausmittel.html').read_text()
        for old in ['ganz ohne Nebenwirkungen', 'absolut unbedenklich', 'kaum Nebenwirkungen', '1/4 Teelöffel', '1 Teelöffel pro 10 kg', 'Einfach 1 Teelöffel', '1–2 Esslöffel']:
            self.assertNotIn(old, s)
        self.assertIn('vcahospitals.com/know-your-pet/chamomile', s)
    def test_no_wait_or_forced_rabbit_water(self):
        cat = (R/'katzenkrankheiten-erkennen.html').read_text()
        self.assertNotIn('Führe 24 Stunden lang', cat)
        self.assertIn('vet.cornell.edu', cat)
        rabbit = (R/'kaninchen-ernaehrung-gesundheit.html').read_text()
        for old in ['Tränken (ggf. mit Spritze)', 'Bis dahin: Tränken', 'Kaninchen-Aufstrich']:
            self.assertNotIn(old, rabbit)
        self.assertGreaterEqual(rabbit.count('Vor einer Zwangsfütterung muss ein Darmverschluss ausgeschlossen sein.'), 2)
        self.assertIn('rabbitwelfare.co.uk', rabbit)
if __name__ == '__main__': unittest.main()
