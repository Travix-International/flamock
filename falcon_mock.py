'''
import falcon
from expectation_manager import ExpectationManager


class FalconMock(object):
    def on_get(self, req, resp):
        pass


class FalconMockAdmin(object):
    def on_get(self, req, resp, path):
        if path == 'remove_all_expectations':
            resp = ExpectationManager.remove_all().to_falcon_response()

app = falcon.API()
falcon_mock = FalconMock()
falcon_mock_admin = FalconMockAdmin()

app.add_route('/flamock/<path>', falcon_mock_admin)
'''