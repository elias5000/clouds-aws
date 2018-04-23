""" Command parser definition """

import logging

from clouds_aws.local_stack import LocalStack
from clouds_aws.remote_stack import RemoteStack
from clouds_aws.remote_stack.aws_client import CloudFormation

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser("dump", help="dump a stack in AWS to current directory")
    parser.add_argument("-a", "--all", action="store_true", help="dump all stacks")
    parser.add_argument("-f", "--force", action="store_true",
                        help="overwrite existing local stack")
    parser.add_argument("stack", help="stack to dump", nargs="*")
    parser.set_defaults(func=cmd_dump)


def cmd_dump(args):
    """
    Dump stack(s) to local disk
    :param args:
    :return:
    """
    if args.all:
        cfn = CloudFormation(args.region, args.profile)
        stacks = cfn.list_stacks()
    else:
        stacks = args.stack
    for stack in stacks:
        dump_stack(args.region, args.profile, stack, args.force)


def dump_stack(region, profile, stack, force):
    """
    Dump one stack to files
    :param region: aws region
    :param profile: aws profile name
    :param stack: stack type
    :param force: force overwrite
    :return:
    """
    LOG.info("Loading remote stack %s", stack)
    remote = RemoteStack(stack, region, profile)
    remote.load()

    LOG.info("Creating local stack %s", stack)
    local = LocalStack(stack)

    if local.template.exists() and not force:
        LOG.warning("Stack %s exists locally. Not overwriting without force", stack)
        return

    LOG.info("Saving local stack %s", stack)
    local.update(remote.template, remote.parameters)
    local.save()
