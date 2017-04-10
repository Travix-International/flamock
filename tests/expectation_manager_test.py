import json
import logging
import unittest
from logging_format import logging_format

from expectation_manager import ExpectationManager

logging.basicConfig(level=logging.DEBUG, format=logging_format)


class ExpectationManagerTest(unittest.TestCase):
    _expectation_manager = None

    def setUp(self):
        self._expectation_manager = ExpectationManager()

    def test_010_add(self):
        exp = {
            'request': {
                'path': 'pathv'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(200, resp.status_code)
        self.assertEqual(len(self._expectation_manager.get_expectations()), 1)

        for key, value in self._expectation_manager.get_expectations().items():
            self.assertEqual(exp, value)

    def test_020_remove(self):
        exp = {
            'request': {
                'path': 'pathv1'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(200, resp.status_code)
        exp = {
            'request': {
                'path': 'pathv2'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 2)

        for key, value in items:
            resp = self._expectation_manager.remove({'key': key})
            self.assertEquals(200, resp.status_code)
            break
        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 1)

    def test_030_remove_all(self):
        exp = {
            'request': {
                'path': 'pathv1'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(200, resp.status_code)
        exp = {
            'request': {
                'path': 'pathv2'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 2)

        self._expectation_manager.clear()
        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 0)

    def test_040_json_to_dict_positive(self):
        exp = {
            'request': {
                'path': 'pathv1'
            },
            'response': {
                'httpcode': 200,
                'body': 'Mock answer!'
            }}
        exp_dict, resp = self._expectation_manager.json_to_dict(json.dumps(exp))
        self.assertEquals(200, resp.status_code)
        self.assertEquals(exp_dict['request'], exp['request'])
        self.assertEquals(exp_dict['response']['httpcode'], exp['response']['httpcode'])
        self.assertEquals(exp_dict['response']['body'], exp['response']['body'])

    def test_050_json_to_dict_negative(self):
        exp = "{'request': {'path': 'pathv1'}," \
              " 'response': {'httpcode': 200, 'body': 'Mock answer!'}}"
        exp_dict, resp = self._expectation_manager.json_to_dict(str(exp))
        self.assertEquals(400, resp.status_code)
        self.assertEquals(exp_dict, None)

    def test_060_add_expectation_with_key(self):
        custom_key = 'custom_key'
        exp = {
            'key': custom_key,
            'request': {
                'path': 'pathv1'
            },
            'response': {
                'httpcode': 200,
                'body': "Mock answer!"
            }}
        resp = self._expectation_manager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 1)

        resp = self._expectation_manager.remove({'key': custom_key})
        self.assertEquals(200, resp.status_code)

        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 0)

    def test_070_update_existing_expectation(self):
        exp1 = {
            'key': 'custom_key',
            'request': {
                'path': 'pathv1'
            }}
        resp = self._expectation_manager.add(exp1)
        self.assertEquals(200, resp.status_code)

        exp2 = {'key': 'custom_key', 'request': {'path': 'pathv2'}}
        resp = self._expectation_manager.add(exp2)
        self.assertEquals(200, resp.status_code)

        items = self._expectation_manager.get_expectations().items()
        self.assertEqual(len(items), 1)

        for key, value in items:
            self.assertEqual(exp2, value)


if __name__ == '__main__':
    unittest.main()
