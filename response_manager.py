import re
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
     - delay
     - remaining_times
     - unlimited
     - priority # int. 0 - lowest priority

    """
    re_flags = re.DOTALL
    logger = logging.getLogger()

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
            if 'request' not in expectation:
                cls.logger.debug("Not found 'request' in expectation. Skip expectation: %s" % expectation)
                continue

            if cls.is_expectation_match_request(expectation['request'], request):
                list_matched_expectations.append(expectation)
        logging.debug("Count of matched expectations: %s" % len(list_matched_expectations))
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
            return CustomResponse(expected_response['body'], expected_response['httpcode'])

        if 'forward' in expectation:
            return cls.make_request(expectation['forward'], request['method'], request['path'])
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
        cls.logger.debug("Incoming request:\r\n%s" % request)
        list_matched_expectations = cls.get_matched_expectations_for_request(request)

        if len(list_matched_expectations) > 0:
            expectation = cls.sort_expectation_list_according_priority(list_matched_expectations)[0]
            cls.logger.debug("Matched expectation: %s" % expectation)
            response = cls.apply_action_from_expectation_to_request(expectation, request)
        else:
            cls.logger.info("list of expectations is empty")
            response = CustomResponse("No expectation for request:\r\n" + str(request))
        logging.debug(str(response))
        return response

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
            cls.logger.exception(e)
            return expected_value in actual_value

    @classmethod
    def is_expectation_match_request(cls, request_exp, request_act):
        """
        Compares two requests field by field
        :param request_exp: request from expectations
        :param request_act: actual request
        :return: True if all fields of actual request are match to particular expected request
        """
        list_of_attributes_to_compare = ['method', 'path', 'body']

        for attr in list_of_attributes_to_compare:
            if attr in request_exp:
                result = cls.value_matcher(request_exp[attr], request_act[attr])
                if result is False:
                    cls.logger.warning(
                        'Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                            attribute=attr, expected_value=request_exp[attr], actual_value=request_act[attr])
                    )
                    return False

        cls.logger.debug('Requests are match expected: {expected_value}, actual: {actual_value}'.format(
                        expected_value=str(request_exp), actual_value=str(request_act)))
        return True

    @classmethod
    def make_request(cls, expectation_forward, request_method, request_path):
        """
        Makes request to 3rd party
        :param expectation_forward: description of forwarding request
        :param request: actual request is been forwarded
        :return: response from 3rd party as CustomResponse
        """
        url_for_request = "%s://%s/%s" % (expectation_forward['scheme'], expectation_forward['host'], request_path)
        logging.debug("url_for_request: %s" % url_for_request)
        try:
            resp = requests.request(method=request_method, url=url_for_request)
            cust_resp = CustomResponse(resp.text, resp.status_code)
        except Exception as e:
            logging.exception(e)
            cust_resp = CustomResponse(str(e), codes.not_found)
        return cust_resp

    @classmethod
    def do_action(cls, expectation):
        if 'response' in expectation:
            expected_response = expectation['response']
            return CustomResponse(expected_response['body'], expected_response['httpcode'])
        return None

