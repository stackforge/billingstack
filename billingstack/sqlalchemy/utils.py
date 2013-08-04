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
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from billingstack.openstack.common import uuidutils


def get_prop_dict(obj):
    return dict([(p.key, p) for p in obj.__mapper__.iterate_properties])


def get_prop_names(obj, exclude=[]):
    props = get_prop_dict(obj)

    local, remote = [], []
    for k, p in props.items():
        if k not in exclude:
            if isinstance(p, ColumnProperty):
                local.append(k)
            if isinstance(p, RelationshipProperty):
                remote.append(k)
    return local, remote


def is_valid_id(id_):
    """
    Return true if this is a valid ID for the cls.id
    """
    if uuidutils.is_uuid_like(id_) or isinstance(id_, int):
        return True
    else:
        return False


def filter_merchant_by_join(query, cls, criterion, pop=True):
    if criterion and 'merchant_id' in criterion:
        if not hasattr(cls, 'merchant_id'):
            raise RuntimeError('No merchant_id attribute on %s' % cls)

        query = query.join(cls).filter(
            cls.merchant_id == criterion['merchant_id'])

        if pop:
            criterion.pop('merchant_id')

    return query
