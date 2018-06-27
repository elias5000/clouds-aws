""" Load command interpreter """

import clouds_aws.cli.change
import clouds_aws.cli.clone
import clouds_aws.cli.console
import clouds_aws.cli.delete
import clouds_aws.cli.describe
import clouds_aws.cli.dump
import clouds_aws.cli.events
import clouds_aws.cli.format
import clouds_aws.cli.list
import clouds_aws.cli.update
import clouds_aws.cli.validate


def add_parsers(subparsers):
    """
    Add command parser to argument parser
    :param subparsers: argparse subparsers
    :return:
    """
    clouds_aws.cli.change.add_parser(subparsers)
    clouds_aws.cli.clone.add_parser(subparsers)
    clouds_aws.cli.console.add_parser(subparsers)
    clouds_aws.cli.delete.add_parser(subparsers)
    clouds_aws.cli.describe.add_parser(subparsers)
    clouds_aws.cli.dump.add_parser(subparsers)
    clouds_aws.cli.events.add_parser(subparsers)
    clouds_aws.cli.format.add_parser(subparsers)
    clouds_aws.cli.list.add_parser(subparsers)
    clouds_aws.cli.update.add_parser(subparsers)
    clouds_aws.cli.validate.add_parser(subparsers)
