import json
import unittest
from pathlib import Path
from _faq_consistency import check_faq

class FAQTests(unittest.TestCase):
    def page(self, answer='Body answer', question='Body question?', body='<h3>Body question?</h3><p>Body answer</p>', graph=False):
        faq={'@type':'FAQPage','mainEntity':[{'@type':'Question','name':question,'acceptedAnswer':{'@type':'Answer','text':answer}}]}
        if graph: faq={'@graph':[faq]}
        return '<head><script type="application/ld+json">'+json.dumps(faq)+'</script></head><body>'+body+'</body>'
    def test_all_article_questions_and_answers_present(self):
        count=0
        for p in (Path(__file__).parent/'artikel').glob('*.html'):
            count+=check_faq(p.read_text(),p.name)
        self.assertGreater(count,100)
    def test_wrong_topic_is_rejected(self):
        with self.assertRaises(ValueError):
            check_faq(self.page(question='Unrelated puppy question?'),'fixture')
    def test_stale_answer_is_rejected(self):
        with self.assertRaises(ValueError):
            check_faq(self.page(answer='Stale answer'),'fixture')
    def test_markup_entities_and_graph(self):
        self.assertEqual(check_faq(self.page(answer='Cat & dog',body='<h3>Body question?</h3><p><b>Cat</b> &amp; dog</p>',graph=True),'fixture'),1)
    def test_script_content_does_not_count_as_visible(self):
        with self.assertRaises(ValueError):
            check_faq(self.page(body='<script>Body question? Body answer</script>'),'fixture')
    def test_cat_plant_schema_and_jade_correction(self):
        s=(Path(__file__).parent/'artikel/katzen-zimmerpflanzen-giftig.html').read_text()
        self.assertNotIn('Welpe',s)
        self.assertNotIn('Calathea, Geldbaum',s)
        self.assertIn('Geldbaum (Crassula ovata) ist giftig',s)
        self.assertIn('nicht auf Symptome warten',s)
        self.assertEqual(check_faq(s,'cat plants'),5)

if __name__=='__main__': unittest.main()
