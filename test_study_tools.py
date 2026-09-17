import unittest
from datetime import date,time
from study_tools import *
class ToolsTests(unittest.TestCase):
    def test_budgets(self):
        for exam in ANCHORS:
            for minutes in [15,30,45,60,90,180]:
                tasks=micro_plan(exam,days=3,minutes=minutes,panic=True)
                for d in range(3):
                    rows=[r for r in tasks if r['day']==d]
                    self.assertEqual(sum(r['minutes'] for r in rows),minutes)
                    self.assertEqual(rows[-1]['start']+rows[-1]['minutes'],minutes)
                    self.assertTrue(all(r['minutes']>0 for r in rows))
    def test_priority(self):
        tasks=micro_plan('neet',{'cells':0,'motion':100},3,90)
        self.assertGreater(sum(t['minutes'] for t in tasks if t['topic']=='cells'),sum(t['minutes'] for t in tasks if t['topic']=='motion'))
    def test_context(self):
        reply,exam,topic=context_reply('NEET ke liye aaj kya karu','10')
        self.assertEqual(exam,'neet');self.assertIn('Cell biology',reply)
        reply,exam,topic=context_reply('cells samjhao',exam)
        self.assertEqual(topic,'cells');self.assertIn('factory',reply)
        self.assertIn('factory',context_reply('aur simple samjhao',exam,topic)[0])
        self.assertIn('Which concept',context_reply('explain black holes',exam,topic)[0])
    def test_exports(self):
        tasks=micro_plan('cat',days=2,minutes=30)
        pdf=pdf_bytes(tasks,date(2026,9,17))
        self.assertTrue(pdf.startswith(b'%PDF'))
        ics=calendar_bytes(tasks,date(2026,9,17),time(18))
        self.assertIn(b'DTSTART:20260917T123000Z',ics)
        self.assertEqual(ics.count(b'BEGIN:VEVENT'),len(tasks))
        self.assertTrue(all(len(l)<=75 for l in ics.split(b'\r\n')))
    def test_bank(self):
        for data in CONCEPTS.values():
            self.assertEqual(len(data[3]),3)
            for question,options,answer,reason in data[3]:self.assertIn(answer,options)
if __name__=='__main__': unittest.main()
