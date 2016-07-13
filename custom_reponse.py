from requests.status_codes import codes


class CustomResponse(object):
    _status_code = codes.ok
    _text = ''
    _headers = {}

    @property
    def text(self):
        return self._text

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers

    def __init__(self, text='', status_code=codes.ok, headers={}):
        self._status_code = status_code
        self._text = text
        self._headers = headers

    def __str__(self):
        return "status_code: %s, text: %s, headers: %s" % (self._status_code, self._text, self._headers)

    def to_flask_response(self):
        from flask import make_response
        return make_response((self._text,self._status_code, self._headers))
