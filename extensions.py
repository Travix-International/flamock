class Extensions:

    @classmethod
    def list_of_tuples_to_dict(cls, headers_list):
        headers_dict = {}
        for key, value in headers_list:
            headers_dict[key] = value
        return headers_dict

    @classmethod
    def order_by_priority(cls, list_of_dicts_with_priority):
        """
        Sorts  list of dicts according key 'priority'.
        0 - lowest priority. Item with highest priority will be as first element
        :param list_of_dicts_with_priority: list of dicts with key 'priority'
        :return: sorted list of dicts. first element has the biggest 'priority'
        """
        sorted_list = sorted(list_of_dicts_with_priority,
                             key=lambda exp: exp['priority'] if 'priority' in exp else 0,
                             reverse=True)
        return sorted_list

    @staticmethod
    def remove_linebreaks(string_with_linebreaks):
        return string_with_linebreaks.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
