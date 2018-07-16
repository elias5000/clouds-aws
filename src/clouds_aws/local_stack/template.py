""" Template class """

import json

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import logging
from os import path, unlink

import yaml

from clouds_aws.local_stack.helpers import load_yaml

LOG = logging.getLogger(__name__)

TYPE_JSON = 1
TYPE_YAML = 2
TYPE_DEFAULT = TYPE_JSON


class TemplateError(Exception):
    """ Custom Errors for Template class """
    pass


class Template:
    """ CloudFormation template"""

    def __init__(self, stack_path):
        """
        Initialize empty CloudFormation template of specific type
        :param stack_path: stack directory path
        """
        LOG.debug("Initializing new template in path %s", stack_path)
        self.path = stack_path

        loaded = False
        for tpl_type in (TYPE_YAML, TYPE_JSON):
            self.tpl_format = tpl_type
            LOG.debug("Testing file %s", self._filename())
            if path.isfile(self._filename()):
                self.load()
                loaded = True
                break

        if not loaded:
            self.tpl_format = TYPE_DEFAULT
            self._template = ""

    def __repr__(self):
        return "Template({})".format(self.path)

    def __str__(self):
        return self._template

    def load(self):
        """
        Load template from file
        :return:
        """
        with open(self._filename()) as tpl_file:
            self._template = tpl_file.read()

    def save(self):
        """
        Save template to file
        :return:
        """
        self.unlink()
        LOG.debug("Writing file %s", self._filename())
        with open(self._filename(), "w") as tpl_file:
            tpl_file.write(self._template)

    def from_string(self, template):
        """
        Update template from string
        :type template: str
        :param template: template string
        :return:
        """
        self._template = template

        try:
            json.loads(template)
            self.tpl_format = TYPE_JSON
            return
        except JSONDecodeError:
            pass

        try:
            load_yaml(template)
            self.tpl_format = TYPE_YAML
            return
        except yaml.YAMLError:
            pass

        raise TemplateError("Unable to determine template format")

    def as_string(self):
        """
        Return template as string
        :return:
        """
        return str(self)

    def as_dict(self):
        """
        Return template as dictionary
        :return:
        """
        if self.tpl_format == TYPE_JSON:
            return json.loads(self._template)

        if self.tpl_format == TYPE_YAML:
            return load_yaml(self._template)

        raise TemplateError("Invalid template format value")

    def exists(self):
        """
        Return true if file exists on disk
        :return:
        """
        return path.exists(self._filename())

    def unlink(self):
        """
        Cleanup template files
        :return:
        """
        for ext in ["json", "yaml"]:
            try:
                unlink(self._filename(extension=ext))
            except FileNotFoundError:
                pass

    def _filename(self, with_path=True, extension=None):
        """
        Return file name (with path)
        :param with_path: include path
        :return:
        """
        if extension:
            pass
        elif self.tpl_format == TYPE_JSON:
            extension = "json"
        elif self.tpl_format == TYPE_YAML:
            extension = "yaml"
        else:
            raise TemplateError("Invalid type value")

        if with_path:
            return path.join(self.path, "template.%s" % extension)

        return "template.%s" % extension
