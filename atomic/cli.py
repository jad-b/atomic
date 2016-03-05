from argparse import ArgumentParser


def todo_parser():
    # top-level parser
    root = ArgumentParser(prog='todo')
    subparsers = root.add_subparsers(title='subcommands', dest='subparser_name')

    # add
    add = subparsers.add_parser('add', aliases=['a'], help='Add a todo')
    add.add_argument('name')
    add.add_argument('-t', '--time', help='Time estimate')

    # list
    liszt = subparsers.add_parser('list', aliases=['l'], help='List todos')
    liszt.set_defaults(func=list_todos)

    return root


def list_todos():
    """Load and display TODOs."""
    print("TODOs go here.")


def main():
    parser = todo_parser()
    args = vars(parser.parse_args())
    if args.get('name'):
        print(args['name'])
    elif args.get('func'):
        args['func']()


if __name__ == '__main__':
    main()
