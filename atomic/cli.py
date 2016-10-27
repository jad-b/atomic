#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse

from atomic import fileapi, log, display, graph, parse

logger = log.get_logger('cli')


def add_arguments(parser, api):
    # Sub-commands
    subs = parser.add_subparsers(help='sub-command help', dest='command')

    # List/Get
    # atomic list
    # atomic list key=value
    # atomic list q=Lucene||Solr, haven't decided
    p_list = subs.add_parser('list', help='List nodes', aliases=['ls'])

    def list_func(api, **kwargs):
        logger.debug("Listing nodes")
        print("Nodes:\n=====")
        nodes = api.Node.get()  # Grab all nodes
        display.print_tree(nodes)
    p_list.set_defaults(func=list_func)

    # Show
    # atomic show <nodeID>
    p_show = subs.add_parser('show', help='Show node')
    p_show.add_argument('index', help='Node to show', type=int)

    def show_func(api, index, **kwargs):
        n = api.Node.get(index)
        display.print_node(index, n)
    p_show.set_defaults(func=show_func)

    # Add
    # atomic add
    p_add = subs.add_parser('add', help='Add a node to the graph.',
                            aliases=['a'])
    p_add.add_argument('-p', '--parent', help='Parent node')
    p_add.add_argument('args', nargs='+', help='<Node name>... [key=value...]')

    def add_func(api, args, parent=None, **kwargs):
        line = ' '.join(args)  # Rejoin args for regex parsing
        name = parse.parse_non_kv(line)
        kwargs = parse.parse_key_values(line[len(name):])
        api.Node.add(parent=parent, name=name, **kwargs)
    p_add.set_defaults(func=add_func)

    # Update
    # atomic update --replace node1 [key=value,...] --rm [key1 tag1 ...]
    p_update = subs.add_parser('update', help='Update attributes of a node',
                               aliases=['u'])
    p_update.add_argument('index', help='Index of node to update', type=int)
    p_update.add_argument('args', nargs='+',
                          help='<Node name>... [key=value...]')
    p_update.add_argument('-r', '--remove', help='Properties to remove',
                          nargs='+')
    p_update.add_argument('--replace', help='Replace the given Node',
                          action='store_true')

    def update_func(api, index, args, remove=None, replace=False, **kwargs):
        line = ' '.join(args)  # Rejoin args for regex parsing
        kvs = parse.parse_key_values(line)
        if replace:
            api.Node.update(index, **kvs)
        else:  # Assemble patch
            if remove is not None:
                for prop in remove:
                    kvs[prop] = None
            api.Node.patch(index, **kvs)
    p_update.set_defaults(func=update_func)

    # Delete
    # atomic delete node1
    p_delete = subs.add_parser('delete', help='Delete a node from the graph',
                               aliases=['d'])
    p_delete.add_argument('index', help='Index to remove', type=int)

    def delete_func(api, index=-1, **kwargs):
        api.Node.delete(index)
    p_delete.set_defaults(func=delete_func)

    # Link
    # atomic link node1 node2 parent [key=value,...]
    # atomic link --delete node1 node2
    # atomic link node1 node2
    p_link = subs.add_parser('link', help='Link two nodes', aliases='l')
    p_link.add_argument('src', help='Starting node', type=int)
    p_link.add_argument('dest', help='Destination node', type=int)
    p_link.add_argument('type', help='Relationship type',
                        choices=[graph.PARENT, graph.RELATED, graph.PRECEDES],
                        default=graph.RELATED)
    p_link.add_argument('kvs', nargs='*', help='key=value...')
    p_link.add_argument('-d', '--delete', help='Delete the link')

    def link_func(api, src, dest, type, kvs=None, *args, **kwargs):
        if kvs is not None:
            key_values = parse.parse_key_values(' '.join(kvs))
        else:
            key_values = {}
        api.Edge.add(src, dest, type_=type, **key_values)
    p_link.set_defaults(func=link_func)


def new_parser(api):
    """Create a new argument parser."""
    parser = argparse.ArgumentParser()
    add_arguments(parser, api)
    return parser


def process(parser, api, args=None):
    """Process arguments and call the matching function."""
    # print("Pre-process: %s" % args)
    ns = parser.parse_args(args)
    # print("Post-parse: %s" % ns)
    ns.func(api=api, parser=parser, **vars(ns))


def main():
    api = fileapi.FileAPI()
    parser = new_parser(api)
    from atomic import shell  # Prevents circular dependency
    parser.set_defaults(func=shell.Valence.run)
    process(parser, api)


if __name__ == '__main__':
    main()
