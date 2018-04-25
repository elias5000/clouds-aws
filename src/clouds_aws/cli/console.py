""" Command for console access """

import json
import logging
from urllib.parse import urlencode
from urllib.request import urlopen

import boto3

LOG = logging.getLogger(__name__)
FEDERATION_URL = "https://signin.aws.amazon.com/federation?Action=getSigninToken&%s"
SIGNIN_URL = "https://signin.aws.amazon.com/federation?Action=login&" \
             "Destination=https%%3A%%2F%%2Fconsole.aws.amazon.com&SigninToken=%s"


def add_parser(subparsers):
    """
    Add command subparser
    :param subparsers:
    :return:
    """
    parser = subparsers.add_parser('console', help='get web console login URL')
    parser.add_argument('--export', action="store_true", help="export credentials for CLI use")
    parser.set_defaults(func=cmd_delete)


def cmd_delete(args):
    """
    Return login URL for assumed role profile
    :param args:
    :return:
    """
    session = boto3.Session(profile_name=args.profile)
    creds = session.get_credentials()
    data = {
        "sessionId": creds.access_key,
        "sessionKey": creds.secret_key,
        "sessionToken": creds.token
    }

    if not data["sessionToken"]:
        LOG.error("Only federation tokens or assume role tokens may be used for federated login.")
        exit(1)

    if args.export:
        print("export AWS_ACCESS_KEY_ID={}".format(data["sessionId"]))
        print("export AWS_SECRET_ACCESS_KEY={}".format(data["sessionKey"]))
        print("export AWS_SESSION_TOKEN={}".format(data["sessionToken"]))
        return

    url_data = urlencode({"Session": json.dumps(data)})

    with urlopen(FEDERATION_URL % url_data) as res:
        token = json.loads(res.read().decode("utf-8"))["SigninToken"]
        print(SIGNIN_URL % token)
