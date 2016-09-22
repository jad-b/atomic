import cmd
import os
import shlex
import sys
import traceback
from importlib import reload

from atomic import cli, log, parse


class ShlexMixin:
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
                # func = getattr(self, 'do_' + cmd)
                # Use the CLI parser
                cli.process(self.parser, self.api, shlex.split(line))
            except SystemExit:
                # TODO Return CLI help message
                self.parser.print_help()
                return self.default(line)


class ReloadMixin:
    """Run a reloadable :class:`cmd.` shell."""

    def cmdloop(self, intro=None):
        """Run the REPL, handling special-case exceptions."""
        while True:
            try:
                super().cmdloop()
            except (self._ReloadException, self._QuitException):
                raise
            except Exception:     # Don't die on exceptions, only (^-c)
                traceback.print_exception(*sys.exc_info())

    def do_EOF(self, args):
        """Save the graph before quitting."""
        raise KeyboardInterrupt

    def emptyline(self):
        """Handle empty lines by printing available options."""
        self.do_help('')

    def do_reload(self, *args):
        """Live reload the shell's source code."""
        raise self._ReloadException("Code reload requested by user")

    @classmethod
    def loop(cls, *args, **kwargs):
        """Run the command loop."""
        v = None
        try:
            v = cls(*args, **kwargs)
            v.cmdloop()
        except KeyboardInterrupt:
            print('Goodbye,', os.getenv("USER", 'you person, you.'))
            sys.exit(0)
        finally:
            pass

    # Semi-private exception classes, only for use inside the ReloadMixin.
    class _ReloadException(Exception):
        """The user has requested a source code reload."""
        pass

    class _QuitException(Exception):
        """The user has requested to exit the REPL."""

        def __init__(self, message):
            super().__init__(message)
            self.message = message

        def __str__(self):
            return self.message

    @staticmethod
    def run(api, parser, **kwargs):
        """Run the Valence command-line shell.

        If an error is encountered during initialization, the user is given the
        opportunity to fix the error without quitting the process. This process
        will loop until the code initalizes without exception or the user
        aborts.  The user can also initiate a code reload via 'reload', which
        enters into a error-fix-retry loop.
        """
        while True:
            # Act as if we're importing this code as a module
            from atomic import shell
            try:
                shell.Valence.loop(api, parser)
            except shell.ReloadMixin._ReloadException:
                while True:
                    try:
                        curr_id = id(shell.Valence)
                        print("Reloading Valence ({:d}) shell...".format(
                            curr_id), end="")
                        reload(shell)
                        print("reload complete. "
                              "Restarting Valence ({:d}).".format(curr_id))
                        curr_id = id(shell.Valence)
                        break
                    except:
                        traceback.print_exception(*sys.exc_info())
                        # Allow user to fix code before exiting
                        if parse.input_bool('\nRetry?'):
                            continue
                        raise  # Exit program via exception
            except shell.ReloadMixin._QuitException as qe:
                print(qe)
                break


class Valence(ShlexMixin, ReloadMixin, cmd.Cmd):
    """Valence is the command-line shell a user interacts with."""
    intro = "Welcome to Valence."
    prompt = '(valence)> '

    def __init__(self, api, parser):
        super().__init__()
        self.api = api
        self.parser = parser
        self.logger = log.get_logger('valence')

    def precmd(self, line):
        """Record all cmd interactions."""
        self.logger.debug(line.lower())
        return line
