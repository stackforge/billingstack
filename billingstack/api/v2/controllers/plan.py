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


class ItemController(RestController):
    def __init__(self, id_):
        self.id_ = id_

    @wsme.validate(models.PlanItem)
    @wsme_pecan.wsexpose(models.PlanItem, body=models.PlanItem)
    def put(self, body):
        values = {
            'plan_id': request.context['plan_id'],
            'product_id': self.id_
        }

        row = central_api.create_plan_item(request.ctxt, values)

        return models.PlanItem.from_db(row)

    @wsme.validate(models.PlanItem)
    @wsme_pecan.wsexpose(models.PlanItem, body=models.PlanItem)
    def patch(self, body):
        row = central_api.update_plan_item(
            request.ctxt,
            request.context['plan_id'],
            self.id_,
            body.to_db())

        return models.PlanItem.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self, id_):
        central_api.delete_plan_item(
            request.ctxt,
            request.context['plan_id'],
            id_)


class ItemsController(RestController):
    @expose()
    def _lookup(self, id_, *remainder):
        return ItemController(id_), remainder


class PlanController(RestController):
    items = ItemsController()

    def __init__(self, id_):
        self.id_ = id_
        request.context['plan_id'] = id_

    @wsme_pecan.wsexpose(models.Plan)
    def get_all(self):
        row = central_api.get_plan(request.ctxt, self.id_)

        return models.Plan.from_db(row)

    @wsme.validate(models.Plan)
    @wsme_pecan.wsexpose(models.Plan, body=models.Plan)
    def patch(self, body):
        row = central_api.update_plan(request.ctxt, self.id_, body.to_db())

        return models.Plan.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        central_api.delete_plan(request.ctxt, self.id_)


class PlansController(RestController):
    @expose()
    def _lookup(self, plan_id, *remainder):
        return PlanController(plan_id), remainder

    @wsme.validate(models.Plan)
    @wsme_pecan.wsexpose(models.Plan, body=models.Plan, status_code=202)
    def post(self, body):
        row = central_api.create_plan(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.Plan.from_db(row)

    @wsme_pecan.wsexpose([models.Plan], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(
            q,
            merchant_id=request.context['merchant_id'])

        rows = central_api.list_plans(
            request.ctxt, criterion=criterion)

        return map(models.Plan.from_db, rows)
