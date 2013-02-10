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

from pecan import request
from pecan.rest import RestController

import wsmeext.pecan as wsme_pecan
from wsme.types import Base, text


class Base(Base):
    id = text


class Currency(Base):
    id = text
    letter = text
    name = text


class Language(Base):
    id = text
    letter = text
    name = text


class User(Base):
    pass


class Account(Base):
    currency_id = text
    language_id = text

    name = text


class Merchant(Account):
    pass


class Customer(Account):
    merchant_id = text


class CurrenciesController(RestController):
    @wsme_pecan.wsexpose([Currency], unicode)
    def get_all(self):
        return [Currency(**o) for o in request.storage_conn.currency_list()]


class LanguagesController(RestController):
    @wsme_pecan.wsexpose([Language], unicode)
    def get_all(self):
        return [Language(**o) for o in request.storage_conn.language_list()]


class UsersController(RestController):

    @wsme_pecan.wsexpose([User], unicode)
    def get_all(self):
        return [User(**o) for o in request.storage_conn.user_list()]

    @wsme_pecan.wsexpose(User, unicode)
    def get_one(self):
        return User(*dict(id=1))


class MerchantsController(RestController):
    """Merchants controller"""

    users = UsersController()

    @wsme_pecan.wsexpose([Merchant], unicode)
    def get_all(self):
        return [Merchant(**o) for o in request.storage_conn.merchant_list()]

    @wsme_pecan.wsexpose(Merchant, unicode)
    def get_one(self, merchant_id):
        """Get merchant details

        :param merchant_id: The UUID of the merchant
        """
        m = request.storage_conn.merchant_get(merchant_id)
        return Merchant(**dict(m))


class CustomersController(RestController):
    """Merchants controller"""

    @wsme_pecan.wsexpose([Customer], unicode)
    def get_all(self):
        return [Customer(**o) for o in request.storage_conn.customer_list()]

    @wsme_pecan.wsexpose(Customer, unicode)
    def get_one(self, merchant_id):
        """Get customer details

        :param customer_id: The UUID of the customer
        """
        m = request.storage_conn.merchant_get(customer_id)
        return Customer(**dict(m))


class V1Controller(object):
    """Version 1 API controller."""

    currencies = CurrenciesController()
    languages = LanguagesController()

    users = UsersController()
    merchants = MerchantsController()
    customers = CustomersController()
