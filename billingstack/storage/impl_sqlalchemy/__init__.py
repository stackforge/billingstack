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
from sqlalchemy import or_
from sqlalchemy.orm import exc
from billingstack.openstack.common import cfg
from billingstack.openstack.common import log as logging
from billingstack import exceptions
from billingstack import utils as common_utils
from billingstack.storage.impl_sqlalchemy import utils as db_utils
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
        models.BASE.metadata.create_all(self.session.bind)

    def teardown_schema(self):
        """ Semi-Private Method to reset the database schema """
        models.BASE.metadata.drop_all(self.session.bind)

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

    def _get(self, cls, identifier, by_name=False):
        """
        Get an instance of a Model matching ID

        :param cls: The model to try to get
        :param identifier: The ID to get
        :param by_name: Search by name as well as ID
        """
        filters = [cls.id == identifier]
        if by_name:
            filters.append(cls.name == identifier)

        query = self.session.query(cls)\
            .filter(or_(*filters))

        try:
            obj = query.one()
        except exc.NoResultFound:
            raise exceptions.NotFound(identifier)
        return obj

    def _get_id_or_name(self, *args, **kw):
        """
        Same as _get but with by_name on ass default
        """
        kw['by_name'] = True
        return self._get(*args, **kw)

    def _update(self, cls, id_, values):
        """
        Update an instance of a Model matching an ID with values

        :param cls: The model to try to update
        :param id_: The ID to update
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

    def _get_row(self, obj, cls=None, **kw):
        """
        Used to either check that passed 'obj' is a ModelBase inheriting object
        and just return it

        :param obj: ID or instance / ref of the object
        :param cls: The class to run self._get on if obj is not a ref
        """
        if cls and obj:
            return self._get(cls, obj)
        elif isinstance(obj, models.ModelBase):
            return obj
        else:
            msg = 'Missing obj and/or obj and cls...'
            raise exceptions.BadRequest(msg)

    def _make_rel_row(self, row, rel_attr, values):
        """
        Get the class of the relation attribute in 'rel_attr' and make a
        row from values with it.

        :param row: A instance of ModelBase
        :param rel_attr: The relation attribute
        :param values: The values to create the new row from
        """
        cls = row.__mapper__.get_property(rel_attr).mapper.class_
        return cls(**values)

    def _dict(self, row, extra=[]):
        data = dict(row)
        for key in extra:
            if isinstance(row[key], list):
                data[key] = map(dict, row[key])
            else:
                data[key] = dict(row[key])
        return data

    def _kv_rows(self, rows, key='name'):
        """
        Return a Key, Value dict where the "key" will be the key and the row as value
        """
        data = {}
        for row in rows:
            if callable(key):
                data_key = key(row)
            else:
                data_key = row[key]
            data[data_key] = row
        return data

    def set_properties(self, obj, properties, cls=None, rel_attr='properties', purge=False):
        """
        Set's a dict with key values on a relation on the row

        :param obj: Either a row object or a id to use in connection with cls
        :param properties: Key and Value dict with props to set. 1 row item.
        :param cls: The class to use if obj isn't a row to query.
        :param rel_attr: The relation attribute name to get the class to use
        :param purge: Purge entries that doesn't exist in existing but in DB
        """
        row = self._get_row(obj, cls=cls)

        existing = self._kv_rows(row[rel_attr])

        for key, value in properties.items():
            values = {'name': key, 'value': value}

            if key not in existing:
                rel_row = self._make_rel_row(row, rel_attr, values)
                row[rel_attr].append(rel_row)
            else:
                existing[key].update(values)

        if purge:
            for key in existing:
                if not key in properties:
                    row[rel_attr].remove(existing[key])

    # Currency
    def currency_add(self, values):
        """
        Add a supported currency to the database
        """
        data = common_utils.get_currency(values['letter'])
        row = models.Currency(**data)
        self._save(row)
        return dict(row)

    def currency_list(self):
        rows = self._list(models.Currency)
        return map(dict, rows)

    def currency_get(self, currency_id):
        row = self._get(models.Currency, currency_id)
        return dict(row)

    def currency_update(self, currency_id, values):
        row = self._update(models.Currency, currency_id, values)
        return dict(row)

    def currency_delete(self, currency_id):
        self._delete(models.Currency, currency_id)

    # Language
    def language_add(self, values):
        """
        Add a supported language to the database
        """
        data = common_utils.get_language(values['letter'])
        row = models.Language(**data)
        self._save(row)
        return dict(row)

    def language_list(self):
        rows = self._list(models.Language)
        return map(dict, rows)

    def language_get(self, id_):
        row = self._get(models.Language, id_)
        return dict(row)

    def language_update(self, id_, values):
        row = self._update(models.Language, id_, values)
        return dict(row)

    def language_delete(self, id_):
        self._delete(models.Language, id_)

    # ContactInfo
    def contact_info_add(self, obj, values, cls=None,
                         rel_attr='contact_info'):
        """
        :param entity: The object to add the contact_info to
        :param values: The values to add
        """
        row = self._get_row(obj, cls=cls)

        rel_row = self._make_rel_row(obj, rel_attr, values)

        local, remote = db_utils.get_prop_names(row)

        if rel_attr in remote:
            if isinstance(row[rel_attr], list):
                row[rel_attr].append(rel_row)
            else:
                row[rel_attr] = rel_row
        else:
            msg = 'Attempted to set non-relation %s' % rel_attr
            raise exceptions.BadRequest(msg)

        if cls:
            self._save(rel_row)
            return dict(rel_row)
        else:
            return rel_row

    def contact_info_get(self, info_id):
        self._get(models.ContactInfo, info_id)

    def contact_info_update(self, info_id, values):
        return self._update(models.ContactInfo, info_id, values)

    def contact_info_delete(self, info_id):
        self._delete(models.ContactInfo, info_id)

    # Payment Gateway Providers
    def pg_provider_register(self, values, methods=[]):
        """
        Register a Provider and it's Methods
        """
        query = self.session.query(models.PGProvider)\
            .filter_by(name=values['name'])

        try:
            provider = query.one()
        except exc.NoResultFound:
            provider = models.PGProvider()

        provider.update(values)

        self._set_provider_methods(provider, methods)

        self._save(provider)
        return self._dict(provider, extra=['methods'])

    def pg_provider_list(self, **kw):
        """
        List available PG Providers
        """
        q = self.session.query(models.PGProvider)

        rows = self._list(query=q, **kw)

        return [self._dict(r, extra=['methods']) for r in rows]

    def pg_provider_get(self, pgp_id):
        row = self._get(models.PGProvider, pgp_id)
        return self._dict(row, extra=['methods'])

    def pg_provider_deregister(self, pgp_id):
        self._delete(models.PGProvider, pgp_id)

    def _get_provider_methods(self, provider):
        """
        Used internally to form a "Map" of the Providers methods
        """
        methods = {}
        for m in provider.methods:
            m_key = m.key()
            key = '%s:%s' % (m.owner_id, m_key) if m.owner_id else m_key
            methods[key] = m
        return methods

    def _set_provider_methods(self, provider, config_methods):
        """
        Helper method for setting the Methods for a Provider
        """
        rows = self.pg_method_list(criterion={"owner_id": None})
        system_methods = self._kv_rows(rows, key=models.PGMethod.make_key)

        existing = self._get_provider_methods(provider)

        for method in config_methods:
            self._set_method(provider, method, existing, system_methods)
        self._save(provider)

    def _set_method(self, provider, method, existing, all_methods):
        method_key = models.PGMethod.make_key(method)
        key = '%s:%s' % (provider.id, method_key)

        if method.pop('owned', False):
            if method_key in existing:
                provider.methods.remove(existing[method_key])

            if key in existing:
                existing[key].update(method)
            else:
                row = models.PGMethod(**method)
                provider.methods.append(row)
                provider.provider_methods.append(row)
        else:
            if key in existing:
                provider.methods.remove(existing[key])

            try:
                all_methods[method_key].providers.append(provider)
            except KeyError:
                msg = 'Provider %s tried to associate to non-existing method %s' \
                    % (provider.name, method_key)
                LOG.error(msg)
                raise exceptions.ConfigurationError(msg)

    # PGMethods
    def pg_method_add(self, values):
        row = models.PGMethod(**values)
        self._save(row)
        return dict(row)

    def pg_method_list(self, **kw):
        return self._list(models.PGMethod, **kw)

    def pg_method_get(self, method_id):
        return self._get(models.PGMethod, method_id)

    def pg_method_update(self, method_id, values):
        row = self._update(models.PGMethod, method_id, values)
        return dict(row)

    def pg_method_delete(self, method_id):
        return self._delete(models.PGMethod, method_id)

    # Payment Gateway Configuration
    def pg_config_add(self, merchant_id, provider_id, values):
        merchant = self._get_id_or_name(models.Merchant, merchant_id)
        provider = self._get_id_or_name(models.PGProvider, provider_id)

        row = models.PGAccountConfig(**values)
        row.merchant = merchant
        row.provider = provider

        self._save(row)
        return dict(row)

    def pg_config_list(self, merchant_id, **kw):
        q = self.session.query(models.PGAccountConfig)\
            .filter_by(merchant_id=merchant_id)
        rows = self._list(query=q, **kw)
        return map(dict, rows)

    def pg_config_get(self, cfg_id):
        row = self._get(models.PGAccountConfig, cfg_id)
        return dict(row)

    def pg_config_update(self, cfg_id, values):
        row = self._update(models.PGAccountConfig, cfg_id, values)
        return dict(row)

    def pg_config_delete(self, cfg_id):
        self._delete(models.PGAccountConfig, cfg_id)

    # PaymentMethod
    def payment_method_add(self, customer_id, pg_method_id, values):
        """
        Configure a PaymentMethod like a CreditCard
        """
        customer = self._get_id_or_name(models.Customer, customer_id)
        pg_method = self._get_id_or_name(models.PGMethod, pg_method_id)

        row = models.PaymentMethod(**values)
        row.customer = customer
        row.provider_method = pg_method

        self._save(row)
        return self._dict(row, extra=['provider_method'])

    def payment_method_list(self, customer_id, **kw):
        q = self.session.query(models.PaymentMethod)\
            .filter_by(customer_id=customer_id)
        rows = self._list(query=q, **kw)
        return [self._dict(row, extra=['provider_method']) for row in rows]

    def payment_method_get(self, pm_id, **kw):
        row = self._get_id_or_name(models.PaymentMethod, pm_id)
        return self._dict(row)

    def payment_method_update(self, pm_id, values):
        row = self._update(models.PaymentMethod, pm_id, values)
        return self._dict(row, extra=['provider_method'])

    def payment_method_delete(self, pm_id):
        self._delete(models.PaymentMethod, pm_id)

    # Merchant
    def merchant_add(self, values):
        row = models.Merchant(**values)

        self._save(row)
        return dict(row)

    def merchant_list(self, **kw):
        rows = self._list(models.Merchant, **kw)
        return map(dict, rows)

    def merchant_get(self, merchant_id):
        row = self._get(models.Merchant, merchant_id)
        return dict(row)

    def merchant_update(self, merchant_id, values):
        row = self._update(models.Merchant, merchant_id, values)
        return dict(row)

    def merchant_delete(self, merchant_id):
        self._delete(models.Merchant, merchant_id)

    # Customer
    def _customer(self, row):
        data = dict(row)
        data['default_info'] = dict(row.default_info) if row.default_info\
            else None
        return data

    def customer_add(self, merchant_id, values, contact_info=None):
        merchant = self._get(models.Merchant, merchant_id)

        customer = models.Customer(**values)
        merchant.customers.append(customer)

        if contact_info:
            info_row = self.contact_info_add(customer, contact_info)
            customer.default_info = info_row

        self._save(customer)
        return self._customer(customer)

    def customer_list(self, **kw):
        rows = self._list(models.Customer, **kw)
        return map(dict, rows)

    def customer_get(self, customer_id):
        row = self._get(models.Customer, customer_id)
        return self._customer(row)

    def customer_update(self, customer_id, values):
        row = self._update(models.Customer, customer_id, values)
        return self._customer(row)

    def customer_delete(self, customer_id):
        return self._delete(models.Customer, customer_id)

    # Users
    def _user(self, row):
        """
        Serialize a SQLAlchemy row to a User dictionary

        :param row: The row
        """
        user = dict(row)
        user['contact_info'] = dict(row.contact_info) if row.contact_info\
            else None
        return user

    def user_add(self, merchant_id, values, customer_id=None,
                 contact_info=None):
        """
        Add user

        :param merchant_id: Merchant ID
        :param values: Values to create the new User from
        :param customer_id: The Customer to link this user to
        """
        merchant = self._get(models.Merchant, merchant_id)

        user = models.User(**values)
        user.merchant = merchant

        if customer_id:
            customer = self._get(models.Customer, customer_id)
            customer.users.append(user)

        if contact_info:
            self.contact_info_add(user, contact_info)

        self._save(user)
        return self._user(user)

    def user_list(self, merchant_id, customer_id=None, **kw):
        """
        List users

        :param merchant_id: Merchant to list users for
        """
        q = self.session.query(models.User)
        q = q.filter_by(merchant_id=merchant_id)

        if customer_id:
            q = q.join(models.User.customers).\
                filter(models.Customer.id == customer_id)

        rows = self._list(query=q, **kw)

        return map(self._user, rows)

    def user_get(self, user_id):
        """
        Get a user

        :param user_id: User ID
        """
        row = self._get(models.User, user_id)
        return self._user(row)

    def user_update(self, user_id, values):
        """
        Update user

        :param user_id: User ID
        :param values: Values to update
        """
        row = self._update(models.User, user_id, values)
        return self._user(row)

    def user_delete(self, user_id):
        """
        Delete a user

        :param user_id: User ID
        """
        self._delete(models.User, user_id)

    # Products
    def _product(self, row):
        product = dict(row)

        product['properties'] = map(dict, row.properties) if row.properties\
            else None
        return product

    def product_add(self, merchant_id, values):
        """
        Add a new Product

        :param merchant_id: The Merchant
        :param values: Values describing the new Product
        """
        merchant = self._get(models.Merchant, merchant_id)

        product = models.Product(**values)
        product.merchant = merchant

        self._save(product)
        return self._product(product)

    def product_list(self, merchant_id, **kw):
        """
        List Products

        :param merchant_id: The Merchant to list it for
        """
        q = self.session.query(models.Product)
        q = q.filter_by(merchant_id=merchant_id)

        rows = self._list(query=q, **kw)
        return map(self._product, rows)

    def product_get(self, product_id):
        """
        Get a Product

        :param product_id: The Product ID
        """
        row = self._get(models.Product, product_id)
        return self._product(row)

    def product_update(self, product_id, values):
        """
        Update a Product

        :param product_id: The Product ID
        :param values: Values to update with
        """
        row = self._get(models.Product, product_id)
        row.update(values)

        self._save(row)
        return self._product(row)

    def product_delete(self, product_id):
        """
        Delete a Product

        :param product_id: Product ID
        """
        self._delete(models.Product, product_id)
