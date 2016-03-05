#!/usr/bin/env python3
import cmd
import os
import itertools
import json
import re
import sys
import traceback
from collections import namedtuple
from importlib import reload

import networkx as nx

from atomic.todo import Todo, log
from atomic import survey, messages, graphops


_user = os.getenv('USER', 'user')


class ReloadException(Exception):
    pass


class QuitException(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.graph = None
        self.message = message

    def __str__(self):
        return self.message


class Valence(cmd.Cmd):
    """Valence is the command-line shell a user interacts with. It is composed
    of:

        1. A graph
        2. A backing datastore
        3. An auto-incrementing number generator
        4. The cmd.Cmd REPL shell
    """
    savefile = 'valence.pickle'
    intro = messages.INTRO.format(user=_user)
    prompt = '(valence)> '

    def __init__(self):
        super().__init__()
        #: The graph of data
        self.graph = None
        self.load()
        #: The auto-incrementing number generator
        self._serial = max(self.graph.nodes())

    @property
    def serial(self):
        tmp = self._serial
        self._serial += 1
        return tmp

    def cmdloop(self, intro=None):
        while True:
            try:
                super().cmdloop()
            except (ReloadException, QuitException):
                raise
            except Exception:     # Don't die on exceptions, only (^-c)
                traceback.print_exception(*sys.exc_info())

    def do_hi(self, arg):
        """Return a greeting."""
        print(messages.HI)

    def do_goodnight(self, arg):
        """Exit Valence with a parting quote."""
        raise QuitException(messages.SWEET_PRINCE)

    def do_list(self, arg):
        if arg == "-a":  # Print all nodes
            pprint_items(self.graph, graphops.toplevel(self.graph))
        elif arg == "":  # No keys given; only print name
            graphops.filter(self.graph, 'name')
            for node_id, data in self.graph.nodes_iter(data=True):
                if graphops.is_toplevel(self.graph, node_id):
                    print("{id}) {name}".format(
                        id=node_id, name=data.get('name'))
                    )
        else:  # Filter on given keys
            keys = set(arg.split())
            print("Filtering on {}".format(keys))
            for node_id, node_data in self.graph.nodes_iter(data=True):
                keyed = {k: v for k, v in node_data.items() if k in keys}
                pprint_node(node_id, keyed)

    def do_ls(self, arg):
        """Alias for 'list'."""
        self.do_list(arg)

    def do_show(self, arg):
        """Display a single item.

        Usage:
            itemID
        """
        if arg == "":
            print("You asked for nothing, and that's what you got.")
            return
        pprint_items(self.graph, [int(arg)])

    def do_eval(self, arg):
        if arg == "":
            print("You need to supply the item index")
            self.do_ls("name")
            return
        idx = int(arg)
        node = self.graph[idx]
        if 'eval' in node:
            # Re-use saved questions and previous answers
            q, a = zip(*node['eval'])
        else:
            q, a = (survey.QUESTIONS['power_of_less'] +
                    survey.QUESTIONS['one_to_ten']), itertools.repeat('')
        node['eval'] = survey.conduct_survey(q, a)

    def do_push(self, arg):
        # Push a new todo on the end
        self.graph.add_node(self.serial, Todo.parse(arg).to_dict())

    def do_add(self, arg):
        self.do_push(arg)

    def do_pop(self, arg):
        if len(self.graph) == 0:
            print('There is no node to pop')
        elif len(arg) > 0:
            for val in arg.split():
                try:
                    print(self.graph.remove_node(int(val)))
                except ValueError:
                    print("'{}' is an invalid index".format(val))
        else:
            print("Please give the node name")

    def do_set(self, arg):
        idx, key, val = arg.split(maxsplit=2)
        node = self.graph[int(idx)]
        curr = node.get(key, False)
        if curr and not isinstance(curr, str):
            orig = type(curr)
            print("Trying to save value as {}".format(str(orig)))
            node[key] = orig(val)
        else:
            node[key] = val

    def do_clear(self, arg):
        if input_bool():
            self.graph.clear()

    def do_done(self, arg):
        idx, delta = arg.split()
        # Update with logged time and 'complete' status
        item = self.graph[int(idx)]
        item['log'] = log(item['log'], delta)
        item['tags'] += ('complete',)

    def do_link(self, arg):
        """Create a connection between two entries.

        Usage:
            <src> <dest> [<key1> <val1>]...
        """
        u, v, *rem = arg.split()
        u, v = int(u), int(v)  # Retrieve node indices
        # Parse remaining args as "key value..." repeating
        # Group remaining args into 2-tuple
        n = 2
        d = dict((tuple(rem[i:i+n]) for i in range(0, len(rem), n)))
        self.graph.add_edge(u, v, attr_dict=d)

    def do_split(self, arg):
        """Create a child node off of an existing node.

        Usage:
            <parent> <child> [<key> <value>]...
        """
        u, rem = arg.split(maxsplit=1)
        u, entry = int(u), Todo.parse(rem).to_dict()
        child_id = self.serial
        # Create a new child node
        self.graph.add_node(child_id, entry)
        # Ensure we note the parent-child relationship
        self.graph.add_edge(u, child_id, parent=True)
        print("Linked {parent:d} to {child:d}".format(
            parent=u, child=child_id))

    def do_birth(self, arg):
        self.do_split(arg)

    def do_begat(self, arg):
        self.do_split(arg)

    def do_adopt(self, arg):
        """Relate a child to a parent.

        Usage:
            <parent> [<child>]
        """
        parent, *children = arg.split()
        parent = int(parent)
        for child in children:
            self.graph.add_edge(parent, int(child), attr_dict={'parent': True})

    def do_lineage(self, arg):
        """Print children of an item.

        Usage:
            <parent>
        """
        indent = "  "
        parent = int(arg)
        FamilyDepth = namedtuple('FamilyDepth', ['id', 'depth'])
        q = [FamilyDepth(parent, 0)]
        while len(q):
            curr = q.pop()
            print("{indent}{id}) {name}".format(
                indent=indent*curr.depth,
                id=curr.id,
                name=self.graph.node[curr.id]['name'])
            )
            for succ in self.graph.successors(curr.id)[::-1]:
                # Check for a parent-child relationship
                if self.graph.edge[curr.id][succ].get('parent'):
                    q.append(FamilyDepth(succ, curr.depth+1))

    def do_tag(self, arg):
        # 3 cat dog
        # idx: 3
        # tags: (cat, dog)
        m = re.match(r'^(?P<idx>\d+)\s+(?P<tags>.+)$', arg)
        idx = int(m.groupdict()['idx'])
        tags = m.groupdict()['tags'].split()
        node = self.graph[idx]
        if node.get('tags', False):   # Retieve existing tag list
            node.extend(tags)
        else:                               # Attach new tag list
            node['tags'] = tags

    def do_tags(self, arg):
        """Show all objects with insersection of ``tags``."""
        tags = arg.split()
        intersect = {x for x in self.graph if set(tags).issubset(set(x.tags))}
        pprint_items(intersect)

    def do_move(self, arg):
        try:
            old, new = tuple(map(int, arg.split()))
        except ValueError:
            print("""{} is a bad argument.

Usage: move <old position> <new position>
""".format(arg))
        if old >= len(self.graph):
            print('{} is out of range'.format(old))
            return
        if old < new:   # Subtract one for temporary decrement
            new -= 1
        self.graph.insert(new, self.graph.pop(old))
        # Re-print the list
        self.do_list()

    def do_save(self, arg):
        nx.write_gpickle(self.graph, self.savefile)

    def do_load(self, arg):
        self.load()

    def load(self):
        try:
            self.graph = nx.read_gpickle(self.savefile)
        except (FileNotFoundError,  # Obvious.
                json.decoder.JSONDecodeError,   # Bad JSON
                EOFError):          # Empty file
            print("trouble unpickling graph")
            self.graph = nx.DiGraph()

    def postcmd(self, stop, line):
        self.do_save(line)

    def do_reload(self, arg):
        raise ReloadException("Code reload requested by user")

    def do_active(self, arg):
        for i, node in self.active:
            print('{}) {}'.format(i, node))

    @property
    def active(self):
        return ((i, x) for i, x in enumerate(self.graph)
                if 'complete' not in x.get('tags', []))


def input_bool(msg='Are you sure?', truths=('y', 'yes')):
    b = input(msg + ' ')
    return b in truths


def pprint_items(graph, nodes):
    for node in nodes:
        pprint_node(node, graph.node[node])


def pprint_node(id, data):
    print('{})'.format(id))
    print('\n'.join(pformat_dict(data)))


def pformat_dict(data, prefix=''):
    for k, v in data.items():
        yield ("{}{}: {}".format(prefix, k, v))


def loop():
    v = None
    try:
        v = Valence()
        v.cmdloop()
    except KeyboardInterrupt:
        print('Goodbye, ', _user)
        sys.exit(0)
    finally:
        if v:
            v.do_save(None)
            print('Saving work')


def main():
    """Run the Valence command-line shell.

    If an error is encountered during initialization, the user is given the
    opportunity to fix the error without quitting the process. This process
    will loop until the code initalizes without exception or the user aborts.
    The user can also initiate a code reload via 'reload', which enters into a
    error-fix-retry loop.
    """
    while True:
        # Act as if we're importing this code as a module
        from atomic import shell
        try:
            shell.loop()
        except shell.ReloadException:
            while True:
                try:
                    curr_id = id(shell.Valence)
                    print("Reloading Valence ({:d}) shell...".format(curr_id),
                          end="")
                    reload(shell)
                    print("reload complete. "
                          "Restarting Valence ({:d}).".format(curr_id))
                    curr_id = id(shell.Valence)
                    break
                except:
                    traceback.print_exception(*sys.exc_info())
                    # Allow user to fix code before exiting
                    if input_bool('\nRetry?'):
                        continue
                    raise                       # Exit program via exception
        except QuitException as qe:
            print(qe)
            break

if __name__ == '__main__':
    main()
