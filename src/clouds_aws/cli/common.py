""" Common CLI functions """
import logging

from clouds_aws.local_stack import LocalStack, LocalStackError

LOG = logging.getLogger(__name__)


def load_local_stack(name):
    """
    Return loaded local stack or bail out
    :param name: stack name
    :return:
    """
    local_stack = LocalStack(name)
    try:
        local_stack.load()
    except LocalStackError as err:
        LOG.error(err)
        exit(1)

    return local_stack
