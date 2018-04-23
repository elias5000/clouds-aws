""" Clouds-aws main module """

import argparse
import logging

from botocore.exceptions import ClientError

from .cli import add_parsers

LOG = logging.getLogger('clouds-aws')


def main():
    """
    Main entry point
    :return:
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser.add_argument('-d', '--debug', action='store_true', help='loglevel: debug')
    parser.add_argument('-f', '--force', action='store_true',
                        help='force action (use as global flag deprecated)')
    parser.add_argument('-r', '--region', help='specify region (default: use environment)',
                        nargs='?', default=None)
    parser.add_argument('-p', '--profile', help='use AWS config profile (default: use environment)',
                        nargs='?', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', help='loglevel: info')

    # add command parser
    add_parsers(subparsers)

    args = parser.parse_args()

    # set log level
    if args.verbose:
        LOG.setLevel(logging.INFO)
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        LOG.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

    try:
        args.func(args)
    except ClientError as err:
        LOG.error(err)
        exit(1)
