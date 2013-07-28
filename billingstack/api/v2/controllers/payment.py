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


class PGProviders(RestController):
    @wsme_pecan.wsexpose([models.PGProvider], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(q)

        rows = central_api.list_pg_providers(
            request.ctxt, criterion=criterion)

        return map(models.PGProvider.from_db, rows)


class PGConfigController(RestController):
    def __init__(self, id_):
        self.id_ = id_

    @wsme_pecan.wsexpose(models.PGConfig)
    def get_all(self):
        row = central_api.get_pg_config(request.ctxt, self.id_)

        return models.PGConfig.from_db(row)

    @wsme.validate(models.PGConfig)
    @wsme_pecan.wsexpose(models.PGConfig, body=models.PGConfig)
    def patch(self, body):
        row = central_api.update_pg_config(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.PGConfig.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        central_api.delete_pg_config(request.ctxt, self.id_)


class PGConfigsController(RestController):
    @expose()
    def _lookup(self, method_id, *remainder):
        return PGConfigController(method_id), remainder

    @wsme.validate(models.PGConfig)
    @wsme_pecan.wsexpose(models.PGConfig, body=models.PGConfig,
                         status_code=202)
    def post(self, body):
        row = central_api.create_pg_config(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.PGConfig.from_db(row)

    @wsme_pecan.wsexpose([models.PGConfig], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(
            q, merchant_id=request.context['merchant_id'])

        rows = central_api.list_pg_configs(
            request.ctxt, criterion=criterion)

        return map(models.PGConfig.from_db, rows)


class PaymentMethodController(RestController):
    def __init__(self, id_):
        self.id_ = id_
        request.context['payment_method_id'] = id_

    @wsme_pecan.wsexpose(models.PaymentMethod)
    def get_all(self):
        row = central_api.get_payment_method(request.ctxt, self.id_)

        return models.PaymentMethod.from_db(row)

    @wsme.validate(models.PaymentMethod)
    @wsme_pecan.wsexpose(models.PaymentMethod, body=models.PaymentMethod)
    def patch(self, body):
        row = central_api.update_payment_method(
            request.ctxt,
            self.id_,
            body.to_db())

        return models.PaymentMethod.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        central_api.delete_payment_method(request.ctxt, self.id_)


class PaymentMethodsController(RestController):
    @expose()
    def _lookup(self, method_id, *remainder):
        return PaymentMethodController(method_id), remainder

    @wsme.validate(models.PaymentMethod)
    @wsme_pecan.wsexpose(models.PaymentMethod, body=models.PaymentMethod,
                         status_code=202)
    def post(self, body):
        row = central_api.create_payment_method(
            request.ctxt,
            request.context['customer_id'],
            body.to_db())

        return models.PaymentMethod.from_db(row)

    @wsme_pecan.wsexpose([models.PaymentMethod], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(
            q, merchant_id=request.context['merchant_id'],
            customer_id=request.context['customer_id'])

        rows = central_api.list_payment_methods(
            request.ctxt, criterion=criterion)

        return map(models.PaymentMethod.from_db, rows)
