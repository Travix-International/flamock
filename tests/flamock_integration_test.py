import json
import logging
import unittest
from flamock import logging_format
from flamock import admin_path as flamock_admin_path
from flamock import app as flamock_app

logging.basicConfig(level=logging.DEBUG, format=logging_format)


class FlamockTest(unittest.TestCase):

    host = 'http://0.0.0.0:1080'

    def setUp(self):
        flamock_app.config['TESTING'] = True
        self.app = flamock_app.test_client()
        self.app.set_cookie('localhost', 'cookie1', 'cookie1_value')
        self.app.set_cookie('localhost', 'cookie2', 'cookie2_value')

    def tearDown(self):
        self.app.delete_cookie('localhost', 'cookie1')
        self.app.delete_cookie('localhost', 'cookie2')

    def test_010_check_status(self):
        resp = self.app.get(self.host + '/' + flamock_admin_path + '/status')

        self.assertEqual(resp.status_code, 200)
        self.assertEquals('OK', resp.data.decode())

    def test_020_no_expectation_get_headers_and_cookies(self):
        path = 'a/b/c'

        resp = self.app.get(self.host + '/' + path,
                            headers={'header1': 'header1_value', 'header2': 'header2_value'})

        self.assertEqual(resp.status_code, 200)
        resp_text = resp.data.decode()
        self.assertIn('No expectation for request', resp_text)
        self.assertIn("'path': '%s'" % path, resp_text)
        self.assertIn("'Header1': 'header1_value'", resp_text)
        self.assertIn("'Header2': 'header2_value'", resp_text)
        self.assertIn("'cookie1': 'cookie1_value'", resp_text)
        self.assertIn("'cookie2': 'cookie2_value'", resp_text)

    def test_030_configure_transparent_mock(self):
        fwd_host = 'google.com'
        fwd_scheme = 'https'

        exp_resp = {
            'request': {
                'path': 'folder/service.aspx',
                'body': '<session_id>123.*<'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            },
            'priority': 1
        }
        exp_fwd = {
            'request': {
                'path': 'folder/service.aspx'
            },
            'forward': {
                'scheme': fwd_scheme,
                'host': fwd_host
            },
            'priority': 0
        }

        resp = self.app.post(self.host + '/' + flamock_admin_path + '/add_expectation',
                             data=json.dumps(exp_fwd))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post(self.host + '/' + flamock_admin_path + '/add_expectation',
                             data=json.dumps(exp_resp))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.host + '/folder/service.aspx',
                            data='<session_id>1234</session_id>',
                            headers={'header1': 'header1_value', 'header2': 'header2_value'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.decode(), 'Mock answer!')

        resp = self.app.get(self.host + '/folder/service.aspx',
                            data='<session_id>456</session_id>',
                            headers={'header1': 'header1_value', 'header2': 'header2_value'})
        self.assertEqual(resp.status_code, 400)

    def test_040_wide_expectation_with_empyt_path(self):
        fwd_host = 'google.com'
        fwd_scheme = 'https'

        exp_fwd = {
            'request': {
                'path': '.*'
            },
            'forward': {
                'scheme': fwd_scheme,
                'host': fwd_host
            },
            'priority': 0
        }

        resp = self.app.post(self.host + '/' + flamock_admin_path + '/add_expectation',
                             data=json.dumps(exp_fwd))
        self.assertEqual(resp.status_code, 200)

        resp = self.app.get(self.host + '/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('title="Google"', resp.data.decode())

if __name__ == '__main__':
    unittest.main()
