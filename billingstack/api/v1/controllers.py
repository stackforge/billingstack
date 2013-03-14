# -*- encoding: utf-8 -*-
#
# Copyright © 2012 Woorea Solutions, S.L
#
# Author: Luis Gervaso <luis@woorea.es>
# Author: Endre Karlson <endre.karlson@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from pecan import request

import wsmeext.pecan as wsme_pecan

from billingstack.openstack.common import log
from billingstack.api.base import RestBase
from billingstack.api.v1 import models

LOG = log.getLogger(__name__)


class CurrenciesController(RestBase):
    """Currsencies controller"""

    @wsme_pecan.wsexpose([models.Currency])
    def get_all(self):
        rows = request.central_api.list_currency(request.ctxt)

        return [models.Currency.from_db(r) for r in rows]


class LanguagesController(RestBase):
    """Languages controller"""

    @wsme_pecan.wsexpose([models.Language])
    def get_all(self):
        rows = request.central_api.list_language(request.ctxt)

        return [models.Language.from_db(r) for r in rows]


class PGProvidersController(RestBase):
    """
    PaymentGatewayProviders
    """
    @wsme_pecan.wsexpose([models.PGProvider])
    def get_all(self):
        rows = request.central_api.list_pg_provider(request.ctxt)

        return [models.PGProvider.from_db(r) for r in rows]


class PGMethodsController(RestBase):
    """
    PGMethods lister...
    """
    @wsme_pecan.wsexpose([models.PGMethod])
    def get_all(self):
        rows = request.central_api.list_pg_method(request.ctxt)

        return [models.PGMethod.from_db(r) for r in rows]


# Plans
class PlanController(RestBase):
    __id__ = 'plan'

    @wsme_pecan.wsexpose(models.Plan)
    def get_all(self):
        row = request.central_api.get_plan(request.ctxt, self.id_)

        return models.Plan.from_db(row)

    @wsme_pecan.wsexpose(models.Plan, body=models.Plan)
    def put(self, body):
        row = request.central_api.update_plan(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.Plan.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.delete_plan(request.ctxt, self.id_)


class PlansController(RestBase):
    __resource__ = PlanController

    @wsme_pecan.wsexpose([models.Plan])
    def get_all(self):
        rows = request.central_api.list_plan(request.ctxt)

        return [models.Plan.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(models.Plan, body=models.Plan)
    def post(self, body):
        row = request.central_api.create_plan(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.Plan.from_db(row)


class PaymentMethodController(RestBase):
    """PaymentMethod controller"""
    __id__ = 'payment_method'

    @wsme_pecan.wsexpose(models.PaymentMethod, unicode)
    def get_all(self):
        row = request.central_api.get_payment_method(request.ctxt, self.id_)

        return models.PaymentMethod.from_db(row)

    @wsme_pecan.wsexpose(models.PaymentMethod, body=models.PaymentMethod)
    def put(self, body):
        row = request.central_api.update_payment_method(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.PaymentMethod.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.delete_payment_method(request.ctxt, self.id_)


class PaymentMethodsController(RestBase):
    """PaymentMethods controller"""
    __resource__ = PaymentMethodController

    @wsme_pecan.wsexpose([models.PaymentMethod], unicode)
    def get_all(self):
        criterion = {
            'customer_id': request.context['customer_id']
        }

        rows = request.central_api.list_payment_method(
            request.ctxt,
            criterion=criterion)

        return [models.PaymentMethod.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(models.PaymentMethod, body=models.PaymentMethod)
    def post(self, body):
        row = request.central_api.create_payment_method(
            request.ctxt,
            request.context['customer_id'],
            body.to_db())

        return models.PaymentMethod.from_db(row)


# Products
class ProductController(RestBase):
    __id__ = 'product'

    @wsme_pecan.wsexpose(models.Product)
    def get_all(self):
        row = request.central_api.get_product(request.ctxt, self.id_)

        return models.Product.from_db(row)

    @wsme_pecan.wsexpose(models.Product, body=models.Product)
    def put(self, body):
        row = request.central_api.update_product(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.Product.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.delete_product(request.ctxt, self.id_)


class ProductsController(RestBase):
    __resource__ = ProductController

    @wsme_pecan.wsexpose([models.Product])
    def get_all(self):
        rows = request.central_api.list_product(request.ctxt)

        return [models.Product.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(models.Product, body=models.Product)
    def post(self, body):
        row = request.central_api.create_product(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.Product.from_db(row)


# Customers
class CustomerController(RestBase):
    """Customer controller"""
    __id__ = 'customer'
    __resource__ = {
        "payment-methods": PaymentMethodsController,
    }

    @wsme_pecan.wsexpose(models.Customer, unicode)
    def get_all(self):
        row = request.central_api.get_customer(request.ctxt, self.id_)

        return models.Customer.from_db(row)

    @wsme_pecan.wsexpose(models.Customer, body=models.Customer)
    def put(self, body):
        row = request.central_api.update_customer(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.Customer.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.delete_customer(request.ctxt, self.id_)


class CustomersController(RestBase):
    """Customers controller"""
    __resource__ = CustomerController

    @wsme_pecan.wsexpose([models.Customer])
    def get_all(self):
        rows = request.central_api.list_customer(
            request.ctxt, criterion={"merchant_id": self.parent.id_})

        return [models.Customer.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(models.Customer, body=models.Customer)
    def post(self, body):
        row = request.central_api.create_customer(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.Customer.from_db(row)


class MerchantController(RestBase):
    __id__ = 'merchant'
    __resource__ = {
        "customers": CustomersController,
        "plans": PlansController,
        "products": ProductsController,
    }

    @wsme_pecan.wsexpose(models.Merchant)
    def get_all(self):
        row = request.central_api.get_merchant(request.ctxt, self.id_)

        return models.Merchant.from_db(row)

    @wsme_pecan.wsexpose(models.Merchant, body=models.Merchant)
    def put(self, body):
        row = request.central_api.update_merchant(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.Merchant.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.delete_merchant(request.ctxt, self.id_)


class MerchantsController(RestBase):
    """Merchants controller"""
    __resource__ = MerchantController

    @wsme_pecan.wsexpose([models.Merchant])
    def get_all(self):
        rows = request.central_api.list_merchant(request.ctxt)

        return [models.Merchant.from_db(i) for i in rows]

    @wsme_pecan.wsexpose(models.Merchant, body=models.Merchant)
    def post(self, body):
        row = request.central_api.create_merchant(
            request.ctxt,
            body.to_db())

        return models.Merchant.from_db(row)


class V1Controller(RestBase):
    """Version 1 API controller."""

    __resource__ = {
        'payment-gateway-providers': PGProvidersController,
        'payment-gateway-methods': PGMethodsController
    }

    currencies = CurrenciesController()
    languages = LanguagesController()

    merchants = MerchantsController()
