""" LocalStack class """

import logging
from os import path, curdir, mkdir, scandir

from clouds_aws.local_stack.parameters import Parameters
from clouds_aws.local_stack.template import Template, TYPE_YAML, TYPE_JSON

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

    def save(self, tpl_format=None):
        """
        Save stack to disk
        :param tpl_format: template format
        :return:
        """
        if not path.isdir(path.dirname(self.path)):
            mkdir(path.dirname(self.path))
        if not path.isdir(self.path):
            mkdir(self.path)

        save_as = None
        if tpl_format == "json":
            save_as = TYPE_JSON
        elif tpl_format == "yaml":
            save_as = TYPE_YAML

        self.template.save(save_as)
        self.parameters.save()

    def load(self):
        """
        Re-Loading stack from disk
        :return:
        """
        self.template.load()
        self.parameters.load()

    def update(self, template, parameters):
        """
        Update template and parameters
        :param template: template dict
        :param parameters: parameters dict
        :return:
        """
        self.template.template = template
        self.parameters.parameters = parameters


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
            stacks.append(item.name)

    return stacks
