""" describe command parser definition """

import logging

from tabulate import tabulate

from clouds_aws.local_stack.helpers import dump_json
from clouds_aws.remote_stack import RemoteStack, CloudFormationError

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser("describe", help="output parameters, outputs, and "
                                                    "resources of a stack in AWS")
    parser.add_argument("-j", "--json", action="store_true", help="output as JSON")
    parser.add_argument("stack", help="stack to describe")
    parser.set_defaults(func=cmd_describe)


def cmd_describe(args):
    """
    Print details of a stack
    :param args:
    :return:
    """
    try:
        stack = RemoteStack(args.stack, args.region)
        stack.load()

        if args.json:
            print(dump_json({
                "Parameters": stack.parameters,
                "Outputs": stack.outputs,
                "Resources": stack.resources
            }))
            return

        if stack.parameters:
            print(tabulate(sorted(stack.parameters.items()), ("Parameter", "Value")))
            print()

        if stack.outputs:
            print(tabulate(sorted(stack.outputs.items()), ("Output", "Value")))
            print()

        print(tabulate(
            sorted([(key, val["ResourceType"], val["PhysicalResourceId"])
                    for key, val in stack.resources.items()]),
            ("Resource", "Type", "PhysicalId")
        ))
        print()

    except CloudFormationError as err:
        LOG.error(err)
        exit(1)
