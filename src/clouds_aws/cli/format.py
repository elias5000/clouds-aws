""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('format',
                                   help='normalize stack template(s) (for better diffs)')
    parser.add_argument('-a', '--all', action='store_true', help='reformat all stacks')
    parser.add_argument('-p', '--pipe', action='store_true',
                        help='pipe mode - read template from stdin and output to stdout')
    parser.add_argument('stack', help='stack to reformat', nargs='*')
    parser.set_defaults(func=cmd_reformat)


def cmd_reformat(args):
    """reformat stack"""
    raise RuntimeError("Not implemented")
