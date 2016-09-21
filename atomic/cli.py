#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse

from atomic import shell, fileapi, log, display, graph, parse

logger = log.get_logger('cli')


def add_arguments(parser, api):
    # Sub-commands
    subs = parser.add_subparsers(help='sub-command help', dest='command')

    # List/Get
    # atomic list
    # atomic list key=value
    # atomic list q=Lucene||Solr, haven't decided
    p_list = subs.add_parser('list', help='List nodes', aliases=['ls', 'show'])

    def list_func(args):
        logger.debug("Listing nodes")
        print("Nodes:\n=====")
        nodes = api.Node.get()  # Grab all nodes
        display.print_tree(nodes)
    p_list.set_defaults(func=list_func)

    # Add
    # atomic add
    p_add = subs.add_parser('add', help='Add a node to the graph.',
                            aliases=['a'])
    p_add.add_argument('-p', '--parent', help='Parent node')
    p_add.add_argument('args', nargs='+', help='<Node name>... [key=value...]')

    def add_func(args):
        name = parse.parse_non_kv(args.args)
        kwargs = parse.parse_key_values(args.args[len(name):])
        api.Node.add(parent=args.parent, name=name, **kwargs)
    p_add.set_defaults(func=add_func)

    # Update
    # atomic update node1 [key=value,...]
    p_update = subs.add_parser('update', help='Update attributes of a node',
                               aliases=['u'])
    p_update.add_argument('index', help='Index of node to update', type=int)

    def update_func(args):
        name_str = ' '.join(args.name)
        api.Node.update(args.index, name=name_str, body=args.body)
    p_update.set_defaults(func=update_func)

    # Delete
    # atomic delete node1
    p_delete = subs.add_parser('delete', help='Delete a node from the graph',
                               aliases=['d'])
    p_delete.add_argument('index', help='Index to remove', type=int)

    def delete_func(args):
        api.Node.delete(args.index)
    p_delete.set_defaults(func=delete_func)

    # Link
    # atomic link node1 node2 parent [key=value,...]
    # atomic link --delete node1 node2
    # atomic link node1 node2
    p_link = subs.add_parser('link', help='Link two nodes', aliases='l')
    p_link.add_argument('src', help='Starting node')
    p_link.add_argument('dest', help='Destination node')
    p_link.add_argument('type', help='Relationship type',
                        choices=[graph.PARENT, graph.RELATED, graph.PRECEDES],
                        default=graph.RELATED)
    p_link.add_argument('-d', '--delete', help='Delete the link')

    def link_func(args):
        api.Edge.add(args.src, args.dest, type_=args.type)
    p_link.set_defaults(func=link_func)


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=shell.main)
    api = fileapi.FileAPI()
    add_arguments(parser, api)

    args = parser.parse_args()
    logger.debug("Arguments: %s", args.command)
    args.func(args)


if __name__ == '__main__':
    main()
