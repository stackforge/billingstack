#!/usr/bin/env python

import sys

from billingstack.openstack.common import cfg
from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.samples import get_samples
from billingstack.storage import get_connection
from billingstack.storage.impl_sqlalchemy import models


cfg.CONF.import_opt('storage_driver', 'billingstack.api',
                    group='service:api')

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

    currencies = {}
    for c in samples['currency']:
        print "ADDING", c
        currencies[c['letter']] = conn.currency_add(c)

    languages = {}
    for l in samples['language']:
        languages[l['letter']] = conn.language_add(l)

    merchant = samples['merchant'][0].copy()
    merchant['currency_id'] = currencies['nok']['id']
    merchant['language_id'] = languages['nor']['id']

    country_data = {
        "currency_id": currencies['nok']['id'],
        "language_id": languages['nor']['id']}

    merchant = conn.merchant_add(
        get_fixture('merchant', values=country_data))

    customer = conn.customer_add(
        merchant['id'], get_fixture('customer', values=country_data))

    contact_info = get_fixture('contact_info')
    merchant_user = get_fixture('user')
    merchant_user['username'] = 'demo_merchant'

    merchant_user = conn.user_add(
        merchant['id'], merchant_user, contact_info=contact_info)

    customer_user = get_fixture('user')
    customer_user['username'] = 'demo_customer'

    customer_user = conn.user_add(
        merchant['id'],
        customer_user,
        contact_info=contact_info,
        customer_id=customer['id'])
