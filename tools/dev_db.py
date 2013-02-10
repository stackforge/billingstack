#!/usr/bin/env python

import sys

from billingstack.openstack.common import cfg
from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.storage import get_connection


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('storage_driver', 'billingstack.api',
                    group='service:api')

cfg.CONF.import_opt('database_connection', 'billingstack.storage.impl_sqlalchemy',
                    group='storage:sqlalchemy')


if __name__ == '__main__':
    service.prepare_service(sys.argv)
    conn = get_connection()

    LOG.info("Re-Syncing database")
    conn.teardown_schema()
    conn.setup_schema()
