class Extensions:

    @classmethod
    def list_of_tuples_to_dict(cls, headers_list):
        headers_dict = {}
        for key, value in headers_list:
            headers_dict[key] = value
        return headers_dict
