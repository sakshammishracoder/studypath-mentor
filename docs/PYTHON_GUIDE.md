# Understanding StudyPath as a Python project

The interface uses standard Streamlit widgets. There is no custom HTML, CSS or JavaScript interface code. Streamlit turns Python function calls into a web page.

This guide explains the implementation; it is not a claim about who wrote every line. When presenting the project, describe the parts you understand, the libraries and services used, and any assistance you received accurately.

## 1. Start with the interface

Read `design.py` first. It uses familiar Python functions, `if` statements, lists and loops:

```python
import streamlit as st

st.title("StudyPath")
st.write("Check marks and make a study plan.")

with st.expander("How to use it"):
    st.write("Enter your topic marks, then generate a plan.")
```

Streamlit supplies the layout, buttons and typography. `.streamlit/config.toml` changes its built-in theme to a simple blue-and-white palette. It is configuration, not a custom stylesheet.

## 2. Understand a widget

```python
minutes = st.slider("Study minutes per day", 30, 180, 60)

if st.button("Create plan"):
    st.write(f"You chose {minutes} minutes.")
```

The slider returns a Python number. Clicking the button reruns the script; the button returns `True` for that run.

## 3. Why session state is needed

Normal variables are recreated when the page reruns. `st.session_state` keeps values for that browser session:

```python
if "results" not in st.session_state:
    st.session_state.results = []
```

That does **not** by itself mean data is saved permanently. Guest users have session-only data. InsForge stores progress for signed-in users, who sign in again after losing their browser session to restore it.

## 4. Explain weakness detection

The basic calculation is:

```python
percentage = marks / maximum_marks * 100

if percentage < 60:
    level = "Weak"
elif percentage < 80:
    level = "Developing"
else:
    level = "Strong"
```

`mentor.py` also checks invalid input: a missing topic, a non-positive maximum or marks outside the valid range. Topic-level marks are more useful than one overall exam score. These fixed thresholds are rules, not a trained model.

## 5. Explain the timetable

`make_plan()` in `mentor.py`:

1. Checks the entered results.
2. Gives lower-scoring topics larger scheduling weights.
3. Chooses topics repeatedly using those weights.
4. Adds study blocks and short breaks within the daily time budget.
5. Rotates between revision, practice and self-testing.

The micro-task planner in `study_tools.py` does something similar for the supported exam concepts, using diagnostic scores. A low score gets more practice time; it does not produce a guaranteed passing score.

## 6. Explain language support and the chatbot

The interface uses a small helper:

```python
def t(english, hindi):
    return hindi if hi else english
```

Roadmaps and concept explanations are stored in Python dictionaries. Chat code checks supported keywords and remembers the selected exam/concept. It is not an unrestricted language model and cannot understand every Hinglish question.

## 7. Explain downloads

- `csv` creates spreadsheet-friendly timetable files.
- ReportLab creates PDFs from Python text and paragraphs.
- `datetime` helps calculate dates and times for calendar exports.
- `io.BytesIO` holds a file in memory so Streamlit can offer it as a download.

PDF layouts use ReportLab's own formatting API. Some ReportLab paragraphs contain its small text-markup format for links; that is not a hand-built website interface.

## 8. The backend is a separate, more advanced part

The frontend and HTTP client are Python. The managed database also uses **SQL policies**, and deployment uses a **Dockerfile**. It would not be accurate to say that every file in the complete cloud system is Python.

- `backend.py` sends HTTP requests with Python's `requests` library.
- InsForge manages email-code verification, user sessions, PostgreSQL and file storage.
- `cloud_state.py` converts supported Python values into JSON and back.
- `cloud_ui.py` connects account controls and cloud saving to Streamlit.
- `migrations/` contains SQL rules restricting rows and PDF objects to their owner.

These security rules matter: hiding another user's data in the interface alone is not sufficient. The backend must reject unauthorized requests too. Do not remove security checks just to make the source look shorter.

## Suggested reading order

1. `design.py` — page title, help text and footer.
2. `app.py` — widgets, forms, language helper and tabs.
3. `mentor.py` — results and scheduling.
4. `roadmaps.py` — dictionary-based content.
5. `study_tools.py` and `lab_ui.py` — tasks and diagnostics.
6. `downloads.py` — PDF generation.
7. `cloud_state.py`, `backend.py`, `cloud_ui.py` — persistence and accounts.

## Questions to practise answering

- How is a weak topic detected?
- What happens when the user enters marks higher than the maximum?
- Why is session state needed?
- How does a weak topic get more study time?
- Which parts work without an internet connection?
- What happens when the app does not recognize a question?
- How are one user's PDFs kept separate from another user's?
- What are the limitations of the repeated three-question diagnostics?

Run the tests while learning:

```bash
python -m unittest discover -v
```
