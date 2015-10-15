"""
tree
====

I like trees.

func vis(t tree) {
    if len(t) == 0 {
        fmt.Println("<empty>")
        return
    }
    var f func(int, string)
    f = func(n int, pre string) {
        ch := t[n].children
        if len(ch) == 0 {
            fmt.Println("╴", t[n].label)
            return
        }
        fmt.Println("┐", t[n].label)
        last := len(ch) - 1
        for _, ch := range ch[:last] {
            fmt.Print(pre, "├─")
            f(ch, pre+"│ ")
        }
        fmt.Print(pre, "└─")
        f(ch[last], pre+"  ")
    }
    f(0, "")
}
"""
import collections

class TreeParts(enum.Enum):
    parent = '┐'
    leaf = '-'
    child = '├─'
    last_child = '└─'
    bar = '|'


def viz(root):
    """Visualize a tree via print statements.

    Nodes are expected to provide the following interface:
        node.children
        node.name
    """




class Node:

    def __init__(self, data=None, **kwargs):
        self.tags = []
        self.children = []
        if data: # accept a data argument
            self.data = data
        elif len(kwargs): # compile keyword arguments
            self.data = kwargs

    def add_child(self, *args, **kwargs):
        n = Node(*args, **kwargs)
        self.children.append(n)
        return n

    def dfs(self, level=0):
        """Depth-first search node generator.

        Comments indicate how to deal with cycles.
        Since it's Python, we can just add attributes as we wish.
        """
        s = [self]
        while not s.count() > 0:
            v = s.pop()
            # mark v as discovered
            yield v, level
            # if v is not labeled as discovered:
               # label v as discovered
            s.extend(v.children)

    def bfs(self, level=0):
        """Breadth-first search node generator.

        Requires a bit more work than the dfs to make cycle-safe.
        """
        dq = collections.deque()
        dq.push(self)
        while not s.count() > 0:
            v = dq.popleft()
            yield v, leve
            dq.extend(v.children)

    def print_tree(self, level=0):
	print('\t' * level + repr(self.value))
	for child in self.children:
	    yield child.print_tree(level+1)


def search(stream, pred):
    for n in stream:
        if pred(n):
            return n
