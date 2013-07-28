# -*- encoding: utf-8 -*-
#
# Author: Endre Karlson <endre.karlson@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pecan.rest

from wsme.types import Base, Enum, UserType, text, Unset, wsproperty

from oslo.config import cfg

from billingstack.openstack.common import log


LOG = log.getLogger(__name__)


cfg.CONF.register_opts([
    cfg.StrOpt('cors_allowed_origin', default='*', help='Allowed CORS Origin'),
    cfg.IntOpt('cors_max_age', default=3600)])


CORS_ALLOW_HEADERS = [
    'origin',
    'authorization',
    'accept',
    'content-type',
    'x-requested-with'
]


class RestController(pecan.rest.RestController):
    def _handle_patch(self, method, remainder):
        return self._handle_post(method, remainder)


class Property(UserType):
    """
    A Property that just passes the value around...
    """
    def tonativetype(self, value):
        return value

    def fromnativetype(self, value):
        return value


property_type = Property()


def _query_to_criterion(query, storage_func=None, **kw):
    """
    Iterate over the query checking against the valid signatures (later).

    :param query: A list of queries.
    :param storage_func: The name of the storage function to very against.
    """
    translation = {
        'customer': 'customer_id'
    }

    criterion = {}
    for q in query:
        key = translation.get(q.field, q.field)
        criterion[key] = q.as_dict()

    criterion.update(kw)

    return criterion


operation_kind = Enum(str, 'lt', 'le', 'eq', 'ne', 'ge', 'gt')


class Query(Base):
    """
    Query filter.
    """

    _op = None  # provide a default

    def get_op(self):
        return self._op or 'eq'

    def set_op(self, value):
        self._op = value

    field = text
    "The name of the field to test"

    #op = wsme.wsattr(operation_kind, default='eq')
    # this ^ doesn't seem to work.
    op = wsproperty(operation_kind, get_op, set_op)
    "The comparison operator. Defaults to 'eq'."

    value = text
    "The value to compare against the stored data"

    def __repr__(self):
        # for LOG calls
        return '<Query %r %s %r>' % (self.field, self.op, self.value)

    @classmethod
    def sample(cls):
        return cls(field='resource_id',
                   op='eq',
                   value='bd9431c1-8d69-4ad3-803a-8d4a6b89fd36',
                   )

    def as_dict(self):
        return {
            'op': self.op,
            'field': self.field,
            'value': self.value
        }


class ModelBase(Base):
    def as_dict(self):
        """
        Return this model as a dict
        """
        data = {}

        for attr in self._wsme_attributes:
            value = attr.__get__(self, self.__class__)
            if value is not Unset:
                if isinstance(value, Base) and hasattr(value, "as_dict"):
                    value = value.as_dict()
                data[attr.name] = value
        return data

    def to_db(self):
        """
        Returns this Model object as it's DB form

        Example
            'currency' vs 'currency_name'
        """
        return self.as_dict()

    @classmethod
    def from_db(cls, values):
        """
        Return a class of this object from values in the from_db
        """
        return cls(**values)
