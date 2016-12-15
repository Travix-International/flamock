import json
import logging
import unittest
from flamock import logging_format
from flamock import admin_path as flamock_admin_path
from flamock import app
from expectation_manager import ExpectationManager
from response_manager import ResponseManager

logging.basicConfig(level=logging.DEBUG, format=logging_format)


class FlamockTest(unittest.TestCase):

    base_port = 1080
    base_host = "0.0.0.0"
    base_url = 'http://%s:%s' % (base_host, base_port)

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.response_manager.host_whitelist = ["0.0.0.0"]

    def setUp(self):
        app.response_manager.clear_log_messages()
        app.expectation_manager.clear()
        self.client = app.test_client()
        self.client.set_cookie('localhost', 'cookie1', 'cookie1_value')
        self.client.set_cookie('localhost', 'cookie2', 'cookie2_value')

    def test_010_check_status(self):
        resp = self.client.get(self.base_url + '/' + flamock_admin_path + '/status')

        self.assertEqual(resp.status_code, 200)
        self.assertEquals('OK', resp.get_data(as_text=True))

    def test_020_no_expectation_get_headers_and_cookies(self):
        path = 'a/b/c'

        resp = self.client.get(self.base_url + '/' + path,
                               headers={'header1': 'header1_value', 'header2': 'header2_value'})

        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
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

        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_fwd))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_resp))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(self.base_url + '/folder/service.aspx',
                               data='<session_id>1234</session_id>',
                               headers={'header1': 'header1_value', 'header2': 'header2_value'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_data(as_text=True), 'Mock answer!')

        resp = self.client.get(self.base_url + '/folder/service.aspx',
                               data='<session_id>456</session_id>',
                               headers={'header1': 'header1_value', 'header2': 'header2_value'})
        self.assertEqual(resp.status_code, 400)

    def test_040_wide_expectation_with_empty_path(self):
        fwd_host = 'google.nl'
        fwd_scheme = 'https'

        exp_fwd = {
            'forward': {
                'scheme': fwd_scheme,
                'host': fwd_host
            }
        }

        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_fwd))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(self.base_url + '/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('>Google<', resp.get_data(as_text=True))

    def test_050_response_for_headers(self):

        exp_mock_header = {
            'request': {
                'headers': {'Sid':'123'}
            },
            'response': {
                'httpcode': 503,
                'body': "Mock answer for header!"
            },
            'priority': 1
        }
        exp_mock_all = {
            'response': {
                'httpcode': 200,
                'body': "Mock answer without header!"
            },
            'priority': 0
        }

        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_mock_header))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_mock_all))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(self.base_url + '/', headers={'sid': '123'})
        self.assertEqual(resp.status_code, 503)
        self.assertIn('Mock answer for header!', resp.get_data(as_text=True))

        resp = self.client.get(self.base_url + '/', headers={'sid': '345'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Mock answer without header!', resp.get_data(as_text=True))

    def test_055_wide_expectation_with_empty_path(self):
        fwd_host = 'yandex.ru/search'
        fwd_scheme = 'https'

        exp_fwd = {
            'forward': {
                'scheme': fwd_scheme,
                'host': fwd_host
            }
        }

        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_fwd))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(self.base_url + '/?text=Hello')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text=Hello', resp.get_data(as_text=True))

    def test_060_header_when_forward(self):
        fwd_host = 'yandex.ru/search'
        fwd_scheme = 'https'

        exp_fwd = {
            'request': {
                'path': 'search'
            },
            'forward': {
                'scheme': fwd_scheme,
                'host': fwd_host,
                'headers': {
                    'Host': 'yandex.ru'
                }
            }
        }

        resp = self.client.post(self.base_url + '/' + flamock_admin_path + '/add_expectation',
                                data=json.dumps(exp_fwd))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(self.base_url + '/?text=Hello')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text=Hello', resp.get_data(as_text=True))

    def test_070_get_empty_logs(self):
        resp = self.client.get(self.base_url + '/' + flamock_admin_path + '/logs')

        self.assertEqual(resp.status_code, 200)
        self.assertEquals('{}', resp.get_data(as_text=True))

    def test_080_get_all_logs(self):
        self.client.get(self.base_url + '/')

        resp = self.client.get(self.base_url + '/' + flamock_admin_path + '/logs')

        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)

        self.assertGreater(len(resp_text), 3)
        self.assertIn('request', resp_text)
        self.assertIn('response', resp_text)
        self.assertIn('No expectation for request', resp_text)

    def test_090_get_log_by_id(self):
        self.client.get(self.base_url + '/')

        resp = self.client.get(self.base_url + '/' + flamock_admin_path + '/logs/0')

        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)

        self.assertGreater(len(resp_text), 3)
        self.assertIn('request', resp_text)
        self.assertIn('response', resp_text)
        self.assertIn('No expectation for request', resp_text)

if __name__ == '__main__':
    unittest.main()
