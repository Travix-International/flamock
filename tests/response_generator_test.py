import sys
import unittest
import logging
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
        ResponseGenerator.add_expectation(exp)
        resp = ResponseGenerator.generate(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('Mock answer!'.encode(), resp.data)

    def test_030_request_matcher_substring_test(self):
        req = {'method': 'GET', 'path': 'http:\\hostname.com\subp1', 'body': 'bodycontent'}
        exp_request = {'method': 'GET'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))
        exp_request = {'path': 'hostname'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))
        exp_request = {'body': 'content'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))

    def test_040_request_matcher_regex_test(self):
        req = {'method': 'GET', 'path': 'http:\\hostname.com\subp1', 'body': 'bodycontent'}
        exp_request = {'body': 'b.dy.onte.t'}
        self.assertTrue(ResponseGenerator.is_expectation_match_request(exp_request, req))
