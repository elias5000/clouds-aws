""" Command parser definition """

import logging

from botocore.exceptions import ClientError

from clouds_aws.cli.common import load_local_stack
from clouds_aws.cli.events import poll_events
from clouds_aws.remote_stack import RemoteStack, list_stacks as remote_stacks

LOG = logging.getLogger(__name__)


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
    """
    Update or create a stack in AWS
    :param args:
    :return:
    """
    local_stack = load_local_stack(args.stack)
    remote_stack = RemoteStack(args.stack, args.region, args.profile)

    try:
        if args.stack in remote_stacks(args.region, args.profile):
            remote_stack.load()
            remote_stack.update(
                local_stack.template,
                local_stack.parameters
            )

        elif args.create_missing:
            remote_stack.create(
                local_stack.template,
                local_stack.parameters
            )

        else:
            LOG.error("Stack %s does not exist. Not updating without explicit create", args.stack)
            exit(1)

    except ClientError as err:
        if "No updates are to be performed" in str(err):
            LOG.warning("No updates are to be performed")
            exit(0)

        # throw up if not "no updates" case
        raise err

    # poll until stable state is reached
    if args.events or args.wait:
        poll_events(remote_stack, args.events)
