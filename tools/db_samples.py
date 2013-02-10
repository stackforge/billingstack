#!/usr/bin/env python

import sys

from billingstack.openstack.common import cfg
from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.storage import get_connection
from billingstack.storage.impl_sqlalchemy import models


cfg.CONF.import_opt('storage_driver', 'billingstack.api',
                    group='service:api')

cfg.CONF.import_opt('database_connection', 'billingstack.storage.impl_sqlalchemy',
                    group='storage:sqlalchemy')


if __name__ == '__main__':
    service.prepare_service(sys.argv)
    conn = get_connection()
    import ipdb
    ipdb.set_trace()
