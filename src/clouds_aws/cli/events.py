""" Command parser definition """

import logging
from sys import stdout
from time import sleep

from clouds_aws.remote_stack import RemoteStack, RemoteStackError

LOG = logging.getLogger(__name__)


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('events', help='output all events of a stack')
    parser.add_argument('-f', '--follow', action='store_true',
                        help='follow events until stack transition complete')
    parser.add_argument('-l', '--limit', help='limit number of most recent events displayed')
    parser.add_argument('stack', help='stack name')
    parser.set_defaults(func=cmd_events)


def cmd_events(args):
    """
    Print stack events
    :param args:
    :return:
    """
    stack = RemoteStack(args.stack, args.region, args.profile)
    stack.load()

    events = stack.events
    if args.limit:
        events = events[int(args.limit) * -1:]

    print_events(events)

    # poll until stable state is reached
    if args.follow:
        poll_events(stack)


def poll_events(stack, display=True):
    """
    :param stack: remote stack object
    :param display:
    :return:
    """
    while True:
        try:
            new_events = stack.poll_events()

            if new_events and display:
                print_events(new_events)
            exit_if_transition_finished(stack.events)

        except RemoteStackError as err:
            LOG.warning(err)
            exit(0)

        sleep(5)


def exit_if_transition_finished(events):
    """
    Exits if the stack reached a stable state
    :param events:
    :return:
    """
    if events and events[-1]["ResourceType"] == "AWS::CloudFormation::Stack":
        if events[-1]["ResourceStatus"][-8:] == 'COMPLETE':
            exit(0)
        if events[-1]["ResourceStatus"] == 'DELETE_FAILED':
            exit(1)


def print_events(events):
    """
    Pretty print events
    :param events: list
    :return:
    """
    for event in events:
        event_line = "%s %s\t%s\t%s\t%s" % (
            event['Timestamp'].strftime('%Y-%m-%d/%H:%M:%S'),
            event['ResourceStatus'].ljust(18),
            event['ResourceType'].ljust(25),
            event['LogicalResourceId'],
            event.get("ResourceStatusReason", "")
        )

        # if stdout is a tty use some pretty color
        if stdout.isatty():
            attr = []
            if event['ResourceStatus'][-8:] == 'COMPLETE':
                attr.append('32')
            elif event['ResourceStatus'][-6:] == 'FAILED':
                attr.append('31')
            event_line = '\x1b[%sm%s\x1b[0m' % (';'.join(attr), event_line)

        print(event_line)
