"""Guard the targeted November 2026 safety corrections, including FAQ data."""
from pathlib import Path
import unittest
R = Path(__file__).resolve().parent / 'artikel'
class HealthSafetyTests(unittest.TestCase):
    def test_bird_cage_evidence_and_zinc(self):
        s=(R/'vogelkaefig-voliere-kaufen-vergleich-2026.html').read_text()
        for old in ['tag=nova079-20', 'Weatherproof 200', 'FOPATO', 'Die 7 besten', 'Unser Urteil:', '80 × 50 × 50', 'mindestens 80 cm']:
            self.assertNotIn(old,s)
        for new in ['Zinkvergiftung', 'keine Sicherheitsgarantie', '2 × 1 × 2 Meter', 'keine Testauszeichnung', 'Herstellerkatalog 2026', 'keine tierärztliche Freigabe']:
            self.assertIn(new,s)
        self.assertNotIn('FAQPage',s)
        self.assertNotIn('lastReviewed',s)

    def test_anxiety_comfort_and_timing(self):
        import json,re
        s=(R/'hundeangst-training-tipps.html').read_text()
        for old in ['übermäßiges Trösten, da dies die Angst verstärken kann','erst zu belohnen, sobald der Hund sich entspannt','Tröstende Zuwendung im falschen Moment','aber nur, wenn dein Hund ruhig bleibt']:
            self.assertNotIn(old,s)
        for new in ['Angst ist eine Emotion','erst Auslöser, dann Futter','ohne es aufzudrängen','Bei Stress beende die Belastung']:
            self.assertIn(new,s)
        data=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
        faq=next(x for x in data if x.get('@type')=='FAQPage')
        q=next(x for x in faq['mainEntity'] if 'trösten' in x['name'])
        self.assertIn(q['acceptedAnswer']['text'],s)

    def test_small_pet_comparison_welfare(self):
        s=(R/'kleintiere-hamster-meerschweinchen.html').read_text()
        for old in ['bewusst anonymisiert, aber wahr','Familie Hoffmann','Erfahrungen aus unserem Freundeskreis','Markus','lassen sich gerne streicheln','verschmuste Familienfreund','80 x 50 cm','120 × 60 × 50 cm']:
            self.assertNotIn(old,s)
        for new in ['keine Berichte über konkrete Halter','Kleine Kinder sollen Meerschweinchen nicht tragen','Angstreaktion','Torpor','100 × 50 cm']:
            self.assertIn(new,s)

    def test_chihuahua_chip_scope(self):
        s=next(R.glob('*chihuahua*.html')).read_text()
        self.assertNotIn('Seit 2011 müssen alle Hunde in Deutschland',s)
        for term in ['3. Juli 2011','landesrechtliche Vorgaben','31. August 2030','31. August 2036','Suchregister','Tätowierung']:
            self.assertIn(term,s)

    def test_puppy_buying_law_and_import(self):
        import json,re
        s=(R/'welpenkauf-zuuechter-tierheim-checkliste.html').read_text()
        for old in ['§ 4 Abs. 2','mindestens 12 Wochen alt sein','andere Hunde (nach Impfung!)','mindestens eine Grundimmunisierung','getrennt und verkauft werden']:
            self.assertNotIn(old,s)
        for new in ['§ 2 Absatz 4','über acht Wochen','frühestens 15 Wochen','TRACES','Eigentumsübertragung','Tollwut-Antikörpertest']:
            self.assertIn(new,s)
        data=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
        faq=next(x for x in data if x.get('@type')=='FAQPage')
        q=next(x for x in faq['mainEntity'] if 'alt' in x['name'].lower())
        self.assertIn(q['acceptedAnswer']['text'],s)

    def test_puppy_vaccination_socialisation(self):
        import json,re
        s=(R/'welpen-eingewoehnung.html').read_text()
        for old in ['Grundimmunisierung (zweite Impfung)','wenn alle Impfungen durch sind','auf dem Schoß oder','wird als erwachsener Hund selbstbewusst, ausgeglichen und angstfrei sein']:
            self.assertNotIn(old,s)
        for new in ['örtlichem Infektionsrisiko','16 Wochen','mindestens sieben Tage','keine pauschale Teilnahmefreigabe','nicht automatisch infektionssicher']:
            self.assertIn(new,s)
        data=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
        faq=next(x for x in data if x.get('@type')=='FAQPage')
        q=next(x for x in faq['mainEntity'] if x['name']=='Wann darf mein Welpe das erste Mal unter andere Hunde?')
        self.assertIn(q['acceptedAnswer']['text'],s)

    def test_ferret_feeding_and_faq(self):
        import json,re
        s=(R/'frettchen-haustier-haltung-pflege-kosten.html').read_text()
        for old in ['20–30 %','entsprechende Mengen Frischfleisch','niemals länger als 3–4 Stunden','rohe Eier (nur das Eigelb)','aus Rinderhaut']:
            self.assertNotIn(old,s)
        for new in ['Alleinfuttermittel','nicht einfach grammweise','feeding-ferrets','Infektions- und Darmverschlussrisiken']:
            self.assertIn(new,s)
        data=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
        faq=next(x for x in data if x.get('@type')=='FAQPage')
        q=next(x for x in faq['mainEntity'] if x['name']=='Was fressen Frettchen am liebsten?')
        self.assertIn(q['acceptedAnswer']['text'],s)

    def test_parasite_risk_based_guidance(self):
        s=next(R.glob('parasiten-alarm*.html')).read_text()
        for old in ['Kotproben statt Routine','authochthone Fälle','Resistenzen bei Spulwürmern (Toxocara spp.)','Peilomavirus','Trixacarus diversus','jährliche E.-cuniculi-Blutprobe','prophylaktische Therapie mit Fenbendazol']:
            self.assertNotIn(old,s)
        for new in ['nicht als Endemiegebiet','mindestens vier','negativer Kotbefund schließt','gleichen Abständen','Bandwürmer','Trixacarus caviae','risikobasiert','positiver Antikörpertest']:
            self.assertIn(new,s)

    def test_cross_species_dental_no_wait_threshold(self):
        import re, json, xml.etree.ElementTree as ET
        name='stille-leiden-vermeiden-2026-wie-sie-zahnprobleme-bei-hund-katze-und-kleintier-r'
        s=(R/(name+'.html')).read_text()
        for text in [s,(R.parent/'rss.xml').read_text()]:
            for old in ['Verweigerung von Futter und Wasser über mehr als 24 Stunden','binnen 24 Stunden in eine lebensbedrohliche Stoffwechsellage']:
                self.assertNotIn(old,text)
        for term in ['nicht bis zum nächsten Tag warten','weniger oder keine Köttel','nicht schlucken kann','my-rabbit-isn-t-eating-properly','guinea-pig-health','symptom-choking-or-difficulty-swallowing']:
            self.assertIn(term,s)
        data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
        article=next(d for d in data['@graph'] if d.get('@type')=='Article')
        self.assertEqual(article['dateModified'],'2026-11-14')
        sm=ET.parse(R.parent/'sitemap-articles.xml'); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        item=next(u for u in sm.findall('s:url',ns) if u.findtext('s:loc',namespaces=ns).endswith('/'+name))
        self.assertEqual(item.findtext('s:lastmod',namespaces=ns),'2026-11-14')

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
    def test_home_remedy_urgency_and_sales_consistency(self):
        import re,json
        s=(R/'hunde-hausmittel.html').read_text()
        for old in ['Fressunlust über 24 Stunden','Erbrechen länger als 24 Stunden','Quark kühlt und wirkt entzündungshemmend','Naturheilkunde+Hunde','Hundegesundheit+Hausmittel+Natur','Kurkuma-Präparate und Pflegeprodukte']:
            self.assertNotIn(old,s)
        for new in ['keine sichere Wartefrist','erfolgloses Würgen','insect-bites-and-stings-in-dogs','common-emergencies-in-dogs','kaltes, feuchtes Tuch','Gesicht, Hals oder Rachen']:
            self.assertIn(new,s)
        post=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
        self.assertEqual(post['dateModified'],'2026-11-14')
        self.assertNotIn('lastReviewed',post)
        for path in [R.parent/'index.html',R.parent/'rss.xml']:
            self.assertNotIn('Natürliche Hilfe bei Durchfall',path.read_text())

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
    def test_dog_illness_heatstroke(self):
        import re, json
        s=(R/'hunde-krankheiten-symptome-erste-hilfe.html').read_text()
        for old in ['41,5', '(nicht eiskaltem)', 'Körpertemperatur messen (Zwischenraum)', 'Keine Autos in der Sonne parken']:
            self.assertNotIn(old,s)
        for new in ['kaltem Leitungswasser', 'Halte Nase und Maul frei', 'vor der Fahrt zu kühlen', 'nicht mit nassen Handtüchern', 'Auch bei scheinbarer Besserung', 'pdsa.org.uk', 'HOW%20TO%20COOL']:
            self.assertIn(new,s)
        blocks=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
        faq=next(x for x in blocks if x.get('@type')=='FAQPage')
        answer=faq['mainEntity'][0]['acceptedAnswer']['text']
        visible=re.search(r'<div class="faq-item"><h3>Wie messe.*?</h3><p>(.*?)</p>',s,re.S)[1]
        self.assertEqual(answer,re.sub('<[^>]+>','',visible))
        self.assertNotIn('lastReviewed',blocks[0])
    def test_emergency_kit_species_specific_products(self):
        import re, json
        s=next(R.glob('notfall-checkliste*')).read_text()
        for old in ['z. B. Octenidin-Lösung', 'z. B. mit Panthenol oder Zink', '<strong>Elektrolytlösung</strong> bei Durchfall und Erbrechen']:
            self.assertNotIn(old,s)
        for new in ['nur nach tierärztlichem Plan', 'keine pauschale Selbstbehandlung', 'Wiederholtes Ablecken', 'unter Druck ins Gewebe', 'keine Freigabe für die Anwendung am Tier', 'Sterile Kochsalzlösung']:
            self.assertIn(new,s)
        blocks=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
        faq=next(x for x in blocks if x.get('@type')=='FAQPage')
        answer=faq['mainEntity'][1]['acceptedAnswer']['text']
        visible=re.search(r'<h3>Was gehört in eine Notfallapotheke für unterwegs\?</h3>\s*<p>(.*?)</p>',s,re.S)[1]
        self.assertEqual(answer,visible)
        self.assertNotIn('lastReviewed',faq)
    def test_cat_plant_emergency_and_deterrents(self):
        s=(R/'katzen-zimmerpflanzen-giftig.html').read_text()
        for old in ['Maul vorsichtig spülen', 'mit Orangen- oder Zitronenschalen mulchen', '030 – 192 40', '089 – 192 40', 'oder den Giftnotruf kontaktieren', 'Zimt oder Pfeffer']:
            self.assertNotIn(old,s)
        for new in ['Keine eigenständige Maulspülung', 'Flöße nichts ein', 'tierärztlichen Notdienst', 'nicht für Tiervergiftungen ausgebildet', 'Keine Zitrusschalen', 'first-aid-for-poisons-and-toxins']:
            self.assertIn(new,s)
    def test_budgie_feeding_risks(self):
        s=(R/'wellensittich-ernaehrung-futter.html').read_text()
        for old in ['Schnittlauch (selten)', 'Nierenschädigend', 'Weintrauben & Rosinen', 'Keine Pellets als Hauptfutter', 'in kleinen Mengen frei zur Verfügung stehen', 'sichtbarer Kropf am Abend ist normal']:
            self.assertNotIn(old,s)
        for new in ['Kein unlöslicher Verdauungsgrit', 'Kein Futterentzug', 'Schnittlauch', 'budgies-feeding', 'vetmed.illinois.edu', 'rvc.ac.uk']:
            self.assertIn(new,s)
    def test_budgie_millet_sprouts_and_toxicity(self):
        s=(R/'wellensittich-ernaehrung-futter.html').read_text()
        for old in ['15+', 'Schritt-für-Schritt', 'Kolbenhirse enthält sehr viel Fett', 'verfettetem Gefieder', 'nicht länger als 12 Stunden an', 'innerhalb von 12 Stunden verfüttert', 'damit kein Schimmel entsteht', 'Fördert Verdauung, Gefieder & Brutstimmung', 'ätherische Öle reizen die Nieren', 'Adipositas (Fettleber)']:
            self.assertNotIn(old,s)
        for new in ['kohlenhydratreiche Saat', 'Spülen garantiert keine Keimfreiheit', 'spätestens nach zwei Stunden', 'Ungeeignet ist nicht automatisch akut giftig', 'nicht für ihre Grit-Empfehlung']:
            self.assertIn(new,s)
    def test_fish_symptoms_not_blanket_treatments(self):
        s=(R/'aquarium-fische-einsteiger.html').read_text()
        for old in ['Wöchentliche Wasserwechsel sind Pflicht', '1 cm Fischlänge pro Liter', 'Temperatur langsam auf 28–30 °C erhöhen', 'Fasten für 2–3 Tage', 'Schwimmblasenmedikation', 'Bauchflossenfäule', 'ein Teelöffel Meersalz pro 10 Liter', '2–3 Wochen in einem Quarantäne']:
            self.assertNotIn(old,s)
        for new in ['Symptome, keine fertige Diagnose', 'Keine pauschale Fasten-', 'mindestens 30 Tage', 'Ammonium/Ammoniak', 'nicht automatisch', 'edis.ifas.ufl.edu', 'cafishvet.com']:
            self.assertIn(new,s)
    def test_guinea_pig_anorexia_no_wait_or_forced_feeding(self):
        for name in ['meerschweinchen-haltung', 'meerschweinchen-krankheiten-gesundheit']:
            s=(R/(name+'.html')).read_text()
            for old in ['6–8 Stunden', '6–12 Stunden', 'biete unverzüglich Breifutter', 'Wärme das Tier an']:
                self.assertNotIn(old,s)
            for new in ['Spritzenfütterung nur nach tierärztlicher Beurteilung', 'fehlendem Schlucken', 'nichts ins Maul zwingen', 'Tierarzt', 'vcahospitals.com']:
                self.assertIn(new,s)
            self.assertNotIn('lastReviewed',s)
    def test_guinea_pig_stone_prevention_not_calcium_panacea(self):
        s=(R/'meerschweinchen-krankheiten-gesundheit.html').read_text()
        for old in ['ist die beste Vorbeugung gegen Blasensteine', 'am besten aus einer Trinkflasche', 'spült die Harnwege durch', 'tropft nicht']:
            self.assertNotIn(old,s)
        for new in ['Rückfälle sind möglich', 'angepasste Calciumzufuhr', 'trächtigen oder säugenden', 'Futterpigmente', 'mspca.org', 'standsichere Schale']:
            self.assertIn(new,s)
        self.assertNotIn('Begünstigt durch falsche Calcium-Fütterung', (R/'meerschweinchen-haltung.html').read_text())
    def test_berner_markup_and_nutrition(self):
        import re
        s=(R/'berner-sennenhund-rasseguide.html').read_text()
        for old in ['<<', '**', '## ', '500–700 g', 'mindestens 25 %', 'Allergien reduzieren', 'kein Trinken in großen Mengen']:
            self.assertNotIn(old,s)
        for new in ['Wasser nicht vorenthalten', 'nicht automatisch', 'Alleinfuttermittel', 'Zahnfrakturen', 'dateModified']:
            self.assertIn(new,s)
        for h in re.findall(r'<h[23]>(.*?)</h[23]>',s):
            self.assertLess(len(h),150)
        from html.parser import HTMLParser
        class Structure(HTMLParser):
            def __init__(self): super().__init__(); self.stack=[]
            def handle_starttag(self,tag,attrs):
                if tag in ['div','section','ul','li','p','h1','h2','h3']: self.stack.append(tag)
            def handle_endtag(self,tag):
                if tag in ['div','section','ul','li','p','h1','h2','h3']:
                    assert self.stack and self.stack.pop()==tag
        a=s.index('<div class="content">'); b=s.index('<section class="related-posts">',a)
        parser=Structure(); parser.feed(s[a:b]); self.assertEqual(parser.stack,[])

    def test_breed_guides_no_generator_artifacts(self):
        from html.parser import HTMLParser
        class Structure(HTMLParser):
            def __init__(self): super().__init__(); self.stack=[]
            def handle_starttag(self,tag,attrs):
                if tag in ['div','section','ul','li','p','h1','h2','h3']:
                    if tag=='li': assert self.stack and self.stack[-1]=='ul'
                    self.stack.append(tag)
            def handle_endtag(self,tag):
                if tag in ['div','section','ul','li','p','h1','h2','h3']: assert self.stack and self.stack.pop()==tag
        for name in ['cocker-spaniel','dalmatiner','malteser','beagle','havaneser','zwergspitz-pomeranian','westie-west-highland-white-terrier']:
            s=(R/(name+'-rasseguide.html')).read_text()
            for old in ['<<','**','## ','<p>---</p>']: self.assertNotIn(old,s)
            a=s.index('<div class="content">');b=s.index('<section class="related-posts">',a)
            parser=Structure();parser.feed(s[a:b]);self.assertEqual(parser.stack,[])
    def test_berner_care_and_health_qualified(self):
        s=(R/'berner-sennenhund-rasseguide.html').read_text()
        for old in ['6–8 Jahren', 'nicht wegen des Hundes', '1,5–2 Stunden', 'Ein Bad alle 6–8', 'Bei Temperaturen über 25', 'zwischen 4 und 7 Jahren']:
            self.assertNotIn(old,s)
        for new in ['8,4 Jahren', 'Geburtsjahrgängen 2001 und 2002', 'aktiv beaufsichtigen', 'kinderfreien Rückzugsort', 'SOD1A und SOD1B', 'keine feste Lebenserwartung']:
            self.assertIn(new,s)
    def test_breed_health_first_batch(self):
        for n in ['cocker-spaniel','zwergspitz-pomeranian','westie-west-highland-white-terrier']:
            s=(R/(n+'-rasseguide.html')).read_text()
            for old in ['60–80 g Trockenfutter pro Kilogramm', '300–400 g', '150 und 250 Gramm', 'mindestens 70 %', 'Kauknochen', 'In vielen Fällen heilt sie von selbst aus', 'Reinige sie wöchentlich', 'Reinige die Ohren wöchlich']:
                self.assertNotIn(old,s)
            for new in ['Alleinfuttermittel','Körperzustand','Krankheitserreger','zuerst tierärztlich abklären']:
                self.assertIn(new,s)
    def test_breed_health_second_batch(self):
        for n in ['dalmatiner','malteser','beagle','havaneser']:
            s=(R/(n+'-rasseguide.html')).read_text()
            for old in ['300 bis 500 g', '60–80 g', '200–450 g', '40–60 g', 'mindestens 70 %', 'Beagle-Erkrankung', 'wöchentlich mit spezieller Lösung', 'Ohren wöchentlich reinigen', 'Reinige sie wöchentlich']:
                self.assertNotIn(old,s)
            for new in ['Alleinfuttermittel','Körperzustand','Krankheitserreger','zuerst tierärztlich abklären']: self.assertIn(new,s)
        d=(R/'dalmatiner-rasseguide.html').read_text()
        for new in ['Low-Uric-Acid','nicht gleich pauschal proteinarm','wenig oder keinem Urin']: self.assertIn(new,d)
        self.assertIn('SRMA', (R/'beagle-rasseguide.html').read_text())
if __name__ == '__main__': unittest.main()
