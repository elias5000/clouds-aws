""" Template class """

import json
import logging
from os import path

import yaml

from clouds_aws.helpers import dump_json, dump_yaml

LOG = logging.getLogger(__name__)

TYPE_JSON = 0
TYPE_YAML = 1
TYPE_DEFAULT = TYPE_YAML


class TemplateError(Exception):
    """ Custom Errors for Template class """
    pass


class Template(object):
    """ CloudFormation template"""

    def __init__(self, stack_path):
        """
        Initialize empty CloudFormation template of specific type
        :param stack_path: stack directory path
        :param template_type:
        """
        LOG.debug("Initializing new template in path %s", stack_path)
        self.path = stack_path

        loaded = False
        for tpl_type in (TYPE_YAML, TYPE_JSON):
            self.type = tpl_type
            LOG.debug("Testing file %s", self._filename())
            if path.isfile(self._filename()):
                self.load()
                loaded = True
                break

        if not loaded:
            self.type = TYPE_DEFAULT
            self.template = {}

    def load(self):
        """
        Load template from file
        :return:
        """
        if self.type == TYPE_JSON:
            self._load_json()

        elif self.type == TYPE_YAML:
            self._load_yaml()

        else:
            raise TemplateError("Invalid type value")

    def save(self):
        """
        Save template to file
        :return:
        """
        if self.type == TYPE_JSON:
            self._save_json()

        elif self.type == TYPE_YAML:
            self._save_yaml()

        else:
            raise TemplateError("Invalid type value")

    def exists(self):
        """
        Return true if file exists on disk
        :return:
        """
        return path.exists(self._filename())

    def _filename(self, with_path=True):
        """
        Return file name (with path)
        :param with_path: include path
        :return:
        """
        if self.type == TYPE_JSON:
            extension = "json"
        elif self.type == TYPE_YAML:
            extension = "yaml"
        else:
            raise TemplateError("Invalid type value")

        if with_path:
            return path.join(self.path, "template.%s" % extension)

        return "template.%s" % extension

    def _load_json(self):
        """
        Load template from JSON file
        :return:
        """
        LOG.debug("Loading template from file %s", self._filename())
        with open(self._filename()) as tpl_fp:
            self.template = json.load(tpl_fp)

    def _save_json(self):
        """
        Save template to JSON file
        :return:
        """
        LOG.debug("Saving template to file %s", self._filename())
        with open(self._filename(), "w") as tpl_fp:
            tpl_fp.write(dump_json(self.template))

    def _load_yaml(self):
        """
        Load template from YAML file
        :return:
        """
        LOG.debug("Loading template from file %s", self._filename())
        with open(self._filename()) as tpl_fp:
            self.template = yaml.load(tpl_fp)

    def _save_yaml(self):
        """
        Save template to YAML file
        :return:
        """
        LOG.debug("Saving template to file %s", self._filename())
        with open(self._filename(), "w") as tpl_fp:
            tpl_fp.write(dump_yaml(self.template))
