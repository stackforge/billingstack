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
from billingstack.storage import base


class StorageEngine(base.StorageEngine):
    """Base class for the rater storage"""
    __plugin_ns__ = 'billingstack.rater.storage'


class Connection(base.Connection):
    """Define the base API for rater storage"""
    def create_usage(self, ctxt, values):
        raise NotImplementedError

    def list_usages(self, ctxt, **kw):
        raise NotImplementedError

    def get_usage(self, ctxt, id_):
        raise NotImplementedError

    def update_usage(self, ctxt, id_, values):
        raise NotImplementedError

    def delete_usage(self, ctxt, id_):
        raise NotImplementedError
