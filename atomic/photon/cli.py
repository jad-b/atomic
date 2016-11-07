#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse

from atomic import fileapi, log, graph, client

logger = log.get_logger('cli')


def _add_arguments(parser, client, *cli_commands):
    """Prepare CLI commands."""
    subp = parser.add_subparsers(help='sub-command help', dest='command')
    for cmd in cli_commands:
        cmd(subp, client)


def list_cmd(subparser, client):
    """List/Get

    Examples:
        atomic list
        atomic list key=value
        atomic list q=Lucene||Solr, haven't decided
    """
    p_list = subparser.add_parser('list', help='List nodes', aliases=['ls'])
    p_list.set_defaults(func=client.list)


def show_cmd(subparser, client):
    """Show

    Examples:
        atomic show <nodeID>
    """
    p_show = subparser.add_parser('show', help='Show node')
    p_show.add_argument('index', help='Node to show', type=int)
    p_show.set_defaults(func=client.show)


def add_cmd(subparser, client):
    """Add

    Examples:
        atomic add
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
    """Link

    Examples:
        atomic link node1 node2 parent [key=value,...]
        atomic link --delete node1 node2
        atomic link node1 node2
    """
    p_link = subparser.add_parser('link', help='Link two nodes', aliases='l')
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
    _add_arguments(
        parser,
        api_client,
        list_cmd,
        show_cmd,
        add_cmd,
        update_cmd,
        delete_cmd,
        link_cmd
    )
    return parser


def process(parser, api, args=None):
    """Process arguments and call the matching function."""
    # print("Pre-process: %s" % args)
    ns = parser.parse_args(args)
    # print("Post-parse: %s" % ns)
    ns.func(api=api, parser=parser, **vars(ns))


def main():
    api = fileapi.FileAPI()
    api_client = client.ApiClient(api)
    parser = new_parser(api_client)
    from atomic import shell  # Prevents circular dependency
    parser.set_defaults(func=shell.Valence.run)
    process(parser, api)


if __name__ == '__main__':
    main()
