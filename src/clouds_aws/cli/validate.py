""" Command parser definition """

import logging

from clouds_aws.cli.common import load_local_stack
from clouds_aws.local_stack import list_stacks as local_stacks
from clouds_aws.remote_stack.aws_client import CloudFormation, CloudFormationError

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('validate', help='validate stack template')
    parser.add_argument('-a', '--all', action='store_true', help='validate all stacks')
    parser.add_argument('stack', help='stack to validate', nargs='*')
    parser.set_defaults(func=cmd_validate)


def cmd_validate(args):
    """
    Validate one or several stacks
    :param args:
    :return:
    """
    stacks = args.stack
    if args.all:
        stacks = local_stacks()

    cfn = CloudFormation(args.region, args.profile)
    success = True
    for stack in stacks:
        LOG.info("Validating stack %s", stack)
        success = success and validate_stack(cfn, stack)

    if not success:
        exit(1)


def validate_stack(cfn, stack):
    """
    Validate a stack against the AWS API
    :type cfn: CloudFormation
    :param cfn: CloudFormation client object
    :param stack: stack name
    :return:
    """
    local_stack = load_local_stack(stack)
    try:
        cfn.validate(local_stack.template.as_string())
    except CloudFormationError as err:
        LOG.error("Failed to validate stack %s:", stack)
        LOG.error(err)
        return False

    return True
