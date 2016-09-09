import cmd
import os
import re
import sys
import traceback
from importlib import reload

from atomic import messages
from atomic.fileapi import FileAPI


_user = os.getenv('USER', 'user')


class Valence(cmd.Cmd):
    """Valence is the command-line shell a user interacts with. It is composed
    of:

        1. A graph
        3. An auto-incrementing number generator
        4. The cmd.Cmd REPL shell
    """
    intro = "Hi."
    prompt = '(valence)> '

    def __init__(self):
        super().__init__()
        self.api = FileAPI()

    def cmdloop(self, intro=None):
        """Run the REPL, handling special-case exceptions."""
        while True:
            try:
                super().cmdloop()
            except (ReloadException, QuitException):
                raise
            except Exception:     # Don't die on exceptions, only (^-c)
                traceback.print_exception(*sys.exc_info())

    def do_EOF(self, args):
        """Save the Q before quitting."""
        raise KeyboardInterrupt

    def emptyline(self):
        """Handle empty lines by printing available options."""
        self.do_help('')

    def postcmd(self, stop, line):
        self.do_save(line)

    def precmd(self, line):
        """Record all cmd interactions."""
        self.logger.debug(line.lower())
        return line

    def do_list(self, arg):
        pass

    def do_show(self, arg):
        """Display a single item.

        Usage:
            itemID
        """
        if arg == "":
            print("You asked for nothing, and that's what you got.")
            return
        pass

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

    def do_goodnight(self, arg):
        """Exit Valence with a parting quote."""
        raise QuitException(messages.SWEET_PRINCE)

    def do_reload(self, arg):
        raise ReloadException("Code reload requested by user")


def input_bool(msg='Are you sure?', truths=('y', 'yes')):
    """Confirm action via the CLI."""
    b = input(msg + ' ')
    return b in truths


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


class ReloadException(Exception):
    """The user has requested a source code reload."""
    pass


class QuitException(Exception):
    """The user has requested to exit the REPL."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


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
