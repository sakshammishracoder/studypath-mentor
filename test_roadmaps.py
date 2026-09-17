import unittest
from roadmaps import CATALOG, find_path, render_path
from mentor import career_reply

class RoadmapTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(len(CATALOG),16)
        self.assertEqual(len({e['id'] for e in CATALOG}),16)
        for e in CATALOG:
            for lang in ['en','hi']:
                self.assertEqual(len(e[lang]),5)
                self.assertTrue(all(e[lang]))
                self.assertIn('2026',render_path(e,lang))
    def test_routing(self):
        for q, expected in [('NEET kaise clear kare','neet'),('CA roadmap','ca'),('कक्षा 10','10'),('बैंकिंग','bank'),('ssc gd','police'),('rrb ntpc','rail'),('CAT eligibility','cat')]:
            self.assertEqual(find_path(q)['id'],expected)
            self.assertIn(find_path(q)['title'],career_reply(q))
        self.assertIsNone(find_path('communication skills'))
        self.assertIsNone(find_path('education'))
    def test_unverified(self):
        self.assertIn('not verified',render_path(find_path('upsc')))
        self.assertIn('22 September',render_path(find_path('cat')))

if __name__ == '__main__': unittest.main()
