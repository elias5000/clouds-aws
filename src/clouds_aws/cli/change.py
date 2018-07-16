""" Command parser definition """

import logging
from time import sleep

from botocore.exceptions import ClientError
from tabulate import tabulate

from clouds_aws.cli.common import load_local_stack
from clouds_aws.cli.events import poll_events
from clouds_aws.local_stack.helpers import dump_yaml, dump_json
from clouds_aws.remote_stack import RemoteStack, list_stacks as remote_stacks
from clouds_aws.remote_stack.change_set import ChangeSet

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('change', help='use change sets to manipulate stacks in AWS')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    p_create = subparsers.add_parser('create', help='create new change set')
    p_create.add_argument('-c', '--create_missing', action='store_true',
                          help='create stack in AWS if it does not exist')
    p_create.add_argument('-d', '--description', default="")
    p_create.add_argument('-q', '--quiet', action='store_true',
                          help='do not output change set details')
    p_create.add_argument('stack', help="stack name")
    p_create.add_argument('name', help="change set name")
    p_create.set_defaults(func=cmd_create)

    p_list = subparsers.add_parser('list', help='list existing change sets')
    p_list.add_argument('stack', help="stack name")
    p_list.set_defaults(func=cmd_list)

    p_describe = subparsers.add_parser('describe', help='describe a change set')
    p_describe.add_argument('stack', help="stack name")
    p_describe.add_argument('name', help="change set name")
    p_describe.add_argument('--json', help="output as json", action='store_true')
    p_describe.add_argument('--yaml', help="output as yaml", action='store_true')
    p_describe.set_defaults(func=cmd_describe)

    p_execute = subparsers.add_parser('execute', help='execute a change set')
    p_execute.add_argument('stack', help="stack name")
    p_execute.add_argument('name', help="change set name")
    p_execute.add_argument('-e', '--events', action='store_true',
                           help='display events while waiting for the update to complete ('
                                'implies --wait)')
    p_execute.add_argument('-w', '--wait', action='store_true',
                           help='wait for update to finish (synchronous mode)')
    p_execute.set_defaults(func=cmd_execute)

    p_delete = subparsers.add_parser('delete', help='delete a change set')
    p_delete.add_argument('stack', help="stack name")
    p_delete.add_argument('name', help="change set name")
    p_delete.set_defaults(func=cmd_delete)


def cmd_create(args):
    """
    Create a new change set
    :param args: parser arguments
    :return:
    """
    local_stack = load_local_stack(args.stack)
    remote_stack = RemoteStack(args.stack, args.region, args.profile)

    try:
        if args.stack in remote_stacks(args.region, args.profile):
            remote_stack.load()
            if args.name in remote_stack.change_sets:
                LOG.warning("Change set %s already exists.", args.name)
                exit(1)

        elif not args.create_missing:
            LOG.error("Stack %s does not exist. Aborting without explicit create", args.stack)
            exit(1)

        change_set = ChangeSet(remote_stack, args.name)
        change_set.create(local_stack.template, local_stack.parameters, args.description)

        if not args.quiet:
            loop = 0
            while True and loop < 10:
                change_set.load()
                if change_set.change["Status"] == "CREATE_COMPLETE":
                    break

                if change_set.change["Status"] == "FAILED":
                    LOG.error("Failed to create change set.")
                    exit(1)

                # poll for completion
                sleep(3)
                loop += 1

            cmd_describe(args)

    except ClientError as err:
        raise err


def cmd_list(args):
    """
    Print list of change sets
    :param args:
    :return:
    """
    remote_stack = RemoteStack(args.stack, args.region, args.profile)

    try:
        remote_stack.load()
        if remote_stack.change_sets:
            print(tabulate(remote_stack.change_sets.values(), ("Name", "Description", "Status")))

    except ClientError as err:
        raise err


def cmd_describe(args):
    """
    Describe a change set
    :param args:
    :return:
    """
    remote_stack = RemoteStack(args.stack, args.region, args.profile)
    remote_stack.load()

    try:
        if args.json:
            print(dump_json(remote_stack.get_change_set(args.name).change["Changes"]))
            return
        if args.yaml:
            print(dump_yaml(remote_stack.get_change_set(args.name).change["Changes"]))
            return

    except AttributeError:
        pass

    changes = remote_stack.get_change_set(args.name).changes()
    print(tabulate(changes, headers='keys'))


def cmd_execute(args):
    """
    Execute a change set
    :param args:
    :return:
    """
    remote_stack = RemoteStack(args.stack, args.region, args.profile)
    remote_stack.load()
    change = remote_stack.get_change_set(args.name)
    change.execute()

    # poll until stable state is reached
    if args.events or args.wait:
        poll_events(remote_stack, args.events)


def cmd_delete(args):
    """
    Delete a change set
    :param args:
    :return:
    """
    remote_stack = RemoteStack(args.stack, args.region, args.profile)
    remote_stack.load()
    change = remote_stack.get_change_set(args.name)
    change.delete()
