""" Command parser definition """

import json
import logging
from sys import stdin

from clouds_aws.cli.common import load_local_stack
from clouds_aws.local_stack import list_stacks as local_stacks
from clouds_aws.local_stack.helpers import dump_json
from clouds_aws.local_stack.template import TYPE_JSON

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('format',
                                   help='normalize stack template(s) (for better diffs)')
    parser.add_argument('-a', '--all', action='store_true', help='reformat all stacks')
    parser.add_argument('-p', '--pipe', action='store_true',
                        help='pipe mode - read template from stdin and output to stdout')
    parser.add_argument('stack', help='stack to reformat', nargs='*')
    parser.set_defaults(func=cmd_reformat)


def cmd_reformat(args):
    """
    Reformat stack(s)
    :param args:
    :return:
    """
    if args.pipe:
        print(dump_json(json.loads(stdin.read())))
        exit()

    stacks = args.stack
    if args.all:
        stacks = local_stacks()

    for stack in stacks:
        LOG.info("Formatting stack %s", stack)
        reformat_stack(stack)


def reformat_stack(stack_name):
    """
    Reformat stack in place
    :param stack_name:
    :return:
    """
    stack = load_local_stack(stack_name)
    if stack.template.tpl_format != TYPE_JSON:
        LOG.warning("Cannot reformat stack %s: not of type JSON")
        return

    stack.update(dump_json(stack.template.as_dict()), stack.parameters.parameters)
    stack.save()
