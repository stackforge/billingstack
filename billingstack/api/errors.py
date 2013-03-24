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
import flask
import webob.dec
from billingstack import exceptions
from billingstack import wsgi
from billingstack.openstack.common.rpc import common as rpc_common
from billingstack.openstack.common import log
from billingstack.openstack.common import jsonutils as json

LOG = log.getLogger(__name__)


class FaultWrapperMiddleware(wsgi.Middleware):
    @webob.dec.wsgify
    def __call__(self, request):
        try:
            return request.get_response(self.application)
        except exceptions.Base, e:
            # Handle Moniker Exceptions
            status = e.error_code if hasattr(e, 'error_code') else 500

            # Start building up a response
            response = {
                'code': status
            }

            if hasattr(e, 'error_type'):
                response['type'] = e.error_type

            if hasattr(e, 'errors'):
                response['errors'] = e.errors

            response['message'] = e.get_message()

            return self._handle_exception(request, e, status, response)
        except rpc_common.Timeout, e:
            # Special case for RPC timeout's
            response = {
                'code': 504,
                'type': 'timeout',
            }

            return self._handle_exception(request, e, 504, response)
        except Exception, e:
            # Handle all other exception types
            return self._handle_exception(request, e)

    def _handle_exception(self, request, e, status=500, response={}):
        # Log the exception ASAP
        LOG.exception(e)

        headers = [
            ('Content-Type', 'application/json'),
        ]

        # Set a response code, if one is missing.
        if 'code' not in response:
            response['code'] = status

        # TODO(kiall): Send a fault notification

        # Return the new response
        return flask.Response(status=status, headers=headers,
                              response=json.dumps(response))
