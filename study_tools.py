"""Offline learning tools: curated concepts, transparent tasks, diagnostics and exports."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from hashlib import sha256
from io import BytesIO
import re

# Stable concept IDs tie questions, explanations and study tasks together.
CONCEPTS = {
 'algebra': ('Algebra / बीजगणित',
  'Think of an equation as a balanced weighing scale. Do the same operation to both sides to keep it balanced. For 2x + 6 = 14, subtract 6 from both sides: 2x = 8. Divide both sides by 2: x = 4. Check: 2×4 + 6 = 14. Common mistake: changing only one side. Try: 3x + 3 = 12; answer x = 3.',
  'Equation ko balanced tarazu samjho. Dono sides par same operation karo. 2x + 6 = 14 mein dono taraf 6 ghatao: 2x = 8. Dono taraf 2 se divide: x = 4. Check: 2×4 + 6 = 14. Galti: sirf ek side badalna. Try: 3x + 3 = 12; answer x = 3.',
  [('2x + 6 = 14: x = ?', ['2','4','6'], '4', 'Subtract 6, then divide by 2. / 6 ghatao, phir 2 se divide.'), ('3x = 15: x = ?', ['3','5','12'], '5', 'Divide both sides by 3. / Dono sides ko 3 se divide karo.'), ('x − 4 = 7: x = ?', ['3','11','28'], '11', 'Add 4 to both sides. / Dono sides mein 4 jodo.')]),
 'percent': ('Percentages / प्रतिशत',
  'Percent means out of 100. Imagine 100 equal squares: 20 shaded squares means 20%. To find 20% of 250, calculate 20/100 × 250 = 50. A 20% discount on ₹250 leaves ₹200. Common mistake: confusing the discount amount with the final price. Try: 10% of 80 = 8.',
  'Percent ka matlab har 100 mein. 100 squares mein 20 shaded ho to 20%. 250 ka 20% = 20/100 × 250 = 50. ₹250 par 20% discount ke baad price ₹200 hai. Galti: discount aur final price ko same samajhna. Try: 80 ka 10% = 8.',
  [('20% of / का 250?', ['25','50','200'], '50', '0.20 × 250 = 50.'), ('₹100, 10% discount: final price / अंतिम मूल्य?', ['₹10','₹90','₹110'], '₹90', '100 − 10 = 90.'), ('50 → 60: percentage increase / प्रतिशत वृद्धि?', ['10%','20%','60%'], '20%', '(60−50)/50 × 100 = 20%.')]),
 'probability': ('Probability / प्रायिकता',
  'Probability measures how likely something is, from 0 (impossible) to 1 (certain). With equally likely outcomes, use favourable outcomes divided by total outcomes. A fair die has six equally likely faces, so P(rolling 6) = 1/6. Common mistake: using this counting rule when outcomes are not equally likely. Try: P(even number) = 3/6 = 1/2.',
  'Probability batati hai koi event kitna likely hai: 0 impossible, 1 certain. Equally likely outcomes mein favourable / total karo. Fair die ke 6 faces: P(6) = 1/6. Galti: unequal chances mein bhi seedha counting rule lagana. Try: even number ke chances = 3/6 = 1/2.',
  [('Fair coin: P(heads) / निष्पक्ष सिक्का: P(चित)?', ['0','1/2','1'], '1/2', 'One favourable outcome out of two. / Do mein ek.'), ('Fair die: P(6) / निष्पक्ष पासा: P(6)?', ['1/6','1/2','1'], '1/6', 'One face out of six. / Chhah mein ek.'), ('Fair die: P(even) / P(सम संख्या)?', ['1/6','1/3','1/2'], '1/2', '2, 4, 6: 3/6 = 1/2.')]),
 'cells': ('Cell biology / कोशिका विज्ञान',
  'A cell is a tiny working unit of life. Imagine a factory: the membrane controls what crosses its boundary, ribosomes assemble proteins, and mitochondria help release usable energy in eukaryotic cells. The analogy is simplified: cells are chemical systems, not people operating machines. Common mistake: saying all cells have a nucleus; bacteria do not have a membrane-bound nucleus.',
  'Cell ko tiny factory samjho: membrane andar-bahar ka flow control karti hai, ribosomes proteins banate hain, aur eukaryotic cells mein mitochondria usable energy release karne mein madad karte hain. Yeh simple analogy hai, literal factory nahi. Galti: har cell mein nucleus hota hai; bacteria mein membrane-bound nucleus nahi hota.',
  [('Protein synthesis / प्रोटीन निर्माण?', ['Ribosome','Cell wall','Vacuole'], 'Ribosome', 'Ribosomes assemble proteins. / Ribosomes protein banate hain.'), ('Boundary controlling entry/exit / प्रवेश-निकास नियंत्रक?', ['Membrane','DNA','Ribosome'], 'Membrane', 'The cell membrane regulates transport. / Membrane transport regulate karti hai.'), ('Bacteria have a membrane-bound nucleus / बैक्टीरिया में झिल्ली-बद्ध केंद्रक?', ['Yes / हाँ','No / नहीं'], 'No / नहीं', 'Bacteria are prokaryotes. / Bacteria prokaryotes hain.')]),
 'motion': ('Motion / गति',
  'Speed is distance travelled per unit time, like kilometres in one hour. If you travel 100 metres in 20 seconds, average speed = 100/20 = 5 m/s. Velocity also includes direction and uses displacement. Common mistake: mixing kilometres and metres without conversion. Try: 60 metres in 10 seconds gives 6 m/s.',
  'Speed matlab ek unit time mein kitni distance. 100 metres ko 20 seconds mein cover kiya: average speed = 100/20 = 5 m/s. Velocity mein direction bhi hoti hai aur displacement use hota hai. Galti: km aur metres bina conversion mix karna. Try: 60 metres / 10 seconds = 6 m/s.',
  [('100 m / 20 s = ?', ['2 m/s','5 m/s','20 m/s'], '5 m/s', 'Speed = distance/time. / Speed = distance/time.'), ('1 km = ? m', ['10','100','1000'], '1000', 'Kilo means 1000. / Kilo = 1000.'), ('Velocity includes direction / वेग में दिशा होती है?', ['Yes / हाँ','No / नहीं'], 'Yes / हाँ', 'Velocity is a vector. / Velocity vector hai.')]),
 'accounting': ('Accounting equation / लेखांकन समीकरण',
  'A business owns resources (assets). These are funded by money owed (liabilities) or the owner’s claim (equity): Assets = Liabilities + Equity. If the owner puts ₹1,000 cash into a new business, assets and equity both rise by ₹1,000. Borrowing ₹500 adds both cash and a liability. Common mistake: treating a loan as income.',
  'Business ke resources assets hain. Funding ya to udhaar (liabilities) hai ya owner ka claim (equity): Assets = Liabilities + Equity. Owner ₹1,000 cash lagaye to assets aur equity dono ₹1,000 badhenge. ₹500 loan lene se cash aur liability badhti hai. Galti: loan ko income maanna.',
  [('Assets = / संपत्ति = ?', ['Liabilities + Equity','Income only','Liabilities − Equity'], 'Liabilities + Equity', 'This is the accounting equation. / Yeh accounting equation hai.'), ('Borrowed cash increases / नकद ऋण से बढ़ते हैं?', ['Assets and liabilities','Only profit','Only equity'], 'Assets and liabilities', 'Cash and loan obligation both rise. / Cash aur loan obligation dono badhte hain.'), ('Assets 1000, liabilities 400: equity?', ['400','600','1400'], '600', '1000 − 400 = 600.')]),
 'polity': ('Indian Constitution / भारतीय संविधान',
  'Think of the Constitution as the country’s basic rulebook. It sets institutions, powers and rights. The legislature makes laws, the executive implements them and courts interpret laws and review constitutionality within their jurisdiction. This is a simplified map: their roles interact through checks and balances. Common mistake: confusing Fundamental Rights with Fundamental Duties.',
  'Constitution ko desh ki basic rulebook samjho. Yeh institutions, powers aur rights define karta hai. Legislature laws banati hai, executive implement karti hai, courts laws interpret karti hain aur apne jurisdiction mein constitutionality review karti hain. Roles checks and balances se connected hain. Galti: Fundamental Rights aur Duties ko mix karna.',
  [('Union legislature / संघ की विधायिका?', ['Parliament','RBI','Election Commission'], 'Parliament', 'Parliament is the Union legislature. / Parliament sangh ki vidhayika hai.'), ('Fundamental Rights: Part / भाग?', ['III','IV','IVA'], 'III', 'Part III: Fundamental Rights. / Bhag III: Fundamental Rights.'), ('Directive Principles: Part / नीति निदेशक तत्व?', ['II','IV','IVA'], 'IV', 'Part IV contains Directive Principles. / Bhag IV mein Directive Principles hain.')]),
 'reasoning': ('Number patterns / संख्या क्रम',
  'A number pattern is a proposed rule connecting numbers. In 2, 4, 6, 8, a simple rule is add 2, so the next term is 10. Check every gap before choosing a rule. A short sequence can fit many rules; exam questions usually intend a simple one. Common mistake: checking only the first two terms.',
  'Number pattern mein numbers ko jodne wala rule dhoondho. 2, 4, 6, 8 mein simple rule +2, to agla 10. Har gap check karo. Chhoti sequence ke multiple rules ho sakte hain; exam mein usually simple intended rule hota hai. Galti: sirf pehle do numbers check karna.',
  [('2, 4, 6, 8, ? (add 2 / +2)', ['9','10','12'], '10', '8 + 2 = 10.'), ('3, 6, 12, ? (double / दुगुना)', ['15','18','24'], '24', '12 × 2 = 24.'), ('10, 8, 6, ? (subtract 2 / −2)', ['2','4','5'], '4', '6 − 2 = 4.')]),
}
ANCHORS = {
 '10':['algebra','motion','probability'], '12':['algebra','probability','motion'],
 'neet':['cells','motion'], 'cat':['percent','algebra','probability'],
 'ca':['accounting','percent'], 'upsc':['polity','percent'],
 'ssc':['percent','reasoning','algebra'], 'bank':['percent','reasoning'],
 'rail':['reasoning','motion','percent'], 'nda':['algebra','motion'],
 'cds':['percent','polity'], 'police':['reasoning','polity'],
 'teach':['algebra','percent'], 'state':['polity','percent'],
 'technical':['motion','algebra'], 'net':['reasoning','percent'],
}

def micro_plan(exam, scores=None, days=3, minutes=60, panic=False):
    if exam not in ANCHORS or not 1 <= days <= 30 or not 15 <= minutes <= 360:
        raise ValueError('Invalid plan settings')
    scores = scores or {}
    topics = sorted(ANCHORS[exam], key=lambda k: scores.get(k, 50))
    weights = [max(10,100-scores.get(k,50)) for k in topics]
    credits = [0]*len(topics)
    counts = {k:0 for k in topics}
    tasks=[]
    for day in range(days):
        elapsed=0
        while elapsed < minutes:
            duration=min(10,minutes-elapsed)
            for i,w in enumerate(weights): credits[i]+=w
            ix=max(range(len(topics)),key=lambda i:credits[i])
            credits[ix]-=sum(weights)
            topic=topics[ix]
            phase=counts[topic]%3
            counts[topic]+=1
            count=max(1,duration//3)
            task_en=[f'Read one worked example of {CONCEPTS[topic][0].split(" / ")[0]}; write {count} key rules from memory.', f'Solve {count} questions on {CONCEPTS[topic][0].split(" / ")[0]} from your textbook or official past paper; mark each answer.', f'Redo {count} missed questions without notes; write one correction rule for each.'][phase]
            task_hi=[f'{CONCEPTS[topic][0]} का एक solved example पढ़ें; याद से {count} मुख्य नियम लिखें।', f'{CONCEPTS[topic][0]} के {count} प्रश्न अपनी किताब या आधिकारिक पुराने पेपर से हल करें; हर उत्तर जाँचें।', f'{count} गलत प्रश्न बिना नोट्स दोबारा करें; हर प्रश्न का एक सुधार नियम लिखें।'][phase]
            tasks.append(dict(day=day,start=elapsed,minutes=duration,topic=topic,en=task_en,hi=task_hi))
            elapsed+=duration
            if elapsed%30==0 and minutes-elapsed>=5:
                tasks.append(dict(day=day,start=elapsed,minutes=5,topic='break',en='Stand up, drink water and rest your eyes.',hi='उठें, पानी पिएँ और आँखों को आराम दें।'))
                elapsed+=5
    if panic:
        # Prioritize recall/error repair rather than introducing new content.
        for task in tasks:
            if task['topic']!='break':
                task['en']='Recall sprint: '+task['en'].replace('Read one worked example','Review one familiar worked example')
                task['hi']='त्वरित दोहराई: '+task['hi']
    return tasks


def explain(topic, hi=False):
    item=CONCEPTS[topic]
    return f'### {item[0]}\n\n{item[2] if hi else item[1]}'


def context_reply(question, exam, topic=None, hi=False, scores=None):
    from roadmaps import find_path, render_path
    from mentor import career_reply
    found=find_path(question)
    if found and found['id'] != exam:
        exam=found['id']; topic=None; scores={}
    matched_topic=False
    q=question.casefold()
    for key,item in CONCEPTS.items():
        aliases=[key, *item[0].lower().split(' / ')]
        if any(re.search(r'(?<!\w)'+re.escape(a)+r'(?!\w)',q) for a in aliases):
            topic=key; matched_topic=True
    if any(x in q for x in ['explain','samjha','samajh','eli15','समझा','समझ','easy','simple']):
        followup = q.strip(' ?!.') in ['aur simple samjhao','aur samjhao','dobara samjhao','explain again','explain it','explain this','samjhao','simple samjhao','और समझाओ','फिर समझाओ']
        if topic is None or (not matched_topic and not followup):
            return ('कौन सा concept? Study Lab में समर्थित विषय चुनें।' if hi else 'Which concept? Choose a supported topic in Study Lab.'),exam,topic
        return explain(topic,hi),exam,topic
    if any(x in q for x in ['panic','ghabra','kal exam','kal paper','tension','घबरा','कल परीक्षा']):
        return ('Study Lab का Panic Button दबाएँ। तारीख जाँचें; यह केवल चुने हुए विषयों की दोहराई है, पूरी परीक्षा की readiness नहीं।' if hi else 'Use the Panic Button in Study Lab for an immediate recall plan. Check your exam date; this covers selected topics, not full-exam readiness.'),exam,topic
    if any(x in q for x in ['aaj','today','task','plan','weak','कमज़ोर','आज','revision']):
        rows=micro_plan(exam,scores,1,30)
        title='आज के छोटे काम' if hi else 'Today’s micro-tasks'
        return '### '+title+'\n\n'+'\n\n'.join(f"- {r['minutes']} min: {r['hi' if hi else 'en']}" for r in rows),exam,topic
    if found:
        return render_path(found,'hi' if hi else 'en'),exam,topic
    if topic:
        if any(x in q for x in ['aur','again','dobara','फिर']): return explain(topic,hi),exam,topic
    return career_reply(question,'hi' if hi else 'en'),exam,topic


def calendar_bytes(tasks, start_date, start_time, title='StudyPath'):
    def esc(s): return str(s).replace('\\','\\\\').replace('\n','\\n').replace(';','\\;').replace(',','\\,')
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//StudyPath//Study Planner//EN','CALSCALE:GREGORIAN']
    now=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    origin=datetime.combine(start_date,start_time,tzinfo=ZoneInfo('Asia/Kolkata'))
    for task in tasks:
        begin=origin+timedelta(days=task['day'],minutes=task['start'])
        end=begin+timedelta(minutes=task['minutes'])
        uid=sha256((title+begin.isoformat()+task['en']).encode()).hexdigest()[:32]
        lines+=['BEGIN:VEVENT',f'UID:{uid}@studypath.local',f'DTSTAMP:{now}', 'DTSTART:'+begin.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'), 'DTEND:'+end.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'), 'SUMMARY:'+esc(title+' · '+task['topic']), 'DESCRIPTION:'+esc(task['en']), 'END:VEVENT']
    lines+=['END:VCALENDAR']
    # RFC 5545 folding measured in UTF-8 octets, preserving code points.
    folded=[]
    for line in lines:
        part=''
        for char in line:
            if len((part+char).encode())>75:
                folded.append(part); part=' '
            part+=char
        folded.append(part)
    return ('\r\n'.join(folded)+'\r\n').encode()


def pdf_bytes(tasks,start_date,title='StudyPath plan'):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from xml.sax.saxutils import escape
    out=BytesIO(); doc=SimpleDocTemplate(out,title=title)
    styles=getSampleStyleSheet(); styles['Title'].textColor=colors.HexColor('#7054de')
    # English PDF is deliberate: no unreliable Devanagari shaping/font assumptions.
    story=[Paragraph(escape(title),styles['Title']),Paragraph('Offline practice plan. Not a prediction of exam success. Times are minutes after your daily start. Includes breaks. Use the official syllabus for complete coverage.',styles['Normal']),Spacer(1,16)]
    for day in sorted({r['day'] for r in tasks}):
        story.append(Paragraph((start_date+timedelta(days=day)).isoformat(),styles['Heading2']))
        for r in [r for r in tasks if r['day']==day]:
            label = r['topic'] if str(r['topic']).isascii() else 'Custom topic (see calendar/CSV for original name)'
            text=f"{r['start']}-{r['start']+r['minutes']} min | {label}: {r['en']}"
            story.extend([Paragraph(escape(text),styles['Normal']),Spacer(1,8)])
    doc.build(story)
    return out.getvalue()
