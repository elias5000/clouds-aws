""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('validate', help='validate stack template')
    parser.add_argument('-a', '--all', action='store_true', help='validate all stacks')
    parser.add_argument('stack', help='stack to validate', nargs='*')
    parser.set_defaults(func=cmd_validate)


def cmd_validate(args):
    """validate local stack(s)"""
    raise RuntimeError("Not implemented")
