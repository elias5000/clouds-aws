""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('events', help='output all events of a stack')
    parser.add_argument('-f', '--follow', action='store_true',
                        help='follow events until stack transition complete')
    parser.add_argument('stack', help='stack name')
    parser.set_defaults(func=cmd_events)


def cmd_events(args):
    """prints all events for a stack"""
    raise RuntimeError("Not implemented")
