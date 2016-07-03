import unittest
import requests
import logging
import json
from flask import jsonify
import uuid

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class FlamockTest(unittest.TestCase):
    host = 'http://127.0.0.1:5000'

    """
    def login_action(self):
        resp = requests.post(self.host + '/login', json={"login": "admin", "password": "pass"})
        self.assertEquals(resp.status_code, 200)
        resp_json = resp.json()
        self.assertIn('token', resp_json)
        return resp_json['token']

    def test_no_login(self):
        self.assertEqual(requests.get(self.host + '/').status_code, 401)

    def test_login_ok(self):
        resp = requests.post(self.host + '/login', json={"login": "admin", "password": "pass"})
        print(resp.text)
        self.assertEquals(resp.status_code, 200)

    def test_login_err(self):
        resp = requests.post(self.host + '/login', json={"login": "admin", "password": "pass_wrong"})
        print(resp.text)
        self.assertEquals(resp.status_code, 403)

    def test_login_and_request(self):
        token = self.login_action()
        self.assertEqual(requests.get(self.host + '/', headers={'Token': token}).status_code, 200)

    def test_users_getall(self):
        token = self.login_action()
        resp = requests.post(self.host + '/users', headers={'Token': token}, json=
        {
            "action": "getall"
        })
        print(resp.content)
        self.assertEqual(resp.status_code, 200)

    def test_users_add(self):
        token = self.login_action()
        resp = requests.post(self.host + '/users', headers={'Token': token}, json=
        {
          "action": "add",
          "data":
          {
            "login": "test_add",
            "password": "test_add"
          }
        })
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
    """
    def test_010_get_simple(self):
        resp = requests.get(self.host + '/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hello World!', resp.text)

    def test_020_get_path(self):
        resp = requests.get(self.host + '/a/b/c')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hello World!', resp.text)
        self.assertIn('path: a/b/c', resp.text)

    def test_030_get_headers(self):
        resp = requests.get(self.host, headers={'header1': 'header1_value', 'header2': 'header2_value'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hello World!', resp.text)
        self.assertIn('Header1: header1_value', resp.text)
        self.assertIn('Header2: header2_value', resp.text)

    def test_040_get_cookies(self):
        resp = requests.get(self.host, cookies={'cookie1': 'cookie1_value', 'cookie2': 'cookie2_value'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Hello World!', resp.text)
        self.assertIn("'cookie1': 'cookie1_value'", resp.text)
        self.assertIn("'cookie2': 'cookie2_value'", resp.text)
#    def test_db(self):
#        role = Roles("test" + str(uuid.uuid4()))
#        db.session.add(role)
#        db.session.commit()
#        print(Roles.query.all())

if __name__ == '__main__':
    unittest.main()