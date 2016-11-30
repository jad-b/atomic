#!/usr/bin/env python3
"""
API implementation for using a local file as the data store.
"""
import atexit
import json
import os

import networkx as nx
from colorama import Fore, Style
from networkx.readwrite import json_graph

from atomic.darkmatter import api
from atomic.errors import AtomicError
from atomic.graph import graph, serial
from atomic.utils import log


DEFAULT_FILENAME = os.path.expanduser('~/atomic.json')

_logger = log.get_logger('atomic')


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
    with open(filename, 'w') as f:
        data = json_graph.node_link_data(G)
        json.dump(data, f, indent=2)
    _logger.debug("Saved graph")


class FileAPI:
    """File-system backed implementation of the API."""

    def __init__(self, G=None, persist=None):
        self.logger = log.get_logger('api')
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
        self.logger = logger
        self.G = G
        self.filename = filename
        # Find the highest valued node
        serial_idx = max(self.G.nodes_iter()) + 1 if len(self.G) > 1 else 1
        self.serial = serial.Serial(serial_idx)

    def get(self, idx=None, **kwargs):
        """Retrieve an item by index (uuid)."""
        if idx is None:
            self.logger.debug("Retrieving all nodes")
            return graph.hierarchy(self.G)
        self.logger.debug("Retrieving node w/ id=%d", idx)
        return self.G.node.get(idx)

    def create(self, **kwargs):
        idx = self.serial.index
        kwargs['uid'] = idx
        self.logger.debug("Node.add: idx=%d kwargs=%s", idx, kwargs)
        self.G.add_node(idx, attr_dict=kwargs)
        return idx
        _save(self.G, self.filename)

    def update(self, idx, **kwargs):
        """Update an item in-place."""
        if idx not in self.G.node:
            raise AtomicError("Node %d not found" % idx)
        self.G.node[idx] = {**self.G.node[idx], **kwargs}
        _save(self.G, self.filename)

    def patch(self, idx, *args, **kwargs):
        """Modify item attributes."""
        node = self.G.node[idx]
        for k, v in kwargs.items():
            if v is None:
                del node[k]
            else:
                node[k] = v
        _save(self.G, self.filename)

    def delete(self, idx):
        """Remove a node from the graph."""
        try:
            self.G.remove_node(idx)
        except nx.exception.NetworkXError:
            return ValueError("{:d} wasn't found in the graph".format(idx))
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
              .format(lo=Fore.RED + 'lo=' + str(lo) + Style.RESET_ALL,
                      mid=Fore.YELLOW + 'mid=' + str(mid) + Style.RESET_ALL,
                      hi=Fore.GREEN + 'hi=' + str(hi) + Style.RESET_ALL))
        ans = None
        higher = ['h', 'k']
        lower = ['l', 'j']
        while not ans:
            print("Higher[{higher}] or Lower[{lower}]: {items}".format(
                higher=','.join(higher), lower=','.join(lower),
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
        self.G = G
        self.logger = logger
        self.filename = filename

    def get(self, src: int, dst: int, **kwargs):
        """Retrieve an edge by id or source & dstination."""
        if kwargs == {}:  # Single item retrieval
            try:
                return self.G.edge[src][dst]
            except KeyError:
                return None

    def create(self, src: int, dst: int,
               type=graph.EdgeTypes.related.name, **kwargs):
        """Add an edge to the Graph."""
        try:
            self.G.node[src]
            self.G.node[dst]
        except KeyError:
            raise AtomicError(
                "Cannot create Edge (%d, %d); node(s) not found" % (src, dst))
        self.logger.debug("Adding edge between %d => %d", src, dst)
        data = dict(kwargs)
        data['src'] = src
        data['dst'] = dst
        data['type'] = type
        self.G.add_edge(src, dst, **data)
        _save(self.G, self.filename)

    def update(self, src, dst, **kwargs):
        """Update an edge's attributes."""
        self.G.edge[src][dst] = {**self.G.edge[src][dst], **kwargs}
        _save(self.G, self.filename)

    def delete(self, src, dst, **kwargs):
        """Delete an edge from the graph."""
        self.G.remove_edge(src, dst)
        _save(self.G, self.filename)
