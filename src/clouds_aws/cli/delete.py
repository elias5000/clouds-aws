""" Command parser definition """

import logging

from clouds_aws.cli.events import poll_events
from clouds_aws.remote_stack import RemoteStack, list_stacks as remote_stacks

LOG = logging.getLogger(__name__)


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
    """
    Delete stack in AWS
    :param args:
    :return:
    """
    if args.stack not in remote_stacks(args.region, args.profile):
        LOG.warning("Stack %s does not exist", args.stack)
        exit(1)

    if not args.force:
        LOG.warning("You have to apply force to delete %s", args.stack)
        exit(1)

    remote_stack = RemoteStack(args.stack, args.region, args.profile)
    remote_stack.load()
    remote_stack.delete()

    # poll until stable state is reached
    if args.events or args.wait:
        poll_events(remote_stack, args.events)
