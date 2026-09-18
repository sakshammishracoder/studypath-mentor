"""Python-only InsForge REST client. No service/admin key is used at runtime.

Every protected request uses the current user's JWT; PostgreSQL and Storage RLS
are the authorization boundary. Tokens live only in Streamlit session memory.
"""
from dataclasses import dataclass, field
import os
import re
from urllib.parse import quote, unquote, urlparse
from uuid import uuid4, UUID
import requests

BUCKET = 'study-pdfs'
MAX_PDF_BYTES = 5 * 1024 * 1024

class BackendError(Exception):
    pass

class SessionExpired(BackendError):
    pass

class SaveConflict(BackendError):
    pass


def backend_url():
    url = os.environ.get('INSFORGE_BASE_URL', '').rstrip('/')
    if not url:
        return ''
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise BackendError('INSFORGE_BASE_URL must be an HTTPS origin, without credentials or a path.')
    return url


def _checked(response):
    if response.ok:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()
    if response.status_code == 401:
        raise SessionExpired('Your sign-in has expired. Please sign in again.')
    if response.status_code == 409:
        raise SaveConflict('Cloud data changed in another session. Reload it before saving again.')
    if response.status_code == 429:
        raise BackendError('Too many requests. Wait a little before trying again.')
    if response.status_code in (400, 403, 422):
        raise BackendError('Request not accepted. Check your sign-in code, permissions or input and try again.')
    raise BackendError('Cloud service could not complete the request. Your local work has not been discarded.')


def public_request(base, path, body):
    try:
        return _checked(requests.post(base + path, json=body, timeout=25))
    except (requests.RequestException, ValueError) as exc:
        raise BackendError('Could not contact the account service. Try again later.') from exc


def send_login_code(base, email):
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(email) > 254:
        raise BackendError('Enter a valid email address.')
    return public_request(base, '/api/auth/email/send-otp', {'email': email})


def verify_login_code(base, email, code):
    if not re.fullmatch(r'\d{6}', code):
        raise BackendError('Enter the six-digit code from your email.')
    result = public_request(base, '/api/auth/sessions?client_type=server', {'method': 'otp', 'email': email, 'otp': code})
    return CloudSession.from_login(base, result)


@dataclass(repr=False)
class CloudSession:
    base: str
    user_id: str
    email: str
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)

    @classmethod
    def from_login(cls, base, data):
        try:
            user = data['user']
            ident = str(UUID(user['id']))
            token = data['accessToken']
            refresh = data.get('refreshToken', '')
            if not token:
                raise ValueError()
            return cls(base, ident, user.get('email', ''), token, refresh)
        except (KeyError, TypeError, ValueError) as exc:
            raise BackendError('Sign-in was not completed. Verify your email and try again.') from exc

    def __repr__(self):
        return '<CloudSession: credentials redacted>'

    def refresh(self):
        if not self.refresh_token:
            raise SessionExpired('Please sign in again to reconnect your account.')
        result = public_request(self.base, '/api/auth/refresh?client_type=server', {'refreshToken': self.refresh_token})
        new = CloudSession.from_login(self.base, result)
        if new.user_id != self.user_id:
            raise SessionExpired('Session identity changed. Please sign in again.')
        self.access_token, self.refresh_token = new.access_token, new.refresh_token

    def request(self, method, path, *, body=None, params=None, files=None, retry=True, prefer=None):
        if not path.startswith('/api/') or path.startswith('//'):
            raise BackendError('Invalid service path.')
        headers = {'Authorization': 'Bearer ' + self.access_token}
        if prefer:
            headers['Prefer'] = prefer
        try:
            response = requests.request(method, self.base + path, json=body, params=params, files=files, headers=headers, timeout=30)
            if response.status_code == 401 and retry:
                self.refresh()
                return self.request(method, path, body=body, params=params, files=files, retry=False, prefer=prefer)
            return _checked(response)
        except (requests.RequestException, ValueError) as exc:
            raise BackendError('Cloud connection failed. Keep this page open and retry; your local work is still here.') from exc

    def logout(self):
        try:
            self.request('POST', '/api/auth/logout?client_type=server', body={'refreshToken': self.refresh_token}, retry=False)
        finally:
            self.access_token = self.refresh_token = ''

    def load_state(self):
        rows = self.request('GET', '/api/database/records/study_state', params={'user_id': 'eq.' + self.user_id, 'limit': 1})
        if not rows:
            return {}, 0
        return rows[0]['payload'], rows[0]['revision']

    def save_state(self, payload, revision):
        from datetime import datetime, timezone
        data = {'payload': payload, 'revision': revision + 1, 'updated_at': datetime.now(timezone.utc).isoformat()}
        if revision == 0:
            data['user_id'] = self.user_id
            rows = self.request('POST', '/api/database/records/study_state', body=[data], prefer='return=representation')
        else:
            rows = self.request('PATCH', '/api/database/records/study_state', params={'user_id': 'eq.' + self.user_id, 'revision': f'eq.{revision}'}, body=data, prefer='return=representation')
        if not rows:
            raise SaveConflict('Another window saved newer progress. Reload cloud progress before continuing.')
        return rows[0]['revision']

    def _object_path(self, key):
        if not key.startswith(self.user_id + '/') or '..' in key or not key.endswith('.pdf'):
            raise BackendError('That document does not belong to the signed-in account.')
        return '/api/storage/buckets/' + BUCKET + '/objects/' + quote(key, safe='/')

    def list_documents(self):
        rows = []
        offset = 0
        while True:
            batch = self.request('GET', '/api/database/records/study_documents', params={'user_id': 'eq.' + self.user_id, 'order': 'created_at.desc,id.asc', 'limit': 100, 'offset': offset}) or []
            rows.extend(batch)
            if len(batch) < 100:
                return rows
            offset += len(batch)

    def save_pdf(self, data, title):
        if not data.startswith(b'%PDF') or not 0 < len(data) <= MAX_PDF_BYTES:
            raise BackendError('Only generated PDFs up to 5 MB can be saved.')
        title = title.strip()
        if not 1 <= len(title) <= 160:
            raise BackendError('Use a document title of 1–160 characters.')
        if len(self.list_documents()) >= 100:
            raise BackendError('Your library has reached the 100-document app limit. Delete a saved PDF before adding another.')
        key = self.user_id + '/' + str(uuid4()) + '.pdf'
        path = self._object_path(key)
        metadata = self.request('POST', '/api/database/records/study_documents', body=[{'user_id': self.user_id, 'object_key': key, 'title': title, 'byte_size': len(data)}], prefer='return=representation')[0]
        try:
            strategy = self.request('POST', '/api/storage/buckets/' + BUCKET + '/upload-strategy', body={'filename': key, 'contentType': 'application/pdf', 'size': len(data)})
            if strategy.get('key') != key:
                raise BackendError('Storage returned an unexpected object key.')
            if strategy['method'] == 'direct':
                self.request('PUT', path, files={'file': ('document.pdf', data, 'application/pdf')})
            elif strategy['method'] == 'presigned':
                url = strategy['uploadUrl']
                if urlparse(url).scheme != 'https':
                    raise BackendError('Storage upload requires HTTPS.')
                # Never send the user's JWT to the external S3 URL.
                response = requests.post(url, data=strategy.get('fields', {}), files={'file': ('document.pdf', data, 'application/pdf')}, timeout=60)
                if not response.ok:
                    raise BackendError('PDF upload did not complete. Try again.')
                confirm = strategy.get('confirmUrl', '/api/storage/buckets/' + BUCKET + '/objects/' + quote(key, safe='') + '/confirm-upload')
                if unquote(confirm) != unquote(path) + '/confirm-upload':
                    raise BackendError('Storage returned an unexpected confirmation path.')
                self.request('POST', confirm, body={'size': len(data), 'contentType': 'application/pdf'})
            else:
                raise BackendError('Unsupported storage upload strategy.')
            return metadata
        except Exception as exc:
            # Compensate partial writes; metadata remains discoverable if object
            # cleanup fails, so the user can retry removal in the library.
            try:
                self.request('DELETE', path)
            except BackendError:
                pass
            try:
                self.request('DELETE', '/api/database/records/study_documents', params={'id': 'eq.' + metadata['id'], 'user_id': 'eq.' + self.user_id})
            except BackendError:
                pass
            if isinstance(exc, BackendError):
                raise
            raise BackendError('PDF upload could not be completed. Check the library before retrying.') from exc

    def read_pdf(self, key):
        self._object_path(key)
        strategy = self.request('GET', '/api/storage/buckets/' + BUCKET + '/download-strategy/objects/' + quote(key, safe='/'))
        url = strategy['url']
        if url.startswith('/api/'):
            url = self.base + url
        if urlparse(url).scheme != 'https':
            raise BackendError('Storage download requires HTTPS.')
        headers = {'Authorization': 'Bearer ' + self.access_token} if urlparse(url).netloc == urlparse(self.base).netloc else {}
        try:
            with requests.get(url, headers=headers, timeout=45, stream=True) as response:
                if not response.ok:
                    raise BackendError('PDF is unavailable or access was denied.')
                data = bytearray()
                for chunk in response.iter_content(65536):
                    data.extend(chunk)
                    if len(data) > MAX_PDF_BYTES:
                        raise BackendError('PDF exceeds the download size limit.')
                if not data.startswith(b'%PDF'):
                    raise BackendError('Stored document is not a PDF.')
                return bytes(data)
        except requests.RequestException as exc:
            raise BackendError('Could not download that PDF. Try again.') from exc

    def delete_pdf(self, doc):
        # Re-read authorized metadata rather than trusting a browser-supplied key.
        rows = self.request('GET', '/api/database/records/study_documents', params={'id': 'eq.' + str(UUID(doc['id'])), 'user_id': 'eq.' + self.user_id})
        if not rows:
            raise BackendError('Document not found in your account.')
        path = self._object_path(rows[0]['object_key'])
        try:
            self.request('DELETE', path)
        except BackendError:
            # A metadata-only failed upload can be removed if storage confirms
            # absence; otherwise retain metadata to let the user retry.
            objects = self.request('GET', '/api/storage/buckets/' + BUCKET + '/objects', params={'prefix': rows[0]['object_key']})
            if any(r.get('key') == rows[0]['object_key'] for r in objects.get('data', [])):
                raise
        self.request('DELETE', '/api/database/records/study_documents', params={'id': 'eq.' + rows[0]['id'], 'user_id': 'eq.' + self.user_id})
