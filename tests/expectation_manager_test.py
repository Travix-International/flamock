import sys
import unittest
import logging
from expectation_manager import ExpectationManager

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class ExpectationManagerTest(unittest.TestCase):
    def setUp(self):
        ExpectationManager.expectations.clear()

    def test_010_add(self):
        exp = {'request': {'path': 'pathv'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.expectations.items()
        self.assertEqual(len(items), 1)

        for key, value in items:
            self.assertEqual(exp, value)

    def test_020_remove(self):
        exp = {'request': {'path': 'pathv1'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        exp = {'request': {'path': 'pathv2'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.get_expectations().items()
        self.assertEqual(len(items), 2)

        for key, value in items:
            resp = ExpectationManager.remove(key)
            self.assertEquals(200, resp.status_code)
            break
        items = ExpectationManager.get_expectations().items()
        self.assertEqual(len(items), 1)

    def test_030_remove_all(self):
        exp = {'request': {'path': 'pathv1'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        exp = {'request': {'path': 'pathv2'}, 'response': {'httpcode': 200, 'body': "Mock answer!"}}
        resp = ExpectationManager.add(exp)
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.get_expectations().items()
        self.assertEqual(len(items), 2)

        resp = ExpectationManager.remove_all()
        self.assertEquals(200, resp.status_code)
        items = ExpectationManager.get_expectations().items()
        self.assertEqual(len(items), 0)
