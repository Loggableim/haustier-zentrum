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
    def test_cat_plants_and_heatstroke(self):
        s = (R/'erste-hilfe-haustiere-notfall-ratgeber.html').read_text()
        for old in ['Alle Lilienarten', 'schon ein Tierchen Blatt', 'innerhalb von 18 Stunden', 'feuchte kühle Tücher auf Pfoten und Bauch']:
            self.assertNotIn(old, s)
        for new in ['Lilium', 'Hemerocallis', 'healthtopics.vetmed.ucdavis.edu', 'aspca.org', 'conditions/heatstroke-in-cats', 'Nicht auf eine Temperaturmessung warten', 'nicht mit nassen Tüchern zudecken']:
            self.assertIn(new, s)
    def test_bleeding_and_fall_transport(self):
        s = (R/'erste-hilfe-haustiere-notfall-ratgeber.html').read_text()
        for old in ['innerhalb von 5 Minuten abdrücken', 'Fixierung, Abbinde', 'Abbinde oberhalb', 'maximal 15 Minuten', 'Wenn die Blutung nach 5 Minuten', 'Blutung, die nach 5 Minuten', 'am Sofa liegen', 'ab dem 3. Stock']:
            self.assertNotIn(old, s)
        for new in ['first-aid-for-bleeding', 'how-to-safely-move-an-injured-pet', 'sofort den tierärztlichen Notdienst kontaktieren']:
            self.assertIn(new, s)
    def test_no_unsupervised_emergency_procedures(self):
        s = (R/'erste-hilfe-haustiere-notfall-ratgeber.html').read_text()
        for old in ['zwei Finger links und rechts', 'Stabile Schienung improvisieren', 'Pfoten-Schiene (improvisiert)', 'Octenisept', 'Kranke Vögel brauchen Wärme (30–32', 'Wasser oder Elektrolytlösung an den Schnabel', 'Deckel öffnen (Sauerstoffzufuhr)', '0700 5000 9911', '<li>Wärme und Ruhe.</li>']:
            self.assertNotIn(old, s)
        for new in ['first-aid-for-choking', 'first-aid-for-broken-bones', 'heatstroke-in-rabbits', 'care-of-open-wounds-in-cats', 'injuries-and-accidents-of-pet-birds']:
            self.assertIn(new, s)
        section = s.split('<h3>Hitzeunfall bei Kleintieren</h3>')[1].split('<h2>Erste Hilfe bei Vögeln</h2>')[0]
        self.assertIn('sofort den tierärztlichen Notdienst', section)
    def test_dog_emergency_guide(self):
        s = (R/'hunde-krankheiten-symptome-erste-hilfe.html').read_text()
        for old in ['Ausnahme: innerhalb von 10 Minuten', 'Kein Urin über 12+', 'Parvovirose (Hundestaupe)', 'Bei komplettem Harnaufhalt', 'kein Urin über mehrere Stunden']:
            self.assertNotIn(old, s)
        for source in ['first-aid-for-poisons-and-toxins', 'what-to-do-if-your-catdog-can-t-pee', 'canine-parvovirus-infection']:
            self.assertIn(source, s)
    def test_small_animal_emergency_duplicates(self):
        for prefix in ['kleintier-gesundheit-2026-', 'notfall-checkliste-2026-', 'meerschweinchen-krankheiten-gesundheit', 'wellensittich-ernaehrung-gesundheit']:
            p = next(R.glob(prefix+'*.html'))
            s = p.read_text()
            for old in ['Kotabsatz über 12 Stunden', 'zum Eingeben von Flüssigkeit', 'Massiere vorsichtig den Bauch', 'massiere den Bauch sanft', 'länger als 12 Stunden', 'mehr als einen Tag nichts frisst', 'Einfach ins Trinkwasser', 'Ergänzung ins Trinkwasser', 'ohne Futter nur 24–48 Stunden', 'keine Injektionsnarkose!', 'vertragen Injektionsnarkosen sehr schlecht']:
                self.assertNotIn(old, s, str(p))
            self.assertTrue('pdsa.org.uk' in s or 'vcahospitals.com' in s, str(p))
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
