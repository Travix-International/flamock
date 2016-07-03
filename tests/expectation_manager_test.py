import json
import unittest

from expectation_manager import ExpectationManager


class ExpectationManagerTest(unittest.TestCase):

    def setUp(self):
        ExpectationManager.expectations.clear()

    def test_010_add(self):
        exp = {'request': {'path': 'pathv'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        self.assertEqual(len(ExpectationManager.expectations), 1)

        for key, value in ExpectationManager.expectations.items():
            self.assertEqual(exp, value)

    def test_020_remove(self):
        exp = {'request': {'path': 'pathv1'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        exp = {'request': {'path': 'pathv2'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.get_expectations_as_dict().items()
        self.assertEqual(len(items), 2)

        for key, value in items:
            resp = ExpectationManager.remove({'key': key})
            self.assertEquals(200, resp.status_code)
            break
        items = ExpectationManager.get_expectations_as_dict().items()
        self.assertEqual(len(items), 1)

    def test_030_remove_all(self):
        exp = {'request': {'path': 'pathv1'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        exp = {'request': {'path': 'pathv2'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.get_expectations_as_dict().items()
        self.assertEqual(len(items), 2)

        resp = ExpectationManager.remove_all()
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.get_expectations_as_dict().items()
        self.assertEqual(len(items), 0)

    def test_040_json_to_dict_positive(self):
        exp = {'request': {'path': 'pathv1'}, 'response': {'httpcode': 200, 'body': 'Mock answer!'}}
        exp_dict, resp = ExpectationManager.json_to_dict(json.dumps(exp))
        self.assertEquals(200, resp.status_code)
        self.assertEquals(exp_dict['request'], exp['request'])
        self.assertEquals(exp_dict['response']['httpcode'], exp['response']['httpcode'])
        self.assertEquals(exp_dict['response']['body'], exp['response']['body'])

    def test_050_json_to_dict_negative(self):
        exp = "{'request': {'path': 'pathv1'}, 'response': {'httpcode': 200, 'body': 'Mock answer!'}}"
        exp_dict, resp = ExpectationManager.json_to_dict(str(exp))
        self.assertEquals(400, resp.status_code)
        self.assertEquals(exp_dict, None)

if __name__ == '__main__':
    unittest.main()
