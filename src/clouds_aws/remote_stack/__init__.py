""" RemoteStack class """

import logging

from clouds_aws.remote_stack.aws_client import CloudFormation, CloudFormationError

LOG = logging.getLogger(__name__)


class RemoteStackError(Exception):
    """ Custom errors for RemoteStack class """
    pass


class RemoteStack(object):
    """ Remote CloudFormation stack in AWS """

    def __init__(self, name, region, profile):
        """
        Initialize remote stack
        """
        self.name = name
        self.cfn = CloudFormation(region, profile)

        self.template = ""
        self.parameters = {}

        self.outputs = {}
        self.resources = {}

        self.events = []

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
        self._update_events()

    def create(self, template, parameters):
        """
        Create stack in CloudFormation
        :param template: template object
        :param parameters: parameters object
        :return:
        """
        self.cfn.create_stack(self.name, template, parameters)

    def update(self, template, parameters):
        """
        Update stack in CloudFormation
        :type template: Template
        :param template: template object
        :type parameters: Parameters
        :param parameters: parameters object
        :return:
        """
        self.cfn.update_stack(self.name, template, parameters)

    def delete(self):
        """
        Deletes stack from AWS
        :return:
        """
        self.cfn.delete_stack(self.name)

    def _update_events(self):
        """
        Update stack events from AWS API
        :return:
        """
        try:
            for event in self.cfn.describe_stack_events(self.name):
                if self.events and event["Timestamp"] <= self.events[-1]["Timestamp"]:
                    continue
                self.events.append(event)
        except CloudFormationError as err:
            raise RemoteStackError(err)

    def poll_events(self):
        """
        Return new events
        :return:
        """
        num_events = len(self.events)
        self._update_events()
        return self.events[num_events:]


def list_stacks(region, profile):
    """
    List remote stacks
    :param region:
    :return:
    """
    return CloudFormation(region, profile).list_stacks()
