""" RemoteStack class """

import logging

from clouds_aws.remote_stack.aws_client import CloudFormation, CloudFormationError

LOG = logging.getLogger(__name__)


class RemoteStack(object):
    """ Remote CloudFormation stack in AWS """

    def __init__(self, name, region=None):
        """
        Initialize remote stack
        """
        self.name = name
        self.cfn = CloudFormation(region)

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
        :param template: template body
        :param parameters: parameters dict
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


def list_stacks(region):
    """
    List remote stacks
    :param region:
    :return:
    """
    return CloudFormation(region).list_stacks()
