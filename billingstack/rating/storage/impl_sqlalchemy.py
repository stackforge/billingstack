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
"""
A Usage plugin using sqlalchemy...
"""
from oslo.config import cfg
from sqlalchemy import Column
from sqlalchemy import Unicode, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

from billingstack.openstack.common import log as logging
from billingstack.rating.storage import Connection, StorageEngine
from billingstack.sqlalchemy.types import UUID
from billingstack.sqlalchemy import api, model_base, session


# DB SCHEMA
BASE = declarative_base(cls=model_base.ModelBase)

LOG = logging.getLogger(__name__)


cfg.CONF.register_group(cfg.OptGroup(
    name='rating:sqlalchemy', title='Config for rating sqlalchemy plugin'))


cfg.CONF.register_opts(session.SQLOPTS, group='rating:sqlalchemy')


class Usage(BASE, model_base.BaseMixin):
    """
    A record of something that's used from for example a Metering system like
    Ceilometer
    """
    measure = Column(Unicode(255))
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)

    price = Column(Float)
    total = Column(Float)
    value = Column(Float)
    merchant_id = Column(UUID)
    product_id = Column(UUID, nullable=False)
    subscription_id = Column(UUID, nullable=False)


class SQLAlchemyEngine(StorageEngine):
    def get_connection(self):
        return Connection()


class Connection(Connection, api.HelpersMixin):
    def __init__(self):
        self.setup('rating:sqlalchemy')

    def base(self):
        return BASE

    def create_usage(self, ctxt, values):
        row = Usage(**values)
        self._save(row)
        return dict(row)

    def list_usages(self, ctxt, **kw):
        return self._list(Usage, **kw)

    def get_usage(self, ctxt, id_):
        return self._get(Usage, id_)

    def update_usage(self, ctxt, id_, values):
        return self._update(Usage, id_, values)

    def delete_usage(self, ctxt, id_):
        self._delete(Usage, id_)
