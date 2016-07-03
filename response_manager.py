import re
import logging
import requests
from urllib.parse import urlparse
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse


class ResponseManager:
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
    def generate_response(cls, request):
        """
        Makes response for request.
        Two main actions is possible:
        - response : returns saved response
        - forward : makes request to 3rd resource

        :param request: Any request into mock
        :return: custom response with result
        """
        expectations = ExpectationManager.get_expectations_as_dict()
        if len(expectations) > 0:
            for key, expectation in expectations.items():
                if 'request' not in expectation:
                    continue

                if ResponseManager.is_expectation_match_request(expectation['request'], request):
                    if 'response' in expectation:
                        expected_response = expectation['response']
                        return CustomResponse(expected_response['body'], expected_response['httpcode'])

                    if 'forward' in expectation:
                        cls.make_request(expectation['forward'], request)
        return CustomResponse("No expectation for request:\r\n" + str(request))

    @classmethod
    def value_matcher(cls, expected_value, actual_value):
        """
        compares two values: actual and expected. Try to decide expected value as regex pattern.
        If unsuccssfull, try to find expected value as substring of actual
        :param expected_value: regex pattern or string
        :param actual_value: string
        :return: true if actual value matches expected value or contains expected value as substring. Otherwise - false
        """
        try:
            compiled_pattern = re.compile(expected_value, cls.re_flags)
            search_result = compiled_pattern.search(actual_value)
            return search_result is not None
        except TypeError as e:
            logging.exception(e)
            return expected_value in actual_value

    @classmethod
    def is_expectation_match_request(cls, request_exp, request_act):
        """
        Compares two requests field by field
        :param request_exp: request from expectations
        :param request_act: actual request
        :return: True if all fields of actual request are match to particular expected request
        """
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
        """
        Makes request to 3rd party
        :param expectation_forward: description of forwarding request
        :param request: actual request is been forwarded
        :return: response from 3rd party as CustomResponse
        """
        url = "%s://%s" % (expectation_forward['scheme'], expectation_forward['host'])
        url_obj = urlparse(request['path'])
        url_for_request = request['path'].replace("%s://%s" % (url_obj.scheme, url_obj.netloc), "%s://%s" % (expectation_forward['scheme'], expectation_forward['host']) )
        resp = requests.request(method=request['method'], url=url_for_request)
        return CustomResponse(resp.text, resp.status_code)

    @classmethod
    def do_action(cls, expectation):
        if 'response' in expectation:
            expected_response = expectation['response']
            return CustomResponse(expected_response['body'], expected_response['httpcode'])
        return None

