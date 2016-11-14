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
        """Retrieve a node by index, or many nodes."""
        pass

    @abstractmethod
    def create(self, parent=None, **kwargs):
        """Add a node to the Graph."""
        pass

    @abstractmethod
    def update(self, uid, **kwargs):
        """Update a node in-place."""
        pass

    @abstractmethod
    def delete(self, uid):
        """Delete a node from the graph."""
        pass

    def patch(self, uid, *args, **kwargs):
        """Modify properties of a node.

        Arguments:
            args (list[dict]): Array of dictionaries containing patch
                instructions in `RFC 6902`_ format.
            kwargs (dict): Key-value pairs in JSON merge patch format
                (`RFC 7386`_).

        .. _RFC 6902: https://tools.ietf.org/html/rfc6902
        .. _RFC 7386: https://tools.ietf.org/html/rfc7386
        """
        pass


class EdgeAPISpec(metaclass=ABCMeta):
    """API Specification for interacting with Edge resources.

    /edges
    /edges/{id}
    /edges/{src}[/{dest}]
    """

    @abstractmethod
    def get(self, src, dest):
        """Retrieve an edge by id or source & destination."""
        pass

    @abstractmethod
    def add(self, src, dest, type_, **kwargs):
        """Add an edge to the Graph."""
        pass

    @abstractmethod
    def update(self, src, dest, **kwargs):
        """Update an edge's attributes."""
        pass

    @abstractmethod
    def delete(self, src, dest):
        """Delete an edge from the graph."""
        pass
