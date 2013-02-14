# -*- encoding: utf-8 -*-
#
# Copyright © 2012 Woorea Solutions, S.L
#
# Author: Luis Gervaso <luis@woorea.es>
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

import pecan
from pecan import request
from pecan.rest import RestController

import wsmeext.pecan as wsme_pecan
from wsme.types import Base, text


from billingstack.openstack.common import log


LOG = log.getLogger(__name__)


class Base(Base):
    id = text


class Currency(Base):
    id = text
    letter = text
    name = text


class Language(Base):
    letter = text
    name = text


class ContactInfo(Base):
    address1 = text
    address2 = text
    city = text
    company = text
    country = text
    state = text
    zip = text


class User(Base):
    def __init__(self, **kw):
        kw['contact_info'] = ContactInfo(**kw.get('contact_info', {}))
        super(User, self).__init__(**kw)

    username = text
    merchant_id = text
    contact_info = ContactInfo


class Account(Base):
    currency_id = text
    language_id = text

    name = text


class Merchant(Account):
    pass


class Customer(Account):
    merchant_id = text


class RestBase(RestController):
    resource = None
    __id__ = None

    def __init__(self, parent=None, id_=None):
        self.parent = parent
        if self.__id__:
            request.context[self.__id__ + '_id'] = id_
        self.id_ = id_

    @pecan.expose()
    def _lookup(self, *url_data):
        id_ = None
        if len(url_data) >= 1:
            id_ = url_data[0]
        parts = url_data[1:] if len(url_data) > 1 else ()
        LOG.debug("Lookup: id '%s' parts '%s'", id_, parts)

        values = None, ()
        if type(self.resource) == dict:
            cls = self._lookup_resource(id_, parts)
            values = cls(parent=self, id_=id_), parts
        elif self.resource and issubclass(self.resource, RestBase):
            values = self.resource(parent=self, id_=id_), parts
        LOG.debug("Returning %s", values)
        return values

    def _lookup_resource(self, key, parts):
        return self.resource.get(key)


class CurrenciesController(RestBase):
    """Currencies controller"""

    @wsme_pecan.wsexpose([Currency])
    def get_all(self):
        return [Currency(**o) for o in request.storage_conn.currency_list()]


class LanguagesController(RestBase):
    """Languages controller"""

    @wsme_pecan.wsexpose([Language])
    def get_all(self):
        return [Language(**o) for o in request.storage_conn.language_list()]


class UsersController(RestBase):
    """Users controller"""

    @wsme_pecan.wsexpose([User], unicode)
    def get_all(self):
        users = request.storage_conn.user_list(
            request.context['merchant_id'],
            customer_id=request.context.get('customer_id'))
        return [User(**o) for o in users]


class CustomerController(RestBase):
    """Customer controller"""
    __id__ = 'customer'
    resource = {
        "users": UsersController
    }

    @wsme_pecan.wsexpose(Customer, unicode)
    def get_all(self):
        customer = request.storage_conn.customer_get(self.id_)
        return Customer(**dict(customer))


class CustomersController(RestBase):
    """Customers controller"""

    resource = CustomerController

    @wsme_pecan.wsexpose([Customer])
    def get_all(self):
        customers = request.storage_conn.customer_list(self.parent.id_)
        return [Customer(**o) for o in customers]


class MerchantController(RestBase):
    __id__ = 'merchant'
    resource = {
        "customers": CustomersController,
        "users": UsersController
    }

    @wsme_pecan.wsexpose(Merchant)
    def get_all(self):
        m = request.storage_conn.merchant_get(self.id_)
        return Merchant(**dict(m))


class MerchantsController(RestBase):
    """Merchants controller"""
    resource = MerchantController

    @wsme_pecan.wsexpose([Merchant])
    def get_all(self):
        return [Merchant(**o) for o in request.storage_conn.merchant_list()]

    @wsme_pecan.wsexpose(Merchant, body=Merchant)
    def post(self, body):
        #print body
        return Merchant(**{})


class V1Controller(object):
    """Version 1 API controller."""

    currencies = CurrenciesController()
    languages = LanguagesController()

    merchants = MerchantsController()
    users = UsersController()
