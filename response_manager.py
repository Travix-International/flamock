import re
import urllib3
import logging
import requests
from requests.status_codes import codes
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse

class ResponseManager:
    """
    possible expectation fields:
     - request
     - - method
     - - path
     - - body
     - - headers
     - - - - key
     - - - - value

     - forward
     - - scheme
     - - host
     - - headers
     - - - - key
     - - - - value

     - response
     - - httpcode
     - - headers
     - - body

     - priority # int. 0 - lowest priority

    """
    re_flags = re.DOTALL
    logger = logging.getLogger(__name__)

    @classmethod
    def sort_expectation_list_according_priority(cls, list_of_expectations):
        """
        Sorts  list of dicts according key 'priority'.
        0 - lowest priority. Item with highest priority will be as first element
        :param list_of_expectations: list of dicts with key 'priority'
        :return: sorted list of dicts. first element has the biggest 'priority'
        """
        sorted_list = sorted(list_of_expectations,
                             key=lambda exp: exp['priority'] if 'priority' in exp else 0,
                             reverse=True)
        return sorted_list

    @classmethod
    def get_matched_expectations_for_request(cls, request):
        """
        Gets list of all matched expectations for this request
        :param request: incoming request
        :return: list of all matched expectations in random order
        """
        list_matched_expectations = []
        expectations = ExpectationManager.get_expectations_as_dict()
        if len(expectations) == 0:
            return list_matched_expectations

        for key, expectation in expectations.items():
            if 'request' not in expectation or cls.is_expectation_match_request(expectation['request'], request):
                list_matched_expectations.append(expectation)
        cls.logger.debug("Count of matched expectations: %s" % len(list_matched_expectations))
        return list_matched_expectations

    @classmethod
    def apply_action_from_expectation_to_request(cls, expectation, request):
        """
        executes 'action' of expectation
        :param expectation: expectation to be executed
        :param request: incoming request
        :return: custom response with result of action
        """
        if 'response' in expectation:
            expected_response = expectation['response']
            response_body = expected_response['body'] if 'body' in expected_response else ""
            response_code = expected_response['httpcode'] if 'httpcode' in expected_response else 200
            response_headers = expected_response['headers'] if 'headers' in expected_response else {}
            return CustomResponse(text=response_body, status_code=response_code, headers=response_headers)

        if 'forward' in expectation:
            return cls.make_forward_request(expectation['forward'], request)
        return None

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
        cls.logger.info("Request: %s" % request)
        list_matched_expectations = cls.get_matched_expectations_for_request(request)

        if len(list_matched_expectations) > 0:
            expectation = cls.sort_expectation_list_according_priority(list_matched_expectations)[0]
            cls.logger.debug("Matched expectation: %s" % expectation)
            response = cls.apply_action_from_expectation_to_request(expectation, request)
        else:
            cls.logger.warning("List of expectations is empty!")
            response = CustomResponse("No expectation for request: " + str(request))
        cls.logger.info("Response: %s" % response)
        return response

    @classmethod
    def value_matcher_str(cls, expected_value, actual_value):
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
            cls.logger.exception(e)
            return expected_value in actual_value

    @classmethod
    def value_matcher_dict(cls, expected_dict, actual_dict):
        """
        compares two dictionaries
        :param expected_dict: dict
        :param actual_dict: dict
        :return: true if actial dict contains all the headers from expected
        """
        for key, value in expected_dict.items():
            if key not in actual_dict:
                return False

            if value != actual_dict[key]:
                return False
        return True

    @classmethod
    def value_matcher(cls, expected_value, actual_value):
        """
        compares two values: actual and expected. Depends on types (str or dict) uses particular matcher
        :returns  True or False

        """
        if isinstance(expected_value, str) and isinstance(actual_value, str):
            return cls.value_matcher_str(expected_value, actual_value)
        elif isinstance(expected_value, dict) and isinstance(actual_value, dict):
            return cls.value_matcher_dict(expected_value, actual_value)
        else:
            return False

    @classmethod
    def is_expectation_match_request(cls, request_exp, request_act):
        """
        Compares two requests field by field
        :param request_exp: request from expectations
        :param request_act: actual request
        :return: True if all fields of actual request are match to particular expected request
        """
        list_of_attributes_to_compare = ['method', 'path', 'body', 'headers']

        for attr in list_of_attributes_to_compare:
            if attr in request_exp:
                result = (attr in request_act) and cls.value_matcher(request_exp[attr], request_act[attr])
                if result is False:
                    cls.logger.debug(
                        'Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                            attribute=attr,
                            expected_value=request_exp[attr],
                            actual_value=request_act[attr] if attr in request_act else 'None')
                    )
                    return False

        cls.logger.debug('Requests are match expected: {expected_value}, actual: {actual_value}'.format(
                        expected_value=str(request_exp), actual_value=str(request_act)))
        return True

    @classmethod
    def make_forward_request(cls, expectation_forward, request):
        """
        Makes request to 3rd party
        :param expectation_forward: description of forwarding request
        :param request: actual request is been forwarded
        :return: response from 3rd party as CustomResponse
        """
        headers_in_request_to_ignore = ['Host', 'Content-Encoding', 'Content-Length']
        headers_in_response_to_ignore = ['Content-Encoding', 'Content-Length', 'Transfer-Encoding', 'Strict-Transport-Security']
        request_method = request['method'] if 'method' in request else 'GET'
        request_path = request['path'] if 'path' in request else '/'
        request_body = request['body'] if 'body' in request else ''
        request_headers = request['headers'] if 'headers' in request else {}

        url_for_request = "%s://%s/%s" % (expectation_forward['scheme'], expectation_forward['host'], request_path)

        forward_headers = {}
        for key, value in request_headers.items():
            if key not in headers_in_request_to_ignore:
                forward_headers[key] = value

        if 'headers' in expectation_forward:
            for key, value in expectation_forward['headers'].items():
                forward_headers[key] = value

        cls.logger.info("Make forward request: %s %s body: %s headers: %s" % (
            request_method, url_for_request, CustomResponse.remove_linebreaks(request_body), forward_headers))

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            resp = requests.request(
                method=request_method,
                url=url_for_request,
                data=request_body,
                headers=forward_headers,
                verify=False,
                timeout=60)

            response_headers = {}
            for key, value in resp.headers.items():
                if key not in headers_in_response_to_ignore:
                    response_headers[key] = value

            cust_resp = CustomResponse(resp.content, resp.status_code, response_headers)
        except Exception as e:
            cls.logger.exception(e)
            cust_resp = CustomResponse(str(e), codes.not_found)
        return cust_resp

    @classmethod
    def do_action(cls, expectation):
        if 'response' in expectation:
            expected_response = expectation['response']
            return CustomResponse(expected_response['body'], expected_response['httpcode'])
        return None

    @classmethod
    def headers_list_to_dict(cls, headers_list):
        headers_dict = {}
        for key, value in headers_list:
            headers_dict[key] = value
        return headers_dict

