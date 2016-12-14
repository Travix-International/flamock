import unittest
from extensions import Extensions


class ExtensionsTest(unittest.TestCase):

    def test_010_list_of_tuples_to_dict(self):
        tuples_list = [('h1', 'hv1'), ('h2', 'hv2')]

        self.assertEqual(Extensions.list_of_tuples_to_dict(tuples_list), {'h1': 'hv1', 'h2': 'hv2'})