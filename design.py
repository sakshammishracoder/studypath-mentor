"""Simple page headings using only built-in Streamlit components.

Streamlit creates the web page for us, so no HTML, CSS or JavaScript is needed
for this interface. Colours are set in .streamlit/config.toml.
"""
import streamlit as st


def sidebar_brand():
    st.sidebar.title("StudyPath")
    st.sidebar.caption("A Python + Streamlit project")
    st.sidebar.divider()


def dashboard_header(hi=False):
    st.title("StudyPath — Study & Career Mentor")

    if hi:
        st.write("अपने अंक जाँचें, पढ़ाई का प्लान बनाएँ और करियर के बारे में जानें।")
        instructions_title = "कैसे इस्तेमाल करें"
        instructions = [
            "अंक डालें या छोटी प्रश्नोत्तरी पूरी करें।",
            "अपने कमज़ोर विषय देखें और अध्ययन प्लान बनाएँ।",
            "करियर और परीक्षा रोडमैप देखें। Study Lab में अभ्यास करें।",
            "Downloads से PDF लें। प्रगति सेव करने के लिए लॉग इन करें।",
        ]
    else:
        st.write("Check your marks, plan your studies and explore career options.")
        instructions_title = "How to use this project"
        instructions = [
            "Enter your marks or take the short quiz.",
            "Check your weak topics and create a study plan.",
            "Explore career and exam roadmaps. Practise in Study Lab.",
            "Get PDFs from Downloads. Sign in if you want to save progress.",
        ]

    with st.expander(instructions_title):
        for number, instruction in enumerate(instructions, start=1):
            st.write(f"{number}. {instruction}")

    st.divider()


def footer(hi=False):
    st.divider()
    if hi:
        st.caption("Python • Streamlit • InsForge | सुझाव तय नियमों पर आधारित हैं, प्रशिक्षित AI मॉडल पर नहीं।")
    else:
        st.caption("Python • Streamlit • InsForge | Recommendations use rules, not a trained AI model.")
