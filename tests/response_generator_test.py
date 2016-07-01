import sys
import unittest
import logging
from expectation_manager import ExpectationManager
from response_generator import ResponseGenerator

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class ResponseGeneratorTest(unittest.TestCase):

    def test_010_no_expectation(self):
        req = {'path': 'pathv', 'headers': {'h1': 'hv1'}, 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        resp = ResponseGenerator.generate(req)
        self.assertEquals(200, resp.status_code)
        self.assertIn('No expectation for request:'.encode(), resp.data)
        self.assertIn('pathv'.encode(), resp.data)
        self.assertIn("'h1': 'hv1'".encode(), resp.data)
        self.assertIn('bodyv'.encode(), resp.data)
        self.assertIn("'c1': 'cv1'".encode(), resp.data)

    def test_020_expected_response(self):
        req = {'path': 'pathv', 'headers': {'h1': 'hv1'}, 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        exp = {'request': {'path': 'pathv'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        ExpectationManager.add(exp)
        resp = ResponseGenerator.generate(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('Mock answer!'.encode(), resp.data)

    def test_030_request_matcher_substring(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1', 'body': 'bodycontent'}
        exp_request = {'method': 'GET'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))
        exp_request = {'path': 'hostname'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))
        exp_request = {'body': 'content'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))

    def test_040_request_matcher_regex(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1', 'body': 'bodycontent'}
        exp_request = {'body': 'b.dy.onte.t'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))

    @staticmethod
    def request_mock(method='', url=''):
        return (method, url)

    def test_050_make_request(self):
        mock_host = 'mock_hostname.com'
        mock_scheme = 'http'
        mock_path = '/subp1'
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        req = {'method': 'GET', 'path': '%s://%s%s' % (mock_scheme, mock_host, mock_path), 'body': 'bodycontent'}
        exp_forward = {'scheme': real_scheme, 'host': real_host}
        import requests
        requests.request = ResponseGeneratorTest.request_mock

        method, url = ResponseGenerator.make_request(exp_forward, req)
        self.assertEqual(method, req['method'])
        self.assertEqual(url, '%s://%s%s' % (real_scheme, real_host, mock_path))
