#!/usr/bin/env python

import sys

from oslo.config import cfg

from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.storage import get_connection


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('storage_driver', 'billingstack.central',
                    group='service:central')


cfg.CONF.import_opt('state_path', 'billingstack.paths')


cfg.CONF.import_opt('database_connection',
                    'billingstack.storage.impl_sqlalchemy',
                    group='storage:sqlalchemy')

if __name__ == '__main__':
    service.prepare_service(sys.argv)
    conn = get_connection()

    LOG.info("Re-Syncing database")
    conn.teardown_schema()
    conn.setup_schema()
