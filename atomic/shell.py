#!/usr/bin/env python3
import cmd
import os
import itertools
import pickle
import re
import sys
import traceback
import textwrap
from pprint import pprint
from datetime import timedelta
from importlib import reload

from atomic.todo import Todo, log
from atomic import survey

import pytimeparse

_user = os.getenv('USER', 'user')


class ReloadException(Exception):
    pass


class QuitException(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class Valence(cmd.Cmd):
    savefile = 'valence.db'
    intro = textwrap.dedent("""
1) Apply limitations.
2) Choose the essential.

Hello, {user}.""".format(user=_user))
    prompt = '(valence)> '

    def __init__(self):
        super().__init__()
        self.things = self.load()

    def cmdloop(self, intro=None):
        while True:
            try:
                super().cmdloop()
            except (ReloadException, QuitException):
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
        if arg == "":
            pprint_items(self.things)
        else:
            # Filter on given keys
            keys = set(arg.split())
            print("Filtering on {}".format(keys))
            view = []
            for thing in self.things:
                view.append({k:v for k, v in thing.items() if k in keys})
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
        thing = self.things[idx]
        if 'eval' in thing:
            # Re-use saved questions and previous answers
             q, a = zip(*thing['eval'])
        else:
            q, a = (survey.QUESTIONS['power_of_less'] +
                survey.QUESTIONS['one_to_ten']), itertools.repeat('')
        thing['eval'] = survey.conduct_survey(q, a)

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

    def do_set(self, arg):
        idx, key, val = arg.split(maxsplit=2)
        thing = self.things[int(idx)]
        curr = thing.get(key, False)
        if curr and not isinstance(curr, str):
            orig = type(curr)
            print("Trying to save value as {}".format(str(orig)))
            thing[key] = orig(val)
        else:
            thing[key] = val

    def get(self, idx):
        return self.things[idx]

    def do_clear(self, arg):
        if input_bool():
            self.things.clear()

    def do_done(self, arg):
        idx, delta = arg.split()
        # Update with logged time and 'complete' status
        item = self.get(int(idx))
        item['log'] = todo.log(item['log'], delta)
        item['tags'] +=('complete',)

    def do_tag(self, arg):
        # 3 cat dog
        # idx: 3
        # tags: (cat, dog)
        m = re.match(r'^(?P<idx>\d+)\s+(?P<tags>.+)$', arg)
        idx = int(m.groupdict()['idx'])
        tags = m.groupdict()['tags'].split()
        thing = self.things[idx]
        if thing.get('tags', False):   # Retieve existing tag list
            thing.extend(tags)
        else:                               # Attach new tag list
            thing['tags']  = tags

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

    def do_load(self, arg):
        self.load()

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

    def do_active(self, arg):
        for i, thing in self.active:
            print('{}) {}'.format(i, thing))

    @property
    def active(self):
        return ((i, x) for i, x in enumerate(self.things) if 'complete' not in x.tags)


def input_bool(msg='Are you sure?', truths=('y', 'yes')):
    b = input(msg + ' ')
    return b in truths


def pprint_items(things):
    for i, thing in enumerate(things):
        print('{})'.format(i))
        print('\n'.join(pformat_dict(thing, '  ')))


def pformat_dict(d, prefix=''):
    for k, v in d.items():
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
        except QuitException as qe:
            print(qe)
            break

if __name__ == '__main__':
    main()
