""" Function for local template handling """

import json
import re
import sys
from os import path, mkdir

import yaml


def load_template(stack, raw=False):
    """load template json from disk and return as dictionary"""
    tpl_path = path.join('stacks', stack, 'template.json')
    with open(tpl_path, encoding='utf-8') as file:
        if raw:
            return file.read()
        else:
            try:
                return json.load(file)
            except ValueError as exception:
                print("Failed parsing template file %s %s" %
                      (tpl_path, exception))
                sys.exit(1)


def save_template(stack, tpl_body):
    """saves template body to disk"""
    stack_dir = path.join('stacks', stack)
    tpl_path = path.join(stack_dir, 'template.json')

    # ensure paths are present
    if not path.exists('stacks'):
        mkdir('stacks')
    if not path.exists(stack_dir):
        mkdir(stack_dir)

    with open(tpl_path, mode='w', encoding='utf-8') as file:
        file.write(normalize_tpl(tpl_body))


def load_parameters(stack):
    """load parameters from yaml file and return as dictionary"""
    params = []
    param_path = path.join('stacks', stack, 'parameters.yaml')

    if not path.exists(param_path):
        return params

    with open(param_path, encoding='utf-8') as file:
        params_raw = yaml.load(file.read())

        # build parameter dict
        for param in params_raw.keys():
            params.append({
                'ParameterKey': param,
                'ParameterValue': params_raw[param]
            })
    return params


def save_parameters(stack, params):
    """saves parameters to disk"""
    # decode parameter dict
    params_dict = {}
    for param in params:
        params_dict[param['ParameterKey']] = param['ParameterValue']

    stack_dir = path.join('stacks', stack)
    param_path = path.join(stack_dir, 'parameters.yaml')

    # ensure paths are present
    if not path.exists('stacks'):
        mkdir('stacks')
    if not path.exists(stack_dir):
        mkdir(stack_dir)

    with open(param_path, mode='w', encoding='utf-8') as file:
        file.write(yaml.dump(params_dict, default_flow_style=False, explicit_start=True))


def normalize_tpl(tpl_body):
    """takes template body object and returns formatted JSON string."""
    jstr = json.dumps(tpl_body, indent=2, sort_keys=True)

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
