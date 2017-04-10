import logging
import time
import unittest

from custom_reponse import CustomResponse
from expectation_manager import ExpectationManager
from logging_format import logging_format
from response_manager import ResponseManager

logging.basicConfig(level=logging.DEBUG, format=logging_format)

request_mock_response_code = 302
request_mock_response_template = "method: %s, url: %s, body: %s, headers: %s"
request_mock_response_headers = {'mock_header': 'mock_header_value', 'Content-Encoding': 'gzip'}


def do_request_mock(method='', url='', data='', headers=None, **kwarg):
    if headers is None:
        headers = {}

    mock_headers = headers.copy()
    mock_headers.update(request_mock_response_headers)
    rep_str = request_mock_response_template % (method, url, data, headers)
    obj = CustomResponse(rep_str, request_mock_response_code, mock_headers)
    obj.content = rep_str

    return obj


class ResponseManagerTest(unittest.TestCase):
    _response_manager = None
    _expectation_manager = None

    def setUp(self):
        self._expectation_manager = ExpectationManager()
        self._response_manager = ResponseManager(self._expectation_manager)
        self._response_manager._do_request = do_request_mock

    def test_010_no_expectation(self):
        req = {'method': 'GET', 'path': 'pathv', 'headers': [('h1', 'hv1')], 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        resp = self._response_manager.generate_response(req)

        self.assertEquals(200, resp.status_code)
        self.assertIn('No expectation for request:', resp.text)
        self.assertIn('pathv', resp.text)
        self.assertIn("[('h1', 'hv1')]", resp.text)
        self.assertIn('bodyv', resp.text)
        self.assertIn("'c1': 'cv1'", resp.text)

    def test_020_expected_response(self):
        req = {'method': 'GET', 'path': 'pathv', 'headers': [('h1', 'hv1')], 'body': 'bodyv', 'cookies': {'c1': 'cv1'}}
        exp = {'request': {'path': 'pathv'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        self._expectation_manager.add(exp)
        resp = self._response_manager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('Mock answer!', resp.text)

    def test_050_make_request(self):
        req = {'method': 'POST', 'path': 'subp1/subp2.aspx', 'body': 'bodycontent', 'headers': {'h1': 'hv1'}}
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        exp_forward = {'scheme': real_scheme, 'host': real_host}
        resp = self._response_manager.make_forward_request(exp_forward, req)
        self.assertEqual(request_mock_response_code, resp.status_code)

        self.assertEqual(request_mock_response_template
                         % (
                             req['method'],
                             '%s://%s/%s' % (real_scheme, real_host, req['path']),
                             req['body'],
                             req['headers'])
                         ,
                         resp.text)

        expected_headers = request_mock_response_headers.copy()
        expected_headers.update(req['headers'])
        del (expected_headers['Content-Encoding'])
        self.assertEqual(resp.headers, expected_headers)

    def test_060_request_matches_forward(self):
        req = {'method': 'GET', 'path': 'subp1/subp2.aspx', 'body': 'bodycontent', 'headers': {}}
        exp = {'request': {'path': 'subp1/subp2.aspx'}, 'forward': {'scheme': 'https', 'host': 'real_hostname.com'}}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(resp.status_code, 200)

        resp = self._response_manager.generate_response(req)

        self.assertEqual(resp.status_code, request_mock_response_code)
        self.assertEqual(resp.text,
                         request_mock_response_template % (
                             req['method'],
                             '%s://%s/%s' % (exp['forward']['scheme'], exp['forward']['host'], req['path']),
                             req['body'],
                             '{}')
                         )

    def test_070_apply_action_from_expectation_to_request_response_test(self):
        exp_resp = {'response': {'body': 'RSP', 'httpcode': 203}}

        cust_resp = self._response_manager.apply_action_from_expectation_to_request(exp_resp, None)
        self.assertEquals(cust_resp.status_code, exp_resp['response']['httpcode'])
        self.assertEquals(cust_resp.text, exp_resp['response']['body'])

    def test_080_apply_action_from_expectation_to_forward_test(self):
        exp = {'forward': {'scheme': 'https', 'host': 'fwd_host'}}
        req = {'method': 'GET', 'path': 'sub1/sub2.xt'}

        cust_resp = self._response_manager.apply_action_from_expectation_to_request(exp, req)
        self.assertEquals(cust_resp.status_code, request_mock_response_code)
        self.assertEquals(cust_resp.text,
                          request_mock_response_template % (
                              req['method'],
                              '%s://%s/%s' % (exp['forward']['scheme'], exp['forward']['host'], req['path']),
                              '',
                              '{}')
                          )

    def test_090_empty_expectation_response_default_values(self):
        req = {'method': 'GET', 'path': 'pathv', 'headers': ''}
        exp = {'request': {'path': 'pathv'}, 'response': {}}
        self._expectation_manager.add(exp)
        resp = self._response_manager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('', resp.text)

    def test_110_make_request_ignore_host_in_header(self):
        req = {
            'method': 'POST',
            'path': 'subp1/subp2.aspx',
            'body': 'bodycontent',
            'headers': {'h1': 'hv1', 'Host': 'travix.com'}
        }
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        exp_forward = {'scheme': real_scheme, 'host': real_host}
        resp = self._response_manager.make_forward_request(exp_forward, req)
        self.assertEqual(resp.status_code, request_mock_response_code)
        self.assertEqual(request_mock_response_template
                         % (
                             req['method'],
                             '%s://%s/%s' % (real_scheme, real_host, req['path']),
                             req['body'],
                             {'h1': 'hv1'}),
                         resp.text)

    def test_120_make_request_check_headers(self):
        req = {'method': 'POST',
               'path': 'subp1/subp2.aspx',
               'body': 'bodycontent',
               'headers': {'h1': 'hv1', 'Content-Length': '100'}
               }
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        exp_forward = {'scheme': real_scheme, 'host': real_host}
        resp = self._response_manager.make_forward_request(exp_forward, req)
        self.assertEqual(resp.status_code, request_mock_response_code)
        self.assertEqual(resp.text,
                         request_mock_response_template
                         % (
                             req['method'],
                             '%s://%s/%s' % (real_scheme, real_host, req['path']),
                             req['body'],
                             {'h1': 'hv1'})
                         )
        expected_headers = request_mock_response_headers.copy()
        expected_headers.update(req['headers'])
        del (expected_headers['Content-Length'])
        del (expected_headers['Content-Encoding'])

        self.assertEqual(resp.headers, expected_headers)

    def test_130_make_request_ignore_content_encoding_in_header(self):
        req = {'method': 'POST',
               'path': 'subp1/subp2.aspx',
               'body': 'bodycontent',
               'headers': {'h1': 'hv1', 'Content-Encoding': 'gzip'}
               }
        real_host = 'real_hostname.com'
        real_scheme = 'https'

        exp_forward = {'scheme': real_scheme, 'host': real_host}
        resp = self._response_manager.make_forward_request(exp_forward, req)
        self.assertEqual(resp.status_code, request_mock_response_code)
        self.assertEqual(resp.text,
                         request_mock_response_template
                         % (
                             req['method'],
                             '%s://%s/%s' % (real_scheme, real_host, req['path']),
                             req['body'],
                             {'h1': 'hv1'})
                         )

    def test_160_return_response_with_header(self):
        req = {'method': 'GET', 'path': 'pathv', 'headers': ''}
        exp = {'request': {'path': 'pathv'}, 'response': {'httpcode': 200, 'headers': {'h1': 'hv1'}}}
        self._expectation_manager.add(exp)
        resp = self._response_manager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('', resp.text)
        self.assertEquals({'h1': 'hv1'}, resp.headers)

    def test_170_expectation_without_request(self):
        req = {'method': 'GET', 'path': 'pathv', 'headers': ''}
        exp = {'response': {'httpcode': 200}}
        self._expectation_manager.add(exp)
        resp = self._response_manager.generate_response(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('', resp.text)

    def test_180_whitelist_request(self):
        self._response_manager.host_whitelist = ["travix.com"]
        hosts_to_check = ['xxnet-403.appspot.com', 'testp1.piwo.pila.pl', 'testp4.pospr.waw.pl']
        for host in hosts_to_check:
            req = {'method': 'GET', 'path': '', 'headers': {'Host': host}}
            resp = self._response_manager.generate_response(req)
            self.assertEquals(405, resp.status_code)

        hosts_to_check = ['blabla.travix.com']
        for host in hosts_to_check:
            req = {'method': 'GET', 'path': '', 'headers': {'Host': host}}
            resp = self._response_manager.generate_response(req)
            self.assertEquals(200, resp.status_code)

    def test_190_delay(self):
        delay = 3
        req = {'method': 'GET', 'path': 'pathv', 'headers': ''}
        exp = {'response': {'httpcode': 200}, 'delay': delay}
        self._expectation_manager.add(exp)
        start_time = time.time()
        resp = self._response_manager.generate_response(req)
        diff = time.time() - start_time
        self.assertEquals(200, resp.status_code)
        self.assertEquals('', resp.text)
        self.assertGreaterEqual(diff, delay)

    def test_200_get_log_messages(self):
        text = "\r\n<XML></XML>\r\n"
        self._response_manager.log_container.add(text)
        resp = self._response_manager.return_log_messages("0")
        self.assertEquals(200, resp.status_code)
        self.assertEquals(text, resp.text)


if __name__ == '__main__':
    unittest.main()
