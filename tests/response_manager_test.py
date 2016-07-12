import unittest
import logging
from flamock import logging_format
from custom_reponse import CustomResponse
from expectation_manager import ExpectationManager
from response_manager import ResponseManager

logging.basicConfig(level=logging.DEBUG, format=logging_format)


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

    @staticmethod
    def request_mock(method='', url=''):
        return CustomResponse("method: %s, url: %s" % (method, url), 302)

    def test_050_make_request(self):
        req_method = 'GET'
        req_path = 'subp1/subp2.aspx'
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        exp_forward = {'scheme': real_scheme, 'host': real_host}
        import requests
        requests.request = ResponseManagerTest.request_mock

        resp = ResponseManager.make_request(exp_forward, req_method, req_path)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.text,
                         "method: %s, url: %s" % (req_method, '%s://%s/%s' % (real_scheme, real_host, req_path)))

    def test_060_request_matches_forward(self):
        mock_path = 'subp1/subp2.aspx'
        fwd_host = 'real_hostname.com'
        fwd_scheme = 'https'

        req = {'method': 'GET', 'path': mock_path, 'body': 'bodycontent'}
        exp = {'request': {'path': 'subp1/subp2.aspx'}, 'forward': {'scheme': fwd_scheme, 'host': fwd_host}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(resp.status_code, 200)

        import requests
        requests.request = ResponseManagerTest.request_mock

        resp = ResponseManager.generate_response(req)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.text,
                         "method: %s, url: %s" % (req['method'], '%s://%s/%s' % (fwd_scheme, fwd_host, mock_path)))

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

    @staticmethod
    def make_request_mock(expectation_forward, request_method, request_path):
        return CustomResponse(expectation_forward['body'], expectation_forward['httpcode'])

    def test_070_apply_action_from_expectation_to_request_response_test(self):
            exp_resp = {'response': {'body': 'RSP', 'httpcode': 203}}

            cust_resp = ResponseManager.apply_action_from_expectation_to_request(exp_resp, None)
            self.assertEquals(cust_resp.status_code, exp_resp['response']['httpcode'])
            self.assertEquals(cust_resp.text, exp_resp['response']['body'])

    def test_080_apply_action_from_expectation_to_forward_test(self):
            exp_fwd = {'forward': {'body': 'FWD', 'httpcode': 302}}
            req_method = 'GET'
            req_path = 'sub1/sub2.xt'
            req = {'method': req_method, 'path': req_path}

            ResponseManager.make_request = self.make_request_mock
            cust_resp = ResponseManager.apply_action_from_expectation_to_request(exp_fwd, req)
            self.assertEquals(cust_resp.status_code, exp_fwd['forward']['httpcode'])
            self.assertEquals(cust_resp.text, exp_fwd['forward']['body'])

    def test_090_empty_expectation_response_default_values(self):
            req = {'path': 'pathv'}
            exp = {'request': {'path': 'pathv'}, 'response': {}}
            ExpectationManager.add(exp)
            resp = ResponseManager.generate_response(req)
            self.assertEquals(200, resp.status_code)
            self.assertEquals('', resp.text)

if __name__ == '__main__':
    unittest.main()

