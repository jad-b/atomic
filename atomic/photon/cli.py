#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse
import sys

from atomic.darkmatter import fileapi
from atomic.graph import graph
from atomic.utils import log, display, parse

logger = log.get_logger('cli')


class CLIClient:
    """CLIClient provides business logic of the CLI by adapting the standard
    API."""

    def __init__(self, api, file=sys.stdout):
        """Initialize the CLI client.

        Arguments:
            api (:class:`GraphAPISpec`): Backing API.
        """
        self.api = api
        self.logger = log.get_logger('self')
        self.file = file

    def list(self, **kwargs):
        self.logger.debug("Listing nodes")
        self._print("Nodes:\n=====")
        nodes = self.api.Node.get()  # Grab all nodes
        display.print_tree(nodes)

    def show(self, index, **kwargs):
        n = self.api.Node.get(index)
        self._print(graph.Node(**n))

    def add(self, args, parent=None, **kwargs):
        line = ' '.join(args)  # Rejoin args for regex parsing
        name = parse.parse_non_kv(line)
        kvs = parse.parse_key_values(line[len(name):])
        uid = self.api.Node.create(parent=parent, name=name, **kvs)
        self._print("Added node %d " % uid)

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

    def _print(self, *args, **kwargs):
        print(*args, file=self.file, **kwargs)


def list_cmd(subparser, client):
    """List nodes.

    Examples:
        atomic list
        atomic list key=value
        atomic list q=Lucene||Solr, haven't decided
    """
    p_list = subparser.add_parser(
        'list', help=list_cmd.__doc__, aliases=['ls'])
    p_list.set_defaults(func=client.list)


def show_cmd(subparser, client):
    """Display info about a node.

    Examples:
        atomic show <nodeID>
    """
    p_show = subparser.add_parser('show', help=show_cmd.__doc__)
    p_show.add_argument('index', help='Node to show', type=int)
    p_show.set_defaults(func=client.show)


def add_cmd(subparser, client):
    """Add a node to the graph.

    Examples:
        atomic add [-p <parent>] key1=value1 tag1=
    """
    p_add = subparser.add_parser('add', help='Add a node to the graph.',
                                 aliases=['a'])
    p_add.add_argument('-p', '--parent', help='Parent node')
    p_add.add_argument('args', nargs='+', help='<Node name>... [key=value...]')
    p_add.set_defaults(func=client.add)


def update_cmd(subparser, client):
    """Update

    Examples:
        atomic update --replace node1 [key=value,...] --rm [key1 tag1 ...]
    """
    p_update = subparser.add_parser('update',
                                    help='Update attributes of a node',
                                    aliases=['u'])
    p_update.add_argument('index', help='Index of node to update', type=int)
    p_update.add_argument('args', nargs='+',
                          help='<Node name>... [key=value...]')
    p_update.add_argument('-r', '--remove', help='Properties to remove',
                          nargs='+')
    p_update.add_argument('--replace', help='Replace the given Node',
                          action='store_true')
    p_update.set_defaults(func=client.update)


def delete_cmd(subparser, client):
    """Delete

    Examples:
        atomic delete node1
    """
    p_delete = subparser.add_parser('delete',
                                    help='Delete a node from the graph',
                                    aliases=['d'])
    p_delete.add_argument('index', help='Index to remove', type=int)
    p_delete.set_defaults(func=client.delete)


def link_cmd(subparser, client):
    """Link two nodes.

    Examples:
        atomic link node1 node2 parent [key=value,...]
        atomic link --delete node1 node2
        atomic link node1 node2
    """
    p_link = subparser.add_parser('link', help=link_cmd.__doc__, aliases='l')
    p_link.add_argument('src', help='Starting node', type=int)
    p_link.add_argument('dest', help='Destination node', type=int)
    p_link.add_argument('type', help='Relationship type',
                        choices=[graph.PARENT, graph.RELATED, graph.PRECEDES],
                        default=graph.RELATED)
    p_link.add_argument('kvs', nargs='*', help='key=value...')
    p_link.add_argument('-d', '--delete', help='Delete the link')
    p_link.set_defaults(func=client.link)


def new_parser(api_client):
    """Create a new argument parser."""
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(help='sub-command help', dest='command')
    commands = (  # Hook up subcommands
        list_cmd,
        show_cmd,
        add_cmd,
        update_cmd,
        delete_cmd,
        link_cmd
    )
    for cmd in commands:
        cmd(subp, api_client)
    return parser


def process(parser, api, args=None):
    """Process arguments and call the matching function."""
    # print("Pre-process: %s" % args)
    ns = parser.parse_args(args)
    # print("Post-parse: %s" % ns)
    ns.func(api=api, parser=parser, **vars(ns))


def main():
    api = fileapi.FileAPI()
    api_client = CLIClient(api)
    parser = new_parser(api_client)
    from atomic import shell  # Prevents circular dependency
    parser.set_defaults(func=shell.Valence.run)
    process(parser, api)


if __name__ == '__main__':
    main()
