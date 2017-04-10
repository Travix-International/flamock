import unittest
from extensions import Extensions


class ExtensionsTest(unittest.TestCase):
    def test_010_list_of_tuples_to_dict(self):
        tuples_list = [('h1', 'hv1'), ('h2', 'hv2')]
        self.assertEqual(Extensions.list_of_tuples_to_dict(tuples_list), {'h1': 'hv1', 'h2': 'hv2'})

    def test_020_order_by_priority(self):
        list_of_exp = [
            {'priority': 1},
            {'priority': 3},
            {'priority': 2},
            {'not_priority': 0},
        ]
        expected_list = [
            {'priority': 3},
            {'priority': 2},
            {'priority': 1},
            {'not_priority': 0},
        ]
        sorted_list = Extensions.order_by_priority(list_of_exp)
        self.assertEquals(sorted_list, expected_list)
