class LogContainer(object):
    """
    Special container for log messages
    By default, saves 100 messages. When adds 101 message, it rewrites first message.
    """
    DEFAULT_SIZE = 100
    size = None
    container = None

    def __init__(self, size=DEFAULT_SIZE):
        self.container = {}
        self.size = size
        self._latest_id = -1

    def clean(self):
        self.container = dict()
        self._latest_id = -1

    def get_latest_id(self):
        return self._latest_id

    def add(self, value):
        id = (self._latest_id+1) % self.size
        self.container[id] = value
        self._latest_id = id

    def update_last_with_kv(self, key, value):
        if isinstance(self.container[self._latest_id], dict):
            self.container[self._latest_id][key] = value
