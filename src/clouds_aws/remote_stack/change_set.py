""" Change set class """
import logging

LOG = logging.getLogger(__name__)
FIELDMAP = {
    "Resource": {
        "type": "string",
        "key": "LogicalResourceId",
    },
    "Type": {
        "type": "string",
        "key": "ResourceType",
    },
    "PhysicalId": {
        "type": "string",
        "key": "PhysicalResourceId",
    },
    "Action": {
        "type": "string",
        "key": "Action",
    },
    "Scope": {
        "type": "list",
        "key": "Scope",
    },
    "Replacement": {
        "type": "string",
        "key": "Replacement"
    }
}


class ChangeSet:
    """ CloudFormation stack change set """

    def __init__(self, stack, name):
        """
        Initialize change set
        :param stack: stack object
        :param name:
        """
        self.stack = stack
        self.name = name

        self.change = {}

    def __repr__(self):
        return "ChangeSet({}, {})".format(self.stack, self.name)

    def load(self):
        """
        Load change details
        :return:
        """
        self.change = self.stack.cfn.describe_change_set(self.stack.name, self.name)

    def create(self, template, parameters, description):
        """
        Create change set in AWS
        :param template:
        :param parameters:
        :param description:
        :return:
        """
        self.stack.cfn.create_change_set(
            self.stack.name,
            self.name,
            template.as_string(),
            parameters.as_list(),
            description=description
        )

    def changes(self):
        """
        Return list of change lines
        :return:
        """
        lines = []

        for change in self.change["Changes"]:
            line = {}
            for header, properties in FIELDMAP.items():
                if change["Type"] == "Resource":
                    if properties["type"] == "string":
                        line[header] = change["ResourceChange"].get(properties["key"])
                    elif properties["type"] == "list":
                        line[header] = ", ".join(change["ResourceChange"].get(properties["key"]))
                else:
                    LOG.warning("Encountered unknown change type.")
                    continue
            lines.append(line)

        return lines

    def execute(self):
        """
        Execute a change set
        :return:
        """
        self.stack.cfn.execute_change_set(self.stack.name, self.name)

    def delete(self):
        """
        Delete change set
        :return:
        """
        self.stack.cfn.delete_change_set(self.stack.name, self.name)
