#!/usr/bin/env python3
import cmd
import os
import pickle
import re
import sys
import traceback
from pprint import pprint
from importlib import reload

from atomic.todo import Todo


_user = os.getenv('USER', 'user')


class ReloadException(Exception):
    pass


class QuitException(Exception):
    pass


class Valence(cmd.Cmd):
    savefile = 'valence.db'
    intro = 'Hello, ' + _user
    prompt = '(valence)> '

    def __init__(self):
        super().__init__()
        self.things = self.load()

    def cmdloop(self, intro=None):
        while True:
            try:
                super().cmdloop()
            except ReloadException:
                raise
            except Exception as e:     # Don't die on exceptions, only user quits (^-c)
                traceback.print_exception(*sys.exc_info())

    def do_hi(self, arg):
        print("Hi to you too.")

    def do_goodnight(self, arg):
        raise QuitException(textwrap.dedent("""
            Good night, good night!
            Parting is such sweet sorrow, that I shall say good night till it be morrow.
            """))

    def do_list(self, arg):
        pprint_items(self.things)

    def do_ls(self, arg):
        """Alias for 'list'."""
        self.do_list(arg)

    def do_convert(self, arg):
        """Convert all tasks to Todos."""
        for i, thing in enumerate(self.things):
            if not getattr(thing, 'tags', False):
                thing.tags = ()    # Assign default of no tags

    def do_push(self, arg):
        # Push a new todo on the end
        self.things.append(Todo.parse(arg))

    def do_pop(self, arg):
        if len(self.things) == 0:
            print('There is nothing to pop')
        elif len(arg) > 0:
            try:
                print(self.things.pop(int(arg)))
            except ValueError:
                print("'{}' is an invalid index".format(arg))
        else:
            print(self.things.pop())

    def do_clear(self, arg):
        if input_bool():
            self.things.clear()

    def do_tag(self, arg):
        m = re.match(r'^(?P<idx>\d+)\s+(?P<tags>.+)$', arg)
        idx = int(m.groupdict()['idx'])
        tags = m.groupdict()['tags'].split()
        thing = self.things[idx]
        if getattr(thing, 'tags', False):   # Retieve existing tag list
            thing.extend(tags)
        else:                               # Attach new tag list
            setattr(thing, 'tags', tags)

    def do_tags(self, arg):
        """Show all objects with insersection of ``tags``."""
        tags = arg.split()
        intersect = {x for x in self.things if set(tags).issubset(set(x.tags))}
        pprint_items(intersect)

    def do_move(self, arg):
        try:
            old, new = tuple(map(int, arg.split()))
        except ValueError:
            print("""{} is a bad argument.

Usage: move <old position> <new position>
""".format(arg))
        if old >= len(self.things):
            print('{} is out of range'.format(old))
            return
        if old < new:   # Subtract one for temporary decrement
            new -= 1
        self.things.insert(new, self.things.pop(old))
        # Re-print the list
        self.do_list()

    def do_save(self, arg):
        with open(self.savefile, 'w+b') as fp:
            pickle.dump(self.things, fp)

    def load(self):
        try:
            with open(self.savefile, 'r+b') as fp:
                return pickle.load(fp)
        except (FileNotFoundError,  # Obvious.
                EOFError):          # Empty file
            return []

    def postcmd(self, stop, line):
        self.do_save(line)

    def do_reload(self, arg):
        raise ReloadException("Code reload requested by user")


def input_bool(msg='Are you sure?', truths=('y', 'yes')):
    b = input(msg + ' ')
    return b in truths


def pprint_items(things):
    for i, thing in enumerate(things):
        print('{}) {}'.format(i, thing))


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
                    print("Reloading Valence ({:d}) shell...".format(curr_id), end="")
                    reload(shell)
                    print("reload complete. Restarting Valence ({:d}).".format(curr_id))
                    curr_id = id(shell.Valence)
                    break
                except:
                    traceback.print_exception(*sys.exc_info())
                    # Allow user to fix code before exiting
                    if input_bool('\nRetry?'):
                        continue
                    raise                       # Exit program via exception


if __name__ == '__main__':
    main()
