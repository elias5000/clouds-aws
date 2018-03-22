""" Command parser definition """


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('delete', help='delete a stack in AWS')
    parser.add_argument('-e', '--events', action='store_true',
                        help='display events while waiting for the deletion to complete ('
                             'implies --wait)')
    parser.add_argument('-f', '--force', action='store_true', help='force deletion')
    parser.add_argument('-w', '--wait', action='store_true',
                        help='wait for deletion to finish (synchronous mode)')
    parser.add_argument('stack', help='stack to delete')
    parser.set_defaults(func=cmd_delete)


def cmd_delete(args):
    """deletes a stack in AWS."""
    raise RuntimeError("Not implemented")
