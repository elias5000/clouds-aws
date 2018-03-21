""" RemoteStack class """

import logging

from .aws_client import CloudFormation, CloudFormationError

LOG = logging.getLogger(__name__)


class RemoteStack(object):
    """ Remote CloudFormation stack in AWS """

    def __init__(self, name, region=None):
        """
        Initialize remote stack
        """
        self.name = name
        self.cfn = CloudFormation(region)

        self.eventsNextToken = None

        self.template = {}
        self.parameters = {}

        self.outputs = {}
        self.resources = {}

    def load(self):
        """
        Load template/parameters from CloudFormation
        :return:
        """
        stack_data = self.cfn.describe_stack(self.name)
        self.parameters = stack_data["Parameters"]
        self.outputs = stack_data["Outputs"]
        self.resources = stack_data["Resources"]

        self.template = self.cfn.get_template(self.name)

    def update(self, template, parameters):
        """
        Update stack in CloudFormation
        :param template:
        :param parameters:
        :return:
        """
        raise RuntimeError("Not implemented")

    def poll_events(self, tail=None):
        """
        Return new events
        :param tail: Only return <tail> number of old events
        :return:
        """
        raise RuntimeError("Not implemented")

    def describe(self):
        """
        Return information about stack resources
        :return:
        """
        raise RuntimeError("Not implemented")
