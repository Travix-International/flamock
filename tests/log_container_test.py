import unittest
from log_container import LogContainer


class LogContainerTest(unittest.TestCase):

    size = 100
    log_container = LogContainer(size)

    def setUp(self):
        self.log_container.clear()

    def test_010_add_message(self):
        for i in range(0, self.size):
            self.log_container.add(i)

        self.assertEqual(self.size, len(self.log_container.container))
        self.assertEqual(0, self.log_container.container[0])
        self.assertEqual(self.size-1, self.log_container.container[self.size-1])

        self.log_container.add(self.size + 1)
        self.assertEqual(self.size, len(self.log_container.container))
        self.assertEqual(self.size + 1, self.log_container.container[0])
        self.assertEqual(self.size - 1, self.log_container.container[self.size - 1])

    def test_020_add_message_as_key(self):
         self.log_container.add({'key1': 'value1'})
         self.log_container.update_last_with_kv('key2', 'value2')

         self.assertEqual(1, len(self.log_container.container))
         self.assertEqual({'key1': 'value1', 'key2': 'value2'}, self.log_container.container[0])

    def test_030_get_latest_id(self):
        self.assertEqual(-1, self.log_container.get_latest_id())
        self.log_container.add("message")
        self.assertEqual(0, self.log_container.get_latest_id())

    def test_040_update_last_with_kv_empty(self):
        self.assertEqual(-1, self.log_container.get_latest_id())
        self.log_container.update_last_with_kv("key", "value")
        self.assertEqual(0, self.log_container.get_latest_id())
        self.assertEqual("value", self.log_container.container[0]["key"])

    def test_050_update_last_with_kv_not_empty(self):
        self.assertEqual(-1, self.log_container.get_latest_id())
        self.log_container.update_last_with_kv("key", "value")
        self.assertEqual(0, self.log_container.get_latest_id())
        self.assertEqual("value", self.log_container.container[0]["key"])
        self.log_container.update_last_with_kv("key", "value2")
        self.assertEqual(0, self.log_container.get_latest_id())
        self.assertEqual("value2", self.log_container.container[0]["key"])
