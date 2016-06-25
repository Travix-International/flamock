import re
import hashlib
from flask import Response as FlaskResponse
class ResponseGenerator:
    expectations = {} # dict with <md5: json_object>

    @classmethod
    def generate(cls, request):
        if len(ResponseGenerator.expectations) > 0:
            for key, expectation in ResponseGenerator.expectations.items():
                if 'request' in expectation:
                    if ResponseGenerator.is_expectation_mathces_request(expectation['request'], request):
                        return ResponseGenerator.do_action(expectation['action'])
        return "Hello World! \r\n " + str(request)


    @classmethod
    def add_expectation(cls, expectation_as_dict):
        key = hashlib.md5(str(expectation_as_dict).encode()).hexdigest()
        cls.expectations[key] = expectation_as_dict


    @classmethod
    def validate_expectation(cls, expectation_as_dict):
        #todo
        pass


    @staticmethod
    def is_expectation_mathces_request(request_exp, request_act):
        if 'path' in request_exp:
            if request_exp['path'] == request_act.path:
                return True
        return False

    @staticmethod
    def do_action(action):
        response = FlaskResponse("Mock answer!", 200)
        return response

