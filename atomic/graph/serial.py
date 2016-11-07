from atomic.utils import log


class Serial:
    """Mimics the behavior of the serial type in postgresql, returning an auto-
    incremented integer."""

    def __init__(self, start=0):
        self.logger = log.get_logger('api')
        self.logger.debug("Initializing serial to %d", start)
        self._index = start

    @property
    def index(self):
        curr = self._index
        self._index += 1
        return curr

    def __next__(self):
        return self.index

    def __iter__(self):
        return self

    def to_json(self):
        return {'index': self._index}

    @classmethod
    def from_json(cls, json_object):
        return cls(**json_object)
