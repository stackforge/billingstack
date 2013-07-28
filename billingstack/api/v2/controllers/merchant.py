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
from pecan import expose, request
import wsme
import wsmeext.pecan as wsme_pecan


from billingstack.api.base import Query, _query_to_criterion, RestController
from billingstack.api.v2 import models
from billingstack.central.rpcapi import central_api
from billingstack.api.v2.controllers.customer import CustomersController
from billingstack.api.v2.controllers.payment import PGConfigsController
from billingstack.api.v2.controllers.plan import PlansController
from billingstack.api.v2.controllers.product import ProductsController
from billingstack.api.v2.controllers.subscription import \
    SubscriptionsController
from billingstack.api.v2.controllers.invoice import InvoicesController
from billingstack.api.v2.controllers.usage import UsagesController


class MerchantController(RestController):
    customers = CustomersController()
    payment_gateway_configurations = PGConfigsController()
    plans = PlansController()
    products = ProductsController()
    subscriptions = SubscriptionsController()

    invoices = InvoicesController()
    usage = UsagesController()

    def __init__(self, id_):
        self.id_ = id_
        request.context['merchant_id'] = id_

    @wsme_pecan.wsexpose(models.Merchant)
    def get_all(self):
        row = central_api.get_merchant(request.ctxt, self.id_)

        return models.Merchant.from_db(row)

    @wsme.validate(models.InvoiceState)
    @wsme_pecan.wsexpose(models.Merchant, body=models.Merchant)
    def patch(self, body):
        row = central_api.update_merchant(request.ctxt, self.id_, body.to_db())
        return models.Merchant.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        central_api.delete_merchant(request.ctxt, self.id_)


class MerchantsController(RestController):
    @expose()
    def _lookup(self, merchant_id, *remainder):
        return MerchantController(merchant_id), remainder

    @wsme.validate(models.Merchant)
    @wsme_pecan.wsexpose(models.Merchant, body=models.Merchant,
                         status_code=202)
    def post(self, body):
        row = central_api.create_merchant(request.ctxt, body.to_db())

        return models.Merchant.from_db(row)

    @wsme_pecan.wsexpose([models.Merchant], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(q)

        rows = central_api.list_merchants(
            request.ctxt, criterion=criterion)

        return map(models.Merchant.from_db, rows)
