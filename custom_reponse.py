from requests.status_codes import codes

class CustomResponse(object):
    _status_code = codes.ok
    _text = ''

    @property
    def text(self):
        return self._text

    @property
    def status_code(self):
        return self._status_code

    def __init__(self, text='', status_code=codes.ok):
        self._status_code = status_code
        self._text = text

    def to_flask_response(self):
        from flask import Response as FlaskResponse
        return FlaskResponse(self._text, self._status_code )