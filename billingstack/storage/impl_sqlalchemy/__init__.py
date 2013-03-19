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
from sqlalchemy.orm import exc
from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack import exceptions
from billingstack import utils as common_utils
from billingstack.sqlalchemy import utils as db_utils, api
from billingstack.sqlalchemy.session import SQLOPTS
from billingstack.storage import base
from billingstack.storage.impl_sqlalchemy import models


LOG = logging.getLogger(__name__)

cfg.CONF.register_group(cfg.OptGroup(
    name='storage:sqlalchemy', title="Configuration for SQLAlchemy Storage"
))

cfg.CONF.register_opts(SQLOPTS, group='storage:sqlalchemy')


class SQLAlchemyStorage(base.StorageEngine):
    __plugin_name__ = 'sqlalchemy'

    def get_connection(self):
        return Connection(self.name)


class Connection(base.Connection, api.HelpersMixin):
    """
    SQLAlchemy connection
    """
    def __init__(self, config_group):
        self.setup(config_group)

    def base(self):
        return models.BASE

    def set_properties(self, obj, properties, cls=None, rel_attr='properties',
                       purge=False):
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
    def create_currency(self, ctxt, values):
        """
        Add a supported currency to the database
        """
        data = common_utils.get_currency(values['name'])
        row = models.Currency(**data)
        self._save(row)
        return dict(row)

    def list_currencies(self, ctxt, **kw):
        rows = self._list(models.Currency, **kw)
        return map(dict, rows)

    def get_currency(self, ctxt, id_):
        row = self._get_id_or_name(models.Currency, id_)
        return dict(row)

    def update_currency(self, ctxt, id_, values):
        row = self._update(models.Currency, id_, values, by_name=True)
        return dict(row)

    def delete_currency(self, ctxt, id_):
        self._delete(models.Currency, id_, by_name=True)

        # Language
    def create_language(self, ctxt, values):
        """
        Add a supported language to the database
        """
        data = common_utils.get_language(values['name'])
        row = models.Language(**data)
        self._save(row)
        return dict(row)

    def list_languages(self, ctxt, **kw):
        rows = self._list(models.Language, **kw)
        return map(dict, rows)

    def get_language(self, ctxt, id_):
        row = self._get_id_or_name(models.Language, id_)
        return dict(row)

    def update_language(self, ctxt, id_, values):
        row = self._update(models.Language, id_, values, by_name=True)
        return dict(row)

    def delete_language(self, ctxt, id_):
        self._delete(models.Language, id_, by_name=True)

    # Invoice States
    def create_invoice_state(self, ctxt, values):
        """
        Add a supported invoice_state to the database
        """
        row = models.InvoiceState(**values)
        self._save(row)
        return dict(row)

    def list_invoice_states(self, ctxt, **kw):
        rows = self._list(models.InvoiceState, **kw)
        return map(dict, rows)

    def get_invoice_state(self, ctxt, id_):
        row = self._get_id_or_name(models.InvoiceState, id_)
        return dict(row)

    def update_invoice_state(self, ctxt, id_, values):
        row = self._update(models.InvoiceState, id_, values, by_name=True)
        return dict(row)

    def delete_invoice_state(self, ctxt, id_):
        self._delete(models.InvoiceState, id_, by_name=True)

    # ContactInfo
    def create_contact_info(self, ctxt, obj, values, cls=None,
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

    def get_contact_info(self, ctxt, id_):
        self._get(models.ContactInfo, id_)

    def update_contact_info(self, ctxt, id_, values):
        return self._update(models.ContactInfo, id_, values)

    def delete_contact_info(self, ctxt, id_):
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

    def list_pg_providers(self, ctxt, **kw):
        """
        List available PG Providers
        """
        rows = self._list(models.PGProvider, **kw)
        return [self._dict(r, extra=['methods']) for r in rows]

    def get_pg_provider(self, ctxt, pgp_id):
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
        rows = self.list_pg_methods(ctxt, criterion={"owner_id": None})
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
                msg = 'Provider %s tried to associate to non-existing'\
                      'method %s' % (provider.name, method_key)
                LOG.error(msg)
                raise exceptions.ConfigurationError(msg)

    # PGMethods
    def create_pg_method(self, ctxt, values):
        row = models.PGMethod(**values)
        self._save(row)
        return dict(row)

    def list_pg_methods(self, ctxt, **kw):
        return self._list(models.PGMethod, **kw)

    def get_pg_method(self, ctxt, id_):
        return self._get(models.PGMethod, id_)

    def update_pg_method(self, ctxt, id_, values):
        row = self._update(models.PGMethod, id_, values)
        return dict(row)

    def delete_pg_method(self, ctxt, id_):
        return self._delete(models.PGMethod, id_)

    # Payment Gateway Configuration
    def create_pg_config(self, ctxt, merchant_id, provider_id, values):
        merchant = self._get_id_or_name(models.Merchant, merchant_id)
        provider = self._get_id_or_name(models.PGProvider, provider_id)

        row = models.PGConfig(**values)
        row.merchant = merchant
        row.provider = provider

        self._save(row)
        return dict(row)

    def list_pg_configs(self, ctxt, **kw):
        rows = self._list(models.PGConfig, **kw)
        return map(dict, rows)

    def get_pg_config(self, ctxt, id_):
        row = self._get(models.PGConfig, id_)
        return dict(row)

    def update_pg_config(self, ctxt, id_, values):
        row = self._update(models.PGConfig, id_, values)
        return dict(row)

    def delete_pg_config(self, ctxt, id_):
        self._delete(models.PGConfig, id_)

    # PaymentMethod
    def create_payment_method(self, ctxt, customer_id, pg_method_id, values):
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

    def list_payment_methods(self, ctxt, **kw):
        rows = self._list(models.PaymentMethod, **kw)
        return [self._dict(row, extra=['provider_method']) for row in rows]

    def get_payment_method(self, ctxt, id_, **kw):
        row = self._get_id_or_name(models.PaymentMethod, id_)
        return self._dict(row, extra=['provider_method'])

    def update_payment_method(self, ctxt, id_, values):
        row = self._update(models.PaymentMethod, id_, values)
        return self._dict(row, extra=['provider_method'])

    def delete_payment_method(self, ctxt, id_):
        self._delete(models.PaymentMethod, id_)

    # Merchant
    def create_merchant(self, ctxt, values):
        row = models.Merchant(**values)

        self._save(row)
        return dict(row)

    def list_merchants(self, ctxt, **kw):
        rows = self._list(models.Merchant, **kw)
        return map(dict, rows)

    def get_merchant(self, ctxt, id_):
        row = self._get(models.Merchant, id_)
        return dict(row)

    def update_merchant(self, ctxt, id_, values):
        row = self._update(models.Merchant, id_, values)
        return dict(row)

    def delete_merchant(self, ctxt, id_):
        self._delete(models.Merchant, id_)

    # Customer
    def _customer(self, row):
        data = dict(row)

        data['contact_info'] = [dict(i) for i in row.contact_info]
        data['default_info'] = dict(row.default_info) if row.default_info\
            else {}
        return data

    def create_customer(self, ctxt, merchant_id, values):
        merchant = self._get(models.Merchant, merchant_id)

        contact_info = values.pop('contact_info', None)
        customer = models.Customer(**values)
        merchant.customers.append(customer)

        if contact_info:
            info_row = self.create_contact_info(ctxt, customer, contact_info)
            customer.default_info = info_row

        self._save(customer)
        return self._customer(customer)

    def list_customers(self, ctxt, **kw):
        rows = self._list(models.Customer, **kw)
        return map(dict, rows)

    def get_customer(self, ctxt, id_):
        row = self._get(models.Customer, id_)
        return self._customer(row)

    def update_customer(self, ctxt, id_, values):
        row = self._update(models.Customer, id_, values)
        return self._customer(row)

    def delete_customer(self, ctxt, id_):
        return self._delete(models.Customer, id_)

    # Plan
    def _plan(self, row):
        plan = dict(row)

        plan['properties'] = self._kv_rows(row.properties,
                                           func=lambda i: i['value'])
        plan['plan_items'] = map(dict, row.plan_items) if row.plan_items\
            else []
        return plan

    def create_plan(self, ctxt, merchant_id, values):
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
            item_row = self.create_plan_item(ctxt, i, save=False)
            plan.plan_items.append(item_row)

        self._save(plan)
        return self._plan(plan)

    def list_plans(self, ctxt, **kw):
        """
        List Plan

        :param merchant_id: The Merchant to list it for
        """
        rows = self._list(models.Plan, **kw)
        return map(self._plan, rows)

    def get_plan(self, ctxt, id_):
        """
        Get a Plan

        :param id_: The Plan ID
        """
        row = self._get(models.Plan, id_)
        return self._plan(row)

    def update_plan(self, ctxt, id_, values):
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

    def delete_plan(self, ctxt, id_):
        """
        Delete a Plan

        :param id_: Plan ID
        """
        self._delete(models.Plan, id_)

    # PlanItem
    def create_plan_item(self, ctxt, values, save=True):
        ref = models.PlanItem()
        return self._update_plan_item(ref, values, save=save)

    def update_plan_item(self, ctxt, item, values, save=True):
        return self._update_plan_item(item, values, save=save)

    def _update_plan_item(self, item, values, save=True):
        row = self._get_row(item, models.PlanItem)
        row.update(values)
        return self._save(row, save=save)

    def list_plan_items(self, ctxt, **kw):
        return self._list(models.PlanItem, **kw)

    def get_plan_item(self, ctxt, id_):
        row = self._get(models.PlanItem, id_)
        return dict(row)

    def delete_plan_item(self, ctxt, id_):
        self._delete(models.PlanItem, id_)

    # Products
    def _product(self, row):
        product = dict(row)

        product['properties'] = self._kv_rows(row.properties,
                                              func=lambda i: i['value'])
        return product

    def create_product(self, ctxt, merchant_id, values):
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

    def list_products(self, ctxt, **kw):
        """
        List Products

        :param merchant_id: The Merchant to list it for
        """
        rows = self._list(models.Product, **kw)
        return map(self._product, rows)

    def get_product(self, ctxt, id_):
        """
        Get a Product

        :param id_: The Product ID
        """
        row = self._get(models.Product, id_)
        return self._product(row)

    def update_product(self, ctxt, id_, values):
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

    def delete_product(self, ctxt, id_):
        """
        Delete a Product

        :param id_: Product ID
        """
        self._delete(models.Product, id_)

    # Invoices
    def _invoice(self, row):
        invoice = dict(row)
        return invoice

    def create_invoice(self, ctxt, merchant_id, values):
        """
        Add a new Invoice

        :param merchant_id: The Merchant
        :param values: Values describing the new Invoice
        """
        merchant = self._get(models.Merchant, merchant_id)

        invoice = models.Invoice(**values)
        invoice.merchant = merchant

        self._save(invoice)
        return self._invoice(invoice)

    def list_invoices(self, ctxt, **kw):
        """
        List Invoices
        """
        rows = self._list(models.Invoice, **kw)
        return map(self._invoice, rows)

    def get_invoice(self, ctxt, id_):
        """
        Get a Invoice

        :param id_: The Invoice ID
        """
        row = self._get(models.Invoice, id_)
        return self.invoice(row)

    def update_invoice(self, ctxt, id_, values):
        """
        Update a Invoice

        :param id_: The Invoice ID
        :param values: Values to update with
        """
        row = self._get(models.Invoice, id_)
        row.update(values)

        self._save(row)
        return self._invoice(row)

    def delete_invoice(self, ctxt, id_):
        """
        Delete a Invoice

        :param id_: Invoice ID
        """
        self._delete(models.Invoice, id_)

    # Subscriptions
    def _subscription(self, row):
        subscription = dict(row)
        return subscription

    def create_subscription(self, ctxt, customer_id, values):
        """
        Add a new Subscription

        :param merchant_id: The Merchant
        :param values: Values describing the new Subscription
        """
        customer = self._get(models.Customer, customer_id)

        subscription = models.Subscription(**values)
        subscription.customer = customer

        self._save(subscription)
        return self._subscription(subscription)

    def list_subscriptions(self, ctxt, **kw):
        """
        List Subscriptions

        :param merchant_id: The Merchant to list it for
        """
        rows = self._list(models.Subscription, **kw)
        return map(self._subscription, rows)

    def get_subscription(self, ctxt, id_):
        """
        Get a Subscription

        :param id_: The Subscription ID
        """
        row = self._get(models.Subscription, id_)
        return self._subscription(row)

    def update_subscription(self, ctxt, id_, values):
        """
        Update a Subscription

        :param id_: The Subscription ID
        :param values: Values to update with
        """
        row = self._get(models.Subscription, id_)
        row.update(values)

        self._save(row)
        return self._subscription(row)

    def delete_subscription(self, ctxt, id_):
        """
        Delete a Subscription

        :param id_: Subscription ID
        """
        self._delete(models.Subscription, id_)
