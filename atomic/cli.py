#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse

from atomic import shell, fileapi


def add_arguments(parser, api):
    parser.add_argument('-l', '--list',
                        help='List your thoughts, actions, objects.',
                        action='store_true')

    # Sub-commands
    subs = parser.add_subparsers(help='sub-command help', dest='command')

    # Add
    p_add = subs.add_parser('add', help='Add node', aliases=['a'])
    p_add.add_argument('title', nargs='+', help='Title')
    p_add.add_argument('-p', '--parent', help='Parent node')
    p_add.add_argument('-b', '--body', help='Body')

    def add_func(args):
        title_str = ' '.join(args.title)
        api.add(parent=args.parent, name=title_str, body=args.body)
        # api.binary_add(args)  # Guide them through insertion
    p_add.set_defaults(func=add_func)

    # Update
    p_update = subs.add_parser('update', help='Update help',
                               aliases=['u'])
    p_update.add_argument('index', help='Index of node to update', type=int)
    p_update.add_argument('-t', '--title', nargs='+', help='Title')
    p_update.add_argument('-b', '--body', help='Body')

    def update_func(args):
        title_str = ' '.join(args.title)
        api.update(args.index, title=title_str, body=args.body)
    p_update.set_defaults(func=update_func)

    # Delete
    p_delete = subs.add_parser('delete', help='Delete help',
                               aliases=['d'])
    p_delete.add_argument('index', help='Index to remove', type=int)

    def delete_func(args):
        api.delete(args.index)
    p_delete.set_defaults(func=delete_func)


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=shell.main)
    api = fileapi.FileAPI()
    add_arguments(parser, api)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
