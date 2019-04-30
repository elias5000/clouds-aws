""" Common helper functions """

import json
import re

import yaml


def dump_json(template):
    """
    Returns template as normalized JSON string
    :param template: json string
    """
    jstr = json.dumps(template, indent=2, sort_keys=True)

    # Common function
    jstr = re.sub(r'{\s*("Fn::GetAtt")\s*:\s*\[\s*("\S+")\s*,\s*("\S+")\s*\]\s*}',
                  r'{ \1: [ \2, \3 ] }', jstr)
    jstr = re.sub(r'{\s*("Fn::Select")\s*:\s*\[\s*("\d+")\s*,\s*({[^}]+})\s*]\s*}',
                  r'{ \1: [ \2, \3 ] }', jstr)
    jstr = re.sub(r'{\s*("Fn::GetAZs")\s*:\s*("\S*")\s*}', r'{ \1: \2 }', jstr)

    # References
    jstr = re.sub(r'{\s*("Ref")\s*:\s*("\S+")\s*}', r'{ \1: \2 }', jstr)

    # Key/Value pairs
    jstr = re.sub(r'{\s*("Name"):\s*("\S+"),\s*("Value"):\s*("\S*")\s*}',
                  r'{ \1: \2, \3: \4 }', jstr)
    jstr = re.sub(r'{\s*("Key"):\s*("\S+"),\s*("Value"):\s*("[\S ]*")\s*}',
                  r'{ \1: \2, \3: \4 }', jstr)
    jstr = re.sub(r'{\s*("Key"):\s*("\S+"),\s*("Value"):\s*({[^}]*})\s*}',
                  r'{ \1: \2, \3: \4 }', jstr)
    jstr = re.sub(r'{\s*("Field"):\s*("\S+"),\s*("Values"):\s*\[\s*(\S+)\s*\]\s*}',
                  r'{ \1: \2, \3: [ \4 ] }', jstr)

    jstr = re.sub(r'\[\n\r?\s*([^\n]*)\n\r?\s*\](,?)', r'[ \1 ]\2', jstr)
    jstr = re.sub(r'\s+$', r'', jstr, flags=re.MULTILINE)
    jstr = re.sub(r'([^\n]*)\n\s*("\\n",?)', r'\1\2', jstr, flags=re.MULTILINE)
    return jstr


def dump_yaml(template):
    """
    Return template as normalized YAML string
    :param template:
    :return:
    """
    return yaml.dump(template, default_flow_style=False, explicit_start=True)


def _general_constructor(loader, tag_suffix, node):
    # pylint: disable=unused-argument
    """
    Constructor for short function syntax
    :param loader:
    :param tag_suffix:
    :param node:
    :return:
    """
    return node.value


def load_yaml(data):
    """
    Safely load YAML into dictionary
    :param data:
    :return:
    """
    yaml.add_multi_constructor(u'!', _general_constructor)
    return yaml.load(data, Loader=yaml.FullLoader)
