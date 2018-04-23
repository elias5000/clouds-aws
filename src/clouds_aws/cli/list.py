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
    parser.add_argument("-l", "--local", action="store_true", help="list only local stacks")
    parser.add_argument("-r", "--remote", action="store_true", help="list only stacks in AWS")
    parser.set_defaults(func=cmd_list)


def cmd_list(args):
    """
    Print a list of stacks
    :param args:
    :return:
    """
    stacks = {}
    if args.remote or not (args.remote or args.local):
        stacks = remote_stacks(args.region, args.profile)

    if args.local or not (args.remote or args.local):
        for stack in [key for key in local_stacks() if key not in stacks.keys()]:
            stacks[stack] = "LOCAL_ONLY"

    print(tabulate(sorted(stacks.items()), ("Name", "Status")))
