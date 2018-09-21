""" AWS API client class """

import logging
from collections import OrderedDict

import boto3
from botocore.exceptions import ClientError

from clouds_aws.local_stack.helpers import dump_json

LOG = logging.getLogger(__name__)
CAPABILITIES = ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']


class CloudFormationError(Exception):
    """ Custom error class for CloudFormation"""
    pass


class CloudFormation:
    """ AWS API wrapper """

    def __init__(self, region, profile):
        """
        Initialize AWS CloudFormation client
        :param region: AWS region
        """
        self.region = region
        self.profile = profile
        self.client = self._get_client("cloudformation")

        self.remote_stacks = {}

    def __repr__(self):
        return "CloudFormation({}, {})".format(self.region, self.profile)

    def _get_client(self, service):
        """
        Return AWS client object for a service
        :param service:
        :return:
        """
        if self.profile:
            session = boto3.Session(profile_name=self.profile)
            return session.client(service, self.region)

        return boto3.client(service, self.region)

    def _get_resource(self, service):
        """
        Return AWS resource
        :param service:
        :return:
        """
        if self.profile:
            session = boto3.Session(profile_name=self.profile)
            return session.resource(service, self.region)

        return boto3.resource(service, self.region)

    def list_stacks(self):
        """
        Return all remote stacks
        :return:
        """
        paginator = self.client.get_paginator('describe_stacks')
        remote_stacks = {}

        for page in paginator.paginate():
            for stack in page["Stacks"]:
                remote_stacks[stack["StackName"]] = stack["StackStatus"]

        return remote_stacks

    def describe_stack_events(self, stack):
        """
        Return all stack events
        :param stack: stack name
        :return:
        """
        if stack not in self.list_stacks():
            raise CloudFormationError("No such stack: %s" % stack)

        paginator = self.client.get_paginator('describe_stack_events')
        events = []

        for page in paginator.paginate(StackName=stack):
            for raw_event in page["StackEvents"]:
                events.append(raw_event)

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
        stack = self._get_resource("cloudformation").Stack(name)
        stack.update(
            TemplateBody=template.as_string(),
            Parameters=parameters.as_list(),
            Capabilities=CAPABILITIES
        )

    def delete_stack(self, name):
        """
        Deletes stack in AWS
        :param name: stack name
        :return:
        """
        stack = self._get_resource("cloudformation").Stack(name)
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

    def create_change_set(self, stack, set_name, template, parameters, **kwargs):
        """
        Create change set in AWS
        :param stack: stack name
        :param set_name: Change set name
        :param template:
        :param parameters:
        :return:
        """
        set_type = "CREATE"
        stacks = self.list_stacks()
        if stack in stacks and stacks[stack] != "REVIEW_IN_PROGRESS":
            set_type = "UPDATE"

        description = kwargs.get("description")
        if description:
            response = self.client.create_change_set(
                StackName=stack,
                TemplateBody=template,
                Parameters=parameters,
                Capabilities=CAPABILITIES,
                ChangeSetName=set_name,
                ChangeSetType=set_type,
                Description=description
            )
        else:
            response = self.client.create_change_set(
                StackName=stack,
                TemplateBody=template,
                Parameters=parameters,
                Capabilities=CAPABILITIES,
                ChangeSetName=set_name,
                ChangeSetType=set_type
            )
        LOG.info("Created change set: %s", response["Id"])

    def list_change_sets(self, stack):
        """
        Retun a list of change sets
        :param stack:
        :return:
        """
        raw_change_sets = self.client.list_change_sets(StackName=stack)
        return raw_change_sets["Summaries"]

    def describe_change_set(self, stack, name):
        """
        Returns a change set description
        :param stack:
        :param name:
        :return:
        """
        return self.client.describe_change_set(
            StackName=stack,
            ChangeSetName=name
        )

    def delete_change_set(self, stack, name):
        """
        Delete a change set in AWS
        :param stack:
        :param name:
        :return:
        """
        self.client.delete_change_set(
            StackName=stack,
            ChangeSetName=name
        )

    def execute_change_set(self, stack, name):
        """
        Execute change set in AWS
        :param stack:
        :param name:
        :return:
        """
        self.client.execute_change_set(
            StackName=stack,
            ChangeSetName=name
        )

    def validate(self, tpl_body):
        """
        Validate template using the API
        :param tpl_body: template as string
        :return:
        """
        try:
            self.client.validate_template(TemplateBody=tpl_body)
        except ClientError as err:
            raise CloudFormationError(err)
