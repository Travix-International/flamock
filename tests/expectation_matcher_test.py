import unittest
import logging
from flamock import logging_format
from expectation_matcher import ExpectationMatcher

logging.basicConfig(level=logging.DEBUG, format=logging_format)


class ExpectationMatcherTest(unittest.TestCase):

    def test_010_request_matcher_substring(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1', 'body': 'bodycontent'}
        exp_request = {'method': 'GET'}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))
        exp_request = {'path': 'hostname'}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))
        exp_request = {'body': 'content'}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))

    def test_020_request_matcher_regex(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1', 'body': 'bodycontent'}
        exp_request = {'body': 'b.dy.onte.t'}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))

    def test_030_request_matcher_empty_request_body(self):
        req = {'method': 'GET', 'path': 'http://hostname.com/subp1'}
        exp_request = {'method': 'GET'}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))
        exp_request = {'path': 'hostname'}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))
        exp_request = {'body': 'content'}
        self.assertFalse(ExpectationMatcher.is_expectation_match_request(exp_request, req))

    def test_040_request_matcher_headers(self):
        req = {'method': 'GET', 'path': '', 'headers': {'h1': 'hv1'}}
        req = dict(req)
        exp_request = {'headers': {'h1': 'hv1'}}
        self.assertTrue(ExpectationMatcher.is_expectation_match_request(exp_request, req))
        exp_request = {'headers': {'h1': 'hv2'}}
        self.assertFalse(ExpectationMatcher.is_expectation_match_request(exp_request, req))