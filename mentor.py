"""Transparent recommendation logic; no trained model or external services."""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Result:
    topic: str
    marks: float
    total: float

    def __post_init__(self):
        if not self.topic.strip():
            raise ValueError('Topic cannot be empty.')
        if not (0 < self.total <= 100000 and 0 <= self.marks <= self.total):
            raise ValueError('Maximum must be positive and marks must be between zero and maximum.')

    @property
    def percent(self):
        return round(100 * self.marks / self.total, 1)

    @property
    def level(self):
        return 'Weak' if self.percent < 60 else 'Developing' if self.percent < 80 else 'Strong'


def analyze(results):
    if not results:
        raise ValueError('Add at least one topic.')
    names = [r.topic.strip().casefold() for r in results]
    if len(set(names)) != len(names):
        raise ValueError('Use a different name for each topic.')
    return sorted(results, key=lambda r: r.percent)


def make_plan(results, days=7, minutes=120):
    results = analyze(results)
    if not 1 <= days <= 30 or not 30 <= minutes <= 360:
        raise ValueError('Choose 1–30 days and 30–360 daily minutes.')
    # Weighted fair scheduling: lower scores get more slots, but other topics recur.
    weights = [max(10, 100 - r.percent) for r in results]
    credits = [0.0] * len(results)
    plan = []
    counts = [0] * len(results)
    for day in range(1, days + 1):
        remaining = minutes
        elapsed = 0
        while remaining:
            duration = min(45, remaining)
            for i, weight in enumerate(weights):
                credits[i] += weight
            index = max(range(len(results)), key=lambda i: credits[i])
            credits[index] -= sum(weights)
            counts[index] += 1
            phase = (counts[index] - 1) % 3
            plan.append({'day': day, 'start': elapsed, 'minutes': duration,
                         'topic': results[index].topic, 'phase': phase})
            remaining -= duration
            elapsed += duration
            if remaining > 10:
                plan.append({'day': day, 'start': elapsed, 'minutes': 5,
                             'topic': '', 'phase': -1})
                elapsed += 5
                remaining -= 5
    return plan


QUIZ = [
    ('Algebra', 'Solve: 2x + 6 = 14', 'हल करें: 2x + 6 = 14', ['2', '4', '6', '8'], '4'),
    ('Algebra', 'If y = 3x, find y when x = 5.', 'यदि y = 3x और x = 5, तो y क्या है?', ['8', '10', '15', '20'], '15'),
    ('Probability', 'Probability of heads on a fair coin?', 'एक निष्पक्ष सिक्के पर चित आने की प्रायिकता?', ['0', '1/4', '1/2', '1'], '1/2'),
    ('Probability', 'Probability of rolling a 6 on a fair six-sided die?', 'निष्पक्ष छह-मुखी पासे पर 6 आने की प्रायिकता?', ['1/2', '1/3', '1/6', '1'], '1/6'),
    ('Python', 'What is len([1, 2, 3])?', 'len([1, 2, 3]) का परिणाम?', ['2', '3', '4', '6'], '3'),
    ('Python', 'Which keyword defines a function?', 'फ़ंक्शन परिभाषित करने वाला कीवर्ड?', ['for', 'class', 'def', 'if'], 'def'),
]

ROADS = {
 'AI Engineer': {
  'aliases': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'एआई', 'ए आई', 'मशीन लर्निंग'],
  'en': [('Foundations', 'Learn Python, algebra, probability and basic statistics.'), ('Work with data', 'Practice NumPy, pandas, data cleaning and visualization.'), ('Machine learning', 'Use scikit-learn for regression and classification; learn train/test splits, metrics and data leakage.'), ('Deep learning and AI apps', 'Try PyTorch basics, then build a small app using a pretrained model. Learn evaluation, privacy and responsible AI.'), ('Portfolio and opportunities', 'Publish two documented projects, deploy one, and prepare Python, SQL and ML interview questions. Apply for internships.')],
  'hi': [('बुनियाद', 'Python, बीजगणित, प्रायिकता और बुनियादी सांख्यिकी सीखें।'), ('डेटा पर काम', 'NumPy, pandas, डेटा की सफ़ाई और विज़ुअलाइज़ेशन का अभ्यास करें।'), ('मशीन लर्निंग', 'scikit-learn से regression और classification करें। Train/test split, metrics और data leakage समझें।'), ('डीप लर्निंग और AI ऐप', 'PyTorch की बुनियाद सीखें और pretrained model से छोटा ऐप बनाएँ। मूल्यांकन, गोपनीयता और ज़िम्मेदार AI समझें।'), ('पोर्टफ़ोलियो और अवसर', 'दो प्रोजेक्ट दस्तावेज़ों सहित प्रकाशित करें, एक deploy करें और Python, SQL व ML के इंटरव्यू प्रश्नों का अभ्यास करें। इंटर्नशिप के लिए आवेदन करें।')]},
 'Data Analyst': {
  'aliases': ['data analyst', 'data analytics', 'डेटा एनालिस्ट', 'डेटा विश्लेषक'],
  'en': [('Foundations', 'Learn spreadsheets, descriptive statistics and analytical thinking.'), ('Query data', 'Practice SQL filtering, joins, grouping and window functions.'), ('Analyze', 'Use Python and pandas to clean data and answer business questions.'), ('Communicate', 'Build clear charts and a dashboard; explain findings and limitations.'), ('Portfolio and opportunities', 'Publish two analyses with reproducible steps and practice SQL interviews. Apply for entry-level roles.')],
  'hi': [('बुनियाद', 'स्प्रेडशीट, वर्णनात्मक सांख्यिकी और विश्लेषणात्मक सोच सीखें।'), ('डेटा क्वेरी', 'SQL में filtering, joins, grouping और window functions करें।'), ('विश्लेषण', 'Python और pandas से डेटा साफ़ करें और व्यावसायिक सवालों के उत्तर निकालें।'), ('प्रस्तुति', 'स्पष्ट चार्ट और dashboard बनाएँ। निष्कर्ष और सीमाएँ समझाएँ।'), ('पोर्टफ़ोलियो और अवसर', 'दो विश्लेषण उनके चरणों सहित प्रकाशित करें। SQL इंटरव्यू का अभ्यास करें और शुरुआती भूमिकाओं के लिए आवेदन करें।')]},
 'Python Developer': {
  'aliases': ['python developer', 'software', 'web developer', 'backend', 'पाइथन', 'पायथन', 'सॉफ्टवेयर', 'python'],
  'en': [('Foundations', 'Learn Python syntax, functions, collections and error handling.'), ('Developer tools', 'Practice Git, virtual environments, debugging and automated tests.'), ('Backend skills', 'Learn HTTP, APIs, FastAPI or Django, and SQL databases.'), ('Build and deploy', 'Build a task manager with validation and tests. Deploy it without exposing secrets.'), ('Portfolio and opportunities', 'Document your project, practice data structures and Python interviews, and apply for internships.')],
  'hi': [('बुनियाद', 'Python syntax, functions, collections और error handling सीखें।'), ('डेवलपर टूल', 'Git, virtual environments, debugging और automated tests का अभ्यास करें।'), ('बैकएंड कौशल', 'HTTP, API, FastAPI या Django और SQL डेटाबेस सीखें।'), ('बनाएँ और deploy करें', 'Validation और tests के साथ task manager बनाएँ। Secrets उजागर किए बिना deploy करें।'), ('पोर्टफ़ोलियो और अवसर', 'प्रोजेक्ट के दस्तावेज़ बनाएँ, data structures व Python इंटरव्यू का अभ्यास करें और इंटर्नशिप के लिए आवेदन करें।')]}
}


def career_reply(question, language='en', results=None):
    from roadmaps import find_path, render_path
    pathway = find_path(question)
    if pathway:
        return render_path(pathway, language)
    hi = language == 'hi'
    q = question.casefold()
    role = next((name for name, data in ROADS.items() if any(
        re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', q)
        for alias in data['aliases'])), None)
    if not role:
        return ('मैं tech careers, कक्षा 10/12, NEET, CAT, CA और प्रमुख परीक्षा समूहों के मार्ग दे सकता हूँ। मार्ग का नाम पूछें या परीक्षा रोडमैप में पूरी सूची देखें।' if hi else
                'I currently support tech careers plus Class 10/12, NEET, CAT, CA and major exam families. Ask for a named pathway, or browse Exam roadmaps for the full list.')
    lines = [f'### {role}', 'यह कौशल-आधारित मार्गदर्शन है, नौकरी या समय-सीमा की गारंटी नहीं।' if hi else 'A skills-based guide, not a job or timeline guarantee.']
    for i, (title, body) in enumerate(ROADS[role][language], 1):
        lines.append(f'**{i}. {title}**\n\n{body}')
    if results:
        weak = ', '.join(r.topic for r in analyze(results) if r.level == 'Weak')
        if weak:
            lines.append(('**आपकी पढ़ाई का संकेत:** ' + weak + ' में अंक कम हैं। करियर तैयारी के साथ अपने अध्ययन प्लान में इनकी दोहराई रखें।' if hi else '**Your study signal:** Lower scores in ' + weak + '. Keep reviewing these in your study plan alongside career preparation.'))
    lines.append('**आज का कदम:** पहले चरण का 30 मिनट अभ्यास करें और अपने नोट्स लिखें।' if hi else '**Start today:** Spend 30 minutes on step one and write down what you learned.')
    return '\n\n'.join(lines)
