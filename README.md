# StudyPath — Study + Career Mentor

A small Python-only Streamlit application with an English/Hindi interface. No custom JavaScript, API keys, ML training or database.

## Run

Python 3.10+ recommended.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features

1. **Weakness detection:** enter topic-level marks and maximum marks, or complete a six-question objective quiz. Below 60% is weak, 60–79.9% developing, 80%+ strong. Sample marks are editable demonstration data, not a real student assessment.
2. **Study plan:** choose 1–30 days and 30–360 minutes daily. Weighted scheduling prioritizes lower scores while revisiting stronger topics. Blocks rotate through review, practice and self-testing. Five-minute breaks are included within the daily budget. Download a UTF-8 CSV timetable. Times are minutes relative to your study start, not fixed clock appointments.
3. **Career mentor:** Hindi, English and common Hinglish queries route to curated AI Engineer, Data Analyst or Python Developer roadmaps. Responses follow the selected interface language. Also routes named school/exam questions to the roadmap library. Unsupported questions receive a clear scope message.

## Honest scope

This is a **rule-based prototype**, not a generative AI or trained diagnostic model. Career replies use keyword routing and curated content, not unrestricted conversation or follow-up reasoning. It does not grade free-text answers or infer specific misconceptions from a single overall subject mark. Enter granular topic names for more useful plans. The tiny quiz provides only a rough practice signal. Topic names entered by the user are preserved, not translated. Career advice does not guarantee employment or completion dates.

Data is kept in Streamlit session memory; refreshing/disconnecting can reset it. The app makes no external AI calls and writes no student records to disk. Avoid personal information on a publicly shared demo. A production deployment would need authentication and a privacy/security review.

## Files

- `app.py`: interface, assessment forms, downloads and chat
- `mentor.py`: scoring, scheduling, quiz and bilingual roadmaps
- `test_mentor.py`: validation, thresholds, scheduling and language tests

```bash
python -m unittest -v
```


## New: Exam roadmap library

A fourth tab adds 16 bilingual pathways: Class 10, Class 12, NEET UG, CAT/MBA, CA, UPSC civil services, SSC, banking, railways, NDA, CDS/AFCAT, police/CAPF/Agniveer, teaching/TET, state services, engineering/PSU and UGC/CSIR NET. Exam families contain representative examples, not exhaustive post-level guides. Search, category filtering and individual Markdown downloads are included. School/entrance/professional qualifications are explicitly distinguished from government recruitment.

Each guide includes overview, typical entry, stages, subjects, suggested preparation, official links and a verification status. Browsing does not alter student marks. Use topic-level marks in the existing assessment to personalize the daily timetable.

### Current-information limitations

This is a manually researched snapshot checked on **17 September 2026**, not an automatic live feed. CAT dates and detailed eligibility were verified in the official portal/PDF. CBSE, ICAI, SSC and IBPS cards report only verified index/notice-board entries; NEET reports a verified syllabus notice. Underlying full notifications, current eligibility and deadlines were not verified for all pathways. Other cards explicitly say their current details are unverified. No claim is made that all applications are open. Follow amendments on the linked official sites before acting.

The source URLs and bilingual verification notes live in `roadmaps.py`; update them manually when notices change. Add another pathway with `add(...)` and provide all five content fields in both languages. `test_roadmaps.py` tests catalog integrity and query routing. The app still has no trained or generative AI model.

## Visual refresh

`design.py` contains Python-rendered embedded styling and bilingual dashboard components: navy sidebar, violet hero, feature cards, responsive layouts and restyled tabs/forms. No external fonts, image downloads, JavaScript or separate frontend build is required. `.streamlit/config.toml` supplies the light theme. Keep that hidden folder when copying the project. Existing scoring, timetable and roadmap logic is unchanged.

## Study Lab (offline, session-only)

The fifth tab adds:
- **Micro-tasks:** timed 5–10 minute actions with a concrete output (rules written, questions solved, errors corrected), completion checkboxes and budgeted breaks. Lower diagnostic scores receive more slots. The planner is deterministic, not a generative model.
- **Exam anchoring:** the sidebar target selects a small curated concept pack for each roadmap family. These packs are NOT comprehensive syllabi; Class 12, teaching, NET and technical families especially require the user's actual stream/post/subject syllabus.
- **Hinglish context:** chat remembers named exams and supported concepts, handles common task/explanation/panic intents and simple follow-ups. Changing the sidebar target resets chat context. Named exams in chat do not silently change the Study Lab target. This is limited intent routing, not general language understanding.
- **Quick diagnostics:** three fixed questions per concept, with answer feedback, session history and percentage-point change against the previous attempt on the same exam/concept. Repeated questions can inflate recall scores. This history is distinct from the original marks assessment; micro-plans use diagnostic scores, while the original timetable uses entered marks.
- **Panic Button:** instantly builds a shorter recall-focused plan using the user-entered exam date, up to three days and at most 90 minutes daily within the selected budget. For an exam today, an optional 15-minute plan warns to check reporting/travel time first. No readiness probability, full-syllabus coverage or pass guarantee is claimed.
- **Explain like I'm 15:** eight curated concept explanations (Algebra, Percentages, Probability, Cell Biology, Motion, Accounting Equation, Constitution, Number Patterns), using analogies, worked examples or distinctions, and common mistakes. Hindi mode uses Hinglish explanations.
- **Calendar/PDF:** both the original timetable and micro-task/panic plan export to `.ics` and PDF. Calendar starts use Asia/Kolkata and are encoded as UTC instants, with RFC 5545 escaping/folding. Import the file into your preferred calendar; the app does not directly access your calendar account. PDF and calendar activity text are English; non-Latin custom topic labels use a placeholder in PDF and remain intact in calendar/CSV. PDF uses ReportLab.

Progress stays in Streamlit session memory and may disappear on refresh/reconnection. Task completion is self-reported, not proof of mastery. Adjust controls and regenerate to update a saved micro-plan; a different plan has its own completion checklist. Dates are user input, not refreshed official notifications. Existing official-information snapshot remains dated 17 September 2026.

New files: `study_tools.py`, `lab_ui.py`, `test_study_tools.py`. No API keys, database, accounts or external AI service required.

## Download Centre

The sixth tab adds three English PDF downloads, generated in memory from current session state:
1. **Student report:** current marks/weak areas, selected-target diagnostic history with percentage-point changes, the matching saved micro/panic plan and its self-reported checklist, plus the selected roadmap. Missing data and plans belonging to another target are explicitly labelled. Original marks are not falsely mapped to the selected exam.
2. **Concept notes and practice sheets:** select one or more of the eight curated concepts. Each has an explanation, three fixed MCQs and working space. An optional answer-key section starts on a separate page. Questions are the same as Study Lab diagnostics, not unseen assessment material.
3. **Roadmap PDFs:** all 16 exam/study pathways and three tech-career guides. Exam PDFs preserve the dated verification notes and clickable official source links. Career guides are skills advice, not official recruitment notices.

PDFs include page numbers and generation timestamps. Non-Latin custom labels may be omitted because these downloads are English-only. No student PDF is saved on the server by the app. `downloads.py` implements the centre and `test_downloads.py` tests all download types. Full suite: 15 tests.
