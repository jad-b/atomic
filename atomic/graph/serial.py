from atomic.utils import log


class Serial:
    """1-indexed auto-incrementing integer.

    Intended to mimic the behavior of the serial type in postgresql.
    """

    def __init__(self, start=1):
        self.logger = log.get_logger('api')
        self.logger.debug("Initializing serial to %d", start)
        self._index = start

    @property
    def index(self):
        curr = self._index  # Make a copy
        self._index += 1
        return curr

    @property
    def current(self):
        return self._index

    def reset(self):
        """Reset the serial to 1."""
        self._index = 1

    def __next__(self):
        return self.index

    def __iter__(self):
        return self

    def to_json(self):
        return {'index': self._index}

    @classmethod
    def from_json(cls, json_object):
        return cls(**json_object)
