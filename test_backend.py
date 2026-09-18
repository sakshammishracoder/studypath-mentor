import unittest
from unittest.mock import patch, Mock
from datetime import date, time
from backend import CloudSession, BackendError, SessionExpired, SaveConflict, verify_login_code, backend_url
from cloud_state import encode_state, decode_state, fingerprint
from mentor import Result
from study_tools import micro_plan

UID = '00000000-0000-4000-8000-000000000001'

class BackendTests(unittest.TestCase):
    def session(self):
        return CloudSession('https://example.insforge.app', UID, 'test@example.invalid', 'not-a-real-access-token', 'not-a-real-refresh-token')
    def test_repr_redacts_credentials(self):
        self.assertNotIn('not-a-real', repr(self.session()))
    def test_origin_validation(self):
        for value in ['http://example.com', 'https://user:pass@example.com', 'https://example.com/path', 'https://example.com/?key=test']:
            with patch.dict('os.environ', {'INSFORGE_BASE_URL': value}):
                with self.assertRaises(BackendError): backend_url()
    def test_otp_validation(self):
        with patch('backend.public_request') as req:
            with self.assertRaises(BackendError): verify_login_code('https://example.com','x@y.com','invalid')
            req.assert_not_called()
    def test_signup_response_shape(self):
        data={'user':{'id':UID,'email':'x@y.com'},'accessToken':'fake','refreshToken':'fake2'}
        self.assertEqual(CloudSession.from_login('https://example.com',data).user_id,UID)
        data['accessToken']=None
        with self.assertRaises(BackendError):CloudSession.from_login('https://example.com',data)
    def test_codec_preserves_progress_not_secrets(self):
        plan=dict(exam='10',tasks=micro_plan('10',days=2),start=date(2026,9,17),clock=time(18),exam_date=date(2026,9,20),panic=False,signature='x')
        state=dict(results=[Result('Algebra',40,100)],lab_plan=plan,task_completions={'x_0'},messages=['private chat'],password='never serialize',_cloud_client=self.session())
        payload=encode_state(state)
        self.assertNotIn('never serialize',str(payload));self.assertNotIn('private chat',str(payload));self.assertNotIn('not-a-real',str(payload))
        loaded=decode_state(payload)
        self.assertEqual(loaded['lab_plan']['start'],date(2026,9,17))
        self.assertEqual(loaded['task_completions'],{'x_0'})
        self.assertEqual(loaded['results'][0].percent,40)
        self.assertEqual(fingerprint(payload),fingerprint(encode_state(loaded)))
    def test_bad_cloud_state_fails_closed(self):
        for payload in [{'version':2},{'version':1,'target_exam':'bad'},{'version':1,'diagnostic_history':[{'exam':'bad'}]}]:
            with self.assertRaises(ValueError):decode_state(payload)
    def test_revision_conflict(self):
        c=self.session()
        with patch.object(c,'request',return_value=[]):
            with self.assertRaises(SaveConflict):c.save_state({},5)
    def test_owner_path_guard(self):
        c=self.session()
        for key in ['someone/file.pdf',UID+'/../file.pdf',UID+'/file.txt']:
            with self.assertRaises(BackendError):c._object_path(key)
    def test_request_uses_user_token(self):
        c=self.session();response=Mock(ok=True,status_code=200,content=b'[]');response.json.return_value=[]
        with patch('backend.requests.request',return_value=response) as request:
            c.load_state()
            self.assertEqual(request.call_args.kwargs['headers']['Authorization'],'Bearer not-a-real-access-token')
            self.assertNotIn('apikey',request.call_args.kwargs['headers'])
    def test_refresh_rotation(self):
        c=self.session()
        response={'user':{'id':UID},'accessToken':'rotated','refreshToken':'rotated-refresh'}
        with patch('backend.public_request',return_value=response):c.refresh()
        self.assertEqual(c.refresh_token,'rotated-refresh')
    def test_401_retries_once(self):
        c=self.session()
        bad=Mock(ok=False,status_code=401,content=b'error')
        with patch('backend.requests.request',return_value=bad) as req, patch.object(c,'refresh') as refresh:
            with self.assertRaises(SessionExpired):c.load_state()
            self.assertEqual(req.call_count,2);refresh.assert_called_once()
    def test_pdf_validation(self):
        c=self.session()
        with self.assertRaises(BackendError):c.save_pdf(b'not a pdf','test')
        with self.assertRaises(BackendError):c.save_pdf(b'%PDF'+b'a'*(6*1024*1024),'test')

if __name__=='__main__':unittest.main()
