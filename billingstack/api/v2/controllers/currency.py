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


class CurrencyController(RestController):
    def __init__(self, id_):
        self.id_ = id_

    @wsme_pecan.wsexpose(models.Currency)
    def get_all(self):
        row = central_api.get_currency(request.ctxt, self.id_)

        return models.Currency.from_db(row)

    @wsme.validate(models.Currency)
    @wsme_pecan.wsexpose(models.Currency, body=models.Currency)
    def patch(self, body):
        row = central_api.update_currency(request.ctxt, self.id_, body.to_db())
        return models.Currency.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        central_api.delete_currency(request.ctxt, self.id_)


class CurrenciesController(RestController):
    @expose()
    def _lookup(self, currency_id, *remainder):
        return CurrencyController(currency_id), remainder

    @wsme.validate(models.Currency)
    @wsme_pecan.wsexpose(models.Currency, body=models.Currency,
                         status_code=202)
    def post(self, body):
        row = central_api.create_currency(request.ctxt, body.to_db())

        return models.Currency.from_db(row)

    @wsme_pecan.wsexpose([models.Currency], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(q)

        rows = central_api.list_currencies(
            request.ctxt, criterion=criterion)

        return map(models.Currency.from_db, rows)
