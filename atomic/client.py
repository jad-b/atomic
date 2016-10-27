from atomic import log, display, parse


class ApiClient:

    def __init__(self, api):
        self.api = api
        self.logger = log.get_logger('self')

    def list(self, **kwargs):
        self.logger.debug("Listing nodes")
        print("Nodes:\n=====")
        nodes = self.api.Node.get()  # Grab all nodes
        display.print_tree(nodes)

    def show(self, index, **kwargs):
        n = self.api.Node.get(index)
        display.print_node(index, n)

    def add(self, args, parent=None, **kwargs):
        line = ' '.join(args)  # Rejoin args for regex parsing
        name = parse.parse_non_kv(line)
        kwargs = parse.parse_key_values(line[len(name):])
        self.api.Node.add(parent=parent, name=name, **kwargs)

    def update(self, index, args, remove=None, replace=False, **kwargs):
        line = ' '.join(args)  # Rejoin args for regex parsing
        kvs = parse.parse_key_values(line)
        if replace:
            self.api.Node.update(index, **kvs)
        else:  # Assemble patch
            if remove is not None:
                for prop in remove:
                    kvs[prop] = None
            self.api.Node.patch(index, **kvs)

    def delete(self, index=-1, **kwargs):
        self.api.Node.delete(index)

    def link(self, src, dest, type, kvs=None, *args, **kwargs):
        if kvs is not None:
            key_values = parse.parse_key_values(' '.join(kvs))
        else:
            key_values = {}
        self.api.Edge.add(src, dest, type_=type, **key_values)
