import argparse
import json
import logging
import re
import sys
from codecs import open
from os import path, listdir, mkdir
from time import sleep

import boto3
import botocore.exceptions
import yaml

cfn_client = None
remote_stack_cache = None
region = None  # None = default to environment

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
logger = logging.getLogger('clouds-aws')


# aws functions
def get_cfn():
    """cloudformation client singleton"""
    global cfn_client
    global region

    if not cfn_client:
        cfn_client = boto3.client('cloudformation', region)
    return cfn_client


def local_stacks():
    """get local stack names and return as list."""
    stacks = []

    # no local stacks
    if not path.exists('stacks'):
        return stacks

    # local stacks must have at lest a template.json
    for item in listdir('stacks'):
        if path.isdir(path.join('stacks', item)) and path.isfile(path.join('stacks', item, 'template.json')):
            stacks.append(item)

    return stacks


def remote_stacks(refresh=False):
    """get remote stacks and return as dictionary."""
    global remote_stack_cache

    if remote_stack_cache is not None and refresh is False:
        return remote_stack_cache.copy()

    cfn = get_cfn()
    remote_stack_cache = {}

    # remote stacks
    stacks = cfn.describe_stacks()
    for stack in stacks['Stacks']:
        remote_stack_cache[stack['StackName']] = stack['StackStatus']

    # paginate if necessary
    while True:
        try:
            next_token = stacks['NextToken']
            stacks = cfn.describe_stacks(NextToken=next_token)
            for stack in stacks['Stacks']:
                remote_stack_cache[stack['StackName']] = stack['StackStatus']
        except KeyError:
            break

    return remote_stack_cache.copy()


def fetch_all_stack_events(stack):
    """gets all events for a stack and returns them as list."""
    cfn = get_cfn()
    raw_events = cfn.describe_stack_events(StackName=stack)
    all_events = raw_events['StackEvents']

    # paginate if necessary
    while True:
        try:
            next_token = raw_events['NextToken']
            raw_events = cfn.describe_stack_events(StackName=stack, NextToken=next_token)
            all_events = all_events + raw_events['StackEvents']
        except KeyError:
            break

    # return oldest first
    return all_events[::-1]


def stack_events(stack, last_event=None):
    """print events newer than last_event for a stack and returns timestamp."""
    raw_events = fetch_all_stack_events(stack)

    for event in raw_events:
        if last_event and last_event >= event['Timestamp']:
            continue
        try:
            status_reason = event['ResourceStatusReason']
        except KeyError:
            status_reason = ''

        event_line = "%s %s\t%s\t%s\t%s" % (
            event['Timestamp'].strftime('%Y-%m-%d/%H:%M:%S'),
            event['ResourceStatus'].ljust(18),
            event['ResourceType'].ljust(25),
            event['LogicalResourceId'],
            status_reason
        )

        # if stdout is a tty use some pretty color
        if sys.stdout.isatty():
            attr = []
            if event['ResourceStatus'][-8:] == 'COMPLETE':
                attr.append('32')
            elif event['ResourceStatus'][-6:] == 'FAILED':
                attr.append('31')
            event_line = '\x1b[%sm%s\x1b[0m' % (';'.join(attr), event_line)

        print(event_line)

    try:
        return raw_events[-1]['Timestamp']
    except KeyError:
        return None


def wait(stack, show_events=False, last_event=None):
    global region

    stack_obj = boto3.resource('cloudformation', region_name=region).Stack(stack)
    while True:
        try:
            stack_obj.reload()

            # display new events
            if show_events:
                last_event = stack_events(stack, last_event=last_event)

            # exit condition
            if stack_obj.stack_status[-8:] == 'COMPLETE' or stack_obj.stack_status == 'DELETE_FAILED':
                break

        except botocore.exceptions.ClientError:
            break

        # limit requests to API
        sleep(5)


# template handling
def load_template(stack, raw=False):
    """load template json from disk and return as dictionary"""
    tpl_path = path.join('stacks', stack, 'template.json')
    with open(tpl_path, encoding='utf-8') as fp:
        if raw:
            return fp.read()
        else:
            try:
                return json.load(fp)
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

    with open(tpl_path, mode='w', encoding='utf-8') as fp:
        fp.write(normalize_tpl(tpl_body))


def load_parameters(stack):
    """load parameters from yaml file and return as dictionary"""
    params = []
    param_path = path.join('stacks', stack, 'parameters.yaml')

    if not path.exists(param_path):
        return params

    with open(param_path, encoding='utf-8') as fp:
        params_raw = yaml.load(fp.read())

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

    with open(param_path, mode='w', encoding='utf-8') as fp:
        fp.write(yaml.dump(params_dict, default_flow_style=False, explicit_start=True))


def normalize_tpl(tpl_body):
    """takes template body object and returns formatted JSON string."""
    jstr = json.dumps(tpl_body, indent=2, sort_keys=True)
    jstr = re.sub(r'{\s*("Fn::GetAtt")\s*:\s*\[\s*("\S+")\s*,\s*("\S+")\s*\]\s*}', r'{ \1: [ \2, \3 ] }', jstr)
    jstr = re.sub(r'{\s*("Fn::Select")\s*:\s*\[\s*("\d+")\s*,\s*({[^}]+})\s*]\s*}', r'{ \1: [ \2, \3 ] }', jstr)
    jstr = re.sub(r'{\s*("Fn::GetAZs")\s*:\s*("\S*")\s*}', r'{ \1: \2 }', jstr)
    jstr = re.sub(r'{\s*("Ref")\s*:\s*("\S+")\s*}', r'{ \1: \2 }', jstr)
    jstr = re.sub(r'{\s*("Name"):\s*("\S+"),\s*("Value"):\s*("\S*")\s*}', r'{ \1: \2, \3: \4 }', jstr)
    jstr = re.sub(r'{\s*("Key"):\s*("\S+"),\s*("Value"):\s*("\S*")\s*}', r'{ \1: \2, \3: \4 }', jstr)
    jstr = re.sub(r'{\s*("Key"):\s*("\S+"),\s*("Value"):\s*({[^}]*})\s*}', r'{ \1: \2, \3: \4 }', jstr)
    jstr = re.sub(r'\[\n\r?\s*([^\n]*)\n\r?\s*\](,?)', r'[ \1 ]\2', jstr)
    jstr = re.sub(r'\s+$', r'', jstr, flags=re.MULTILINE)
    jstr = re.sub(r'([^\n]*)\n\s*("\\n",?)', r'\1\2', jstr, flags=re.MULTILINE)
    return jstr


# command functions
def clone(args):
    """clone local stack"""
    # source and destination paths
    src = args.stack
    dst = args.new_stack

    # require stack to exist locally
    if src not in local_stacks():
        logger.error("no such local stack: " + src)
        sys.exit(1)

    # overwrite of existing local stack requires force
    if args.force and path.exists(path.join('stacks', dst)):
        logger.warning('stack ' + dst + ' already exists, use --force to overwrite')
        sys.exit(1)

    save_template(dst, load_template(src))
    if path.exists(path.join('stacks', src, 'parameters.yaml')):
        save_parameters(dst, load_parameters(src))


def delete(args):
    """deletes a stack in AWS."""
    stack = args.stack

    # deleting stacks requires force
    if not args.force:
        logger.warning('this command might impact running environments and it needs the --force flag,' +
                       'hopefully you know what you are doing')
        sys.exit(1)

    if stack not in remote_stacks():
        logger.error("no such stack: " + stack)
        sys.exit(1)

    # last existing event - we only want to see newer events in case of --events
    last_event = fetch_all_stack_events(stack)[-1]['Timestamp']

    # action
    cfn = get_cfn()
    cfn.delete_stack(StackName=stack)

    # synchronous mode
    if args.wait or args.events:
        wait(stack, show_events=args.events, last_event=last_event)


def describe(args):
    """outputs parameters, outputs, and resources of a stack"""
    stack = args.stack

    if stack not in remote_stacks():
        logger.error('no such stack: ' + stack)
        sys.exit(1)

    # query API
    cfn = get_cfn()
    stack_desc = cfn.describe_stacks(StackName=stack)['Stacks'][0]

    # Parameters is optional
    try:
        params = stack_desc['Parameters']
    except KeyError:
        params = []

    # Outputs is optional
    try:
        outputs = stack_desc['Outputs']
    except KeyError:
        outputs = []

    # at least resources is always present
    resources = cfn.list_stack_resources(StackName=stack)['StackResourceSummaries']

    # output json
    if args.json:
        stack_data = {}
        if len(params):
            stack_data['Parameters'] = []
            for param in params:
                stack_data['Parameters'].append({param['ParameterKey']: param['ParameterValue']})
        if len(outputs):
            stack_data['Outputs'] = []
            for output in outputs:
                stack_data['Outputs'].append({output['OutputKey']: output['OutputValue']})
        if len(resources):
            stack_data['Resources'] = []
            for resource in resources:
                stack_data['Resources'].append({resource['LogicalResourceId']: {
                    'ResourceType': resource['ResourceType'], 'PhysicalResourceId': resource['PhysicalResourceId']
                }})
        print(normalize_tpl(stack_data))

    # output list
    else:
        if len(params):
            print('Parameters:')
            for param in sorted(params, key=lambda k: k['ParameterKey']):
                print("  %s:%s %s" % (
                    param['ParameterKey'],
                    ''.ljust(max([len(p['ParameterKey']) for p in params]) - len(param['ParameterKey'])),
                    param['ParameterValue']
                ))
        if len(outputs):
            print('Outputs:')
            for output in sorted(outputs, key=lambda k: k['OutputKey']):
                print("  %s:%s %s" % (
                    output['OutputKey'],
                    ''.ljust(max([len(o['OutputKey']) for o in outputs]) - len(output['OutputKey'])),
                    output['OutputValue']
                ))
        if len(resources):
            print('Resources:')
            for resource in resources:
                print("  %s:%s %s %s(%s)" % (
                    resource['LogicalResourceId'],
                    ''.ljust(
                        max([len(res['LogicalResourceId']) for res in resources]) - len(resource['LogicalResourceId'])
                    ),
                    resource['ResourceType'],
                    ''.ljust(max([len(res['ResourceType']) for res in resources]) - len(resource['ResourceType'])),
                    resource['PhysicalResourceId']
                ))


def dump(args):
    """dump stack in AWS to local disk"""
    stacks = args.stack

    # dump all stacks
    if args.all:
        stacks = remote_stacks().keys()

    # filter for existing stacks
    elif len(stacks):
        stacks = [stack for stack in stacks if stack in remote_stacks().keys()]

    # bail if no stacks to dump
    if not len(stacks):
        logger.warning('this command needs a list of remote stacks, or the --all flag to dump all stacks')
        sys.exit(1)

    # action
    retval = 0
    cfn = get_cfn()
    for stack in stacks:
        stack_dir = path.join('stacks', stack)

        # overwriting requires force
        if not args.force and path.exists(stack_dir):
            logger.warning('stack %s already exists locally, use --force to overwrite' % stack)
            retval = 2
            continue

        try:
            logger.info('Dumping stack %s' % stack)
            save_template(stack, cfn.get_template(StackName=stack)['TemplateBody'])
            try:
                params = cfn.describe_stacks(StackName=stack)['Stacks'][0]['Parameters']
                save_parameters(stack, params)
            except KeyError:
                pass
        except Exception as err:
            logger.error(str(err))

    sys.exit(retval)


def events(args):
    """prints all events for a stack"""
    stack = args.stack

    if stack not in remote_stacks().keys():
        logger.error("no such stack: " + stack)
        sys.exit(1)

    if args.follow:
        wait(stack, show_events=True)
    else:
        stack_events(stack)


def lists(args):
    """output a list of stacks"""
    stacks = remote_stacks()

    for stack in [k for k in local_stacks() if k not in stacks.keys()]:
        stacks[stack] = 'LOCAL-ONLY'

    print('stack list and stack status:')
    for stack in sorted(stacks.keys()):
        if args.local and stack not in local_stacks():
            continue
        if args.remote and stack not in remote_stacks().keys():
            continue
        print('%s %s' % (stack.rjust(max([len(key) for key in stacks.keys()])), stacks[stack]))


def reformat(args):
    """reformat stack"""
    stacks = args.stack

    # pipe mode
    if args.pipe:
        tpl_body = json.loads(''.join(sys.stdin))
        print(normalize_tpl(tpl_body))
        return

    # dump all stacks
    if args.all:
        stacks = local_stacks()

    # filter for existing stacks
    elif len(stacks):
        stacks = [stack for stack in stacks if stack in local_stacks()]

    # bail if no stacks to dump
    if not len(stacks):
        logger.warning('this command needs a list if local stacks, or the --all flag to dump all stacks')
        sys.exit(1)

    # action
    for stack in stacks:
        save_template(stack, load_template(stack))


def update(args):
    """update or create a stack in AWS."""
    stack = args.stack

    if stack not in local_stacks():
        logger.error('no such stack: ' + stack)
        return

    if stack not in remote_stacks().keys() and not args.create_missing:
        logger.warning('stack ' + stack + ' does not exist in AWS, add --create_missing to create a new stack')
        return

    # read template and parameters
    tpl_body = load_template(stack, True)
    params = load_parameters(stack)

    # action
    cfn = get_cfn()
    last_event = None

    try:
        if stack in remote_stacks().keys():
            logger.info('updating stack %s' % stack)
            last_event = fetch_all_stack_events(stack)[-1]['Timestamp']
            stack_id = cfn.update_stack(
                StackName=stack,
                TemplateBody=tpl_body,
                Parameters=params,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
            )['StackId']
            logger.info('created stack with physical id %s' % stack_id)
        else:
            logger.info('creating stack %s' % stack)
            stack_id = cfn.create_stack(
                StackName=stack,
                TemplateBody=tpl_body,
                Parameters=params,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
            )['StackId']
            logger.info('created stack with physical id %s' % stack_id)
    except botocore.exceptions.ClientError as err:
        logger.warning(str(err))
        return
    except botocore.exceptions.ParamValidationError as err:
        logger.warning(str(err))
        return

    # synchronous mode
    if args.wait or args.events:
        wait(stack, show_events=args.events, last_event=last_event)


def validate(args):
    """validate local stack(s)"""
    stacks = args.stack

    # validate all stacks
    if args.all:
        stacks = local_stacks()

    # filter for existing stacks
    elif len(stacks):
        stacks = [stack for stack in stacks if stack in local_stacks()]

    # bail if no stack to validate
    if not len(stacks):
        logger.warning('this command needs a list of local stacks, or the --all flag to validate all stacks')
        sys.exit(1)

    # action
    cfn = get_cfn()
    retval = 0
    for stack in stacks:
        tpl_body = load_template(stack, True)
        try:
            cfn.validate_template(TemplateBody=tpl_body)
            res = 'ok'
        except botocore.exceptions.ClientError as err:
            res = 'not ok: %s' % str(err)
            retval = 1
        print('%s:%s %s' % (stack, ''.rjust(max([len(s) for s in stacks]) - len(stack)), res))

    sys.exit(retval)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument('-d', '--debug', action='store_true', help='loglevel: debug')
    parser.add_argument('-f', '--force', action='store_true', help='force action (use as global flag deprecated)')
    parser.add_argument('-r', '--region', help='specify region (default: use environment)', nargs='?', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', help='loglevel: info')

    clone_parser = subparsers.add_parser('clone', help='clone a stack in the current directory')
    clone_parser.add_argument('stack', help='name of the stack to clone')
    clone_parser.add_argument('new_stack', help='name of the new stack')
    clone_parser.set_defaults(func=clone)

    delete_parser = subparsers.add_parser('delete', help='delete a stack in AWS')
    delete_parser.add_argument('-e', '--events', action='store_true',
                               help='display events while waiting for the deletion to complete (implies --wait)')
    delete_parser.add_argument('-f', '--force', action='store_true', help='force deletion')
    delete_parser.add_argument('-w', '--wait', action='store_true',
                               help='wait for deletion to finish (synchronous mode)')
    delete_parser.add_argument('stack', help='stack to delete')
    delete_parser.set_defaults(func=delete)

    describe_parser = subparsers.add_parser('describe',
                                            help='output parameters, outputs, and resources of a stack in AWS')
    describe_parser.add_argument('-j', '--json', action='store_true', help='output as JSON')
    describe_parser.add_argument('stack', help='stack to describe')
    describe_parser.set_defaults(func=describe)

    dump_parser = subparsers.add_parser('dump', help='dump a stack in AWS to current directory')
    dump_parser.add_argument('-a', '--all', action='store_true', help='dump all stacks')
    dump_parser.add_argument('-f', '--force', action='store_true', help='overwrite existing local stack')
    dump_parser.add_argument('stack', help='stack to dump', nargs='*')
    dump_parser.set_defaults(func=dump)

    events_parser = subparsers.add_parser('events', help='output all events of a stack')
    events_parser.add_argument('-f', '--follow', action='store_true',
                               help='follow events until stack transition complete')
    events_parser.add_argument('stack', help='stack name')
    events_parser.set_defaults(func=events)

    format_parser = subparsers.add_parser('format', help='normalize stack template(s) (for better diffs)')
    format_parser.add_argument('-a', '--all', action='store_true', help='reformat all stacks')
    format_parser.add_argument('-p', '--pipe', action='store_true',
                               help='pipe mode - read template from stdin and output to stdout')
    format_parser.add_argument('stack', help='stack to reformat', nargs='*')
    format_parser.set_defaults(func=reformat)

    list_parser = subparsers.add_parser('list', help='list available stacks')
    list_parser.add_argument('-l', '--local', action='store_true', help='list only local stacks')
    list_parser.add_argument('-r', '--remote', action='store_true', help='list only stacks in AWS')
    list_parser.set_defaults(func=lists)

    update_parser = subparsers.add_parser('update', help='update stack in AWS')
    update_parser.add_argument('-c', '--create_missing', action='store_true',
                               help='create stack in AWS if it does not exist')
    update_parser.add_argument('-e', '--events', action='store_true',
                               help='display events while waiting for the update to complete (implies --wait)')
    update_parser.add_argument('-w', '--wait', action='store_true', help='wait for update to finish (synchronous mode)')
    update_parser.add_argument('stack', help='stack to update')
    update_parser.set_defaults(func=update)

    validate_parser = subparsers.add_parser('validate', help='validate stack template')
    validate_parser.add_argument('-a', '--all', action='store_true', help='validate all stacks')
    validate_parser.add_argument('stack', help='stack to validate', nargs='*')
    validate_parser.set_defaults(func=validate)

    args = parser.parse_args()

    # set region globally
    global region
    region = args.region

    # set log level
    if args.verbose:
        logger.setLevel(logging.INFO)
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

    try:
        args.func(args)
    # no subcommand specified (fix for python >=3.3)
    except AttributeError:
        parser.print_help()
        sys.exit(1)
    # catch boto3 exceptions on a high level:
    except botocore.exceptions.NoRegionError as err:
        logger.error(str(err))
        sys.exit(1)
    except botocore.exceptions.ClientError as err:
        logger.error(str(err))
        sys.exit(1)
