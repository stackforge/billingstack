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
from wsme.types import Base, text, Unset


from billingstack.openstack.common import log


LOG = log.getLogger(__name__)


class Base(Base):
    def as_dict(self):
        data = {}

        for attr in self._wsme_attributes:
            value = attr.__get__(self, self.__class__)
            if value is not Unset:
                if isinstance(value, Base) and hasattr(value, "as_dict"):
                    value = value.as_dict()
                data[attr.name] = value
        return data

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
    __resource__ = None
    __id__ = None

    def __init__(self, parent=None, id_=None):
        #import ipdb
        #ipdb.set_trace()
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
        if isinstance(self.__resource__, dict) and id_ in self.__resource__:
            cls = self.__resource__[id_]
            values = cls(parent=self, id_=id_), parts
        elif self.__resource__ and issubclass(self.__resource__, RestBase):
            values = self.__resource__(parent=self, id_=id_), parts
        print "Returning", values
        return values

    def __getattr__(self, name):
        """
        Overload this to look in self.__resource__ if name is defined as a
        Controller
        """
        if name in self.__dict__:
            return self.__dict__[name]
        elif isinstance(self.__resource__, dict) and name in self.__resource__:
            return self.__resource__[name]()
        else:
            raise AttributeError


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


class UserController(RestBase):
    """User controller"""
    __id__ = 'user'

    @wsme_pecan.wsexpose(Customer, unicode)
    def get_all(self):
        user = request.storage_conn.user_get(self.id_)
        return User(**dict(user))

    @wsme_pecan.wsexpose(User, body=User)
    def put(self, body):
        m = request.storage_conn.user_update(self.id_, body.as_dict())
        return User(**m)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.user_delete(self.id_)


class UsersController(RestBase):
    """Users controller"""
    __resource__ = UserController

    @wsme_pecan.wsexpose([User], unicode)
    def get_all(self):
        criterion = {}

        if 'customer_id' in request.context:
            criterion['customer_id'] = request.context['customer_id']

        users = request.storage_conn.user_list(
            request.context['merchant_id'],
            criterion=criterion)

        return [User(**o) for o in users]

    @wsme_pecan.wsexpose(User, body=User)
    def post(self, body):
        user = request.storage_conn.user_add(body.as_dict())
        return User(**user)


class CustomerController(RestBase):
    """Customer controller"""
    __id__ = 'customer'
    __resource__ = {
        "users": UsersController
    }

    @wsme_pecan.wsexpose(Customer, unicode)
    def get_all(self):
        customer = request.storage_conn.customer_get(self.id_)
        return Customer(**dict(customer))

    @wsme_pecan.wsexpose(Customer, body=Customer)
    def put(self, body):
        m = request.storage_conn.customer_update(self.id_, body.as_dict())
        return Customer(**m)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.customer_delete(self.id_)


class CustomersController(RestBase):
    """Customers controller"""
    __resource__ = CustomerController

    @wsme_pecan.wsexpose([Customer])
    def get_all(self):
        customers = request.storage_conn.customer_list(
            criterion={"merchant_id": self.parent.id_})
        return [Customer(**o) for o in customers]

    @wsme_pecan.wsexpose(Customer, body=Customer)
    def post(self, body):
        customer = request.storage_conn.customer_add(
            request.context['merchant_id'],
            body.as_dict())
        return Customer(**customer)


class MerchantController(RestBase):
    __id__ = 'merchant'
    __resource__ = {
        "customers": CustomersController,
        "users": UsersController
    }

    @wsme_pecan.wsexpose(Merchant)
    def get_all(self):
        m = request.storage_conn.merchant_get(self.id_)
        return Merchant(**dict(m))

    @wsme_pecan.wsexpose(Merchant, body=Merchant)
    def put(self, body):
        m = request.storage_conn.merchant_update(self.id_, body.as_dict())
        return Merchant(**m)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.merchant_delete(self.id_)


class MerchantsController(RestBase):
    """Merchants controller"""
    __resource__ = MerchantController

    @wsme_pecan.wsexpose([Merchant])
    def get_all(self):
        return [Merchant(**o) for o in request.storage_conn.merchant_list()]

    @wsme_pecan.wsexpose(Merchant, body=Merchant)
    def post(self, body):
        merchant = request.storage_conn.merchant_add(body.as_dict())
        return Merchant(**merchant)


class V1Controller(object):
    """Version 1 API controller."""

    currencies = CurrenciesController()
    languages = LanguagesController()

    merchants = MerchantsController()
    users = UsersController()
