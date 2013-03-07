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
from oslo.config import cfg
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

    def _save(self, obj, save=True):
        if not save:
            return obj
        try:
            obj.save(self.session)
        except exceptions.Duplicate:
            raise

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
        if isinstance(obj, models.ModelBase):
            return obj
        elif isinstance(obj, basestring) and cls:
            return self._get(cls, obj)
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

    def _kv_rows(self, rows, key='name', func=lambda i: i):
        """
        Return a Key, Value dict where the "key" will be the key and the row as value
        """
        data = {}
        for row in rows:
            if callable(key):
                data_key = key(row)
            else:
                data_key = row[key]
            data[data_key] = func(row)
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
    def currency_add(self, ctxt, values):
        """
        Add a supported currency to the database
        """
        data = common_utils.get_currency(values['name'])
        row = models.Currency(**data)
        self._save(row)
        return dict(row)

    def currency_list(self, ctxt, **kw):
        rows = self._list(models.Currency, **kw)
        return map(dict, rows)

    def currency_get(self, ctxt, id_):
        row = self._get(models.Currency, id_)
        return dict(row)

    def currency_update(self, ctxt, id_, values):
        row = self._update(models.Currency, id_, values)
        return dict(row)

    def currency_delete(self, ctxt, id_):
        self._delete(models.Currency, id_)

    # Language
    def language_add(self, ctxt, values):
        """
        Add a supported language to the database
        """
        data = common_utils.get_language(values['name'])
        row = models.Language(**data)
        self._save(row)
        return dict(row)

    def language_list(self, ctxt, **kw):
        rows = self._list(models.Language, **kw)
        return map(dict, rows)

    def language_get(self, ctxt, id_):
        row = self._get(models.Language, id_)
        return dict(row)

    def language_update(self, ctxt, id_, values):
        row = self._update(models.Language, id_, values)
        return dict(row)

    def language_delete(self, ctxt, id_):
        self._delete(models.Language, id_)

    # ContactInfo
    def contact_info_add(self, ctxt, obj, values, cls=None,
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

    def contact_info_get(self, ctxt, id_):
        self._get(models.ContactInfo, id_)

    def contact_info_update(self, ctxt, id_, values):
        return self._update(models.ContactInfo, id_, values)

    def contact_info_delete(self, ctxt, id_):
        self._delete(models.ContactInfo, id_)

    # Payment Gateway Providers
    def pg_provider_register(self, ctxt, values, methods=[]):
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

        self._set_provider_methods(ctxt, provider, methods)

        self._save(provider)
        return self._dict(provider, extra=['methods'])

    def pg_provider_list(self, ctxt, **kw):
        """
        List available PG Providers
        """
        rows = self._list(models.PGProvider, **kw)
        return [self._dict(r, extra=['methods']) for r in rows]

    def pg_provider_get(self, ctxt, pgp_id):
        row = self._get(models.PGProvider, pgp_id)
        return self._dict(row, extra=['methods'])

    def pg_provider_deregister(self, ctxt, id_):
        self._delete(models.PGProvider, id_)

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

    def _set_provider_methods(self, ctxt, provider, config_methods):
        """
        Helper method for setting the Methods for a Provider
        """
        rows = self.pg_method_list(ctxt, criterion={"owner_id": None})
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
    def pg_method_add(self, ctxt, values):
        row = models.PGMethod(**values)
        self._save(row)
        return dict(row)

    def pg_method_list(self, ctxt, **kw):
        return self._list(models.PGMethod, **kw)

    def pg_method_get(self, ctxt, id_):
        return self._get(models.PGMethod, id_)

    def pg_method_update(self, ctxt, id_, values):
        row = self._update(models.PGMethod, id_, values)
        return dict(row)

    def pg_method_delete(self, ctxt, id_):
        return self._delete(models.PGMethod, id_)

    # Payment Gateway Configuration
    def pg_config_add(self, ctxt, merchant_id, provider_id, values):
        merchant = self._get_id_or_name(models.Merchant, merchant_id)
        provider = self._get_id_or_name(models.PGProvider, provider_id)

        row = models.PGAccountConfig(**values)
        row.merchant = merchant
        row.provider = provider

        self._save(row)
        return dict(row)

    def pg_config_list(self, ctxt, **kw):
        rows = self._list(models.PGAccountConfig, **kw)
        return map(dict, rows)

    def pg_config_get(self, ctxt, id_):
        row = self._get(models.PGAccountConfig, id_)
        return dict(row)

    def pg_config_update(self, ctxt, id_, values):
        row = self._update(models.PGAccountConfig, id_, values)
        return dict(row)

    def pg_config_delete(self, ctxt, id_):
        self._delete(models.PGAccountConfig, id_)

    # PaymentMethod
    def payment_method_add(self, ctxt, customer_id, pg_method_id, values):
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

    def payment_method_list(self, ctxt, **kw):
        rows = self._list(models.PaymentMethod, **kw)
        return [self._dict(row, extra=['provider_method']) for row in rows]

    def payment_method_get(self, ctxt, id_, **kw):
        row = self._get_id_or_name(models.PaymentMethod, id_)
        return self._dict(row, extra=['provider_method'])

    def payment_method_update(self, ctxt, id_, values):
        row = self._update(models.PaymentMethod, id_, values)
        return self._dict(row, extra=['provider_method'])

    def payment_method_delete(self, ctxt, id_):
        self._delete(models.PaymentMethod, id_)

    # Merchant
    def merchant_add(self, ctxt, values):
        row = models.Merchant(**values)

        self._save(row)
        return dict(row)

    def merchant_list(self, ctxt, **kw):
        rows = self._list(models.Merchant, **kw)
        return map(dict, rows)

    def merchant_get(self, ctxt, id_):
        row = self._get(models.Merchant, id_)
        return dict(row)

    def merchant_update(self, ctxt, id_, values):
        row = self._update(models.Merchant, id_, values)
        return dict(row)

    def merchant_delete(self, ctxt, id_):
        self._delete(models.Merchant, id_)

    # Customer
    def _customer(self, row):
        data = dict(row)

        data['contact_info'] = [dict(i) for i in row.contact_info]
        data['default_info'] = dict(row.default_info) if row.default_info\
            else {}
        return data

    def customer_add(self, ctxt, merchant_id, values):
        merchant = self._get(models.Merchant, merchant_id)

        contact_info = values.pop('contact_info', None)
        customer = models.Customer(**values)
        merchant.customers.append(customer)

        if contact_info:
            info_row = self.contact_info_add(ctxt, customer, contact_info)
            customer.default_info = info_row

        self._save(customer)
        return self._customer(customer)

    def customer_list(self, ctxt, **kw):
        rows = self._list(models.Customer, **kw)
        return map(dict, rows)

    def customer_get(self, ctxt, id_):
        row = self._get(models.Customer, id_)
        return self._customer(row)

    def customer_update(self, ctxt, id_, values):
        row = self._update(models.Customer, id_, values)
        return self._customer(row)

    def customer_delete(self, ctxt, id_):
        return self._delete(models.Customer, id_)

    # Users
    def _user(self, row):
        """
        Serialize a SQLAlchemy row to a User dictionary

        :param row: The row
        """
        user = dict(row)
        user['contact_info'] = dict(row.contact_info) if row.contact_info\
            else {}
        del user['password']
        return user

    def _user_set_info(self, ctxt, row, values):
        """
        Add or Update contact info on a user with values
        """
        if not values:
            return
        if not row.contact_info:
            self.contact_info_add(ctxt, row, values)
        else:
            row.contact_info.update(values)

    def user_add(self, ctxt, merchant_id, values):
        """
        Add user

        :param merchant_id: Merchant ID
        :param values: Values to create the new User from
        """
        merchant = self._get(models.Merchant, merchant_id)

        customer_id = values.pop('customer_id', None)
        contact_info = values.pop('contact_info', None)

        user = models.User(**values)
        user.merchant = merchant

        if customer_id:
            customer = self._get(models.Customer, customer_id)
            customer.users.append(user)

        self._user_set_info(ctxt, user, contact_info)

        self._save(user)
        return self._user(user)

    def user_list(self, ctxt, criterion={}, **kw):
        """
        List users
        """
        query = self.session.query(models.User)

        customer_id = criterion.pop('customer_id', None)
        if customer_id:
            query = query.join(models.User.customers)\
                .filter(models.Customer.id == customer_id)
        rows = self._list(query=query, criterion=criterion, **kw)

        return map(self._user, rows)

    def user_get(self, ctxt, id_):
        """
        Get a user

        :param id_: User ID
        """
        row = self._get(models.User, id_)
        return self._user(row)

    def user_update(self, ctxt, id_, values):
        """
        Update user

        :param id_: User ID
        :param values: Values to update
        """
        contact_info = values.pop('contact_info', None)

        row = self._update(models.User, id_, values)

        self._user_set_info(ctxt, row, contact_info)
        return self._user(row)

    def user_delete(self, ctxt, id_):
        """
        Delete a user

        :param id_: User ID
        """
        self._delete(models.User, id_)

    # Products
    def _product(self, row):
        product = dict(row)

        product['properties'] = self._kv_rows(row.properties, func=lambda i: i['value'])
        return product

    def product_add(self, ctxt, merchant_id, values):
        """
        Add a new Product

        :param merchant_id: The Merchant
        :param values: Values describing the new Product
        """
        merchant = self._get(models.Merchant, merchant_id)

        properties = values.pop('properties', {})

        product = models.Product(**values)
        product.merchant = merchant

        self.set_properties(product, properties)

        self._save(product)
        return self._product(product)

    def product_list(self, ctxt, **kw):
        """
        List Products

        :param merchant_id: The Merchant to list it for
        """
        rows = self._list(models.Product, **kw)
        return map(self._product, rows)

    def product_get(self, ctxt, id_):
        """
        Get a Product

        :param id_: The Product ID
        """
        row = self._get(models.Product, id_)
        return self._product(row)

    def product_update(self, ctxt, id_, values):
        """
        Update a Product

        :param id_: The Product ID
        :param values: Values to update with
        """
        properties = values.pop('properties', {})

        row = self._get(models.Product, id_)
        row.update(values)

        self.set_properties(row, properties)

        self._save(row)
        return self._product(row)

    def product_delete(self, ctxt, id_):
        """
        Delete a Product

        :param id_: Product ID
        """
        self._delete(models.Product, id_)

    # PlanItem
    def plan_item_add(self, ctxt, values, save=True):
        ref = models.PlanItem()
        return self._plan_item_update(ref, values, save=save)

    def plan_item_update(self, ctxt, item, values, save=True):
        return self._plan_item_update(item, values, save=save)

    def _plan_item_update(self, item, values, save=True):
        row = self._get_row(item, models.PlanItem)
        row.update(values)
        return self._save(row, save=save)

    def plan_item_list(self, ctxt, **kw):
        return self._list(models.PlanItem, **kw)

    def plan_item_get(self, ctxt, id_):
        row = self._get(models.PlanItem, id_)
        return dict(row)

    def plan_item_delete(self, ctxt, id_):
        self._delete(models.PlanItem, id_)

    # Plan
    def _plan(self, row):
        plan = dict(row)

        plan['properties'] = self._kv_rows(row.properties, func=lambda i: i['value'])
        plan['plan_items'] = map(dict, row.plan_items) if row.plan_items\
            else []
        return plan

    def plan_add(self, ctxt, merchant_id, values):
        """
        Add a new Plan

        :param merchant_id: The Merchant
        :param values: Values describing the new Plan
        """
        merchant = self._get(models.Merchant, merchant_id)

        items = values.pop('plan_items', [])
        properties = values.pop('properties', {})

        plan = models.Plan(**values)

        plan.merchant = merchant
        self.set_properties(plan, properties)

        for i in items:
            item_row = self.plan_item_add(ctxt, i, save=False)
            plan.plan_items.append(item_row)

        self._save(plan)
        return self._plan(plan)

    def plan_list(self, ctxt, **kw):
        """
        List Plan

        :param merchant_id: The Merchant to list it for
        """
        rows = self._list(models.Plan, **kw)
        return map(self._plan, rows)

    def plan_get(self, ctxt, id_):
        """
        Get a Plan

        :param id_: The Plan ID
        """
        row = self._get(models.Plan, id_)
        return self._plan(row)

    def plan_update(self, ctxt, id_, values):
        """
        Update a Plan

        :param id_: The Plan ID
        :param values: Values to update with
        """
        properties = values.pop('properties', {})

        row = self._get(models.Plan, id_)
        row.update(values)

        self.set_properties(row, properties)

        self._save(row)
        return self._plan(row)

    def plan_delete(self, ctxt, id_):
        """
        Delete a Plan

        :param id_: Plan ID
        """
        self._delete(models.Plan, id_)
