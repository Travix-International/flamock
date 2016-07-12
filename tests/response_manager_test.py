import unittest
import logging
import requests
from flamock import logging_format
from custom_reponse import CustomResponse
from expectation_manager import ExpectationManager
from response_manager import ResponseManager

logging.basicConfig(level=logging.DEBUG, format=logging_format)


def request_mock(method='', url='', data=''):
    return CustomResponse("method: %s, url: %s, body: %s" % (method, url, data), 302)

requests.request = request_mock


class ResponseManagerTest(unittest.TestCase):

    def setUp(self):
        ExpectationManager.remove_all()

    def test_010_no_expectation(self):
        req = {'path': 'pathv', 'headers': {'h1': 'hv1'}, 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        resp = ResponseManager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        # self.assertIn('No expectation for request:'.encode(), resp.data)
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

    def test_050_make_request(self):
        req = {'method': 'POST', 'path': 'subp1/subp2.aspx', 'body': 'bodycontent'}
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        exp_forward = {'scheme': real_scheme, 'host': real_host}
        resp = ResponseManager.make_request(exp_forward, req)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.text,
                         "method: %s, url: %s, body: %s"
                         % (
                             req['method'],
                             '%s://%s/%s' % (real_scheme, real_host, req['path']),
                             req['body'])
                         )

    def test_060_request_matches_forward(self):
        req = {'method': 'GET', 'path': 'subp1/subp2.aspx', 'body': 'bodycontent'}
        exp = {'request': {'path': 'subp1/subp2.aspx'}, 'forward': {'scheme': 'https', 'host': 'real_hostname.com'}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(resp.status_code, 200)

        resp = ResponseManager.generate_response(req)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.text,
                         "method: %s, url: %s, body: %s" % (
                             req['method'],
                             '%s://%s/%s' % (exp['forward']['scheme'], exp['forward']['host'], req['path']),
                             req['body'])
                         )

    def test_060_priority_sort_test(self):
            list_of_exp = [
                {'priority': 1},
                {'priority': 3},
                {'priority': 2},
                {'not_priority': 0},
            ]
            expected_list = [
                {'priority': 3},
                {'priority': 2},
                {'priority': 1},
                {'not_priority': 0},
            ]
            sorted_list = ResponseManager.sort_expectation_list_according_priority(list_of_exp)
            self.assertEquals(sorted_list, expected_list)

    def test_070_apply_action_from_expectation_to_request_response_test(self):
            exp_resp = {'response': {'body': 'RSP', 'httpcode': 203}}

            cust_resp = ResponseManager.apply_action_from_expectation_to_request(exp_resp, None)
            self.assertEquals(cust_resp.status_code, exp_resp['response']['httpcode'])
            self.assertEquals(cust_resp.text, exp_resp['response']['body'])

    def test_080_apply_action_from_expectation_to_forward_test(self):
            exp = {'forward': {'scheme': 'https', 'host': 'fwd_host'}}
            req = {'method': 'GET', 'path': 'sub1/sub2.xt'}

            cust_resp = ResponseManager.apply_action_from_expectation_to_request(exp, req)
            self.assertEquals(cust_resp.status_code, 302)
            self.assertEquals(cust_resp.text,
                              "method: %s, url: %s, body: %s" % (
                                  req['method'],
                                  '%s://%s/%s' % (exp['forward']['scheme'], exp['forward']['host'], req['path']),
                                  '')
                              )

    def test_090_empty_expectation_response_default_values(self):
            req = {'path': 'pathv'}
            exp = {'request': {'path': 'pathv'}, 'response': {}}
            ExpectationManager.add(exp)
            resp = ResponseManager.generate_response(req)
            self.assertEquals(200, resp.status_code)
            self.assertEquals('', resp.text)

if __name__ == '__main__':
    unittest.main()

