""" LocalStack class """

import logging
from os import path, curdir, mkdir, scandir

from clouds_aws.local_stack.parameters import Parameters
from clouds_aws.local_stack.template import Template

LOG = logging.getLogger(__name__)

STACKS_PREFIX = "stacks"


class LocalStack(object):
    """ File representation of CloudFormation stack """

    def __init__(self, name):
        """
        Initialize empty Stack object
        :param name: stack name
        """
        self.name = name
        self.path = path.join(curdir, STACKS_PREFIX, name)
        LOG.debug("Initializing new stack in %s", self.path)

        self.template = Template(self.path)
        self.parameters = Parameters(self.path)

    def save(self):
        """
        Save stack to disk
        :return:
        """
        if not path.isdir(self.path):
            mkdir(self.path)

        self.template.save()
        self.parameters.save()

    def load(self):
        """
        Re-Loading stack from disk
        :return:
        """
        self.template.load()
        self.parameters.load()


def list_stacks():
    """
    Return list of local stacks
    :return:
    """
    stacks = []

    if not path.isdir(path.join(curdir, STACKS_PREFIX)):
        return stacks

    for item in scandir(path.join(curdir, STACKS_PREFIX)):
        if path.isdir(item):
            stacks.append(item)

    return stacks
