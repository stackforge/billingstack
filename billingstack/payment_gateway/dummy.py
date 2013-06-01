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
from billingstack.payment_gateway.base import Provider


class DummyProvider(Provider):
    """
    A Stupid Provider that does nothing
    """
    __plugin_name__ = 'dummy'
    __title__ = 'Dummy Provider'
    __description__ = 'Noop Dummy'

    @classmethod
    def methods(cls):
        return [
            {"name": "visa", "type": "creditcard"}]

    @classmethod
    def properties(cls):
        return {"enabled": 0}
