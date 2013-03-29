from billingstack import exceptions
from billingstack.openstack.common import log

import operator

LOG = log.getLogger(__name__)


class Criteria(object):
    """
    An object to hold Criteria
    """
    def __init__(self, field, op, value):
        self.field = field
        self.op = op
        self.value = value

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class BaseFilterer(object):
    """
    Object to help with Filtering.

    Typical use cases include turning a dict into useful storage backend query
    filters.
    """

    std_op = [
        (('eq', '==', '='), operator.eq),
        (('ne', '!='), operator.ne),
        (('ge', '>='), operator.ge),
        (('le', '<='), operator.le),
        (('gt', '>'), operator.gt),
        (('le', '<'), operator.lt)
    ]

    def __init__(self, criterion, **kw):
        #: Criterion to apply
        self.criterion = self.load_criterion(criterion)

    def get_op(self, op_key):
        """
        Get the operator.

        :param op_key: The operator key as string.
        """
        for op_keys, op in self.std_op:
            if op_key in op_keys:
                return op

    def load_criterion(self, criterion):
        """
        Transform a dict with key values to a filter compliant list of dicts.

        :param criterion: The criterion dict.
        """
        if not isinstance(criterion, dict):
            msg = 'Criterion needs to be a dict.'
            LOG.debug(msg)
            raise exceptions.InvalidObject(msg)

        data = {}
        for key, value in criterion.items():
            # NOTE: Criteria that doesn't have a OP defaults to eq and handle
            # dicts
            if isinstance(value, basestring):
                c = Criteria(key, 'eq', value)
            elif isinstance(value, dict):
                c = Criteria.from_dict(value)
            data[key] = c
        return data
