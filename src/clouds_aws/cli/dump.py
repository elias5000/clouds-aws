""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('dump', help='dump a stack in AWS to current directory')
    parser.add_argument('-a', '--all', action='store_true', help='dump all stacks')
    parser.add_argument('-f', '--force', action='store_true',
                        help='overwrite existing local stack')
    parser.add_argument('stack', help='stack to dump', nargs='*')
    parser.set_defaults(func=cmd_dump)


def cmd_dump(args):
    """dump stack in AWS to local disk"""
    raise RuntimeError("Not implemented")
