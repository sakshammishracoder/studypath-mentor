import unittest
from mentor import Result, analyze, make_plan, career_reply

class MentorTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual([Result('x', n, 100).level for n in [0,59,60,79,80,100]], ['Weak','Weak','Developing','Developing','Strong','Strong'])
    def test_validation(self):
        for marks, total in [(-1,100),(101,100),(0,0),(float('nan'),100)]:
            with self.assertRaises(ValueError): Result('x',marks,total)
        with self.assertRaises(ValueError): analyze([])
        with self.assertRaises(ValueError): analyze([Result('A',1,2),Result('a',2,2)])
    def test_budget_and_priority(self):
        results = [Result('Weak',20,100),Result('Strong',90,100)]
        for minutes in range(30,361,15):
            plan = make_plan(results,7,minutes)
            for day in range(1,8):
                blocks = [b for b in plan if b['day']==day]
                self.assertEqual(sum(b['minutes'] for b in blocks), minutes)
                self.assertTrue(all(b['minutes']>0 for b in blocks))
            self.assertGreater(sum(b['minutes'] for b in plan if b['topic']=='Weak'),sum(b['minutes'] for b in plan if b['topic']=='Strong'))
    def test_career(self):
        self.assertIn('PyTorch',career_reply('AI Engineer kaise bane?'))
        self.assertIn('बुनियाद',career_reply('एआई इंजीनियर कैसे बनें?', 'hi'))
        self.assertIn('currently support',career_reply('doctor'))
        self.assertIn('currently support',career_reply('paid work'))

if __name__=='__main__': unittest.main()
