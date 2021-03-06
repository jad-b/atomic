#!/usr/bin/env python3
"""
API implementation for using a local file as the data store.
"""
import atexit
import enum
import json
import os

import networkx as nx
from colorama import Fore, Style
from networkx.readwrite import json_graph

from atomic.darkmatter import api
from atomic.errors import AtomicError
from atomic.graph import graph, serial
from atomic.utils import log


DEFAULT_FILENAME = os.path.expanduser("~/atomic.json")

_logger = log.get_logger("atomic")


def _load(filename=DEFAULT_FILENAME):
    """Load the persisted :class:`networkx.MultiDiGraph`."""
    try:
        with open(filename) as f:
            data = json.load(f)
            _logger.debug("Loaded %s", filename)
            return json_graph.node_link_graph(data, directed=True,
                                              multigraph=False)
    except FileNotFoundError:
        _logger.debug("No graph file found; instantiating")
        return nx.DiGraph()


def _save(G, filename=DEFAULT_FILENAME):
    """Save the persisted :class:`networkx.MultiDiGraph`.

    Arguments:
        G (:class:`~networkx.classes.digraph.DiGraph`): Graph to save.
        filename (str): Name of file to save graph to. If None, this is a
            no-op, which is useful for testing and any other time the graph is
            only required to be in-memory.
    """
    if filename is None:
        return
    with open(filename, "w") as f:
        data = json_graph.node_link_data(G)
        json.dump(data, f, indent=2)
    _logger.debug("Saved graph")


class FileAPI:
    """File-system backed implementation of the API."""

    def __init__(self, G=None, persist=None):
        """Initialize the instance.

        Args:
            G (:class:`~.networkx.DiGraph`): Graph instance. If ``None``, the
                graph will attempt to be loaded using ``persist``.
            persist (str or bool): Leveraged by :meth:`~.FileAPI.load_graph` to
                load (or not load) the in-memory Graph.
        """
        self.logger = log.get_logger("api")
        if G is not None:
            self.G, self.filename = G, None
        else:
            self.G, self.filename = self.load_graph(persist)

        self.Node = FileNodeAPI(self.G, self.logger, filename=self.filename)
        self.Edge = FileEdgeAPI(self.G, self.logger, filename=self.filename)

        # Save the graph before closing
        if persist:
            atexit.register(_save, self.G, self.filename)

    def load_graph(self, persist):
        """Controls instantiation of the in-memory Graph.

        Args:
            persist (:obj:bool or :obj:str): If False, a blank in-memory graph
                is created. If True, the Graph is loaded from using the
                :attr:`~.DEFAULT_FILENAME`. If a :obj:str, it is interpreted to
                be a filepath to a file containing the graph.
        Returns:
            :class:`~.networkx.digraph.DiGraph`: A directed graph.

        Raises:
            ValueError: If ``persist`` isn't a :obj:str or :obj:bool.
        """
        if not persist:
            return nx.DiGraph(), None
        elif isinstance(persist, bool):
            return _load(DEFAULT_FILENAME), DEFAULT_FILENAME
        elif isinstance(persist, str):
            return _load(persist), persist
        else:
            raise ValueError("persist must be a bool or str")


class FileNodeAPI(api.NodeAPISpec):
    """File-system backed implementation of the Node API."""

    def __init__(self, G, logger, filename=None):
        """Initialize the instance.

        Args:
            G (:class:`~.networkx.DiGraph`): Graph instance.
            logger (:class:`~.logging.Logger`): Python logger.
            filename (str): Filepath to save the Graph to.
        """
        self.logger = logger
        self.G = G
        self.filename = filename
        # Find the highest valued node
        serial_idx = max(self.G.nodes_iter()) + 1 if len(self.G) > 1 else 1
        self.serial = serial.Serial(serial_idx)

    def create(self, **kwargs):
        idx = self.serial.index
        kwargs["uid"] = idx
        self.logger.debug("Node.add: idx=%d kwargs=%s", idx, kwargs)
        self.G.add_node(idx, attr_dict=kwargs)
        return idx
        _save(self.G, self.filename)

    def get(self, idx=None, **kwargs):
        """Retrieve an item by index (uuid)."""
        if idx is None:
            self.logger.debug("Retrieve all nodes")
            return graph.hierarchy(self.G)
        self.logger.debug("Retrieve node id=%d", idx)
        return self.G.node.get(idx)

    def update(self, idx: int, **kwargs):
        """Update an item in-place."""
        self.logger.debug("Update node %d", idx)
        if self.get(idx) is None:
            raise AtomicError("Node %d not found" % int(idx))
        kwargs["uid"] = idx
        self.G.node[idx] = kwargs
        _save(self.G, self.filename)

    def patch(self, idx, *args, **kwargs):
        """Modify item attributes."""
        self.logger.debug("Patch node %d", idx)
        node = self.get(idx)
        if node is None:
            raise AtomicError("Node %d not found" % int(idx))
        for k, v in kwargs.items():
            if v is None:
                del node[k]
            else:
                node[k] = v
        kwargs["uid"] = idx
        self.G.node[idx] = kwargs
        _save(self.G, self.filename)

    def delete(self, idx):
        """Remove a node from the graph."""
        self.logger.debug("Delete node %d", idx)
        try:
            self.G.remove_node(idx)
        except nx.exception.NetworkXError as e:
            raise AtomicError("Node {:d} not found".format(idx)) from e
        _save(self.G, self.filename)

    def binary_add(self, item):
        """Insert an item after using a binary-search comparison."""
        lo, hi = 0, len(self.items) - 1
        while lo <= hi:
            mid = lo + hi >> 1  # Find the midpoint with bit shifting!
            ans = self.guided_prompt(lo, mid, hi)
            if ans is None:
                return
            if ans:  # User said higher
                hi = mid - 1
            else:  # User said lower
                lo = mid + 1
        item.uid = self.serial.index
        self.items.insert(lo, item)

    def guided_prompt(self, lo, mid, hi):
        print("Bracketing: ({lo}, {mid}, {hi})"
              .format(lo=Fore.RED + "lo=" + str(lo) + Style.RESET_ALL,
                      mid=Fore.YELLOW + "mid=" + str(mid) + Style.RESET_ALL,
                      hi=Fore.GREEN + "hi=" + str(hi) + Style.RESET_ALL))
        ans = None
        higher = ["h", "k"]
        lower = ["l", "j"]
        while not ans:
            print("Higher[{higher}] or Lower[{lower}]: {items}".format(
                higher=",".join(higher), lower=",".join(lower),
                items=self.items[mid]))
            try:
                ans = input()
            except EOFError:
                return None
            if ans in higher:  # User said higher
                return True
            elif ans in lower:  # User said lower
                return False
            else:
                print("I'm sorry, I didn't recognize that. "
                      "Hit Ctrl-D to quit.")
                ans = None

    def __str__(self):
        return "FileNodeAPI"

    def __iter__(self):
        return self.graph.nodes_iter()


class FileEdgeAPI(api.EdgeAPISpec):

    def __init__(self, G, logger, filename=None):
        """Initialize the instance.

        Args:
            G (:class:`~.networkx.DiGraph`): Graph instance.
            logger (:class:`~.logging.Logger`): Python logger.
            filename (str): Filepath to save the Graph to.
        """
        self.G = G
        self.logger = logger
        self.filename = filename

    def get(self, src: int, dst: int, **kwargs):
        """Retrieve an edge by id or source & dstination."""
        if kwargs == {}:  # Single item retrieval
            try:
                self.logger.info("Retrieving edge (%d, %d)", src, dst)
                return self.G.edge[src][dst]
            except KeyError:
                return None

    def create(self, src: int, dst: int,
               type="related", **kwargs):
        """Add an edge to the Graph."""
        self.logger.debug("Create edge (%d, %d)", src, dst)
        try:
            self.G.node[src]
            self.G.node[dst]
        except KeyError:
            raise AtomicError(
                "Cannot create Edge (%d, %d); node(s) not found" % (src, dst))
        self.logger.debug("Adding edge between %d => %d", src, dst)
        data = dict(kwargs)
        # Add essential fields
        data["src"] = src
        data["dst"] = dst
        data["type"] = type
        self.G.add_edge(src, dst, **data)
        _save(self.G, self.filename)
        return data

    def update(self, src, dst, **kwargs):
        """Update an edge's attributes."""
        self.logger.info("Update edge (%d, %d)", src, dst)
        self.G.edge[src][dst] = {**self.G.edge[src][dst], **kwargs}
        _save(self.G, self.filename)

    def delete(self, src, dst, **kwargs):
        """Delete an edge from the graph."""
        self.logger.info("Delete edge (%d, %d)", src, dst)
        try:
            self.G.edge[src][dst]
        except KeyError as e:
            raise AtomicError("Edge (%d, %d) not found", src, dst)
        self.G.remove_edge(src, dst)
        _save(self.G, self.filename)


class FileGraphAPI(api.GraphAPISpec):
    """File-system backed implementation of the Graph API."""

    def __init__(self, G, logger, filename=None):
        """Initialize the instance.

        Args:
            G (:class:`~.networkx.DiGraph`): Graph instance.
            logger (:class:`~.logging.Logger`): Python logger.
            filename (str): Filepath to save the Graph to.
        """
        self.G = G
        self.logger = logger
        self.filename = filename

    def search(self, type="depth", node=None):
        """Search within a Graph.

        Todo: Add choice for pre|post|in-order
        Todo: Add choice for edge direction of incoming|outgoing|undirected

        Args:
            type (str): Depth or breadth.
            node (int): ID of node to start from. If None, all nodes in the
                Graph will be iterated through. How will they be iterated
                through? Good question!

        Returns:
            (dict, distance): 2-tuple of the node's contents and its distance
                from the starting node. If ``node`` is empty, than the distance
                will be related to the last previous tuple with distance 0.
        """
        yield ({}, 0)
