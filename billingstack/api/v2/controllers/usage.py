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
from billingstack.rater.rpcapi import rater_api


class UsageController(RestController):
    def __init__(self, id_):
        self.id_ = id_
        request.context['usage_id'] = id_

    @wsme_pecan.wsexpose(models.Usage)
    def get_all(self):
        row = rater_api.get_usage(request.ctxt, self.id_)

        return models.Usage.from_db(row)

    @wsme.validate(models.Usage)
    @wsme_pecan.wsexpose(models.Usage, body=models.Usage)
    def patch(self, body):
        row = rater_api.update_usage(request.ctxt, self.id_, body.to_db())

        return models.Usage.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        rater_api.delete_usage(request.ctxt, self.id_)


class UsagesController(RestController):
    @expose()
    def _lookup(self, usage_id, *remainder):
        return UsageController(usage_id), remainder

    @wsme.validate(models.Usage)
    @wsme_pecan.wsexpose(models.Usage, body=models.Usage, status_code=202)
    def post(self, body):
        row = rater_api.create_usage(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.Usage.from_db(row)

    @wsme_pecan.wsexpose([models.Usage], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(
            q,
            merchant_id=request.context['merchant_id'])

        rows = rater_api.list_usages(
            request.ctxt, criterion=criterion)

        return map(models.Usage.from_db, rows)
