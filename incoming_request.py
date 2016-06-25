class IncomingRequest:
    path = ''
    body = ''
    headers = {}
    cookies = {}

    def __init__(self, path='', headers={}, body='', cookies={}):
        self.path = path
        self.headers = headers
        self.body = body
        self.cookies = cookies

    def __str__(self):
        req_to_str = "\r\npath: " + str(self.path)
        if len(self.headers) != 0:
            req_to_str += "\r\nheaders: " + str(self.headers)
        if len(self.body) != 0:
            req_to_str += "\r\nbody: " + str(self.body)
        if len(self.cookies) != 0:
            req_to_str += "\r\ncookies: " + str(self.cookies)
        return req_to_str