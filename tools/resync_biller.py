#!/usr/bin/env python

import sys

from oslo.config import cfg

from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.biller.storage import get_connection


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('storage_driver', 'billingstack.biller.storage',
                    group='service:biller')

cfg.CONF.import_opt('state_path', 'billingstack.paths')

cfg.CONF.import_opt('database_connection',
                    'billingstack.biller.storage.impl_sqlalchemy',
                    group='biller:sqlalchemy')


if __name__ == '__main__':
    service.prepare_service(sys.argv)
    connection = get_connection()

    LOG.info("Re-Syncing database")
    connection.teardown_schema()
    connection.setup_schema()
