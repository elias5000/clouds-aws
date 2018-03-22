""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('clone', help='clone a stack in the current directory')
    parser.add_argument('stack', help='name of the stack to clone')
    parser.add_argument('new_stack', help='name of the new stack')
    parser.set_defaults(func=cmd_clone)


def cmd_clone(args):
    """clone local stack"""
    raise RuntimeError("Not implemented")
