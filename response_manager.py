import re
import time
import urllib3
import logging
import requests
from requests.status_codes import codes
from expectation_manager import ExpectationManager
from custom_reponse import CustomResponse
from json_logging import JsonLogging
from log_container import LogContainer
from expectation_matcher import ExpectationMatcher


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

     - delay # int
     - priority # int. 0 - lowest priority

    """

    logger = JsonLogging(logging.getLogger(__name__))
    host_whitelist = []
    log_container = LogContainer()
    logs_url = None

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
            if 'request' not in expectation or ExpectationMatcher.is_expectation_match_request(expectation['request'], request):
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
        if 'delay' in expectation:
            time.sleep(int(expectation['delay']))

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
        cls.log_container.add({'request': request})
        if cls.logs_url is None:
            cls.logger.info("Log id %s for request %s %s headers: %s" % (cls.log_container.get_latest_id(), request['method'], request['path'], request['headers']))
        else:
            cls.logger.info("Log %s/%s for request %s %s headers: %s" % (cls.logs_url, cls.log_container.get_latest_id(), request['method'], request['path'], request['headers']))

        if len(cls.host_whitelist) > 0:
            request_headers = request['headers'] if 'headers' in request else []
            request_host = request_headers['Host'] if len(request_headers) > 0 and 'Host' in request['headers'] else ""
            has_wl_match = False
            for wl_host in cls.host_whitelist:
                has_wl_match = has_wl_match or ExpectationMatcher.value_matcher(wl_host, request_host)

            if not has_wl_match:
                cls.logger.warning("Request's host '%s' not in a white list!" % request_host)
                response = CustomResponse(status_code=codes.not_allowed)
                cls.log_container.update_last_with_kv('response', response)
                return response

        list_matched_expectations = cls.get_matched_expectations_for_request(request)

        if len(list_matched_expectations) > 0:
            expectation = cls.sort_expectation_list_according_priority(list_matched_expectations)[0]
            cls.logger.debug("Matched expectation: %s" % expectation)
            response = cls.apply_action_from_expectation_to_request(expectation, request)
        else:
            cls.logger.warning("List of expectations is empty!")
            response = CustomResponse("No expectation for request: " + str(request))
        cls.log_container.update_last_with_kv('response', response.to_dict())
        cls.logger.debug("Response: %s" % response)
        return response

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
        cls.log_container.update_last_with_kv('forward', {
            "request_method": request_method,
            "url": url_for_request,
            "body": CustomResponse.remove_linebreaks(request_body),
            "headers": forward_headers})
        cls.logger.debug("Forward request: %s %s body: %s headers: %s" % (
            request_method, url_for_request, CustomResponse.remove_linebreaks(request_body), forward_headers))

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.ERROR)

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
    def return_logged_messages(cls, id):
        if len(id) > 0:
            try:
                id = int(id)
            except ValueError:
                cls.logger.error("Id for log message is not integer!")
            if id in cls.log_container.container:
                return CustomResponse(str(cls.log_container.container[id]))
        return CustomResponse(str(cls.log_container.container))

