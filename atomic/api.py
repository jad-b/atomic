from abc import ABCMeta, abstractmethod


class APISpec(metaclass=ABCMeta):

    @abstractmethod
    def get(self, idx):
        """Retrieve a node by index."""
        pass

    @abstractmethod
    def add(self, parent=None, **kwargs):
        """Add a node to the Graph."""
        pass

    @abstractmethod
    def update(self, uid, **kwargs):
        """Update a node's attributes."""
        pass

    @abstractmethod
    def delete(self, uid):
        """Delete a node from the graph."""
        pass
