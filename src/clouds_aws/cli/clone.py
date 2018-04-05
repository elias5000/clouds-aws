""" Command parser definition """

import logging

from clouds_aws.local_stack import LocalStack, LocalStackError
from clouds_aws.local_stack.helpers import dump_json, dump_yaml

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser("clone", help="clone a stack in the current directory")
    parser.add_argument("stack", help="name of the stack to clone")
    parser.add_argument("new_stack", help="name of the new stack")
    parser.add_argument("-f", "--force", action="store_true", help="overwrite existing target")
    parser.add_argument("-t", "--type", choices=["yaml", "json"], default=None,
                        help="template format (default: same as source)")
    parser.set_defaults(func=cmd_clone)


def cmd_clone(args):
    """
    Clone an existing local stack into a new stack
    :param args:
    :return:
    """
    local = LocalStack(args.stack)
    try:
        local.load()
    except LocalStackError as err:
        LOG.error(err)
        exit(1)

    new = LocalStack(args.new_stack)

    if new.template.exists() and not args.force:
        LOG.warning("Stack %s already exists. Not overwriting without force", args.new_stack)
        return

    if args.type == "json":
        template = dump_json(local.template.as_dict())
    elif args.type == "yaml":
        template = dump_yaml(local.template.as_dict())
    else:
        template = local.template.as_string()

    new.update(template, local.parameters.parameters)
    new.save()
