import hashlib
from flask import Response as FlaskResponse


class ExpectationManager:
    """
    Class for managing set of expectations

    todo: fix return types
    """
    expectations = {}  # dict with <md5: json_object>

    @classmethod
    def remove_all(cls):
        cls.expectations.clear()
        return FlaskResponse("All expectations were removed", 200)

    @classmethod
    def get_expectations(cls):
        return cls.expectations.copy()

    @classmethod
    def remove(cls, key):
        if key in cls.expectations:
            del(cls.expectations[key])
        return FlaskResponse("Expectation with key %s was removed" % key, 200)

    @classmethod
    def add(cls, expectation_as_dict):
        key = hashlib.md5(str(expectation_as_dict).encode()).hexdigest()
        if key not in cls.expectations:
            cls.expectations[key] = expectation_as_dict
            return FlaskResponse("Expectation was added with key %s" % key, 200)
        return FlaskResponse("Expectation was not added!", 200)

    @classmethod
    def validate_expectation(cls, expectation_as_dict):
        #todo
        pass