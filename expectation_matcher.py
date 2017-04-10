import re

from json_logging import JsonLogging


class ExpectationMatcher:
    _logger = JsonLogging
    _re_flags = re.DOTALL

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
                    cls._logger.debug(
                        'Difference in {attribute}. expected: {expected_value}, actual: {actual_value}'.format(
                            attribute=attr,
                            expected_value=request_exp[attr],
                            actual_value=request_act[attr] if attr in request_act else 'None')
                    )
                    return False

        cls._logger.debug('Requests are match expected: {expected_value}, actual: {actual_value}'.format(
            expected_value=str(request_exp), actual_value=str(request_act)))
        return True

    @classmethod
    def __value_matcher_str(cls, expected_value, actual_value):
        """
        compares two values: actual and expected. Try to decide expected value as regex pattern.
        If unsuccssfull, try to find expected value as substring of actual
        :param expected_value: regex pattern or string
        :param actual_value: string
        :return: true if actual value matches expected value or contains expected value as substring. Otherwise - false
        """
        try:
            compiled_pattern = re.compile(expected_value, cls._re_flags)
            search_result = compiled_pattern.search(actual_value)
            return search_result is not None
        except TypeError as e:
            cls._logger.exception(e)
            return expected_value in actual_value

    @classmethod
    def __value_matcher_dict(cls, expected_dict, actual_dict):
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
            return cls.__value_matcher_str(expected_value, actual_value)
        elif isinstance(expected_value, dict) and isinstance(actual_value, dict):
            return cls.__value_matcher_dict(expected_value, actual_value)
        else:
            return False
