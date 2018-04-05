""" AWS API client class """

import logging
from collections import OrderedDict

import boto3

from clouds_aws.local_stack.helpers import dump_json

LOG = logging.getLogger(__name__)
CAPABILITIES = ['CAPABILITY_IAM']


class CloudFormationError(Exception):
    """ Custom error class for CloudFormation"""
    pass


class CloudFormation(object):
    """ AWS API wrapper """

    def __init__(self, region=None):
        """
        Initialize AWS CloudFormation client
        :param region: AWS region
        """
        self.region = region
        self.client = boto3.client("cloudformation", region)

        self.remote_stacks = {}

    def list_stacks(self):
        """
        Return all remote stacks
        :return:
        """
        remote_stacks = {}

        stacks = self.client.describe_stacks()
        for stack in stacks["Stacks"]:
            remote_stacks[stack["StackName"]] = stack["StackStatus"]

        # paginate if necessary
        while True:
            try:
                next_token = stacks["NextToken"]
                stacks = self.client.describe_stacks(NextToken=next_token)
                for stack in stacks["Stacks"]:
                    remote_stacks[stack["StackName"]] = stack["StackStatus"]
            except KeyError:
                break

        return remote_stacks

    def describe_stack_events(self, stack):
        """
        Return all stack events
        :param stack: stack name
        :return:
        """
        if stack not in self.list_stacks():
            raise CloudFormationError("No such stack: %s" % stack)

        events = []
        raw_events = self.client.describe_stack_events(StackName=stack)
        for raw_event in raw_events["StackEvents"]:
            events.append(raw_event)

        while True:
            try:
                next_token = raw_events["NextToken"]
                raw_events = self.client.describe_stack_events(StackName=stack,
                                                               NextToken=next_token)
                for raw_event in raw_events["StackEvents"]:
                    events.append(raw_event)
            except KeyError:
                break

        return reversed(events)

    def describe_stack(self, stack):
        """
        Return stack details
        :param stack: stack name
        :return:
        """
        if stack not in self.list_stacks():
            raise CloudFormationError("No such stack: %s" % stack)

        # query API
        stack_desc = self.client.describe_stacks(StackName=stack)['Stacks'][0]

        # Parameters is optional
        params = stack_desc.get('Parameters', [])

        # Outputs is optional
        outputs = stack_desc.get('Outputs', [])

        # at least resources is always present
        resources = self.client.list_stack_resources(StackName=stack)['StackResourceSummaries']

        # output json
        stack_data = {
            "Parameters": {},
            "Outputs": {},
            "Resources": {},
        }
        if params:
            for param in params:
                stack_data['Parameters'].update({param['ParameterKey']: param['ParameterValue']})

        if outputs:
            for output in outputs:
                stack_data['Outputs'].update({output['OutputKey']: output['OutputValue']})

        if resources:
            for resource in resources:
                stack_data['Resources'].update({resource['LogicalResourceId']: {
                    'ResourceType': resource['ResourceType'],
                    'PhysicalResourceId': resource['PhysicalResourceId']
                }})

        return stack_data

    def create_stack(self, name, template, parameters):
        """
        Create stack in AWS
        :param name: stack name
        :param template: template dict
        :param parameters: parameters dict
        :return:
        """
        self.client.create_stack(
            StackName=name,
            TemplateBody=template.as_string(),
            Parameters=parameters.as_list(),
            Capabilities=CAPABILITIES,
            OnFailure="DELETE"
        )

    def update_stack(self, name, template, parameters):
        """
        Update stack in AWS
        :param name: stack name
        :type template: Template
        :param template:
        :type parameters: Parameters
        :param parameters:
        :return:
        """
        stack = boto3.resource('cloudformation', self.region).Stack(name)
        stack.update(
            TemplateBody=template.as_string(),
            Parameters=parameters.as_list(),
            Capabilities=CAPABILITIES,
        )

    def delete_stack(self, name):
        """
        Deletes stack in AWS
        :param name: stack name
        :return:
        """
        stack = boto3.resource('cloudformation', self.region).Stack(name)
        stack.delete()

    def get_template(self, stack):
        """
        Return stack template
        :param stack: stack name
        :return:
        """
        # return as string
        tpl_body = self.client.get_template(StackName=stack)["TemplateBody"]

        # JSON is returned as OrderedDict by boto3 client
        if isinstance(tpl_body, OrderedDict):
            return dump_json(tpl_body)

        return tpl_body
