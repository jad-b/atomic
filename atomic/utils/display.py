from io import StringIO


last_child = '└─'
descend = '├─── '
backbone = '│   '


def print_tree(nodes):
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
    print(sio.getvalue().rstrip('\n'))


def print_nodes(nodes):
    i = 0
    for idx, node in nodes:
        print_node(idx, node)
        i += 1
    if i == 0:
        print("No items found")


def print_node(idx, node):
    sio = StringIO()
    header = '[{:d}] {:s}'.format(idx, node.get('name', '<No Name>'))
    sio.write('{}\n'.format(header))
    for k, v in node.items():
        if k == 'name':
            continue
        sio.write('  {key}: {value}\n'.format(key=k, value=v))
    print(sio.getvalue().rstrip('\n'))
