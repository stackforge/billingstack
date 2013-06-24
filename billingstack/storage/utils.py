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


from oslo.config import cfg
from billingstack.openstack.common import importutils


def get_engine(service_name, driver_name):
    """
    Return the engine class from the provided engine name
    """
    path = 'billingstack.%s.storage.StorageEngine' % service_name
    base = importutils.import_object(path)
    return base.get_plugin(driver_name, invoke_on_load=True)


def get_connection(service_name, driver_name=None):
    """
    Return a instance of a storage connection
    """
    driver_name = driver_name or \
        cfg.CONF['service:%s' % service_name].storage_driver
    engine = get_engine(service_name, driver_name)
    return engine.get_connection()
