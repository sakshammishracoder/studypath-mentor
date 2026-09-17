import csv
import io
from datetime import date, timedelta, time
import streamlit as st
from mentor import Result, analyze, make_plan, career_reply, QUIZ
from roadmaps import CATALOG, render_path
from design import apply_design, sidebar_brand, dashboard_header, footer
from study_tools import context_reply
from lab_ui import init_lab, render_lab, scores_for, export_buttons
from downloads import render_downloads

st.set_page_config(page_title='StudyPath • Study + Career Mentor', page_icon='↗', layout='wide')
apply_design()
sidebar_brand()
init_lab()
lang = st.sidebar.radio('Language / भाषा', ['English', 'हिन्दी'])
hi = lang == 'हिन्दी'
def t(en, hindi):
    return hindi if hi else en
def target_changed():
    st.session_state.chat_exam = st.session_state.target_exam
    st.session_state.chat_topic = None
target_exam = st.sidebar.selectbox(t('Study target', 'पढ़ाई का लक्ष्य'), [e['id'] for e in CATALOG], format_func=lambda k: next(e['title'] for e in CATALOG if e['id']==k), key='target_exam', on_change=target_changed)
st.sidebar.caption(t('Anchors Study Lab tasks and new chat context. Starter topics only; not a full syllabus.', 'Study Lab के काम और नई chat context इस लक्ष्य से जुड़ते हैं। शुरुआती विषय, पूरा syllabus नहीं।'))
dashboard_header(hi)
st.sidebar.info(t('Offline prototype: transparent rules and curated career roadmaps, not a generative AI model. No API key needed.', 'ऑफ़लाइन प्रोटोटाइप: स्पष्ट नियम और तैयार करियर रोडमैप, जनरेटिव AI मॉडल नहीं। API key की ज़रूरत नहीं।'))
st.sidebar.caption(t('Scores stay in this session. Do not enter personal details. Refreshing may reset your work.', 'अंक इसी सत्र में रहते हैं। निजी जानकारी न डालें। पेज रिफ्रेश करने पर काम रीसेट हो सकता है।'))
if 'results' not in st.session_state:
    st.session_state.results = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
labels = [t('1 · Find weak topics', '1 · कमज़ोर विषय'), t('2 · My study plan', '2 · मेरा अध्ययन प्लान'), t('3 · Career mentor', '3 · करियर मेंटर'), t('4 · Exam roadmaps', '4 · परीक्षा रोडमैप'), t('5 · Study Lab', '5 · स्टडी लैब'), t('6 · Downloads', '6 · डाउनलोड')]
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(labels)
with tab1:
    st.subheader(t('Start with what you know', 'अपनी तैयारी जाँचें'))
    method = st.radio(t('Assessment', 'मूल्यांकन'), [t('Enter marks', 'अंक डालें'), t('Take a mini quiz', 'छोटी प्रश्नोत्तरी')], horizontal=True)
    if method == t('Enter marks', 'अंक डालें'):
        st.caption(t('Replace the sample marks with your own. Add or delete rows as needed.', 'उदाहरण के अंक अपने अंकों से बदलें। ज़रूरत पर पंक्तियाँ जोड़ें या हटाएँ।'))
        with st.form('marks'):
            rows = st.data_editor([{'Topic': 'Algebra', 'Marks': 40.0, 'Maximum': 100.0}, {'Topic': 'Probability', 'Marks': 55.0, 'Maximum': 100.0}, {'Topic': 'Python', 'Marks': 80.0, 'Maximum': 100.0}], num_rows='dynamic', hide_index=True, use_container_width=True,
                column_config={'Topic': st.column_config.TextColumn(t('Topic', 'विषय'), required=True), 'Marks': st.column_config.NumberColumn(t('Marks', 'प्राप्त अंक'), min_value=0, required=True), 'Maximum': st.column_config.NumberColumn(t('Maximum', 'पूर्णांक'), min_value=1, required=True)})
            submit = st.form_submit_button(t('Analyze my marks', 'मेरे अंकों का विश्लेषण करें'), type='primary')
        if submit:
            try:
                parsed = [Result(str(row['Topic'] or '').strip(), float(row['Marks']), float(row['Maximum'])) for row in rows]
                st.session_state.results = analyze(parsed)
                st.success(t('Assessment saved. Open My study plan next.', 'मूल्यांकन सेव हो गया। अब मेरा अध्ययन प्लान खोलें।'))
            except (ValueError, TypeError):
                st.error(t('Check every row: unique nonempty topic, positive maximum, and marks from 0 to maximum. Previous assessment is unchanged.', 'हर पंक्ति जाँचें: अलग और भरा हुआ विषय, धनात्मक पूर्णांक और 0 से पूर्णांक तक प्राप्त अंक। पिछला मूल्यांकन नहीं बदला है।'))
    else:
        st.caption(t('Six sample questions: two per topic. This is a small practice signal, not a complete assessment.', 'छह उदाहरण प्रश्न: हर विषय पर दो। यह अभ्यास का छोटा संकेत है, पूरा मूल्यांकन नहीं।'))
        with st.form('quiz'):
            answers = [st.radio(f'{i+1}. {q[2] if hi else q[1]}', q[3], index=None, key=f'q{i}') for i, q in enumerate(QUIZ)]
            checked = st.form_submit_button(t('Check answers', 'उत्तर जाँचें'), type='primary')
        if checked:
            if any(a is None for a in answers):
                st.warning(t('Answer all six questions first.', 'पहले सभी छह प्रश्नों के उत्तर दें।'))
            else:
                totals = {}
                for q, a in zip(QUIZ, answers):
                    pair = totals.setdefault(q[0], [0, 0])
                    pair[0] += int(a == q[4]); pair[1] += 1
                    st.write(('✓' if a == q[4] else '✗') + f' {q[2] if hi else q[1]} → {q[4]}')
                st.session_state.results = analyze([Result(topic, *scores) for topic, scores in totals.items()])
                st.success(t('Results saved. Your study plan is ready to generate.', 'नतीजे सेव हो गए। अब अध्ययन प्लान बनाएँ।'))
    results = st.session_state.results
    if results:
        st.divider()
        st.subheader(t('Your learning snapshot', 'आपकी तैयारी की झलक'))
        levels = {'Weak': t('Needs focus', 'अधिक ध्यान दें'), 'Developing': t('Developing', 'सुधार जारी'), 'Strong': t('Strong', 'मज़बूत')}
        st.caption(t('Below 60%: needs focus · 60–79.9%: developing · 80%+: strong', '60% से कम: अधिक ध्यान · 60–79.9%: सुधार जारी · 80%+: मज़बूत'))
        for r in results:
            st.progress(r.percent / 100, text=f'{r.topic} · {r.percent:g}% · {levels[r.level]}')
        if all(r.level != 'Weak' for r in results):
            st.success(t('No weak topics at this threshold. Keep strengthening your lower-scoring topics.', 'इस सीमा पर कोई कमज़ोर विषय नहीं। अपेक्षाकृत कम अंकों वाले विषयों का अभ्यास जारी रखें।'))
with tab2:
    st.subheader(t('A little progress, every day', 'हर दिन थोड़ी प्रगति'))
    results = st.session_state.results
    if not results:
        st.info(t('Complete a marks assessment or quiz in step 1 first.', 'पहले चरण 1 में अंक डालें या प्रश्नोत्तरी पूरी करें।'))
    else:
        a, b = st.columns(2)
        days = a.number_input(t('Days', 'दिन'), 1, 30, 7)
        minutes = b.slider(t('Daily minutes (including breaks)', 'रोज़ के मिनट (ब्रेक सहित)'), 30, 360, 120, 15)
        start = st.date_input(t('Start date', 'शुरुआत की तारीख'), value=date.today())
        st.caption(t('Lower scores receive more practice blocks. Each day fits your time budget, including short breaks. Times are relative to when you start studying.', 'कम अंक वाले विषयों को अधिक अभ्यास मिलता है। छोटे ब्रेक सहित रोज़ का प्लान तय समय में है। समय पढ़ाई शुरू करने के बाद के मिनट दर्शाता है।'))
        plan = make_plan(results, int(days), minutes)
        actions = [t('Review concepts + write a short summary', 'सिद्धांत दोहराएँ और संक्षिप्त नोट्स लिखें'), t('Solve practice questions + check mistakes', 'अभ्यास प्रश्न हल करें और गलतियाँ जाँचें'), t('Self-test without notes + review errors', 'बिना नोट्स टेस्ट दें और गलतियाँ सुधारें')]
        exported = []
        for day in range(1, int(days)+1):
            dt = start + timedelta(days=day-1)
            with st.expander(f'{t("Day", "दिन")} {day} · {dt:%d %b %Y}', expanded=day == 1):
                for block in (p for p in plan if p['day'] == day):
                    action = t('Take a break', 'छोटा ब्रेक लें') if block['phase'] == -1 else actions[block['phase']]
                    subject = block['topic'] or t('Break', 'ब्रेक')
                    interval = f"{block['start']}–{block['start']+block['minutes']}"
                    st.markdown(f'**{interval} {t("min", "मिनट")} · {subject}**  \n{action}')
                    exported.append([str(dt), interval, subject, action])
        buf = io.StringIO()
        writer = csv.writer(buf); writer.writerow(['Date', 'Minutes after start', 'Topic', 'Activity']); writer.writerows(exported)
        st.download_button(t('Download timetable · CSV', 'टाइमटेबल डाउनलोड करें · CSV'), ('\ufeff'+buf.getvalue()).encode('utf-8'), file_name='study_plan.csv', mime='text/csv')
        export_time = st.time_input(t('Calendar daily start · IST', 'कैलेंडर रोज़ शुरुआत · IST'), time(18,0), key='regular_export_time')
        english_actions = ['Review concepts and write a short summary.', 'Solve practice questions and check mistakes.', 'Self-test without notes and review errors.']
        export_tasks = [dict(day=p['day']-1, start=p['start'], minutes=p['minutes'], topic=p['topic'] or 'Break', en='Take a break.' if p['phase']==-1 else english_actions[p['phase']]) for p in plan]
        export_buttons(export_tasks, start, export_time, 'daily_timetable')

with tab3:
    st.subheader(t('Where do you want to go?', 'आप किस करियर की ओर जाना चाहते हैं?'))
    st.caption(t('Ask about tech careers, Class 10/12, NEET, CAT, CA or major exam families. Hindi, English and common Hinglish keywords are supported; use Exam roadmaps to browse. This is keyword-based, not open-ended chat.', 'Tech careers, कक्षा 10/12, NEET, CAT, CA या प्रमुख परीक्षा समूह पूछें। हिंदी, English और सामान्य Hinglish keywords समर्थित हैं। सभी विकल्प परीक्षा रोडमैप में देखें। यह keyword-based चैट है।'))
    st.caption(t('Try: “AI Engineer kaise bane?” or “How do I become a data analyst?”', 'उदाहरण: “AI Engineer kaise bane?” या “डेटा एनालिस्ट कैसे बनें?”'))
    st.caption(t('Try: NEET ke liye aaj kya karu? · cells samjhao · aur simple samjhao. Named exams update chat context; sidebar target controls Study Lab separately. Explanations cover only curated concepts.', 'पूछें: NEET ke liye aaj kya karu? · cells samjhao · aur simple samjhao. परीक्षा का नाम chat context बदलता है; sidebar लक्ष्य Study Lab के लिए है। केवल तैयार concepts समझाए जा सकते हैं।'))
    if st.button(t('Clear chat', 'चैट मिटाएँ')):
        st.session_state.messages = []
        st.session_state.chat_exam = target_exam
        st.session_state.chat_topic = None
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
    question = st.chat_input(t('Ask for a career roadmap…', 'करियर रोडमैप पूछें…'), max_chars=500)
    if question:
        with st.chat_message('user'):
            st.write(question)
        reply, new_exam, new_topic = context_reply(question, st.session_state.chat_exam, st.session_state.chat_topic, hi, scores_for(st.session_state.chat_exam))
        st.session_state.chat_exam, st.session_state.chat_topic = new_exam, new_topic
        reply = f"**Context: {next(e['title'] for e in CATALOG if e['id']==new_exam)}**\n\n" + reply
        with st.chat_message('assistant'):
            st.markdown(reply)
        st.session_state.messages.extend([{'role': 'user', 'content': question}, {'role': 'assistant', 'content': reply}])

with tab4:
    st.subheader(t('Find your next step', 'अपना अगला कदम चुनें'))
    st.caption(t('16 curated pathways covering school, entrance/professional qualifications and major government/public-sector exam families. Representative coverage, not every exam. School, NEET, CAT and CA are not government recruitment exams.', 'स्कूल, प्रवेश/professional qualifications और प्रमुख सरकारी/public-sector परीक्षा समूहों के 16 मार्ग। यह हर परीक्षा की सूची नहीं। स्कूल, NEET, CAT और CA सरकारी भर्ती परीक्षाएँ नहीं हैं।'))
    st.info(t('Current details are a manually checked snapshot dated 17 September 2026, not live notifications. Each guide states exactly what was verified. Only CAT has detailed current eligibility verified here; other guides use typical entry rules.', 'वर्तमान विवरण 17 सितंबर 2026 का manually checked snapshot है, live सूचना नहीं। हर guide में सत्यापन का दायरा है। यहाँ केवल CAT की विस्तृत वर्तमान पात्रता सत्यापित है; अन्य में सामान्य प्रवेश नियम हैं।'))
    search = st.text_input(t('Search exams or classes', 'परीक्षा या कक्षा खोजें'), placeholder='NEET, 10th, SSC, बैंक…')
    categories = ['All'] + list(dict.fromkeys(e['category'] for e in CATALOG))
    category_names = {'All':'सभी', 'School':'स्कूल', 'Entrance & professional':'प्रवेश और पेशेवर', 'Civil services':'सिविल सेवाएँ', 'SSC':'SSC', 'Banking & finance':'बैंकिंग और वित्त', 'Railways':'रेलवे', 'Defence & police':'रक्षा और पुलिस', 'Teaching':'शिक्षण', 'State services':'राज्य सेवाएँ', 'Technical & specialist':'तकनीकी और विशेषज्ञ'}
    category = st.selectbox(t('Category', 'श्रेणी'), categories, format_func=lambda c: category_names[c] if hi else c)
    matches = [e for e in CATALOG if (category == 'All' or e['category'] == category) and (not search.strip() or search.strip().casefold() in ' '.join([e['title'], *e['aliases'], *e['en'], *e['hi']]).casefold())]
    if not matches:
        st.warning(t('No matching guide. Clear the search or select All. A missing exam is not an eligibility decision.', 'कोई guide नहीं मिला। खोज हटाएँ या सभी चुनें। परीक्षा न मिलना पात्रता का निर्णय नहीं है।'))
    else:
        selected = st.selectbox(t('Choose a pathway', 'मार्ग चुनें'), [e['id'] for e in matches], format_func=lambda ident: next(e['title'] for e in matches if e['id']==ident))
        entry = next(e for e in matches if e['id']==selected)
        text = render_path(entry, 'hi' if hi else 'en')
        st.markdown(text)
        st.download_button(t('Download this roadmap', 'यह रोडमैप डाउनलोड करें'), text, file_name=f"roadmap_{selected}_{'hi' if hi else 'en'}.md", mime='text/markdown')
        st.caption(t('To personalize your timetable, enter marks for these syllabus topics in step 1, then open My study plan. Roadmap browsing does not overwrite your assessment.', 'निजी टाइमटेबल के लिए चरण 1 में इन विषयों के अंक डालें, फिर मेरा अध्ययन प्लान खोलें। रोडमैप देखने से आपका मूल्यांकन नहीं बदलता।'))

with tab5:
    render_lab(target_exam, hi)

with tab6:
    render_downloads(target_exam, hi)

footer(hi)
