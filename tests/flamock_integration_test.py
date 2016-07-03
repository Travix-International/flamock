import unittest
import requests
import flamock
import json
import tests.logging_debug_config

class FlamockTest(unittest.TestCase):

    host = 'http://127.0.0.1:5000'

    def test_010_no_expectation_get_headers_and_cookies(self):
        path = 'a/b/c'
        resp = requests.get(self.host + '/' + path,
                            headers={'header1': 'header1_value', 'header2': 'header2_value'},
                            cookies={'cookie1': 'cookie1_value', 'cookie2': 'cookie2_value'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('No expectation for request', resp.text)
        self.assertIn("'path': '%s'" % path, resp.text)
        self.assertIn("'Header1', 'header1_value'", resp.text)
        self.assertIn("'Header2', 'header2_value'", resp.text)
        self.assertIn("'cookie1': 'cookie1_value'", resp.text)
        self.assertIn("'cookie2': 'cookie2_value'", resp.text)

    def test_020_configure_transparent_mock(self):
        fwd_host = 'real_hostname.com'
        fwd_scheme = 'https'
        exp_forward = {'scheme': fwd_scheme, 'host': fwd_host}
        exp_resp = {
            'request': {
                'path': '/folder/service.aspx',
                'body': '<session_id>123.*<'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }
        }

        req_to_fwd = {'path': '/folder/service.aspx', 'headers': {'h1': 'hv1'}, 'body': '<session_id>5678</session_id>'}

        resp = requests.post(self.host + '/' + flamock.admin_path,
                             data=json.dumps(exp_forward))
        self.assertEqual(resp.status_code, 200)

        resp = requests.post(self.host + '/' + flamock.admin_path,
                             data=json.dumps(exp_resp))
        self.assertEqual(resp.status_code, 200)

        resp = requests.get(self.host + '/folder/service.aspx',
                            data='<session_id>1234</session_id>',
                            headers={'header1': 'header1_value', 'header2': 'header2_value'},
                            cookies={'cookie1': 'cookie1_value', 'cookie2': 'cookie2_value'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, 'Mock answer!')

        resp = requests.get(self.host + '/folder/service.aspx',
                            data='<session_id>456</session_id>',
                            headers={'header1': 'header1_value', 'header2': 'header2_value'},
                            cookies={'cookie1': 'cookie1_value', 'cookie2': 'cookie2_value'})
        self.assertEqual(resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()