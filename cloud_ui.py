"""Account controls and persistence integration for the existing Streamlit app."""
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from backend import backend_url, BackendError, SessionExpired, SaveConflict, send_login_code, verify_login_code
from cloud_state import encode_state, decode_state, fingerprint


def client():
    return st.session_state.get('_cloud_client')


def _restore(c):
    payload, revision = c.load_state()
    values = decode_state(payload)
    # Clears account-specific widget and cached PDF state before switching users.
    st.session_state.clear()
    st.session_state.update(values)
    st.session_state['_cloud_client'] = c
    st.session_state['_cloud_revision'] = revision
    st.session_state['_cloud_loaded'] = True
    st.session_state['_cloud_hash'] = fingerprint(payload) if payload else ''


def account_panel():
    """Must run before the main application creates widgets."""
    try:
        base = backend_url()
    except BackendError as exc:
        st.error(str(exc)); st.stop()
    if not base:
        st.sidebar.caption('Guest demo · cloud not configured')
        return
    with st.sidebar.expander('☁ Account & saved progress / खाता', expanded=not bool(client())):
        c = client()
        if c:
            st.caption('Signed in / लॉग इन: ' + c.email)
            st.caption('Progress autosaves after interactions. After refresh, sign in again to restore it. Chats are not saved.')
            if st.session_state.get('_cloud_issue'):
                st.warning(st.session_state['_cloud_issue'])
            discard = st.checkbox('Reload cloud copy (discard unsaved local changes)', key='_reload_consent')
            if st.button('Reload saved progress', disabled=not discard, key='_reload_cloud'):
                try:
                    _restore(c); st.rerun()
                except (BackendError, ValueError, TypeError, KeyError) as exc:
                    st.error(str(exc) if isinstance(exc, BackendError) else 'Saved progress could not be read. Nothing was overwritten.')
            confirm = st.checkbox('I have saved my work / unsaved work can be discarded', key='_signout_consent')
            if st.button('Sign out / लॉग आउट', disabled=not confirm, key='_signout'):
                try:
                    c.logout()
                except BackendError:
                    pass
                st.session_state.clear(); st.rerun()
        else:
            st.caption('Email-code sign-in / ईमेल कोड से प्रवेश. New users get an account after verification. No password needed. Sign-in replaces guest work with your cloud copy; download any guest report first.')
            with st.form('_send_code', clear_on_submit=True):
                email = st.text_input('Email / ईमेल', max_chars=254)
                send = st.form_submit_button('Send sign-in code')
            if send:
                try:
                    email = email.strip().lower()
                    send_login_code(base, email)
                    st.session_state['_pending_email'] = email
                    st.success('If permitted, a code has been sent. Check inbox/spam. Wait before requesting another.')
                except BackendError as exc:
                    st.error(str(exc))
            with st.form('_verify_code', clear_on_submit=True):
                verify_email = st.text_input('Email receiving code', value=st.session_state.get('_pending_email', ''), max_chars=254)
                otp = st.text_input('6-digit code', type='password', max_chars=6)
                verify = st.form_submit_button('Verify & sign in')
            if verify:
                try:
                    c = verify_login_code(base, verify_email.strip().lower(), otp.strip())
                    # Load before enabling writes; a failed load must never cause
                    # blank local state to overwrite existing cloud progress.
                    _restore(c); st.rerun()
                except (BackendError, ValueError, TypeError, KeyError) as exc:
                    st.error(str(exc) if isinstance(exc, BackendError) else 'Cloud progress could not be restored. Nothing was overwritten.')
            st.caption('Guest mode still works without sign-in. Do not enter sensitive personal or financial information. Academic data and PDFs you choose to save are kept in your InsForge account, not in GitHub.')


def sync_progress():
    c = client()
    if not c or not st.session_state.get('_cloud_loaded'):
        return
    if st.session_state.get('_cloud_blocked'):
        st.warning(st.session_state.get('_cloud_issue', 'Cloud saving paused. Reload your cloud copy to continue.'))
        return
    try:
        payload = encode_state(st.session_state)
        hashed = fingerprint(payload)
        if hashed != st.session_state.get('_cloud_hash'):
            revision = c.save_state(payload, st.session_state.get('_cloud_revision', 0))
            st.session_state['_cloud_revision'] = revision
            st.session_state['_cloud_hash'] = hashed
            st.session_state['_cloud_saved_at'] = datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S IST')
        st.session_state.pop('_cloud_issue', None)
        st.caption('☁ Saved to your account · ' + st.session_state.get('_cloud_saved_at', 'cloud copy loaded'))
    except (SaveConflict, SessionExpired) as exc:
        st.session_state['_cloud_issue'] = str(exc)
        st.session_state['_cloud_blocked'] = True
        st.warning(str(exc) + ' Download a report to preserve unsaved work.')
    except (BackendError, ValueError, TypeError) as exc:
        st.session_state['_cloud_issue'] = str(exc)
        st.warning('Not saved to cloud: ' + str(exc) + ' Keep this page open and interact again to retry.')


def save_pdf_button(data, title, key):
    c = client()
    if not c:
        return
    if st.button('☁ Save privately to my PDF library', key='cloud_pdf_' + key):
        try:
            c.save_pdf(data, title)
            st.success('PDF saved privately. Find it in My saved PDFs below.')
        except BackendError as exc:
            st.error(str(exc))


def pdf_library():
    c = client()
    st.markdown('### ☁ My saved PDFs / मेरी सेव की गई PDF')
    if not c:
        st.info('Sign in from the sidebar to save PDFs privately and retrieve them on another visit.')
        return
    try:
        documents = c.list_documents()
    except BackendError as exc:
        st.error(str(exc)); return
    st.caption('Private to your account. Up to 100 PDFs through this app, 5 MB each. Downloads create a copy on your device. Deleting a file does not delete copies already downloaded.')
    if not documents:
        st.info('No saved PDFs yet. Use a “Save privately” button after generating one.'); return
    # Use expander per file, fetch bytes only on request, never cache globally.
    for doc in documents:
        with st.expander(doc['title'] + ' · ' + doc['created_at'][:10]):
            st.caption(f"{doc['byte_size']/1024:.1f} KB")
            cache_key = '_pdf_bytes_' + doc['id']
            if st.button('Prepare download', key='_get_pdf_' + doc['id']):
                try:
                    st.session_state[cache_key] = c.read_pdf(doc['object_key'])
                except BackendError as exc:
                    st.error(str(exc))
            if cache_key in st.session_state:
                st.download_button('Download saved PDF', st.session_state[cache_key], file_name='studypath_' + doc['id'] + '.pdf', mime='application/pdf', key='_dl_pdf_' + doc['id'])
            consent = st.checkbox('Delete this saved PDF permanently', key='_confirm_del_' + doc['id'])
            if st.button('Delete saved PDF', disabled=not consent, key='_delete_pdf_' + doc['id']):
                try:
                    c.delete_pdf(doc)
                    st.session_state.pop(cache_key, None)
                    st.rerun()
                except BackendError as exc:
                    st.error(str(exc))
