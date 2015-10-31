#!/usr/bin/env python3
import cmd
import os
import itertools
import json
import re
import sys
import traceback
import textwrap
from importlib import reload

import networkx as nx
from networkx.readwrite import json_graph

from atomic.todo import Todo, log
from atomic import survey


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
    savefile = 'valence.pickle'
    intro = textwrap.dedent("""
1) Apply limitations.
2) Choose the essential.
3) Simplify by eliminating the nonessential.
4) Focus is effectiveness.
5) Habits create long-term improvement.

Hello, {user}.""".format(user=_user))
    prompt = '(valence)> '

    def __init__(self):
        super().__init__()
        self.load()

    def cmdloop(self, intro=None):
        while True:
            try:
                super().cmdloop()
            except (ReloadException, QuitException):
                raise
            except Exception:     # Don't die on exceptions, only (^-c)
                traceback.print_exception(*sys.exc_info())

    def do_hi(self, arg):
        print("Hi to you too.")

    def do_goodnight(self, arg):
        raise QuitException(textwrap.dedent("""\
            Good night, good night!
            Parting is such sweet sorrow,
            that I shall say good night
            till it be morrow."""))

    def do_list(self, arg):
        if arg == "":
            pprint_items(self.graph)
        else:
            # Filter on given keys
            keys = set(arg.split())
            print("Filtering on {}".format(keys))
            view = []
            for node in self.graph:
                view.append({k: v for k, v in node.items() if k in keys})
            pprint_items(view)

    def do_ls(self, arg):
        """Alias for 'list'."""
        self.do_list(arg)

    def do_show(self, arg):
        pprint_items([self.get(int(arg))])

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
        self.graph.add_node(self.graph.number_of_nodes() + 1,
                            Todo.parse(arg).to_dict())

    def do_pop(self, arg):
        if len(self.graph) == 0:
            print('There is nonode to pop')
        elif len(arg) > 0:
            try:
                print(self.graph.remove_node(int(arg)))
            except ValueError:
                print("'{}' is an invalid index".format(arg))
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
            self.graph = nx.MultiGraph()

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


def pprint_items(graph):
    for node, data in graph.nodes_iter(data=True):
        print('{})'.format(node))
        print('\n'.join(pformat_dict(data, '  ')))


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
