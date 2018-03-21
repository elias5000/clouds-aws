""" Template class """

import json
from os import path

from .helpers import dump_json, dump_yaml

TYPE_JSON = 0
TYPE_YAML = 1


class TemplateError(Exception):
    """ Custom Errors for Template class """
    pass


class Template(object):
    """ CloudFormation template"""

    def __init__(self, stack_path, template_type):
        """
        Initialize empty CloudFormation template of specific type
        :param stack_path: stack directory path
        :param template_type:
        """
        self.path = stack_path
        self.type = template_type
        self.template = ""

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

    def save(self, force=False):
        """
        Save template to file
        :param force: overwrite existing
        :return:
        """
        if path.exists(self._filename()) and not force:
            raise TemplateError("File exists. Apply force to overwrite.")

        if self.type == TYPE_JSON:
            self._save_json()

        elif self.type == TYPE_YAML:
            self._save_yaml()

        else:
            raise TemplateError("Invalid type value")

    def _filename(self, with_path=True):
        """
        Return file name (with path)
        :param with_path: include path
        :return:
        """
        if self.type == TYPE_YAML:
            extension = "yaml"
        elif self.type == TYPE_JSON:
            extension = "json"
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
        with open(self._filename()) as tpl_fp:
            self.template = json.load(tpl_fp)

    def _save_json(self):
        """
        Save template to JSON file
        :return:
        """
        with open(self._filename(), "w") as tpl_fp:
            tpl_fp.write(dump_json(self.template))

    def _load_yaml(self):
        """
        Load template from YAML file
        :return:
        """
        with open(self._filename()) as tpl_fp:
            self.template = json.load(tpl_fp)

    def _save_yaml(self):
        """
        Save template to YAML file
        :return:
        """
        with open(self._filename(), "w") as tpl_fp:
            tpl_fp.write(dump_yaml(self.template))
