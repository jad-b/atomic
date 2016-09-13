from io import StringIO


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
