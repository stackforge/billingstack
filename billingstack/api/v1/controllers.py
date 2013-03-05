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

import inspect
import pecan
from pecan import request
from pecan.rest import RestController

import wsmeext.pecan as wsme_pecan


from billingstack.openstack.common import log
from billingstack.openstack.common import jsonutils
from billingstack.api.v1.models import Currency, Language, PGProvider, PGMethod
from billingstack.api.v1.models import Customer, Merchant, User, Plan, Product

LOG = log.getLogger(__name__)



class RestBase(RestController):
    __resource__ = None
    __id__ = None

    def __init__(self, parent=None, id_=None):
        self.parent = parent
        if self.__id__:
            request.context[self.__id__ + '_id'] = id_
        self.id_ = id_

    @pecan.expose()
    def _lookup(self, *url_data):
        """
        A fun approach to _lookup - checks self.__resource__ for the "id"
        """
        id_ = None
        if len(url_data) >= 1:
            id_ = url_data[0]
        parts = url_data[1:] if len(url_data) > 1 else ()
        LOG.debug("Lookup: id '%s' parts '%s'", id_, parts)

        resource = self.__resource__
        if inspect.isclass(resource) and issubclass(resource, RestBase):
            return resource(parent=self, id_=id_), parts

    def __getattr__(self, name):
        """
        Overload this to look in self.__resource__ if name is defined as a
        Controller
        """
        if name in self.__dict__:
            return self.__dict__[name]
        elif isinstance(self.__resource__, dict) and name in self.__resource__:
            return self.__resource__[name](parent=self)
        else:
            raise AttributeError


class CurrenciesController(RestBase):
    """Currsencies controller"""

    @wsme_pecan.wsexpose([Currency])
    def get_all(self):
        rows = request.central_api.currency_list(request.ctxt)
        return [Currency(**i) for i in rows]


class LanguagesController(RestBase):
    """Languages controller"""

    @wsme_pecan.wsexpose([Language])
    def get_all(self):
        rows = request.central_api.language_list(request.ctxt)
        return [Language(**i) for i in rows]


class PGProvidersController(RestBase):
    """
    PaymentGatewayProviders
    """
    @wsme_pecan.wsexpose([PGProvider])
    def get_all(self):
        rows = request.central_api.pg_provider_list(request.ctxt)
        return [PGProvider(**i) for i in rows]


class PGMethodsController(RestBase):
    """
    PGMethods lister...
    """
    @wsme_pecan.wsexpose([PGMethod])
    def get_all(self):
        rows = request.central_api.pg_method_list(request.ctxt)
        return [PGMethod(**row) for row in rows]


class UserController(RestBase):
    """User controller"""
    __id__ = 'user'

    @wsme_pecan.wsexpose(User, unicode)
    def get_all(self):
        row = request.central_api.user_get(request.ctxt, self.id_)
        return User(**dict(row))

    @wsme_pecan.wsexpose(User, body=User)
    def put(self, body):
        row = request.central_api.user_update(
            request.ctxt,
            self.id_,
            body.as_dict())
        return User(**row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.user_delete(request.ctxt, self.id_)


class UsersController(RestBase):
    """Users controller"""
    __resource__ = UserController

    @wsme_pecan.wsexpose([User], unicode)
    def get_all(self):
        criterion = {
            'merchant_id': request.context['merchant_id']
        }

        if 'customer_id' in request.context:
            criterion['customer_id'] = request.context['customer_id']

        rows = request.central_api.user_list(
            request.ctxt,
            criterion=criterion)

        return [User(**i) for i in rows]

    @wsme_pecan.wsexpose(User, body=User)
    def post(self, body):
        row = request.central_api.user_add(
            request.ctxt,
            request.context['merchant_id'],
            body.as_dict())
        return User(**row)

# Plans
class PlanController(RestBase):
    __id__ = 'plan'

    @wsme_pecan.wsexpose(Plan)
    def get_all(self):
        row = request.central_api.plan_get(request.ctxt, self.id_)
        return Plan(**row)

    @wsme_pecan.wsexpose(Plan, body=Plan)
    def put(self, body):
        row = request.central_api.plan_update(
            request.ctxt,
            self.id_,
            body.as_dict())
        return Plan(**row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.plan_delete(request.ctxt, self.id_)


class PlansController(RestBase):
    __resource__ = PlanController

    @wsme_pecan.wsexpose([Plan])
    def get_all(self):
        rows = request.central_api.plan_list(request.ctxt)
        return [Plan(**i) for i in rows]

    @wsme_pecan.wsexpose(Plan, body=Plan)
    def post(self, body):
        row = request.central_api.plan_add(
            request.ctxt,
            request.context['merchant_id'],
            body.as_dict())
        return Plan(**row)


# Products
class ProductController(RestBase):
    __id__ = 'product'

    @wsme_pecan.wsexpose(Product)
    def get_all(self):
        row = request.central_api.product_get(request.ctxt, self.id_)
        return Product(**row)

    @wsme_pecan.wsexpose(Product, body=Product)
    def put(self, body):
        row = request.central_api.product_update(
            request.ctxt,
            self.id_,
            body.as_dict())
        return Product(**row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.product_delete(request.ctxt, self.id_)


class ProductsController(RestBase):
    __resource__ = ProductController

    @wsme_pecan.wsexpose([Product])
    def get_all(self):
        rows = request.central_api.product_list(request.ctxt)
        return [Product(**i) for i in rows]

    @wsme_pecan.wsexpose(Product, body=Product)
    def post(self, body):
        row = request.central_api.product_add(
            request.ctxt,
            request.context['merchant_id'],
            body.as_dict())
        return Product(**row)


# Customers
class CustomerController(RestBase):
    """Customer controller"""
    __id__ = 'customer'
    __resource__ = {
        "users": UsersController
    }

    @wsme_pecan.wsexpose(Customer, unicode)
    def get_all(self):
        row = request.central_api.customer_get(request.ctxt, self.id_)
        return Customer(**dict(row))

    @wsme_pecan.wsexpose(Customer, body=Customer)
    def put(self, body):
        row = request.central_api.customer_update(
            request.ctxt,
            self.id_,
            body.as_dict())
        return Customer(**row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.customer_delete(request.ctxt, self.id_)


class CustomersController(RestBase):
    """Customers controller"""
    __resource__ = CustomerController

    @wsme_pecan.wsexpose([Customer])
    def get_all(self):
        rows = request.central_api.customer_list(
            request.ctxt, criterion={"merchant_id": self.parent.id_})
        return [Customer(**o) for o in rows]

    @wsme_pecan.wsexpose(Customer, body=Customer)
    def post(self, body):
        rows = request.central_api.customer_add(
            request.ctxt,
            request.context['merchant_id'],
            body.as_dict())
        return Customer(**rows)


class MerchantController(RestBase):
    __id__ = 'merchant'
    __resource__ = {
        "customers": CustomersController,
        "plans": PlansController,
        "products": ProductsController,
        "users": UsersController
    }

    @wsme_pecan.wsexpose(Merchant)
    def get_all(self):
        row = request.central_api.merchant_get(request.ctxt, self.id_)
        return Merchant(**dict(row))

    @wsme_pecan.wsexpose(Merchant, body=Merchant)
    def put(self, body):
        row = request.central_api.merchant_update(
            request.ctxt,
            self.id_,
            body.as_dict())
        return Merchant(**row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.central_api.merchant_delete(request.ctxt, self.id_)


class MerchantsController(RestBase):
    """Merchants controller"""
    __resource__ = MerchantController

    @wsme_pecan.wsexpose([Merchant])
    def get_all(self):
        rows = request.central_api.merchant_list(request.ctxt)
        return [Merchant(**o) for o in rows]

    @wsme_pecan.wsexpose(Merchant, body=Merchant)
    def post(self, body):
        row = request.central_api.merchant_add(
            request.ctxt,
            body.as_dict())
        return Merchant(**row)


class V1Controller(RestBase):
    """Version 1 API controller."""

    __resource__ = {
        'payment-gateway-providers': PGProvidersController,
        'payment-gateway-methods': PGMethodsController
    }

    currencies = CurrenciesController()
    languages = LanguagesController()

    merchants = MerchantsController()
    users = UsersController()