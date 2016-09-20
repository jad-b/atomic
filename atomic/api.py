from abc import ABCMeta, abstractmethod


class GraphAPISpec(metaclass=ABCMeta):
    """API specification for interacting with the Graph.

    /graph
    /graph/algorithms/{name}
    /graph/paths/{type=shortest,longest,maxflow,etc.}
    """
    pass


class NodeAPISpec(metaclass=ABCMeta):
    """API Specification for interacting with Node resources.

    /nodes?q={Solr|Lucene Syntax}
    /nodes/{id}?fields={csv,}
    """

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


def EdgeAPISpec(metaclass=ABCMeta):
    """API Specification for interacting with Edge resources.

    /edges
    /edges/{id}
    /edges/{src}[/{dest}]
    """

    @abstractmethod
    def get(self, idx):
        """Retrieve an edge by id or source & destination."""
        pass

    @abstractmethod
    def add(self, parent=None, **kwargs):
        """Add an edge to the Graph."""
        pass

    @abstractmethod
    def update(self, uid, **kwargs):
        """Update an edge's attributes."""
        pass

    @abstractmethod
    def delete(self, uid):
        """Delete an edge from the graph."""
        pass
