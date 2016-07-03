import unittest
from custom_reponse import CustomResponse
from expectation_manager import ExpectationManager
from response_manager import ResponseManager
import tests.logging_debug_config

class ResponseManagerTest(unittest.TestCase):

    def test_010_no_expectation(self):
        req = {'path': 'pathv', 'headers': {'h1': 'hv1'}, 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        resp = ResponseManager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        #self.assertIn('No expectation for request:'.encode(), resp.data)
        self.assertIn('No expectation for request:', resp.text)
        self.assertIn('pathv', resp.text)
        self.assertIn("'h1': 'hv1'", resp.text)
        self.assertIn('bodyv', resp.text)
        self.assertIn("'c1': 'cv1'", resp.text)

    def test_020_expected_response(self):
        req = {'path': 'pathv', 'headers': {'h1': 'hv1'}, 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        exp = {'request': {'path': 'pathv'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        ExpectationManager.add(exp)
        resp = ResponseManager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('Mock answer!', resp.text)

    def test_030_request_matcher_substring(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1', 'body': 'bodycontent'}
        exp_request = {'method': 'GET'}
        self.assertTrue(ResponseManager.is_expectation_match_request(exp_request, req))
        exp_request = {'path': 'hostname'}
        self.assertTrue(ResponseManager.is_expectation_match_request(exp_request, req))
        exp_request = {'body': 'content'}
        self.assertTrue(ResponseManager.is_expectation_match_request(exp_request, req))

    def test_040_request_matcher_regex(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1', 'body': 'bodycontent'}
        exp_request = {'body': 'b.dy.onte.t'}
        self.assertTrue(ResponseManager.is_expectation_match_request(exp_request, req))

    @staticmethod
    def request_mock(method='', url=''):
        return CustomResponse("method: %s, url: %s" % (method, url), 302)

    def test_050_make_request(self):
        mock_host = 'mock_hostname.com'
        mock_scheme = 'http'
        mock_path = '/subp1'
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        req = {'method': 'GET', 'path': '%s://%s%s' % (mock_scheme, mock_host, mock_path), 'body': 'bodycontent'}
        exp_forward = {'scheme': real_scheme, 'host': real_host}
        import requests
        requests.request = ResponseManagerTest.request_mock

        resp = ResponseManager.make_request(exp_forward, req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.text, "method: %s, url: %s" % (req['method'], '%s://%s%s' % (real_scheme, real_host, mock_path)))

if __name__ == '__main__':
    unittest.main()