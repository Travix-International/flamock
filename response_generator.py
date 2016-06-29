import re
import hashlib
import logging
from flask import Response as FlaskResponse


class ResponseGenerator:
    """
    possible expectation fields:
     - request
     - - method
     - - path
     - - body
     - - headers # later
     - - - - key
     - - - - value
     - - cookies # later
     - - - - key
     - - - - value

     - forward
     - - protocol
     - - host
     - - port

     - response
     - - httpcode
     - - headers
     - - body

     - misc
     - - delay
     - - remaining_times
     - - unlimited

    """
    expectations = {}  # dict with <md5: json_object>
    re_flags = re.DOTALL

    @classmethod
    def generate(cls, request):
        if len(ResponseGenerator.expectations) > 0:
            for key, expectation in ResponseGenerator.expectations.items():
                if 'request' not in expectation:
                    continue

                if ResponseGenerator.is_expectation_match_request(expectation['request'], request):
                    return ResponseGenerator.do_action(expectation)
        return FlaskResponse("No expectation for request: \r\n " + str(request), 200)

    @classmethod
    def remove_all_expectations(cls, key):
        for key in cls.expectations:
            del(cls.expectations[key])
        return FlaskResponse("All expectations were removed", 200)

    @classmethod
    def remove_expectation(cls, key):
        if key in cls.expectations:
            del(cls.expectations[key])
        return FlaskResponse("Expectation with key %s was removed" % key, 200)

    @classmethod
    def add_expectation(cls, expectation_as_dict):
        key = hashlib.md5(str(expectation_as_dict).encode()).hexdigest()
        if key not in cls.expectations:
            cls.expectations[key] = expectation_as_dict
            return FlaskResponse("Expectation was added with key %s" % key, 200)
        return FlaskResponse("Expectation was not added!", 200)

    @classmethod
    def validate_expectation(cls, expectation_as_dict):
        #todo
        pass

    @classmethod
    def is_expectation_match_request(cls, request_exp, request_act):
        if 'method' in request_exp:
            try:
                if request_exp['method'] != request_act['method']:
                    logging.warning('Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                        attribute='method', expected_value=request_exp['method'], actual_value=request_act['method']))
                    return False
            except AttributeError as e:
                logging.exception(e)
                return False

        if 'path' in request_exp:
            try:
                compiled_pattern = re.compile(request_exp['path'], cls.re_flags)
                search_result = compiled_pattern.search(request_act['path'])
                if search_result is None:
                    logging.warning('Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                        attribute='path', expected_value=request_exp['path'], actual_value=request_act['path']))
                    return False
            except TypeError as e:
                logging.exception(e)
                if request_exp['path'] not in request_act['path']:
                    logging.warning('Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                        attribute='path', expected_value=request_exp['path'], actual_value=request_act['path']))
                    return False
        return True

    @staticmethod
    def do_action(expectation):
        response = None
        if 'response' in expectation:
            expected_response = expectation['response']
            response = FlaskResponse(expected_response['body'], expected_response['httpcode'])
        return response

