""" AWS API client class """

import boto3


class CloudFormation(object):
    """ AWS API wrapper """

    def __init__(self, region):
        """
        Initialize AWS CloudFormation client
        :param region: AWS region
        """
        self.region = region
        self.client = boto3.client("cloudformation", region)
