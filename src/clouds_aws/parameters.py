""" Parameters class """
from os import path

import yaml

from .helpers import dump_yaml


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
        self.path = stack_path
        self.parameters = {}

    def load(self):
        """
        Load parameters from file
        :return:
        """
        with open(self._filename()) as param_fp:
            yaml.load(param_fp)

    def save(self):
        """
        Save parameters to file
        :return:
        """
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
