"""On-demand English PDF downloads. No files or student data are stored on disk."""
from io import BytesIO
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
import re
import unicodedata
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from roadmaps import CATALOG, render_path
from mentor import ROADS
from study_tools import CONCEPTS
from cloud_ui import save_pdf_button, pdf_library


def english(text):
    text=str(text).replace('₹','Rs ').replace('→',' -> ').replace('−','-').replace('×',' x ').replace('↗','')
    text=''.join(c for c in text if not ('DEVANAGARI' in unicodedata.name(c,'')))
    text=text.encode('cp1252','replace').decode('cp1252')
    return re.sub(r'\s+/\s*(?=[?.,;:]|$)','',text).strip()


class Document:
    def __init__(self, title, subtitle):
        self.title=title
        self.styles=getSampleStyleSheet()
        self.styles.add(ParagraphStyle('Small',parent=self.styles['Normal'],fontSize=8,leading=11,wordWrap='CJK'))
        self.styles['Title'].textColor=colors.HexColor('#654ac6')
        self.styles['Title'].fontSize=26
        self.styles['Title'].leading=31
        self.styles['Heading2'].textColor=colors.HexColor('#292443')
        self.styles['Normal'].leading=15
        self.styles['Normal'].spaceAfter=7
        self.story=[]
        self.add('STUDYPATH / YOUR LEARNING DOWNLOAD', 'Heading4')
        self.add(title,'Title')
        self.add(subtitle)
        self.add('Generated '+datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d %B %Y, %H:%M IST'))
        self.story.append(Spacer(1,14))
    def add(self,text,style='Normal'):
        self.story.append(Paragraph(escape(english(text)),self.styles[style]))
    def link(self,label,url):
        if not url.startswith(('https://','http://')):return
        self.story.append(Paragraph(f'<link href="{escape(url)}" color="#654ac6">{escape(english(label))}</link>',self.styles['Normal']))
        self.add(url,'Small')
    def markdown(self,text):
        for line in text.splitlines():
            if not line.strip():continue
            links=re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)',line)
            if links:
                for label,url in links:self.link(label,url)
            else:
                heading=line.startswith('#')
                self.add(re.sub(r'^#+\s*','',line).replace('**',''), 'Heading2' if heading else 'Normal')
    def page(self):self.story.append(PageBreak())
    def finish(self):
        out=BytesIO()
        def footer(canvas,doc):
            canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#77738c'))
            canvas.drawString(40,25,'StudyPath | Offline guidance, not a guarantee of exam success')
            canvas.drawRightString(A4[0]-40,25,str(doc.page));canvas.restoreState()
        SimpleDocTemplate(out,pagesize=A4,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=45,title=self.title,author='StudyPath').build(self.story,onFirstPage=footer,onLaterPages=footer)
        return out.getvalue()


def practice_pdf(topics,answers=True):
    if not topics or any(k not in CONCEPTS for k in topics):raise ValueError('Select supported concepts.')
    d=Document('Concept notes & practice','Simple explanations, a short practice sheet and an optional separate answer key. These are fixed starter questions, not official exam papers.')
    for index,key in enumerate(topics):
        if index:d.page()
        item=CONCEPTS[key]
        d.add(english(item[0]).rstrip(' /'),'Heading1')
        d.add('Explain like I am 15','Heading2');d.add(item[1])
        d.add('Practice without looking at the answer key','Heading2')
        for i,(question,options,answer,reason) in enumerate(item[3],1):
            d.add(f'{i}. {question}','Heading3')
            for j,option in enumerate(options):d.add(f'{chr(65+j)}. {option}')
            d.add('Your answer: __________     Working / reason:')
            d.add('________________________________________________________________')
            d.story.append(Spacer(1,12))
    if answers:
        d.page();d.add('Answer key & explanations','Heading1')
        d.add('Retakes repeat these questions. Better scores can reflect memory, not new mastery.')
        for key in topics:
            item=CONCEPTS[key];d.add(item[0],'Heading2')
            for i,q in enumerate(item[3],1):
                d.add(f'{i}. {chr(65+q[1].index(q[2]))}. {q[2]} — {q[3].split(" / ")[0]}')
    return d.finish()


def roadmap_pdf(kind,ident):
    d=Document('Your roadmap','Preparation guidance with source/scope notes. Verify official target-year rules before applying.')
    if kind=='exam':
        entry=next(e for e in CATALOG if e['id']==ident)
        d.markdown(render_path(entry,'en'))
    elif kind=='career':
        d.add(ident,'Heading1')
        d.add('Curated skills roadmap, not a recruitment notice. No job offer, salary or completion timeline is guaranteed.')
        for i,(title,body) in enumerate(ROADS[ident]['en'],1):
            d.add(f'{i}. {title}','Heading2');d.add(body)
        d.add('Start today','Heading2');d.add('Spend 30 minutes practising a foundation skill. Keep a project notebook and review your next step weekly.')
    else:raise ValueError('Unknown roadmap type')
    return d.finish()


def report_pdf(exam,results,history,saved,completed):
    entry=next(e for e in CATALOG if e['id']==exam)
    d=Document('My learning report','Current loaded progress snapshot. Self-entered marks, short diagnostics and task completion are different signals; none predicts full-exam readiness.')
    d.add('Selected target: '+entry['title'],'Heading2')
    d.add('1. Assessment & weak areas','Heading1')
    d.add('These are the current marks/mini-quiz results from step 1. They are not automatically mapped to the selected exam. Below 60% = weak, 60–79.9% = developing, 80%+ = strong.')
    if not results:d.add('No marks assessment saved in your loaded progress. Complete step 1 to include scores.')
    for i,r in enumerate(results,1):
        label=english(r.topic)
        if not label:label=f'Custom topic {i} (non-Latin label omitted)'
        d.add(f'{label}: {r.marks:g}/{r.total:g} | {r.percent:g}% | {r.level}')
    if results and not any(r.level=='Weak' for r in results):d.add('No weak topics at this threshold. Keep reviewing lower-scoring topics.')
    d.add('2. Quick diagnostic progress','Heading1')
    local=[r for r in history if r['exam']==exam]
    d.add('Only this target is included. Three fixed questions per concept; retakes may measure recall. Change is measured in percentage points against the previous attempt on the same concept.')
    if not local:d.add('No diagnostic attempts for this target in your loaded progress.')
    previous={}
    for i,r in enumerate(local,1):
        change=f"{r['score']-previous[r['topic']]:+.1f} pp" if r['topic'] in previous else 'First attempt'
        d.add(f"Attempt {i} | {CONCEPTS[r['topic']][0]} | {r['score']:g}% | {change} | {r['time']} IST")
        previous[r['topic']]=r['score']
    d.add('3. Current micro-task / panic plan','Heading1')
    if not saved:d.add('No micro-task plan saved. Generate one in Study Lab to include it.')
    elif saved['exam']!=exam:d.add('The saved plan belongs to another target and is not included. Generate a plan for this target first.')
    else:
        tasks=saved['tasks'];sig=saved['signature']
        ids=[f'{sig}_{i}' for i,r in enumerate(tasks) if r['topic']!='break']
        count=sum(k in completed for k in ids)
        d.add(f"Mode: {'Panic / recall' if saved['panic'] else 'Normal'} | Daily start: {saved['clock'].strftime('%H:%M')} IST | Checked off: {count}/{len(ids)}")
        d.add('Completion is self-reported, not mastery. Task times are minutes after the daily start. Preserve sleep and check exam travel/reporting arrangements.')
        last_day=None
        for i,r in enumerate(tasks):
            if r['day']!=last_day:
                d.add(str(saved['start']+timedelta(days=r['day'])),'Heading2');last_day=r['day']
            status='Break' if r['topic']=='break' else 'Done' if f'{sig}_{i}' in completed else 'To do'
            d.add(f"[{status}] {r['start']}-{r['start']+r['minutes']} min: {r['en']}")
    d.page();d.add('4. Selected exam / study roadmap','Heading1');d.markdown(render_path(entry,'en'))
    return d.finish()


def render_downloads(exam,hi=False):
    def t(en,hindi):return hindi if hi else en
    st.subheader(t('Download PDFs','PDF डाउनलोड करें'))
    st.caption(t('Download Centre · Reports, practice sheets and roadmaps','डाउनलोड सेंटर · रिपोर्ट, अभ्यास और रोडमैप'))
    st.info(t('PDFs are in English, even in Hindi mode. Non-Latin custom labels may be omitted. Downloads are generated from loaded progress. Signed-in users may also save a private cloud copy using the Save button. Official exam information remains the dated snapshot shown in each guide, not live updates.', 'हिंदी mode में भी PDF English में हैं। गैर-Latin custom labels हट सकते हैं। फ़ाइल loaded progress से बनती है। लॉग इन करके Save बटन से निजी cloud copy रख सकते हैं। परीक्षा सूचना हर guide में दी गई तारीख का snapshot है, live update नहीं।'))
    with st.container(border=True):
        st.markdown('### '+t('01 · Complete student report','01 · पूरी छात्र रिपोर्ट'))
        st.write(t('Current assessment, weak areas, target-specific diagnostic history, saved task checklist and the selected roadmap in one PDF. Missing sections are labelled honestly.', 'एक PDF में वर्तमान अंक, कमज़ोर विषय, लक्ष्य के diagnostics, सेव checklist और चुना रोडमैप। खाली हिस्से स्पष्ट बताए जाते हैं।'))
        st.caption(t('Uses the sidebar study target. No name, email or personal details required.', 'साइडबार का पढ़ाई लक्ष्य उपयोग होगा। नाम, email या निजी जानकारी आवश्यक नहीं।'))
        # Direct download always reflects current state; no stale cached report.
        data=report_pdf(exam,st.session_state.results,st.session_state.diagnostic_history,st.session_state.lab_plan,st.session_state.task_completions)
        st.download_button(t('↓ Download student report · PDF','↓ छात्र रिपोर्ट डाउनलोड करें · PDF'),data,file_name=f'studypath_report_{exam}.pdf',mime='application/pdf',key='report_download')
        save_pdf_button(data, 'Student report - ' + exam, 'student_report')
    with st.container(border=True):
        st.markdown('### '+t('02 · Concept notes & practice','02 · Concept notes और अभ्यास'))
        chosen=st.multiselect(t('Choose concepts','Concept चुनें'),list(CONCEPTS),default=['algebra'],format_func=lambda k:CONCEPTS[k][0],key='pdf_concepts')
        include=st.checkbox(t('Include a separate answer-key section','अलग answer-key section जोड़ें'),True,key='pdf_answers')
        st.caption(t('Each concept includes a simple explanation, three multiple-choice questions and working space. The same questions are used in quick diagnostics.', 'हर concept में आसान explanation, तीन MCQ और उत्तर लिखने की जगह। यही प्रश्न quick diagnostics में हैं।'))
        if chosen:
            practice = practice_pdf(chosen,include)
            st.download_button(t('↓ Download practice pack · PDF','↓ अभ्यास पैक डाउनलोड करें · PDF'),practice,file_name='studypath_practice.pdf',mime='application/pdf',key='practice_download')
            save_pdf_button(practice, 'Practice pack - ' + ', '.join(chosen)[:120], 'practice_pack')
        else:st.warning(t('Select at least one concept to build a practice pack.','अभ्यास पैक के लिए कम-से-कम एक concept चुनें।'))
    with st.container(border=True):
        st.markdown('### '+t('03 · Exam & career roadmaps','03 · परीक्षा और करियर रोडमैप'))
        kind=st.radio(t('Roadmap type','रोडमैप प्रकार'),['exam','career'],format_func=lambda k:t('Exam / study pathway','परीक्षा / पढ़ाई मार्ग') if k=='exam' else t('Tech career','Tech career'),horizontal=True,key='pdf_kind')
        if kind=='exam':
            ident=st.selectbox(t('Exam / study pathway','परीक्षा / पढ़ाई मार्ग'),[e['id'] for e in CATALOG],index=[e['id'] for e in CATALOG].index(exam),format_func=lambda k:next(e['title'] for e in CATALOG if e['id']==k),key='pdf_exam')
        else:ident=st.selectbox(t('Career','करियर'),list(ROADS),key='pdf_career')
        roadmap = roadmap_pdf(kind,ident)
        st.download_button(t('↓ Download roadmap · PDF','↓ रोडमैप डाउनलोड करें · PDF'),roadmap,file_name='studypath_roadmap_'+re.sub(r'[^a-z0-9]+','_',ident.lower())+'.pdf',mime='application/pdf',key='roadmap_pdf_download')
        save_pdf_button(roadmap, 'Roadmap - ' + ident, 'roadmap')
    st.caption(t('Need a dated timetable or calendar? Use the existing PDF / .ics buttons in My study plan and Study Lab.', 'तारीख वाला टाइमटेबल या कैलेंडर चाहिए? मेरा अध्ययन प्लान और Study Lab के PDF / .ics बटन उपयोग करें।'))

    pdf_library()
