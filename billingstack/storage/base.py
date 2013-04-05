# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
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
#
# Copied: Moniker
from billingstack.plugin import Plugin


class StorageEngine(Plugin):
    """ Base class for storage engines """

    __plugin_ns__ = 'billingstack.storage'
    __plugin_type__ = 'storage'

    def get_connection(self):
        """
        Return a Connection instance based on the configuration settings.
        """
        raise NotImplementedError


class Connection(object):
    """
    A Connection
    """
    def ping(self, context):
        """ Ping the Storage connection """
        return {
            'status': None
        }
