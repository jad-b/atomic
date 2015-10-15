#!/usr/bin/env python3
import cmd
import os
import pickle
from pprint import pprint


_user = os.getenv('USER', 'user')


class Valence(cmd.Cmd):
    savefile = 'valence.db'
    intro = 'Hello, ' + _user
    prompt = '(valence)> '

    def __init__(self):
        super().__init__()
        self.things = self.load()

    def do_list(self, arg):
        for i, thing in enumerate(self.things):
            print('{}) {}'.format(i, thing))

    def do_push(self, arg):
        self.things.extend(arg.split())

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
        b = input('Are you sure? ')
        if b in ('y', 'yes'):
            self.things.clear()

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

    def do_save(self):
        with open(self.savefile, 'w+b') as fp:
            pickle.dump(self.things, fp)

    def load(self):
        try:
            with open(self.savefile, 'r+b') as fp:
                return pickle.load(fp)
        except (FileNotFoundError,  # Obvious.
                EOFError):          # Empty file
            return []


if __name__ == '__main__':
    v = None
    try:
        v = Valence()
        v.cmdloop()
    except KeyboardInterrupt:
        if v:
            v.do_save()
            print('Saving work')
        print('Goodbye, ', _user)
