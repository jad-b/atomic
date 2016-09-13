#!/usr/bin/env python3
"""
API implementation for using a local file as the data store.
"""
from io import StringIO

from colorama import Fore, Style

from atomic import api, graph, serial, log


class FileAPI(api.APISpec):
    """File-system backed implementation of the API."""

    def __init__(self):
        self.G = graph.load()
        # A project-unique ID generator
        self.serial = serial.Serial()
        self.logger = log.get_logger('api')

    def get(self, idx):
        """Retrieve an item by index (uuid)."""
        return self.G.node[idx]

    def list(self):
        """Retrieve all items."""
        return self.G.nodes_iter(data=True)

    def add(self, parent=None, **kwargs):
        idx = self.serial.index
        self.logger.debug("Adding node %s", idx)
        self.G.add_node(idx, attr_dict=kwargs)  # Create node
        if parent is not None:
            self.logger.debug("Linking to %s", parent)
            self.G.add_edge(parent, idx, parent_of=True)  # Link to parent
        graph.save(self.G)

    def update(self, idx, **kwargs):
        """Update item attributes."""
        self.G.node[idx] = {**self.G.node[idx], **kwargs}
        graph.save(self.G)

    def delete(self, uid):
        """Remove a node from the graph."""
        self.G.remove_node(uid)
        graph.save(self.G)

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
        """Output the list of items."""
        if len(self.items) == 0:
            return "No items found."
        buf = StringIO()
        for i, x in enumerate(self.items):
            buf.write("{:d}) {:s}\n".format(i, str(x)))
        return buf.getvalue().rstrip()

    def __repr__(self):
        return "Q(items=[{:d}], completed=[{:d}], filename={})".format(
            len(self.items), len(self.completed), self.filename)

    def __iter__(self):
        return self.graph.nodes_iter()

    def save(self):
        graph.save(self.G)
