# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Woorea Solutions, S.L
#
# Author: Luis Gervaso <luis@woorea.es>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import datetime

import flask

from billingstack.openstack.common import log
from billingstack.openstack.common import timeutils

from billingstack import storage


LOG = log.getLogger(__name__)


blueprint = flask.Blueprint('v1', __name__,
                            template_folder='templates',
                            static_folder='static')


def request_wants_html():
    best = flask.request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'text/html' and \
        flask.request.accept_mimetypes[best] > \
        flask.request.accept_mimetypes['application/json']


def _get_metaquery(args):
    return dict((k, v)
                for (k, v) in args.iteritems()
                if k.startswith('metadata.'))

## APIs for working with meters.


@blueprint.route('/merchants')
def merchants_list():
    """Return a list of merchants.
    """
    rq = flask.request
    merchants = rq.storage_conn.merchants_list()
    return flask.jsonify(meters=list(merchants))


@blueprint.route('/merchants/<merchant_id>')
def show_merchant(merchant_id):
    """Return a merchant by ID

    :param merchant_id: The ID of the resource.
    """
    rq = flask.request
    merchant = rq.storage_conn.merchants_get()
    return flask.jsonify(merchant)

