""" RemoteStack class """

import logging

from clouds_aws.local_stack import Template, Parameters
from clouds_aws.remote_stack.aws_client import CloudFormation, CloudFormationError
from clouds_aws.remote_stack.change_set import ChangeSet

LOG = logging.getLogger(__name__)


class RemoteStackError(Exception):
    """ Custom errors for RemoteStack class """
    pass


class RemoteStack:
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
        self.loaded = False

        self.change_sets = {}

    def __repr__(self):
        return "RemoteStack({}, {}, {})".format(self.name, self.cfn.region, self.cfn.profile)

    def load(self):
        """
        Load template/parameters from CloudFormation
        :return:
        """
        try:
            stack_data = self.cfn.describe_stack(self.name)
        except CloudFormationError as err:
            LOG.error(err)
            return

        self.parameters = stack_data["Parameters"]
        self.outputs = stack_data["Outputs"]
        self.resources = stack_data["Resources"]

        self.template = self.cfn.get_template(self.name)
        self._update_events()

        self.change_sets = self.list_change_sets()

        self.loaded = True

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

    def get_change_set(self, name):
        """
        Return change details
        :param name:
        :return:
        """
        change = ChangeSet(self, name)
        change.load()
        return change

    def list_change_sets(self):
        """
        Return dict of change sets
        :return:
        """
        change_sets = {}
        raw_change_sets = self.cfn.list_change_sets(self.name)
        for change_set in raw_change_sets:
            change_sets[change_set["ChangeSetName"]] = [
                change_set["ChangeSetName"],
                change_set.get("Description"),
                change_set["ExecutionStatus"]
            ]
        return change_sets

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
