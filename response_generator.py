import re
import logging
import requests
from urllib.parse import urlparse
from expectation_manager import ExpectationManager
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
     - - scheme
     - - host

     - response
     - - httpcode
     - - headers
     - - body

     - misc
     - - delay
     - - remaining_times
     - - unlimited

    """
    re_flags = re.DOTALL

    @classmethod
    def generate(cls, request):
        if len(ExpectationManager.expectations) > 0:
            for key, expectation in ExpectationManager.expectations.items():
                if 'request' not in expectation:
                    continue

                if ResponseGenerator.is_expectation_match_request(expectation['request'], request):
                    if 'response' in expectation:
                        expected_response = expectation['response']
                        return FlaskResponse(expected_response['body'], expected_response['httpcode'])

                    if 'forward' in expectation:
                        cls.make_request(expectation['forward'], request)
        return FlaskResponse("No expectation for request: \r\n " + str(request), 200)

    @classmethod
    def value_matcher(cls, expected_value, actual_value):
        try:
            compiled_pattern = re.compile(expected_value, cls.re_flags)
            search_result = compiled_pattern.search(actual_value)
            return search_result is not None
        except TypeError as e:
            logging.exception(e)
            return expected_value in actual_value

    @classmethod
    def is_expectation_match_request(cls, request_exp, request_act):
        if 'method' in request_exp:
            result = cls.value_matcher(request_exp['method'], request_act['method'])
            if result is False:
                logging.warning('Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                    attribute='method', expected_value=request_exp['method'], actual_value=request_act['method']))
                return False

        if 'path' in request_exp:
            result = cls.value_matcher(request_exp['path'], request_act['path'])
            if result is False:
                logging.warning('Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                        attribute='path', expected_value=request_exp['path'], actual_value=request_act['path']))
                return False
        return True

    @classmethod
    def make_request(cls, expectation_forward, request):
        url = "%s://%s" % (expectation_forward['scheme'], expectation_forward['host'])
        url_obj = urlparse(request['path'])
        url_for_request = request['path'].replace("%s://%s" % (url_obj.scheme, url_obj.netloc), "%s://%s" % (expectation_forward['scheme'], expectation_forward['host']) )
        return requests.request(method=request['method'], url=url_for_request)

    @classmethod
    def do_action(cls, expectation):
        if 'response' in expectation:
            expected_response = expectation['response']
            return FlaskResponse(expected_response['body'], expected_response['httpcode'])
        return None

