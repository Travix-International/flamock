import json
import hashlib
from requests.status_codes import codes
from custom_reponse import CustomResponse


class ExpectationManager:
    """
    Class for managing set of expectations

    todo: fix return types
    """
    expectations = {}  # dict with <md5: json_object>

    @classmethod
    def remove_all(cls):
        """

        :return: custom response
        """
        cls.expectations.clear()
        return CustomResponse("All expectations were removed")

    @classmethod
    def get_expectations_as_dict(cls):
        """

        :return: expectations as dict. Useful for inner operations
        """
        return cls.expectations.copy()

    @classmethod
    def get_expectations_as_response(cls):
        """

        :return: Expectations as custom response
        """
        return CustomResponse(str(cls.expectations))

    @classmethod
    def remove(cls, dict_with_key):
        """
        Removes particular expectations
        :param dict_with_key: dictionary with field 'key' and md5=value
        :return: custom response
        """
        if 'key' in dict_with_key and dict_with_key['key'] in cls.expectations:
            del(cls.expectations[dict_with_key['key']])
        return CustomResponse("Expectation with key %s was removed" % dict_with_key)

    @classmethod
    def add(cls, expectation_as_dict):
        key = hashlib.md5(str(expectation_as_dict).encode()).hexdigest()
        if key not in cls.expectations:
            cls.expectations[key] = expectation_as_dict
            return CustomResponse("Expectation was added with key %s" % key)
        return CustomResponse("Expectation was not added!")

    @classmethod
    def json_to_dict(cls, json_text):
        json_dict = None
        try:
            json_dict = json.loads(json_text)
        except Exception as e:
            return json_dict, CustomResponse("Error! Can't convert json to dict! Json %s\r\n. Exception: %s" % (json_text, str(e)), codes.bad)
        return json_dict, CustomResponse()