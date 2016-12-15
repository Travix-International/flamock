import time
import urllib3
import logging
import requests
from requests.status_codes import codes
from custom_reponse import CustomResponse
from json_logging import JsonLogging
from log_container import LogContainer
from expectation_matcher import ExpectationMatcher
from extensions import Extensions


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

    host_whitelist = []
    log_container = None
    logs_url = None

    _logger = None
    _expectation_manager = None

    def __init__(self, expectation_manager=None, logger=None):
        if logger is None:
            self._logger = JsonLogging(logging.getLogger(__name__))
        else:
            self._logger = logger

        self._expectation_manager = expectation_manager
        self.log_container = LogContainer()

    def apply_action_from_expectation_to_request(self, expectation, request):
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
            return self.make_forward_request(expectation['forward'], request)
        return None

    def generate_response(self, request):
        """
        Makes response for request.
        Two main actions is possible:
        - response : returns saved response
        - forward : makes request to 3rd resource

        :param request: Any request into mock
        :return: custom response with result
        """
        self.log_container.add({'request': request})
        if self.logs_url is None:
            self._logger.info("Log id %s for request %s %s headers: %s" % (self.log_container.get_latest_id(), request['method'], request['path'], request['headers']))
        else:
            self._logger.info("Log %s/%s for request %s %s headers: %s" % (self.logs_url, self.log_container.get_latest_id(), request['method'], request['path'], request['headers']))

        if len(self.host_whitelist) > 0:
            request_headers = request['headers'] if 'headers' in request else []
            request_host = request_headers['Host'] if len(request_headers) > 0 and 'Host' in request['headers'] else ""
            has_wl_match = False
            for wl_host in self.host_whitelist:
                has_wl_match = has_wl_match or ExpectationMatcher.value_matcher(wl_host, request_host)

            if not has_wl_match:
                self._logger.warning("Request's host '%s' not in a white list!" % request_host)
                response = CustomResponse(status_code=codes.not_allowed)
                self.log_container.update_last_with_kv('response', response)
                return response

        list_matched_expectations = self._expectation_manager.get_matched_expectations_for_request(request)

        if len(list_matched_expectations) > 0:
            expectation = Extensions.order_by_priority(list_matched_expectations)[0]
            self._logger.debug("Matched expectation: %s" % expectation)
            response = self.apply_action_from_expectation_to_request(expectation, request)
        else:
            self._logger.warning("List of expectations is empty!")
            response = CustomResponse("No expectation for request: " + str(request))
        self.log_container.update_last_with_kv('response', response.to_dict())
        self._logger.debug("Response: %s" % response)
        return response

    def make_forward_request(self, expectation_forward, request):
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
        self.log_container.update_last_with_kv('forward', {
            "request_method": request_method,
            "url": url_for_request,
            "body": CustomResponse.remove_linebreaks(request_body),
            "headers": forward_headers})
        self._logger.debug("Forward request: %s %s body: %s headers: %s" % (
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
            self._logger.exception(e)
            cust_resp = CustomResponse(str(e), codes.not_found)
        return cust_resp

    def clear_log_messages(self):
        self.log_container.clear()

    def return_log_messages(self, id):
        if len(id) > 0:
            try:
                id = int(id)
            except ValueError:
                self._logger.error("Id for log message is not integer!")
            if id in self.log_container.container:
                return CustomResponse(str(self.log_container.container[id]))
        return CustomResponse(str(self.log_container.container))

