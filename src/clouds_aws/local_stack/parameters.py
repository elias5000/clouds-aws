""" Parameters class """
import logging
from os import path, unlink

import yaml

from ..helpers import dump_yaml

LOG = logging.getLogger(__name__)


class ParameterError(Exception):
    """ Custom errors for Parameters class """
    pass


class Parameters(object):
    """ Parameters class """

    def __init__(self, stack_path):
        """
        Initialize empty parameters object
        :param stack_path: stack directory path
        """
        LOG.debug("Initializing new parameters in path %s", stack_path)
        self.path = stack_path
        self.parameters = {}

        self.load()

    def load(self):
        """
        Load parameters from file
        :return:
        """
        if not path.isfile(self._filename()):
            LOG.debug("Not loading empty parameters")
            return

        LOG.debug("Loading parameters from file %s", self._filename())
        with open(self._filename()) as param_fp:
            self.parameters = yaml.load(param_fp)

    def save(self):
        """
        Save parameters to file
        :return:
        """
        LOG.debug("Saving parameters to file %s", self._filename())
        if not self.parameters:
            if path.isfile(self._filename()):
                LOG.info("Deleting parameters file %s", self._filename())
                unlink(self._filename())
                return

            LOG.info("Skipping empty parameters")
            return

        with open(self._filename(), "w") as param_fp:
            param_fp.write(dump_yaml(self.parameters))

    def _filename(self, with_path=True):
        """
        Return file name (with path)
        :param with_path: include path
        :return:
        """
        if with_path:
            return path.join(self.path, "parameters.yaml")

        return "parameters.yaml"
