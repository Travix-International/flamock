import unittest
from requests.status_codes import codes
from custom_reponse import CustomResponse

class CustomResponseTest(unittest.TestCase):

    def test_010_response_to_falcon(self):
        '''
        from falcon.status_codes import HTTP_200
        resp = CustomResponse("msg", codes.ok)
        falcon_resp = resp.to_falcon_response()
        self.assertEquals(falcon_resp.status, HTTP_200)
        self.assertEquals(falcon_resp.body, resp.text)
        '''
        pass