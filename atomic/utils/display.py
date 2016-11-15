import sys
from io import StringIO


last_child = '└─'
descend = '├─── '
backbone = '│   '


def print_tree(nodes, file=sys.stdout):
    """Print a horizontal tree using a list of (node, depth) tuples."""
    sio = StringIO()
    for n, depth in nodes:
        if depth == 0:
            pre = ''
        elif depth == 1:
            pre = descend
        else:
            pre = backbone + ' ' * 4 * (depth - 2) + descend
        sio.write("{}{}\n".format(pre, str(n)))
    print(sio.getvalue().rstrip('\n'), file=file)
