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
from oslo.config import cfg


from sqlalchemy import Column, ForeignKey
from sqlalchemy import Unicode
from sqlalchemy.orm import exc, relationship
from sqlalchemy.ext.declarative import declarative_base

from billingstack.collector import states
from billingstack.collector.storage import Connection, StorageEngine
from billingstack.openstack.common import log as logging
from billingstack.sqlalchemy.types import JSON, UUID
from billingstack.sqlalchemy import api, model_base, session, utils


LOG = logging.getLogger(__name__)


BASE = declarative_base(cls=model_base.ModelBase)


cfg.CONF.register_group(cfg.OptGroup(
    name='collector:sqlalchemy',
    title='Config for collector sqlalchemy plugin'))

cfg.CONF.register_opts(session.SQLOPTS, group='collector:sqlalchemy')


class PGProvider(BASE, model_base.BaseMixin):
    """
    A Payment Gateway - The thing that processes a Payment Method

    This is registered either by the Admin or by the PaymentGateway plugin
    """
    __tablename__ = 'pg_provider'

    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    properties = Column(JSON)

    methods = relationship(
        'PGMethod',
        backref='provider',
        lazy='joined')

    def method_map(self):
        return self.attrs_map(['provider_methods'])


class PGMethod(BASE, model_base.BaseMixin):
    """
    This represents a PaymentGatewayProviders method with some information
    like name, type etc to describe what is in other settings known as a
    "CreditCard"

    Example:
        A Visa card: {"type": "creditcard", "visa"}
    """
    __tablename__ = 'pg_method'

    name = Column(Unicode(100), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    type = Column(Unicode(100), nullable=False)
    properties = Column(JSON)

    # NOTE: This is so a PGMethod can be "owned" by a Provider, meaning that
    # other Providers should not be able to use it.
    provider_id = Column(UUID, ForeignKey(
        'pg_provider.id',
        ondelete='CASCADE',
        onupdate='CASCADE'))

    @staticmethod
    def make_key(data):
        return '%(type)s:%(name)s' % data

    def key(self):
        return self.make_key(self)


class PGConfig(BASE, model_base.BaseMixin):
    """
    A Merchant's configuration of a PaymentGateway like api keys, url and more
    """
    __tablename__ = 'pg_config'

    name = Column(Unicode(100), nullable=False)
    title = Column(Unicode(100))

    properties = Column(JSON)

    # Link to the Merchant
    merchant_id = Column(UUID, nullable=False)

    provider = relationship('PGProvider',
                            backref='merchant_configurations')
    provider_id = Column(UUID, ForeignKey('pg_provider.id',
                                          onupdate='CASCADE'),
                         nullable=False)

    state = Column(Unicode(20), default=states.PENDING)


class PaymentMethod(BASE, model_base.BaseMixin):
    name = Column(Unicode(255), nullable=False)

    identifier = Column(Unicode(255), nullable=False)
    expires = Column(Unicode(255))

    properties = Column(JSON)

    customer_id = Column(UUID, nullable=False)

    provider_config = relationship('PGConfig', backref='payment_methods',
                                   lazy='joined')
    provider_config_id = Column(UUID, ForeignKey('pg_config.id',
                                onupdate='CASCADE'), nullable=False)

    state = Column(Unicode(20), default=states.PENDING)


class SQLAlchemyEngine(StorageEngine):
    __plugin_name__ = 'sqlalchemy'

    def get_connection(self):
        return Connection()


class Connection(Connection, api.HelpersMixin):
    def __init__(self):
        self.setup('collector:sqlalchemy')

    def base(self):
        return BASE

    # Payment Gateway Providers
    def pg_provider_register(self, ctxt, values):
        values = values.copy()
        methods = values.pop('methods', [])

        query = self.session.query(PGProvider)\
            .filter_by(name=values['name'])

        try:
            provider = query.one()
        except exc.NoResultFound:
            provider = PGProvider()

        provider.update(values)

        self._set_provider_methods(ctxt, provider, methods)

        self._save(provider)
        return self._dict(provider, extra=['methods'])

    def list_pg_providers(self, ctxt, **kw):
        rows = self._list(PGProvider, **kw)
        return [self._dict(r, extra=['methods']) for r in rows]

    def get_pg_provider(self, ctxt, id_, **kw):
        row = self._get(PGProvider, id_)
        return self._dict(row, extra=['methods'])

    def pg_provider_deregister(self, ctxt, id_):
        self._delete(PGProvider, id_)

    def _get_provider_methods(self, provider):
        """
        Used internally to form a "Map" of the Providers methods
        """
        methods = {}
        for m in provider.methods:
            methods[m.key()] = m
        return methods

    def _set_provider_methods(self, ctxt, provider, config_methods):
        """Helper method for setting the Methods for a Provider"""
        existing = self._get_provider_methods(provider)
        for method in config_methods:
            self._set_method(provider, method, existing)

    def _set_method(self, provider, method, existing):
        key = PGMethod.make_key(method)

        if key in existing:
            existing[key].update(method)
        else:
            row = PGMethod(**method)
            provider.methods.append(row)

    # Payment Gateway Configuration
    def create_pg_config(self, ctxt, values):
        row = PGConfig(**values)

        self._save(row)
        return dict(row)

    def list_pg_configs(self, ctxt, **kw):
        rows = self._list(PGConfig, **kw)
        return map(dict, rows)

    def get_pg_config(self, ctxt, id_, **kw):
        row = self._get(PGConfig, id_, **kw)
        return dict(row)

    def update_pg_config(self, ctxt, id_, values):
        row = self._update(PGConfig, id_, values)
        return dict(row)

    def delete_pg_config(self, ctxt, id_):
        self._delete(PGConfig, id_)

    # PaymentMethod
    def create_payment_method(self, ctxt, values):
        row = PaymentMethod(**values)

        self._save(row)
        return self._dict(row)

    def list_payment_methods(self, ctxt, criterion=None, **kw):
        query = self.session.query(PaymentMethod)

        # NOTE: Filter needs to be joined for merchant_id
        query = utils.filter_merchant_by_join(
            query, PGConfig, criterion)

        rows = self._list(
            cls=PaymentMethod,
            query=query,
            criterion=criterion,
            **kw)

        return [self._dict(row) for row in rows]

    def get_payment_method(self, ctxt, id_, **kw):
        row = self._get_id_or_name(PaymentMethod, id_)
        return self._dict(row)

    def update_payment_method(self, ctxt, id_, values):
        row = self._update(PaymentMethod, id_, values)
        return self._dict(row)

    def delete_payment_method(self, ctxt, id_):
        self._delete(PaymentMethod, id_)
