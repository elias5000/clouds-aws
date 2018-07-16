""" list command parser definition """

import logging

from tabulate import tabulate

from clouds_aws.local_stack import list_stacks as local_stacks
from clouds_aws.remote_stack import list_stacks as remote_stacks

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser("list", help="list available stacks")
    parser.add_argument("-l", "--local", action="store_true",
                        help="list only stacks that exist locally")
    parser.add_argument("-r", "--remote", action="store_true", help="list only stacks in AWS")
    parser.set_defaults(func=cmd_list)


def cmd_list(args):
    """
    Print a list of stacks
    :param args:
    :return:
    """
    stacks = remote_stacks(args.region, args.profile)

    # enrich stacks with local stacks
    if not args.remote:
        for stack in [key for key in local_stacks() if key not in stacks.keys()]:
            stacks[stack] = "LOCAL_ONLY"

    # only list stacks that exist locally
    if args.local:
        stacks = {key: stacks[key] for key in local_stacks() if key in stacks.keys()}

    print(tabulate(sorted(stacks.items()), ("Name", "Status")))
