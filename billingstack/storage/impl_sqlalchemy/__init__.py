# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
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
import time
from sqlalchemy.orm import exc
from billingstack.openstack.common import cfg
from billingstack.openstack.common import log as logging
from billingstack import exceptions
from billingstack import utils
from billingstack.storage import base
from billingstack.storage.impl_sqlalchemy import models
from billingstack.storage.impl_sqlalchemy.session import get_session, SQLOPTS

LOG = logging.getLogger(__name__)

cfg.CONF.register_group(cfg.OptGroup(
    name='storage:sqlalchemy', title="Configuration for SQLAlchemy Storage"
))

cfg.CONF.register_opts(SQLOPTS, group='storage:sqlalchemy')


class SQLAlchemyStorage(base.StorageEngine):
    __plugin_name__ = 'sqlalchemy'

    def get_connection(self):
        return Connection(self.name)


class Connection(base.Connection):
    """
    SQLAlchemy connection
    """
    def __init__(self, config_group):
        self.session = get_session(config_group)

    def setup_schema(self):
        """ Semi-Private Method to create the database schema """
        models.ModelBase.metadata.create_all(self.session.bind)

    def teardown_schema(self):
        """ Semi-Private Method to reset the database schema """
        models.ModelBase.metadata.drop_all(self.session.bind)

    def _save(self, obj):
        try:
            obj.save(self.session)
        except exceptions.Duplicate:
            raise
        return obj

    def _list(self, cls=None, query=None, criterion=None):
        """
        A generic list method

        :param cls: The model to try to delete
        :param criterion: Criterion to match objects with
        """
        if not cls and not query:
            raise ValueError("Need either cls or query")

        query = query or self.session.query(cls)

        if criterion:
            query = query.filter_by(**criterion)

        try:
            result = query.all()
        except exc.NoResultFound:
            LOG.debug('No results found querying for %s: %s' %
                      (cls, criterion))
            return []
        else:
            return result

    def _get(self, cls, id_):
        """
        Get an instance of a Model matching ID

        :param cls: The model to try to delete
        :param id_: The ID to delete
        """
        query = self.session.query(cls)
        obj = query.get(id_)
        if not obj:
            raise exceptions.NotFound(id_)
        else:
            return obj

    def _update(self, cls, id_, values):
        """
        Update an instance of a Model matching an ID with values

        :param cls: The model to try to delete
        :param id_: The ID to delete
        :param values: The values to update the model instance with
        """
        obj = self._get(cls, id_)
        obj.update(values)
        try:
            obj.save(self.session)
        except exceptions.Duplicate:
            raise
        return obj

    def _delete(self, cls, id_):
        """
        Delete an instance of a Model matching an ID

        :param cls: The model to try to delete

        :param id_: The ID to delete
        """
        obj = self._get(cls, id_)
        obj.delete(self.session)

    def _serialize(self, data):
        if isinstance(data, list):
            return [dict(o) for o in data]
        else:
            return dict(data)

    # Currency
    def currency_add(self, values):
        """
        Add a supported currency to the database
        """
        data = utils.get_currency(values['letter'])
        currency = models.Currency(**data)
        self._save(currency)
        return self._serialize(currency)

    def currency_list(self):
        rows = self._list(models.Currency)
        return self._serialize(rows)

    def currency_get(self, currency_id):
        currency = self._get(models.Currency, currency_id)
        return self._serialize(currency)

    def currency_update(self, currency_id, values):
        currency = self._update(models.Currency, currency_id, values)
        return self._serialize(currency)

    def currency_delete(self, currency_id):
        self._delete(models.Currency, currency_id)

    # Language
    def language_add(self, values):
        """
        Add a supported language to the database
        """
        data = utils.get_language(values['letter'])
        language = models.Language(**data)
        self._save(language)
        return self._serialize(language)

    def language_list(self):
        rows = self._list(models.Language)
        return self._serialize(rows)

    def language_get(self, id_):
        languages = self._get(models.Currency, id_)
        return self._serialize(languages)

    def language_update(self, id_, values):
        language = self._update(models.Language, id_, values)
        return self._serialize(language)

    def language_delete(self, id_):
        self._delete(models.Language, id_)

    # Merchant
    def merchant_add(self, values):
        merchant = models.Merchant(**values)
        self._save(merchant)
        return dict(self._save(models.Merchant(**values)))

    def merchant_list(self, **kw):
        rows = self._list(models.Merchant, **kw)
        return self._serialize(rows)

    def merchant_get(self, merchant_id):
        merchant = self._get(models.Merchant, merchant_id)
        return self._serialize(merchant)

    def merchant_update(self, merchant_id, values):
        merchant = self._update(models.Merchant, merchant_id, values)
        return self._serialize(merchant)

    def merchant_delete(self, merchant_id):
        self._delete(models.Merchant, merchant_id)

    # Customer
    def customer_add(self, merchant_id, values):
        merchant = self._get(models.Merchant, merchant_id)
        customer = models.Customer(**values)
        merchant.customers.append(customer)
        self._save(merchant)
        return self._serialize(customer)

    def customer_list(self, merchant_id, **kw):
        q = self.session.query(models.Customer)
        q = q.filter_by(merchant_id=merchant_id)
        rows = self._list(query=q, **kw)
        return self._serialize(rows)

    def customer_get(self, customer_id):
        customer = self._get(models.Customer, customer_id)
        return self._serialize(customer)

    def customer_update(self, customer_id, values):
        customer = self._update(models.Customer, customer_id, values)
        return self._serialize(customer)

    def customer_delete(self, customer_id):
        return self._delete(models.Customer, customer_id)

    # Users
    def user_list(self, merchant_id, **kw):
        q = self.session.query(models.User)
        q = q.filter_by(merchant_id=merchant_id)
        rows = self._list(query=q, **kw)
        return self._serialize(rows)
