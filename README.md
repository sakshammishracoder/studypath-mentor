# StudyPath Mentor

A Python/Streamlit study and career mentor with a bilingual interface, curated exam roadmaps, diagnostics, actionable study plans, PDF/calendar downloads and optional **InsForge accounts with private persistent storage**.

> The learning engine is rule-based, not generative AI. Roadmaps and explanations are curated. No model API key or ML training is needed.

## Run locally

Python 3.10+ (the container uses Python 3.13):

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Without `INSFORGE_BASE_URL`, the app runs in guest mode and stores progress only for the current session.

To enable the provisioned InsForge backend:

```bash
export INSFORGE_BASE_URL=https://esf7ejzp.us-east.insforge.app
python -m streamlit run app.py
```

On PowerShell, use `$env:INSFORGE_BASE_URL="https://esf7ejzp.us-east.insforge.app"` instead of `export`. The `.env.example` file documents configuration; the app does not automatically read `.env` files.

**No admin key is needed by the running app.** This public origin is not a credential. User access/refresh tokens stay in the Streamlit server session and are never written to the repository or stored in the progress payload.

## Features

1. **Assessment:** enter topic-level marks or take a six-question sample quiz. Below 60% is weak, 60–79.9% developing and 80%+ strong. Saved assessment scores populate the marks editor after restore.
2. **Daily timetable:** weighted practice blocks prioritise lower-scoring topics, with breaks included in the daily budget. Export CSV, English PDF or an `.ics` calendar with an IST start time.
3. **Career mentor:** rule-based Hindi/English/Hinglish intents and remembered exam/concept context. Three tech-career skill roadmaps and named exam pathways are supported; this is not unrestricted conversation.
4. **Exam roadmaps:** 16 representative school, entrance/professional and government/public-sector pathway families. Each shows overview, typical entry, stages, subjects, preparation and official links.
5. **Study Lab:** eight curated concepts, three-question quick diagnostics, micro-task checklists, simple explanations and a date-aware panic/recall plan.
6. **Download Centre:** student reports, selectable notes/practice sheets with optional answer keys, exam/career roadmap PDFs, and a private saved-PDF library for signed-in users.

## Accounts & cloud persistence

Sign in from **Account & saved progress** using a six-digit email code. A new account is created only after successful verification. The app does not store passwords.

- Sign-in loads the account's cloud progress, replacing guest work. Export guest work first if needed.
- Current assessment, diagnostic history, selected target/language, normal timetable settings, current micro/panic plan and task completions autosave after interactions.
- A versioned JSON snapshot in `study_state` holds this data. This is **current progress**, not an append-only history of every marks assessment or past plan.
- Each user has their own row. PostgreSQL row-level security (RLS) checks `auth.uid()` against `user_id` on reads and writes. Anonymous access has no grant.
- Revision-based compare-and-swap rejects stale saves from another window rather than silently overwriting newer progress. A conflict pauses saves until the user explicitly reloads the cloud copy. Export unsaved local work first.
- If loading fails, saving is not enabled. A network error does not silently replace cloud data with an empty snapshot.
- Refresh/reconnection may require sign-in again; saved progress then restores. **Chats, credentials and unsaved form input are not persisted.**
- Signing out clears all user-specific session state and cached PDF bytes. Account reloads clear old widgets before restoring another user.

### Private PDF library

Signed-in users can explicitly save generated timetables, reports, practice packs and roadmaps. Merely downloading a PDF does not save it to the cloud.

- Bytes live in the **private** `study-pdfs` bucket; metadata lives in `study_documents`.
- Object keys start with the authenticated user's UUID. Storage RLS enforces ownership even when a client attempts a direct foreign-key request.
- Download URLs are obtained only after authenticated authorization. Signed URLs are bearer capabilities; do not share them. The app fetches their bytes server-side without sending the user JWT to S3.
- The library supports list, download and confirmed deletion. Files already downloaded to a device cannot be recalled.
- App limits: 100 saved PDFs and 5 MB per PDF. These UI/client limits are not a replacement for provider-level quota/rate limits.
- Database metadata and object storage are not a distributed transaction. The client attempts cleanup on upload failure; administrators should periodically check for orphaned provider objects after failures.

## InsForge setup for another project

1. Authenticate with the InsForge CLI and link your own project.
2. Create a private bucket: `npx @insforge/cli storage create-bucket study-pdfs --private`.
3. Apply the checked-in additive migration: `npx @insforge/cli db migrations up --all`.
4. Ensure email-code sign-in and the managed sender/custom SMTP are available for the project.
5. Set `INSFORGE_BASE_URL` to its HTTPS origin and run the app.

For the current project, the bucket and migration have already been provisioned. The migration does not remove existing application data or disable email verification. See `docs/BACKEND.md` for architecture and verification results.

## Scope and accuracy

- Exam guides cover representative families, **not every government recruitment or a complete syllabus**. Class 12, teaching, NET and technical families require the user's specific stream/post/subject syllabus.
- Official information is a manually researched **17 September 2026 snapshot**, not live notifications. CAT has verified dates and detailed eligibility; other guides explicitly describe narrower verification or unverified current details. Always check amended official notices.
- Diagnostic retakes repeat the same questions. Scores can reflect memory and do not estimate full-exam readiness or selection probability.
- Micro-task completions are self-reported, not evidence of mastery. Panic plans prioritise familiar material and must not interfere with sleep, travel or reporting time.
- PDF downloads are English-only. Non-Latin custom labels may be omitted or replaced. Calendar/CSV retain original custom topic labels. Hindi mode includes Hinglish concept explanations.
- Do not enter sensitive personal, medical or financial information. Public deployment requires operational monitoring, appropriate privacy/retention policies and provider quotas. A production security/privacy review is recommended before collecting real students' records at scale.

## Tests

```bash
python -m unittest discover -v
```

27 unit tests cover scoring, budgets, routing, PDF generation, state serialization, token redaction/rotation, stale-write conflict handling and client-side ownership checks. Live two-account tests additionally verified InsForge RLS and private storage isolation; see `docs/BACKEND.md` for exact coverage and limits.

## Main files

| File | Purpose |
|---|---|
| `app.py`, `design.py` | Streamlit interface and styling |
| `mentor.py`, `roadmaps.py` | Assessment logic and bilingual roadmaps |
| `study_tools.py`, `lab_ui.py` | Micro-tasks, diagnostics, explanations, plan exports |
| `downloads.py` | Report/practice/roadmap PDFs |
| `backend.py` | Python requests-based InsForge REST client |
| `cloud_state.py` | Versioned allowlisted progress serialization |
| `cloud_ui.py` | Sign-in, restore/autosave, private PDF library |
| `migrations/` | PostgreSQL and Storage RLS schema migration |
| `Dockerfile`, `.dockerignore` | Non-root container with allowlisted build inputs |

Keep `.streamlit/config.toml` when copying the project. Never commit `.insforge`, `.env`, `.streamlit/secrets.toml`, access tokens or test-account credentials.

## Simple Streamlit interface

The interface now uses only built-in Streamlit components: titles, tabs, forms, expanders and standard widgets. The custom gradient banner, floating cards and HTML/CSS styling were removed. The blue-and-white theme is configured in `.streamlit/config.toml`; learning and backend features are unchanged.

For a beginner-friendly walkthrough, read [`docs/PYTHON_GUIDE.md`](docs/PYTHON_GUIDE.md). It explains widgets, session state, weakness detection, the timetable, downloads and where the more advanced managed backend fits in.
