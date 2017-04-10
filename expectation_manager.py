import hashlib
import json

from requests.status_codes import codes

from custom_reponse import CustomResponse
from expectation_matcher import ExpectationMatcher
from json_logging import JsonLogging


class ExpectationManager:
    """
    Class for managing set of expectations

    todo: fix return types
    """
    _expectations = None  # dict with <md5: json_object>
    _logger = JsonLogging

    def __init__(self):
        self._expectations = dict()

    def clear(self):
        """
        :return: custom response
        """
        self._expectations.clear()

    def get_expectations(self):
        """

        :return: expectations as dict. Useful for inner operations
        """
        return self._expectations.copy()

    def get_expectations_as_response(self):
        """
        :return: Expectations as custom response
        """
        return CustomResponse(str(self._expectations))

    def remove(self, dict_with_key):
        """
        Removes particular expectations
        :param dict_with_key: dictionary with field 'key' and md5=value
        :return: custom response
        """
        self._logger.debug("arg: %s" % str(dict_with_key))
        if 'key' in dict_with_key and dict_with_key['key'] in self._expectations:
            del (self._expectations[dict_with_key['key']])
            self._logger.info("Expectation with key %s was removed" % dict_with_key)
            return CustomResponse("Expectation with key %s was removed" % dict_with_key)
        self._logger.error("Expectation with key %s was NOT removed" % dict_with_key)
        return CustomResponse("Error! Expectation with key %s was NOT removed" % dict_with_key, codes.bad)

    def add(self, expectation_as_dict):
        if 'key' in expectation_as_dict:
            key = expectation_as_dict['key']
        else:
            key = hashlib.md5(str(expectation_as_dict).encode()).hexdigest()

        if key in self._expectations:
            self._logger.warning("Expectation with key '%s' already exists. Expectation will be updated" % key)

        self._expectations[key] = expectation_as_dict
        return CustomResponse("Expectation has been added with key '%s'" % key)

    def json_to_dict(self, json_text):
        json_dict = None
        try:
            json_dict = json.loads(json_text)
        except Exception as e:
            self._logger.error("Can't convert json to dict! Json %s" % json_text)
            self._logger.exception(e)
            return json_dict, CustomResponse("Error! Can't convert json to dict! Json %s"
                                             "Exception: %s" % (json_text, str(e)), codes.bad)
        return json_dict, CustomResponse()

    def status(self):
        return CustomResponse("OK")

    def get_matched_expectations_for_request(self, request):
        """
        Gets list of all matched expectations for this request
        :param request: incoming request
        :return: list of all matched expectations in random order
        """

        if len(self._expectations) == 0:
            return []

        list_matched_expectations = []
        for key, expectation in self._expectations.items():
            if 'request' not in expectation or ExpectationMatcher.is_expectation_match_request(expectation['request'],
                                                                                               request):
                list_matched_expectations.append(expectation)
        self._logger.debug("Count of matched expectations: %s" % len(list_matched_expectations))
        return list_matched_expectations
