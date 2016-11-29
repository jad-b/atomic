#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse
import inspect
import sys

from atomic.darkmatter import fileapi
from atomic.errors import AtomicError
from atomic.graph import graph
from atomic.utils import log, display, parse


class Reactor:
    """Reactor provides a CLI and a customized API client.

    The implementation is broken into two parts: configuring the parser w/
    subcommands, and the functions invoked by those subcommands. Invoked
    function will be passed *all* parsed arguments through **kwargs, allowing
    for named arguments, either positional or keyword, to be specified.
    """

    def __init__(self, api, out=sys.stdout):
        """Initialize a Recator instance.

        No action is taken until :meth:`~.Reactor.setup` is invoked.

        Arguments:
            api: Backing API.
            out (:obj:file): File-like object; defaults to :attr:`sys.stdout`.

        Attributes:
            api: Backing API.
            file (:obj:file): File-like object; defaults to :attr:`sys.stdout`.
            logger (:class:`logging.Logger`): CLI logger.
            parser (:class:`argparse.ArgumentParser`): Argument parser.
        """
        self.api = api
        self.logger = log.get_logger('cli')
        self.out = out

    def setup(self):
        """Create a new argument parser.

        Subcommands are discovered by their suffix of '_cmd'.

        Returns:
            :class:`~.Reactor`: The `Reactor` instance; useful for chaining
                instantiation and setup in one line.
        """
        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers(
            help='sub-command help', dest='command')
        # Hook up subcommands
        for name, method in inspect.getmembers(
                self, predicate=inspect.ismethod):
            if name.endswith('cmd'):
                method(subparsers)
        return self

    def process(self, args=None):
        """Maps CLI input to a function that's invoked with the parsed arguments.

        I.e., process(args) -> g(S), where ``g()`` is the mapped function, and
        ``S`` is the set of arguments parsed from the input.

        Arguments:
            args (List[str]): Shell-parsed arguments, as per
                :func:`shlex.split`.

        Raises:
            AtomicError: If any error is encountered during function
                invocation.
        """
        # self.logger.debug("Pre-process: %s" % args)
        ns = self.parser.parse_args(args)
        # self.logger.debug("Post-parse: %s" % ns)
        try:
            ns.func(**vars(ns))
        except AtomicError as e:
            print(e)
        except:
            self.logger.exception("The unexpected has occurred")

    def add_cmd(self, subparser):
        """Add a node to the graph.

        Examples:
            atomic add [-p <parent>] <name> key1=value1 tag1=
        """
        p_add = subparser.add_parser('add', help=self.add_cmd.__doc__,
                                     aliases=['a'])
        p_add.add_argument('-p', '--parent', help='Parent node', type=int)
        p_add.add_argument('args', nargs='+',
                           help='<Node name>... [key=value...]')
        p_add.set_defaults(func=self.add)

    def add(self, args, parent=None, **kwargs):
        """Add a node to the graph.

        Arguments:
            args (list[str]): Strings to be interpreted as a name, followed by
                any number of key=value or tag= pairs.
            parent (int, optional): The ID of a node to link to as a parent.
            **kwargs: Spillover keywords arguments from the passed
                :class:`.argparse.Namespace` object.

        Returns:
            int: The id of the created node

        Raises:
            AtomicError: If the node can't be created, or the parent doesn't
                exist.
        """
        line = ' '.join(args)  # Rejoin args for regex parsing
        name = parse.parse_non_kv(line)
        kvs = parse.parse_key_values(line[len(name):])
        uid = self.api.Node.create(name=name, **kvs)
        self._print("Added node %d " % uid)
        if parent:
            self.api.Edge.create(uid, parent, type=graph.EdgeTypes.parent.name)
        return uid

    def show_cmd(self, subparser):
        """Display info about a node.

        Examples:
            atomic show <nodeID>
        """
        p_show = subparser.add_parser('show', help=self.show_cmd.__doc__)
        p_show.add_argument('uid', help='Node to show', type=int)
        p_show.set_defaults(func=self.show)

    def show(self, uid: int, **kwargs):
        """Show details about a Node in the graph.

        Arguments:
            uid (int): ID of the node.
            **kwargs: Spillover keywords arguments from the passed
                :class:`.argparse.Namespace` object.

        Returns:
            dict: The retrieved node.

        Raises:
            AtomicError: If the node doesn't exist.
        """
        n = self.api.Node.get(uid)
        if n is None:
            raise AtomicError("Node %d not found" % uid)
        self._print(graph.Node(**n))  # Convert to Node object for display
        return n

    def list_cmd(self, subparser):
        """List nodes.

        Examples:
            atomic list
            atomic list key=value
            atomic list q=Lucene||Solr, haven't decided
        """
        p_list = subparser.add_parser(
            'list', help=self.list_cmd.__doc__, aliases=['ls'])
        p_list.set_defaults(func=self.list)

    def list(self, **kwargs):
        self.logger.debug("Listing nodes")
        self._print("Nodes:\n=====")
        nodes = self.api.Node.get()  # Grab all nodes
        display.print_tree(nodes)
        return nodes

    def update_cmd(self, subparser):
        """Update

        Examples:
            atomic update --replace node1 [key=value,...] --rm [key1 tag1 ...]
        """
        p_update = subparser.add_parser('update',
                                        help='Update attributes of a node',
                                        aliases=['u'])
        p_update.add_argument(
            'index', help='Index of node to update', type=int)
        p_update.add_argument('args', nargs='+',
                              help='<Node name>... [key=value...]')
        p_update.add_argument('-r', '--remove', help='Properties to remove',
                              nargs='+')
        p_update.add_argument('--replace', help='Replace the given Node',
                              action='store_true')
        p_update.set_defaults(func=self.update)

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

    def delete_cmd(self, subparser):
        """Command to remove nodes.

        Examples:
            atomic delete node1
        """
        p_delete = subparser.add_parser('delete',
                                        help='Delete a node from the graph',
                                        aliases=['d'])
        p_delete.add_argument('index', help='Index to remove', type=int)
        p_delete.set_defaults(func=self.delete)

    def delete(self, index=-1, **kwargs):
        self.api.Node.delete(index)

    def link(self, src, dest, type, kvs=None, *args, **kwargs):
        if kvs is not None:
            key_values = parse.parse_key_values(' '.join(kvs))
        else:
            key_values = {}
        self.api.Edge.add(src, dest, type_=type, **key_values)

    def link_cmd(self, subparser):
        """Link two nodes.

        Examples:
            atomic link node1 node2 parent [key=value,...]
            atomic link --delete node1 node2
            atomic link node1 node2
        """
        p_link = subparser.add_parser(
            'link', help=self.link_cmd.__doc__, aliases='l')
        p_link.add_argument('src', help='Starting node', type=int)
        p_link.add_argument('dest', help='Destination node', type=int)
        p_link.add_argument('type', help='Relationship type',
                            choices=[graph.EdgeTypes.parent,
                                     graph.EdgeTypes.related,
                                     graph.EdgeTypes.precedes],
                            default=graph.EdgeTypes.related)
        p_link.add_argument('kvs', nargs='*', help='key=value...')
        p_link.add_argument('-d', '--delete', help='Delete the link')
        p_link.set_defaults(func=self.link)

    def _print(self, *args, **kwargs):
        print(*args, file=self.out, **kwargs)


def main():
    api = fileapi.FileAPI(persist=True)
    cli = Reactor(api).setup()
    from atomic.photon import shell  # Prevents circular dependency
    cli.parser.set_defaults(func=shell.Valence.run)
    cli.process()


if __name__ == '__main__':
    main()
