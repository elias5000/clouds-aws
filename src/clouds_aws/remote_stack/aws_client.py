""" AWS API client class """

import logging
import json

import boto3

LOG = logging.getLogger(__name__)


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
            'Parameters': {},
            'Outputs': {},
            'Resources': {}
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

    def get_template(self, stack):
        """
        Return stack template
        :param stack: stack name
        :return:
        """
        template = self.client.get_template(StackName=stack)["TemplateBody"]
        return json.loads(json.dumps(template))
