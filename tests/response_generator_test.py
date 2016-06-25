import unittest
from incoming_request import IncomingRequest
from response_generator import ResponseGenerator


class ResponseGeneratorTest(unittest.TestCase):
    def test_010_text_response(self):
        req = IncomingRequest('pathv', {'h1': 'hv1'}, 'bodyv', {'c1': 'cv1'})
        resp = ResponseGenerator.generate(req)
        self.assertIn('pathv', resp)
        self.assertIn("'h1': 'hv1'", resp)
        self.assertIn('bodyv', resp)
        self.assertIn("'c1': 'cv1'", resp)


    def test_020_expected_response(self):
        req = IncomingRequest('pathv', {'h1': 'hv1'}, 'bodyv', {'c1': 'cv1'})
        exp = {'request': {'path': 'pathv'}, 'action': ''}
        ResponseGenerator.add_expectation(exp)
        resp = ResponseGenerator.generate(req)
        self.assertEquals(200, resp.status_code)
        self.assertEquals('Mock answer!'.encode(), resp.data)