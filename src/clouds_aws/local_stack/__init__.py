""" LocalStack class """

import logging
from os import path, curdir, mkdir

from scandir import scandir

from clouds_aws.local_stack.parameters import Parameters
from clouds_aws.local_stack.template import Template, TemplateError, TYPE_YAML, TYPE_JSON

LOG = logging.getLogger(__name__)

STACKS_PREFIX = "stacks"


class LocalStackError(Exception):
    """ Custom errors for LocalStack """
    pass


class LocalStack:
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

    def __repr__(self):
        return "LocalStack({})".format(self.name)

    def save(self):
        """
        Save stack to disk
        :return:
        """
        if not path.isdir(path.dirname(self.path)):
            mkdir(path.dirname(self.path))
        if not path.isdir(self.path):
            mkdir(self.path)

        self.template.save()
        self.parameters.save()

    def load(self):
        """
        Re-Loading stack from disk
        :return:
        """
        if not path.isdir(self.path):
            raise LocalStackError("No such stack: %s" % self.name)

        try:
            self.template.load()
        except TemplateError as err:
            raise LocalStackError("Failed to load stack template: %s" % str(err))

        self.parameters.load()

    def update(self, new_template, new_parameters):
        """
        Update template and parameters
        :type new_template: str
        :param new_template: template string
        :type new_parameters: dict
        :param new_parameters: parameters dict
        :return:
        """
        self.template.from_string(new_template)
        self.parameters.parameters = new_parameters


def list_stacks():
    """
    Return list of local stacks
    :return:
    """
    stacks = []

    if not path.isdir(path.join(curdir, STACKS_PREFIX)):
        return stacks

    for item in scandir(path.join(curdir, STACKS_PREFIX)):
        if item.is_dir():
            stacks.append(item.name)

    return stacks
