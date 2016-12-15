import unittest
from custom_reponse import CustomResponse
from flask_factory import FlaskFactory


class CustomResponseTest(unittest.TestCase):
    def test_010_to_flask_response(self):
        app = FlaskFactory.flask_factory()
        text = "\r\n<XML></XML>\r\n"
        resp = CustomResponse(text)
        flask_resp = resp.to_flask_response()
        self.assertEquals(flask_resp.data.decode(), text)