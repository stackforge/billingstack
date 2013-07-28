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


class SubscriptionController(RestController):
    def __init__(self, id_):
        self.id_ = id_
        request.context['subscription_id'] = id_

    @wsme_pecan.wsexpose(models.Subscription)
    def get_all(self):
        row = central_api.get_subscription(request.ctxt, self.id_)

        return models.Subscription.from_db(row)

    @wsme.validate(models.Subscription)
    @wsme_pecan.wsexpose(models.Subscription, body=models.Subscription)
    def patch(self, body):
        row = central_api.update_subscription(request.ctxt, self.id_,
                                              body.to_db())

        return models.Subscription.from_db(row)

    @wsme_pecan.wsexpose(None, status_code=204)
    def delete(self):
        central_api.delete_subscription(request.ctxt, self.id_)


class SubscriptionsController(RestController):
    @expose()
    def _lookup(self, subscription_id, *remainder):
        return SubscriptionController(subscription_id), remainder

    @wsme.validate(models.Subscription)
    @wsme_pecan.wsexpose(models.Subscription, body=models.Subscription,
                         status_code=202)
    def post(self, body):
        row = central_api.create_subscription(
            request.ctxt,
            request.context['merchant_id'],
            body.to_db())

        return models.Subscription.from_db(row)

    @wsme_pecan.wsexpose([models.Subscription], [Query])
    def get_all(self, q=[]):
        criterion = _query_to_criterion(
            q,
            merchant_id=request.context['merchant_id'])

        rows = central_api.list_subscriptions(
            request.ctxt, criterion=criterion)

        return map(models.Subscription.from_db, rows)
