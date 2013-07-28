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
from billingstack.openstack.common import log
from billingstack.api.v2.controllers.currency import CurrenciesController
from billingstack.api.v2.controllers.language import LanguagesController
from billingstack.api.v2.controllers.merchant import MerchantsController
from billingstack.api.v2.controllers.invoice_state import \
    InvoiceStatesController
from billingstack.api.v2.controllers.payment import PGProviders


LOG = log.getLogger(__name__)


class V2Controller(object):
    # Central
    currencies = CurrenciesController()
    languages = LanguagesController()
    merchants = MerchantsController()

    # Biller
    invoice_states = InvoiceStatesController()

    # Collector
    payment_gateway_providers = PGProviders()


class RootController(object):
    v2 = V2Controller()
