"""Presentation layer rendered entirely from Python; no external assets or JS."""
import streamlit as st


def apply_design():
    st.markdown('''<style>
    :root { --ink:#20243e; --muted:#73798f; --purple:#7054de; }
    .stApp { background:#f5f6fb; color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(245,246,251,.94); }
    .block-container { max-width:1160px; padding:2rem 2.7rem 4rem; }
    h1,h2,h3 { letter-spacing:-.035em; color:var(--ink); }
    h3 { font-size:1.45rem !important; }
    [data-testid="stSidebar"] { background:#181c36; border-right:0; }
    [data-testid="stSidebar"] * { color:#e9eafb; }
    [data-testid="stSidebar"] [data-testid="stAlert"] { background:#252a49; border:1px solid #393f61; border-radius:16px; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:#b7bdd7; font-size:.8rem; line-height:1.7; }
    [data-testid="stSidebar"] [data-testid="stRadio"] { margin:20px 0; }
    .brand { font-weight:800; letter-spacing:-1px; font-size:28px; display:flex; align-items:center; gap:10px; margin:6px 0 3px; }
    .brand-mark { background:#9077f4; color:white; border-radius:13px; padding:3px 12px; }
    .brand-note { font-size:10px; letter-spacing:2.4px; color:#9ba4c9 !important; margin:10px 0 32px; }
    .sidebar-label { font-size:10px; letter-spacing:2px; color:#8e98bd !important; margin:24px 0 12px; }
    .side-step { padding:12px 14px; border-radius:10px; color:#c6cce3 !important; font-size:13px; margin:5px 0; background:#202541; }
    .side-step span { color:#ad96ff !important; margin-right:12px; }
    .topline { display:flex; justify-content:space-between; align-items:center; margin:0 0 24px; }
    .eyebrow { font-size:10px; font-weight:700; letter-spacing:2px; color:#7c8097; }
    .top-title { font-size:24px; font-weight:750; letter-spacing:-.7px; margin-top:5px; }
    .pill { border:1px solid #e0dbee; border-radius:30px; padding:8px 14px; font-size:11px; color:#665390; background:#fff; }
    .hero { background:linear-gradient(115deg,#27234d 0%,#463783 65%,#6c54b3 100%); border-radius:24px; padding:36px 38px; position:relative; overflow:hidden; display:flex; align-items:center; justify-content:space-between; gap:24px; box-shadow:0 14px 30px #33226913; }
    .hero-copy { z-index:1; max-width:560px; }
    .hero-tag { display:inline-block; font-size:10px; letter-spacing:1.8px; color:#e1d8ff; border:1px solid #ffffff30; border-radius:20px; padding:7px 12px; margin-bottom:18px; }
    .hero h1 { font-size:39px !important; line-height:1.17; font-weight:750; color:#fff; margin:0 0 16px; padding:0; }
    .hero h1 em { font-style:normal; color:#c7b6ff; }
    .hero p { color:#dad5ef; font-size:14px; line-height:1.8; margin:0; max-width:475px; }
    .hero-foot { color:#c5b6ed; font-size:11px; margin-top:24px; letter-spacing:.3px; }
    .orbit { width:235px; height:215px; position:relative; flex-shrink:0; }
    .orbit-ring { border:1px solid #ffffff21; position:absolute; border-radius:50%; width:210px; height:210px; left:10px; top:0; }
    .orbit-ring.inner { width:155px; height:155px; left:38px; top:28px; border-style:dashed; }
    .book { position:absolute; left:58px; top:64px; font-size:65px; transform:rotate(-10deg); filter:drop-shadow(0 12px 10px #17102d55); }
    .float-card { position:absolute; background:#fff; border-radius:12px; padding:10px 14px; box-shadow:0 10px 25px #19112e25; font-size:11px; font-weight:650; color:#46367f; }
    .float-card.one { top:14px; left:-15px; transform:rotate(-7deg); }
    .float-card.two { bottom:15px; right:-5px; transform:rotate(5deg); }
    .spark { position:absolute; right:13px; top:42px; color:#f6d485; font-size:27px; }
    .feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:15px; margin:22px 0 30px; }
    .feature { background:white; border:1px solid #e9eaf3; border-radius:16px; padding:18px; display:flex; gap:13px; align-items:center; }
    .feature-icon { background:#efeafe; color:#7759db; border-radius:12px; width:43px; height:43px; display:flex; align-items:center; justify-content:center; font-size:20px; flex-shrink:0; }
    .feature:nth-child(2) .feature-icon { background:#e7f5ef; color:#23866b; }
    .feature:nth-child(3) .feature-icon { background:#fff2dd; color:#a47928; }
    .feature strong { font-size:13px; display:block; color:#30334c; }
    .feature small { color:#7c8196; font-size:11px; display:block; margin-top:3px; }
    [data-baseweb="tab-list"] { gap:8px; background:#eaeaf4; border-radius:14px; padding:6px; margin-bottom:24px; overflow-x:auto; }
    [data-baseweb="tab"] { border-radius:10px; padding:12px 16px; height:auto; color:#69708b; flex:1; white-space:nowrap; }
    [data-baseweb="tab"] p { font-size:12px; font-weight:650; }
    [data-baseweb="tab"][aria-selected="true"] { background:white; color:#6c4bcc; box-shadow:0 2px 6px #2520440e; }
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none; }
    [data-testid="stForm"] { background:#fff; border:1px solid #e4e5f0; border-radius:18px; padding:24px; }
    [data-testid="stExpander"] { background:#fff; border-radius:14px; border:1px solid #e7e8f1; overflow:hidden; }
    [data-testid="stButton"] button, [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button { border-radius:10px; font-weight:650; padding:8px 18px; transition:transform .15s; }
    button[kind="primary"] { background:#7153d7; border:1px solid #7153d7; color:white; box-shadow:0 5px 12px #7153d725; }
    button[kind="primary"]:hover { background:#5d40bd; border-color:#5d40bd; transform:translateY(-1px); color:white; }
    [data-testid="stAlert"] { border-radius:12px; }
    [data-testid="stChatMessage"] { background:white; border:1px solid #e8e8f3; border-radius:16px; }
    [data-testid="stTextInput"] input { border-radius:10px; }
    [data-testid="stCaptionContainer"] { color:#727991; }
    .page-footer { margin-top:38px; border-top:1px solid #e4e5ef; padding-top:20px; color:#9095aa; font-size:11px; text-align:center; }
    @media(max-width:900px) { .orbit { display:none; } .hero h1 { font-size:32px !important; } .block-container { padding:1.5rem; } }
    @media(max-width:600px) { .feature-grid { grid-template-columns:1fr; gap:8px; } .feature { padding:12px 16px; } .hero { padding:25px; } .hero h1 { font-size:28px !important; } .pill { display:none; } [data-baseweb="tab"] { padding:10px; } }
    </style>''', unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown('''<div class="brand"><span class="brand-mark">↗</span> StudyPath</div><div class="brand-note">YOUR NEXT CHAPTER STARTS HERE</div>''', unsafe_allow_html=True)


def dashboard_header(hi=False):
    def t(en, hindi): return hindi if hi else en
    st.markdown(f'''<div class="topline"><div><div class="eyebrow">{t('YOUR LEARNING SPACE','आपकी पढ़ाई की जगह')}</div><div class="top-title">{t('Let’s make progress.','आइए, आगे बढ़ें।')}</div></div><div class="pill">● &nbsp; {t('Your pace. Your path.','आपकी गति। आपका रास्ता।')}</div></div>
    <div class="hero"><div class="hero-copy"><div class="hero-tag">{t('SMALL STEPS. BIG POSSIBILITIES.','छोटे कदम। बड़ी संभावनाएँ।')}</div><h1>{t('A clearer plan.<br>A <em>brighter future.</em>','एक स्पष्ट योजना।<br>एक <em>बेहतर भविष्य।</em>')}</h1><p>{t('Turn your weak topics into strengths. Build a study routine that works for you, and discover where your next chapter could lead.','कमज़ोर विषयों को अपनी ताकत बनाएँ। अपने लिए सही अध्ययन दिनचर्या बनाएँ और आगे की पढ़ाई व करियर का रास्ता खोजें।')}</p><div class="hero-foot">{t('ASSESS &nbsp; → &nbsp; PLAN &nbsp; → &nbsp; EXPLORE &nbsp; → &nbsp; GROW','जाँचें &nbsp; → &nbsp; योजना बनाएँ &nbsp; → &nbsp; खोजें &nbsp; → &nbsp; आगे बढ़ें')}</div></div><div class="orbit" aria-hidden="true"><div class="orbit-ring"></div><div class="orbit-ring inner"></div><div class="book">📚</div><div class="float-card one">✦ &nbsp; {t('Made for your goals','आपके लक्ष्य के लिए')}</div><div class="spark">✧</div><div class="float-card two">↗ &nbsp; {t('One step at a time','एक-एक कदम आगे')}</div></div></div>
    <div class="feature-grid"><div class="feature"><div class="feature-icon">◎</div><div><strong>{t('Find your focus','अपना फ़ोकस पहचानें')}</strong><small>{t('Marks & quick assessments','अंक और छोटी प्रश्नोत्तरी')}</small></div></div><div class="feature"><div class="feature-icon">▦</div><div><strong>{t('Study with a plan','योजना के साथ पढ़ें')}</strong><small>{t('A routine built around you','आपके अनुसार दिनचर्या')}</small></div></div><div class="feature"><div class="feature-icon">↗</div><div><strong>{t('Explore 16 pathways','16 मार्गों को जानें')}</strong><small>{t('School, exams & what comes next','स्कूल, परीक्षाएँ और आगे का रास्ता')}</small></div></div></div>''', unsafe_allow_html=True)
    st.sidebar.markdown(f'''<div class="sidebar-label">{t('HOW IT WORKS','कैसे शुरू करें')}</div><div class="side-step"><span>01</span>{t('Understand your strengths','अपनी तैयारी समझें')}</div><div class="side-step"><span>02</span>{t('Make time for progress','प्रगति के लिए समय निकालें')}</div><div class="side-step"><span>03</span>{t('Discover your direction','अपनी दिशा खोजें')}</div><div class="sidebar-label">{t('ABOUT THIS MENTOR','इस मेंटर के बारे में')}</div>''', unsafe_allow_html=True)


def footer(hi=False):
    st.markdown('<div class="page-footer">StudyPath &nbsp; / &nbsp; '+('सोच-समझकर पढ़ें। आत्मविश्वास के साथ आगे बढ़ें।' if hi else 'Learn with intention. Move forward with confidence.')+'</div>', unsafe_allow_html=True)
