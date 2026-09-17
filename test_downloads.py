import unittest
from datetime import date,time
from downloads import practice_pdf, roadmap_pdf, report_pdf
from study_tools import CONCEPTS,micro_plan
from roadmaps import CATALOG
from mentor import ROADS,Result
class DownloadTests(unittest.TestCase):
    def test_practice(self):
        self.assertTrue(practice_pdf(list(CONCEPTS),True).startswith(b'%PDF'))
        self.assertTrue(practice_pdf(['cells'],False).startswith(b'%PDF'))
        with self.assertRaises(ValueError):practice_pdf([])
    def test_roadmaps(self):
        for e in CATALOG:self.assertTrue(roadmap_pdf('exam',e['id']).startswith(b'%PDF'))
        for name in ROADS:self.assertTrue(roadmap_pdf('career',name).startswith(b'%PDF'))
    def test_reports(self):
        self.assertTrue(report_pdf('neet',[],[],None,set()).startswith(b'%PDF'))
        plan=dict(exam='neet',tasks=micro_plan('neet',days=2,minutes=30),signature='demo',start=date(2026,9,17),clock=time(18),panic=True)
        history=[dict(exam='neet',topic='cells',score=33.3,time='18:00:00'),dict(exam='neet',topic='cells',score=66.7,time='18:05:00')]
        self.assertTrue(report_pdf('neet',[Result('<algebra>',1,2)],history,plan,{'demo_0'}).startswith(b'%PDF'))
if __name__=='__main__':unittest.main()
