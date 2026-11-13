"""Guard the targeted November 2026 safety corrections, including FAQ data."""
from pathlib import Path
import unittest
R = Path(__file__).resolve().parent / 'artikel'
class HealthSafetyTests(unittest.TestCase):
    def test_emergency_survival_statistic_removed(self):
        for p in [R/'notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte.html', R.parent/'rss.xml']:
            self.assertNotIn('Überlebenschancen von Tieren bei Notfällen um bis zu 40 Prozent', p.read_text())

    def test_emergency_checklist_heatstroke(self):
        import re, json, html
        s=(R/'notfall-checkliste-2026-erste-hilfe-fuer-hund-katze-und-kleintier-was-jede-halte.html').read_text()
        for old in ['kühle ihn langsam', 'kühle es langsam', 'Kein Eiswasser verwenden', 'Eiswasser oder Eisbeutel direkt auf der Haut können zu Schock', 'Pfoten, Bauch und Kopf']:
            self.assertNotIn(old,s)
        for term in ['kaltem Leitungswasser', 'Nase und Maul', 'nicht zum Trinken zwingen', 'auch bei scheinbarer Besserung', 'nicht mit nassen Handtüchern', 'heatstroke-in-rabbits', 'first-aid-for-heatstroke']:
            self.assertIn(term,s)
        question='Wie erkenne ich einen Hitzschlag bei meinem Haustier?'
        visible=re.search(r'<h3>'+re.escape(question)+r'</h3>\s*<p>(.*?)</p>',s,re.S)[1]
        visible=html.unescape(re.sub('<[^>]+>','',visible))
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
            data=json.loads(block)
            if data.get('@type')=='FAQPage':
                self.assertEqual(next(q['acceptedAnswer']['text'] for q in data['mainEntity'] if q['name']==question),visible)
    def test_cat_vaccination_schedule(self):
        import re, json, html
        s = (R/'katzen-impfungen-vorsorge.html').read_text()
        for old in ['optional in der 16.', '3. Teil – optional', 'Zweite Tollwutimpfung', 'Kernimpfungen (Katzenschnupfen, Katzenseuche, Tollwut)', 'Mit 12 Monaten', 'frühestens in der 8.', 'Grundimmunisierung, 3×', 'alle drei Termine', 'Eine jährliche Auffrischung', 'insgesamt etwa 120–180']:
            self.assertNotIn(old, s)
        for new in ['15 Lebensmonaten', 'Impfleitlinie_Kleintiere_2025-01-06.pdf', 'Friedrich-Loeffler-Institut', 'kein starrer Plan', 'Nicht-Kernimpfung']:
            self.assertIn(new, s)
        core = s.split('<h3>Kernimpfungen')[1].split('<h3>Nicht-Kernimpfungen')[0]
        self.assertNotIn('Tollwut', core)
        visible = dict(re.findall(r'<div class="faq-item"><h3>(.*?)</h3><p>(.*?)</p></div>', s))
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            data=json.loads(block)
            if data.get('@type') == 'FAQPage':
                for item in data['mainEntity']:
                    self.assertEqual(html.unescape(visible[item['name']]), item['acceptedAnswer']['text'])
    def test_cat_parasite_advice(self):
        s=(R/'katzen-impfungen-vorsorge.html').read_text()
        for old in ['entlauben', 'Wohnungskatzen alle 3–4 Monate', 'Pro Behandlung, alle 3 Monate empfohlen', 'Monatliche Anwendung in der Saison', 'So wird nur behandelt, wenn es wirklich nötig ist']:
            self.assertNotIn(old,s)
        for term in ['esccap.de/parasiten/wuermer/wie-oft-katzen-entwurmen/', 'negativer Kotbefund schließt', 'individuellen Risiko', 'esccap.de/parasiten/basisvorsorge/']:
            self.assertIn(term,s)
    def test_dog_food_portions_bones_and_puppy_calcium(self):
        s=(R/'hundefutter-vergleich-2026.html').read_text()
        for old in ['2-3 % seines Körpergewichts', '400-600 g Nassfutter', '250-350 g Trockenfutter', 'mehr Protein und Calcium', 'besonders protein- und calciumreich', 'Knochen immer nur roh und unter Aufsicht']:
            self.assertNotIn(old,s)
        for term in ['Energiedichte', 'Gewichtsverlauf', 'Auch rohe Knochen', 'Zahnbrüche', 'keine Calciumpräparate', 'Raw-Meat-Based-Diets-for-Pets_WSAVA-Global-Nutrition-Toolkit.pdf', 'Frequently-Asked-Questions-and-Myths.pdf', 'introduction-to-feeding-dogs.pdf']:
            self.assertIn(term,s)
    def test_dog_food_selection(self):
        s=(R/'hundefutter-vergleich-2026.html').read_text()
        for old in ['50-70 %', 'Praxiswissen aus dem Alltag', 'Protein an erster Stelle', 'Billigprodukte vom Discounter', 'sollten deshalb an erster Stelle']:
            self.assertNotIn(old,s)
        import json, re, html
        visible = re.search(r'<p>(Prüfe, ob es als Alleinfuttermittel.*?)</p>',s)[1]
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
            data=json.loads(block)
            if data.get('@type')=='FAQPage':
                answers=[x['acceptedAnswer']['text'] for x in data['mainEntity']]
                self.assertIn(html.unescape(visible),answers)
        for name in ['index.html','rss.xml']:
            self.assertNotIn('Die besten Marken, Preisvergleich und Fütterungsempfehlungen.',(R.parent/name).read_text())
        for term in ['kein eigener Produkt- oder Fütterungstest', 'Selecting-a-pet-food-for-your-pet-updated-2021', 'Alleinfuttermittel']:
            self.assertIn(term,s)
    def test_rabbit_appetite_and_hamster_incisors(self):
        s=(R/'kaninchen-ernaehrung-gesundheit.html').read_text()
        self.assertNotIn('Kein Futteraufnahme über 12 Stunden',s)
        self.assertIn('Bei weniger oder keiner Futteraufnahme sofort',s)
        h=next(R.glob('kleintier-gesundheit-2026-*.html')).read_text()
        self.assertNotIn('keine durchgehend wachsenden Zähne',h)
        self.assertIn('Schneidezähne wachsen lebenslang',h)
        self.assertIn('routine-health-care-of-hamsters',h)
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
