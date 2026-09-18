from datetime import date, time, timedelta, datetime
from zoneinfo import ZoneInfo
from hashlib import sha256
import streamlit as st
from study_tools import CONCEPTS, ANCHORS, micro_plan, explain, pdf_bytes, calendar_bytes


def init_lab():
    for key,default in [('diagnostic_history',[]),('task_completions',set()),('lab_plan',None),('chat_exam','10'),('chat_topic',None)]:
        if key not in st.session_state: st.session_state[key]=default


def scores_for(exam):
    scores={}
    for attempt in st.session_state.diagnostic_history:
        if attempt['exam']==exam: scores[attempt['topic']]=attempt['score']
    return scores


def export_buttons(tasks, start, clock, prefix):
    st.caption('Calendar uses Asia/Kolkata (IST). PDF and calendar task text are exported in English. Non-Latin custom topic names use a placeholder in PDF; calendar/CSV retain them. / PDF और कैलेंडर कार्य English में हैं।')
    one,two=st.columns(2)
    one.download_button('↓ Calendar · .ics',calendar_bytes(tasks,start,clock),file_name=f'{prefix}.ics',mime='text/calendar',key=prefix+'_ics')
    pdf = pdf_bytes(tasks,start)
    two.download_button('↓ Printable plan · PDF',pdf,file_name=f'{prefix}.pdf',mime='application/pdf',key=prefix+'_pdf')
    from cloud_ui import save_pdf_button
    save_pdf_button(pdf, 'Study plan - ' + str(start), prefix)


def render_lab(exam,hi=False):
    def t(en,hindi):return hindi if hi else en
    today=datetime.now(ZoneInfo('Asia/Kolkata')).date()
    st.subheader(t('Practice and revision', 'अभ्यास और दोहराई'))
    st.info(t('Anchored to your sidebar target. This offline starter pack covers only the concepts listed below—not the full syllabus. Class 12 and specialist families need your actual stream/post syllabus. Diagnostic scores are practice signals, not exam-readiness percentages.', 'साइडबार लक्ष्य से जुड़े शुरुआती concepts नीचे हैं, पूरा syllabus नहीं। कक्षा 12 और specialist समूहों के लिए अपना stream/post syllabus देखें। Diagnostic score अभ्यास का संकेत है, परीक्षा-readiness प्रतिशत नहीं।'))
    topic=st.selectbox(t('Focus concept','फ़ोकस concept'),ANCHORS[exam],format_func=lambda k:CONCEPTS[k][0],key='lab_topic_'+exam)
    if st.session_state.chat_topic is None:
        st.session_state.chat_topic=topic
    with st.expander(t('💡 Explain like I’m 15','💡 आसान भाषा में समझें'),expanded=False):
        st.markdown(explain(topic,hi))
        st.caption(t('Curated explanation; analogy is a simplification. Hindi mode uses natural Hinglish here.', 'तैयार explanation; analogy सरल उदाहरण है। हिंदी mode में यहाँ Hinglish है।'))
    st.markdown('### '+t('⚡ 3-question quick diagnostic','⚡ 3 प्रश्नों से छोटी जाँच'))
    st.caption(t('The same three questions repeat on retakes. Improvement may reflect recall; compare only the same concept and exam. No full-exam readiness prediction.', 'दोबारा वही तीन प्रश्न आएँगे। सुधार याद होने से भी हो सकता है; एक ही concept और परीक्षा की तुलना करें। पूरी परीक्षा की readiness का अनुमान नहीं।'))
    bank=CONCEPTS[topic][3]
    with st.form('diag_'+exam+'_'+topic):
        answers=[st.radio(q[0],q[1],index=None,key=f'diag_{exam}_{topic}_{i}') for i,q in enumerate(bank)]
        submitted=st.form_submit_button(t('Check & save progress','जाँचें और प्रगति सेव करें'),type='primary')
    if submitted:
        if any(a is None for a in answers):st.warning(t('Answer all three first.','पहले तीनों उत्तर दें।'))
        else:
            score=round(100*sum(a==q[2] for a,q in zip(answers,bank))/len(bank),1)
            st.session_state.diagnostic_history.append(dict(exam=exam,topic=topic,score=score,time=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')))
            for a,q in zip(answers,bank): st.write(('✓ ' if a==q[2] else '✗ ')+q[3])
            st.success(t('Attempt saved. Generate a new plan to use these scores.','प्रयास सेव हुआ। इन अंकों के लिए नया प्लान बनाएँ।'))
    history=[r for r in st.session_state.diagnostic_history if r['exam']==exam and r['topic']==topic]
    if history:
        c1,c2,c3=st.columns(3)
        c1.metric(t('Latest practice score','अंतिम अभ्यास स्कोर'),f"{history[-1]['score']}%")
        c2.metric(t('Change vs previous','पिछले से बदलाव'),f"{round(history[-1]['score']-history[-2]['score'],1):+g} pp" if len(history)>1 else '—')
        c3.metric(t('Saved attempts','सेव प्रयास'),len(history))
        st.dataframe([{'Attempt':i+1,'Score %':r['score'],'Time (IST)':r['time']} for i,r in enumerate(history)],hide_index=True)
    st.divider()
    st.markdown('### '+t('🎯 Your micro-task planner','🎯 छोटे-छोटे कामों का प्लान'))
    a,b,c=st.columns(3)
    days=a.number_input(t('Plan days','प्लान के दिन'),1,30,3,key='micro_days')
    minutes=b.slider(t('Minutes per day','रोज़ के मिनट'),15,180,60,15,key='micro_minutes')
    clock=c.time_input(t('Daily start · IST','रोज़ शुरुआत · IST'),time(18,0),key='micro_clock')
    exam_date=st.date_input(t('Your exam date (for panic plan)','आपकी परीक्षा की तारीख (panic plan)'),today+timedelta(days=7),min_value=today,key='panic_date')
    st.caption(t('This is your date, not an official deadline. Normal plans start today. Panic plans use up to three days before your date, at most 90 minutes/day from your budget; they do not cover the whole exam.','यह आपकी तारीख है, आधिकारिक deadline नहीं। सामान्य प्लान आज से। Panic plan तारीख से पहले अधिकतम 3 दिन, आपके budget से अधिकतम 90 मिनट/दिन; पूरी परीक्षा cover नहीं करता।'))
    normal,panic=st.columns(2)
    make=normal.button(t('Build actionable tasks','ठोस कामों का प्लान बनाएँ'),type='primary',key='build_micro')
    urgent=panic.button(t('🚨 1-click Panic Button','🚨 1-क्लिक Panic Button'),key='panic_build')
    if make or urgent:
        gap=(exam_date-today).days
        if urgent and gap==0:
            st.warning(t('Exam is today: check reporting time first. Skip study if travel/check-in is near. This optional 15-minute recall plan is not a last-minute full mock.', 'परीक्षा आज है: पहले reporting time देखें। यात्रा/check-in पास हो तो पढ़ाई छोड़ें। यह वैकल्पिक 15-मिनट recall है, पूर्ण mock नहीं।'))
        count=max(1,min(3,gap)) if urgent else int(days)
        budget=15 if urgent and gap==0 else min(minutes,90) if urgent else minutes
        tasks=micro_plan(exam,scores_for(exam),count,budget,urgent)
        signature=sha256(repr((exam,tasks,today,clock,urgent)).encode()).hexdigest()[:14]
        st.session_state.lab_plan=dict(tasks=tasks,exam=exam,start=today,clock=clock,panic=urgent,signature=signature,exam_date=exam_date)
    saved=st.session_state.lab_plan
    if saved and saved['exam']==exam:
        st.caption(t('Saved plan: controls above take effect only when you generate again. A new plan may reset its completion checklist.', 'सेव प्लान: ऊपर बदलाव नया प्लान बनाने पर लागू होते हैं। नए प्लान की checklist अलग हो सकती है।'))
        if saved['panic']:
            st.warning(t('Panic mode: prioritise familiar examples, errors and recall. Do not sacrifice sleep. Check admit card, ID, permitted materials, reporting time and route. There is no pass guarantee.', 'Panic mode: परिचित examples, गलतियाँ और recall पर ध्यान दें। नींद न छोड़ें। Admit card, ID, अनुमत सामान, reporting time और रास्ता जाँचें। पास होने की गारंटी नहीं।'))
        sig=saved['signature']; tasks=saved['tasks']
        for day in sorted({r['day'] for r in tasks}):
            with st.expander(f"{saved['start']+timedelta(days=day)} · {t('Micro-tasks','छोटे काम')}",expanded=day==0):
                for i,r in enumerate(tasks):
                    if r['day']!=day:continue
                    label=f"{r['start']}–{r['start']+r['minutes']} min · {r['hi' if hi else 'en']}"
                    if r['topic']=='break':st.caption(label);continue
                    ident=f'{sig}_{i}'
                    checked=st.checkbox(label,value=ident in st.session_state.task_completions,key='done_'+ident)
                    if checked:st.session_state.task_completions.add(ident)
                    else:st.session_state.task_completions.discard(ident)
        ids=[f'{sig}_{i}' for i,r in enumerate(tasks) if r['topic']!='break']
        complete=sum(i in st.session_state.task_completions for i in ids)
        st.progress(complete/len(ids),text=f"{complete}/{len(ids)} "+t('tasks checked off (self-reported, not mastery)','काम पूरे (स्वयं दर्ज, mastery नहीं)'))
        st.caption(f"Start: {saved['clock'].strftime('%H:%M')} IST · {len({r['day'] for r in tasks})} days")
        export_buttons(tasks,saved['start'],saved['clock'],'micro_plan')
    elif saved:st.caption(t('Your saved plan belongs to a different exam. Generate one for this target.','सेव प्लान दूसरी परीक्षा का है। इस लक्ष्य के लिए नया बनाएँ।'))
    if st.button(t('Reset diagnostic history','Diagnostic इतिहास रीसेट करें'),key='reset_diag'):
        st.session_state.diagnostic_history=[]
        st.rerun()
