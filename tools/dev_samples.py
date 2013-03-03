#!/usr/bin/env python

import sys

from oslo.config import cfg

from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.samples import get_samples
from billingstack.storage import get_connection
from billingstack.openstack.common.context import get_admin_context
from billingstack.storage.impl_sqlalchemy import models


cfg.CONF.import_opt('storage_driver', 'billingstack.central',
                    group='service:central')

cfg.CONF.import_opt('database_connection', 'billingstack.storage.impl_sqlalchemy',
                    group='storage:sqlalchemy')


SAMPLES = get_samples()


def get_fixture(name, fixture=0, values={}):
    f = SAMPLES[name][fixture].copy()
    f.update(values)
    return f


if __name__ == '__main__':
    service.prepare_service(sys.argv)
    conn = get_connection()

    samples = get_samples()

    ctxt = get_admin_context()

    currencies = {}
    for c in samples['currency']:
        print "ADDING", c
        currencies[c['name']] = conn.currency_add(ctxt, c)

    languages = {}
    for l in samples['language']:
        languages[l['name']] = conn.language_add(ctxt, l)

    for method in samples['pg_method']:
        conn.pg_method_add(ctxt, method)

    country_data = {
        "currency_id": currencies['nok']['id'],
        "language_id": languages['nor']['id']}

    merchant = conn.merchant_add(
        ctxt, get_fixture('merchant', values=country_data))

    customer = conn.customer_add(
        ctxt, merchant['id'], get_fixture('customer', values=country_data))

    contact_info = get_fixture('contact_info')

    merchant_user = get_fixture('user')
    merchant_user['username'] = 'demo_merchant'
    merchant_user['contact_info'] = contact_info

    merchant_user = conn.user_add(
        ctxt, merchant['id'], merchant_user)

    customer_user = get_fixture('user')
    customer_user['username'] = 'demo_customer'
    customer_user['contact_info'] = contact_info
    customer_user['customer_id'] = customer['id']

    customer_user = conn.user_add(
        ctxt,
        merchant['id'],
        customer_user)
