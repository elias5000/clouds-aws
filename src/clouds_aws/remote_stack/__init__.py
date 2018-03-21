""" RemoteStack class """

import logging

LOG = logging.getLogger(__name__)


class RemoteStack(object):
    """ Remote CloudFormation stack in AWS """

    def __init__(self, name, region):
        """
        Initialize remote stack
        """
        self.name = name
        self.region = region

        self.eventsNextToken = None

        self.template = {}
        self.patameters = {}

    def load(self):
        """
        Load template/parameters from CloudFormation
        :return:
        """
        raise RuntimeError("Not implemented")

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
