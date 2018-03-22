""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('update', help='update stack in AWS')
    parser.add_argument('-c', '--create_missing', action='store_true',
                        help='create stack in AWS if it does not exist')
    parser.add_argument('-e', '--events', action='store_true',
                        help='display events while waiting for the update to complete ('
                             'implies --wait)')
    parser.add_argument('-w', '--wait', action='store_true',
                        help='wait for update to finish (synchronous mode)')
    parser.add_argument('stack', help='stack to update')
    parser.set_defaults(func=cmd_update)


def cmd_update(args):
    """update or create a stack in AWS."""
    raise RuntimeError("Not implemented")
