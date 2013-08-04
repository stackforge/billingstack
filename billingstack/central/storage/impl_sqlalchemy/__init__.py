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
from sqlalchemy.orm import exc
from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack import exceptions
from billingstack import utils as common_utils
from billingstack.sqlalchemy import utils as db_utils, api
from billingstack.sqlalchemy.session import SQLOPTS
from billingstack.central.storage import Connection, StorageEngine
from billingstack.central.storage.impl_sqlalchemy import models


LOG = logging.getLogger(__name__)

cfg.CONF.register_group(cfg.OptGroup(
    name='central:sqlalchemy', title="Configuration for SQLAlchemy Storage"
))

cfg.CONF.register_opts(SQLOPTS, group='central:sqlalchemy')


class SQLAlchemyEngine(StorageEngine):
    __plugin_name__ = 'sqlalchemy'

    def get_connection(self):
        return Connection(self.name)


class Connection(Connection, api.HelpersMixin):
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

    def _entity(self, row):
        """
        Helper to serialize a entity like a Product or a Plan

        :param row: The Row.
        """
        entity = dict(row)
        if hasattr(row, 'properties'):
            entity['properties'] = self._kv_rows(
                row.properties, func=lambda i: i['value'])
        if hasattr(row, 'pricing'):
            entity['pricing'] = row.pricing or []
        return entity

    # Plan
    def _plan(self, row):
        plan = self._entity(row)
        plan['items'] = map(self._plan_item, row.plan_items) if row.plan_items\
            else []
        return plan

    def create_plan(self, ctxt, merchant_id, values):
        """
        Add a new Plan

        :param merchant_id: The Merchant
        :param values: Values describing the new Plan
        """
        merchant = self._get(models.Merchant, merchant_id)

        properties = values.pop('properties', {})

        plan = models.Plan(**values)

        plan.merchant = merchant
        self.set_properties(plan, properties)

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

    def get_plan_by_subscription(self, ctxt, subscription_id):
        q = self.session.query(models.Plan).join(models.Subscription)\
            .filter(models.Subscription.id == subscription_id)
        try:
            row = q.one()
        except exc.NoResultFound:
            msg = 'Couldn\'t find any Plan for subscription %s' % \
                subscription_id
            raise exceptions.NotFound(msg)
        return self._plan(row)

    # PlanItemw
    def _plan_item(self, row):
        entity = self._entity(row)
        entity['name'] = row.product.name
        entity['title'] = row.title or row.product.title
        entity['description'] = row.description or row.product.description
        return entity

    def create_plan_item(self, ctxt, values):
        row = models.PlanItem(**values)
        self._save(row)
        return self._entity(row)

    def list_plan_items(self, ctxt, **kw):
        return self._list(models.PlanItem, **kw)

    def get_plan_item(self, ctxt, plan_id, product_id, criterion={}):
        criterion.update({'plan_id': plan_id, 'product_id': product_id})
        row = self._get(models.PlanItem, criterion=criterion)
        return self._entity(row)

    def update_plan_item(self, ctxt, plan_id, product_id, values):
        criterion = {'plan_id': plan_id, 'product_id': product_id}
        row = self._get(models.PlanItem, criterion=criterion)
        row.update(values)
        self._save(row)
        return self._entity(row)

    def delete_plan_item(self, ctxt, plan_id, product_id):
        """
        Remove a Product from a Plan by deleting the PlanItem.

        :param plan_id: The Plan's ID.
        :param product_id: The Product's ID.
        """
        query = self.session.query(models.PlanItem).\
            filter_by(plan_id=plan_id, product_id=product_id)

        count = query.delete()
        if count == 0:
            msg = 'Couldn\'t match plan_id %s or product_id %s' % (
                plan_id, product_id)
            raise exceptions.NotFound(msg)

    # Products
    def _product(self, row):
        product = self._entity(row)
        return product

    def create_product(self, ctxt, merchant_id, values):
        """
        Add a new Product

        :param merchant_id: The Merchant
        :param values: Values describing the new Product
        """
        values = values.copy()

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
        values = values.copy()
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

    # Subscriptions
    def _subscription(self, row):
        subscription = dict(row)
        return subscription

    def create_subscription(self, ctxt, values):
        """
        Add a new Subscription

        :param merchant_id: The Merchant
        :param values: Values describing the new Subscription
        """
        subscription = models.Subscription(**values)

        self._save(subscription)
        return self._subscription(subscription)

    def list_subscriptions(self, ctxt, criterion=None, **kw):
        """
        List Subscriptions

        :param merchant_id: The Merchant to list it for
        """
        query = self.session.query(models.Subscription)

        # NOTE: Filter needs to be joined for merchant_id
        query = db_utils.filter_merchant_by_join(
            query, models.Customer, criterion)

        rows = self._list(
            query=query,
            cls=models.Subscription,
            criterion=criterion,
            **kw)

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
