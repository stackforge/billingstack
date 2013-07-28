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
from billingstack.biller.rpcapi import biller_api


class InvoiceStateController(RestController):
    def __init__(self, id_):
        self.id_ = id_

    @wsme_pecan.wsexpose(models.InvoiceState)
    def get_all(self):
        row = biller_api.get_invoice_state(request.ctxt, self.id_)

        return models.InvoiceState.from_db(row)

    @wsme.validate(models.InvoiceState)
    @wsme_pecan.wsexpose(models.InvoiceState, body=models.InvoiceState)
    def patch(self, body):
        row = biller_api.update_invoice_state(
            request.ctxt, self.id_, body.to_db())
        return models.InvoiceState.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        biller_api.delete_invoice_state(request.ctxt, self.id_)


class InvoiceStatesController(RestController):
    @expose()
    def _lookup(self, invoice_state_id, *remainder):
        return InvoiceStateController(invoice_state_id), remainder

    @wsme.validate(models.InvoiceState)
    @wsme_pecan.wsexpose(models.InvoiceState, body=models.InvoiceState,
                         status_code=202)
    def post(self, body):
        row = biller_api.create_invoice_state(request.ctxt, body.to_db())

        return models.InvoiceState.from_db(row)

    @wsme_pecan.wsexpose([models.InvoiceState], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(q)

        rows = biller_api.list_invoice_states(
            request.ctxt, criterion=criterion)

        return map(models.InvoiceState.from_db, rows)
