import cmd
import os
import shlex
import sys
import traceback
from importlib import reload

from atomic import messages, log, display, parse
from atomic.fileapi import FileAPI


_user = os.getenv('USER', 'user')


class ShlexCmd:
    """Splits arguments as the shell would."""

    def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF':
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
                return func(shlex.split(arg))
            except AttributeError:
                return self.default(line)


class Valence(ShlexCmd, cmd.Cmd):
    """Valence is the command-line shell a user interacts with. It is composed
    of:

        1. A graph
        3. An auto-incrementing number generator
        4. The cmd.Cmd REPL shell
    """
    intro = "Welcome to Valence."
    prompt = '(valence)> '

    def __init__(self, api=None):
        super().__init__()
        self.api = api or FileAPI()
        self.logger = log.get_logger('valence')

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
        """Save the graph before quitting."""
        raise KeyboardInterrupt

    def emptyline(self):
        """Handle empty lines by printing available options."""
        self.do_help('')

    def precmd(self, line):
        """Record all cmd interactions."""
        self.logger.debug(line.lower())
        return line

    def do_list(self, *args):
        """Display nodes in the system."""
        display.print_nodes(self.api.list())

    def do_add(self, *args):
        """Add a node."""
        self.api.add(name=args)

    def do_update(self, *args):
        """Update a node: <idx> <body arguments>"""
        idx, args = arg.split(' ', 1)  # Split off the index
        ns = None
        self.api.update(int(idx), body=args)

    def do_remove(self, *args):
        """Remove a node."""
        try:
            self.api.delete(int(arg))
        except ValueError:
            print("{:d} not found".format(int(arg)))

    def do_link(self, *args):
        """Create a connection between two entries.

        Usage:
            <src> <dest> <type> [<key1>=<val1>]...
        """
        src, dest, type_, kwargs = parse.parse_link_args(arg)
        self.api.link(src, dest, type_, **kwargs)

    def do_goodnight(self, *args):
        """Exit Valence with a parting quote."""
        raise QuitException(messages.SWEET_PRINCE)

    def do_reload(self, *args):
        """Live reload the shell's source code."""
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
        print('Goodbye,', _user)
        sys.exit(0)
    finally:
        pass


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


def main(*args, **kwargs):
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
