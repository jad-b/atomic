#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli
===
Command line interface.
"""
import argparse


def add_arguments(parser, q):
    parser.add_argument('-l', '--list', help='List your Todos',
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
        q.add(parent=args.parent, name=title_str, body=args.body)
        # q.binary_add(todo)  # Guide them through insertion
    p_add.set_defaults(func=add_func)

    # Update
    p_update = subs.add_parser('update', help='Update help',
                               aliases=['u'])
    p_update.add_argument('index', help='Index of node to update', type=int)
    p_update.add_argument('-t', '--title', nargs='+', help='Title')
    p_update.add_argument('-b', '--body', help='Body')

    def update_func(args):
        title_str = ' '.join(args.title)
        q.update(args.index, title=title_str, body=args.body)
    p_update.set_defaults(func=update_func)

    # Delete
    p_delete = subs.add_parser('delete', help='Delete Todo help',
                               aliases=['d'])
    p_delete.add_argument('index', help='Index to remove', type=int)

    def delete_func(args):
        q.delete(args.index)
    p_delete.set_defaults(func=delete_func)

    # Shell
    parser.add_argument('-s', '--shell', help='Run the Q shell',
                        action='store_true')


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)
    args = parser.parse_args()
    q = None
    add_arguments(parser, q)

    if args.func is not None:
        try:
            args.func(args)
        finally:
            q.save()


if __name__ == '__main__':
    main()
