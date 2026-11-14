"""Regression guard for the bounded dog-weight-management correction."""
import unittest,re,json,html
from pathlib import Path
R=Path(__file__).resolve().parent
class DogWeightTests(unittest.TestCase):
 def test_no_generic_prescription(self):
  s=(R/'artikel/hunde-uebergewicht.html').read_text()
  for x in ['endet oft in Gelenkverschleiß, Diabetes', 'unweigerlich', '30 Prozent weniger Kalorien', 'praxiserprobten','Futter um 15 %','weitere 5–10 %','60–70 %','20–30 Prozent des bisherigen','unter 15 kg','über 30 kg','Ab Woche 8','hohen Fleischanteil','Kalorienbedarf-Tabelle','MER – zur Gewichtsreduktion','ca. 70 %', 'Jeder zweite Hund', '40 und 50 Prozent', 'nur 17 Prozent', '1,8 bis 2,5', 'Fettleibigkeit ist der Hauptauslöser', 'ganzen Schokoriegel', 'Kein Körperfett', 'mehrere ausgedehnte Spaziergänge', 'und leg los', 'glänzenden Fell']:
   self.assertNotIn(x,s)
  for x in ['individuell','Nährstoffmangel','aaha.org','wsava.org','pdsa.org.uk','vet.cornell.edu']:
   self.assertIn(x,s)
 def test_faq_matches_schema(self):
  s=(R/'artikel/hunde-uebergewicht.html').read_text()
  visible=dict(re.findall(r'<div class="faq-item"><h3>(.*?)</h3><p>(.*?)</p></div>',s))
  found=False
  for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
   d=json.loads(raw)
   if d.get('@type')=='FAQPage':
    found=True
    self.assertEqual(len(d['mainEntity']),len(visible))
    self.assertGreater(len(visible),0)
    for q in d['mainEntity']:self.assertEqual(html.unescape(re.sub('<[^>]+>','',visible[q['name']])),q['acceptedAnswer']['text'])
  self.assertTrue(found,'FAQPage missing')
class DogRawDentalTests(unittest.TestCase):
 def test_removed_raw_and_hard_chew_claims(self):
  for name in ['hundeernaehrung','hunde-ernaehrung-barf-trocken-nass']:
   s=(R/f'artikel/{name}.html').read_text()
   for phrase in ['fördert die Zahngesundheit durch Kauen','40–50 % rohes','natürliche Zahnbürste','nur weiche, rohe Knochen','über 90 %','5. Trächtigkeitsmonat']:
    self.assertNotIn(phrase,s)
   for phrase in ['Raw-Meat-Based-Diets-for-Pets','tierärztliche Ernährungsberatung','Zahnfrakturen']:
    self.assertIn(phrase,s)
  s=(R/'artikel/hunde-zahnpflege.html').read_text()
  for phrase in ['Sehr hart, extrem langanhaltend','Nur für kräftige Kauer','splittert kaum','Enzymatische Unterstützung','natürliche Zahnbürste']:
   self.assertNotIn(phrase,s)
  for phrase in ['Zahnfrakturen','vohc.org/accepted-products','Pet-Health-Info-Teeth-Brushing-ADA']:
   self.assertIn(phrase,s)
 def test_faq_alignment_and_revision(self):
  for name in ['hundeernaehrung','hunde-ernaehrung-barf-trocken-nass','hunde-zahnpflege']:
   s=(R/f'artikel/{name}.html').read_text()
   visible=re.findall(r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*</div>',s,re.S)
   plain=lambda x:html.unescape(re.sub('<[^>]+>','',x))
   blocks=[json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)]
   faq=next(b for b in blocks if b.get('@type')=='FAQPage')
   self.assertEqual([(q['name'],q['acceptedAnswer']['text']) for q in faq['mainEntity']],[(plain(q),plain(a)) for q,a in visible])
   post=next(b for b in blocks if b.get('@type')=='BlogPosting')
   self.assertEqual(post['dateModified'],'2026-11-14')
   self.assertNotIn('lastReviewed',post)
if __name__=='__main__':unittest.main()
