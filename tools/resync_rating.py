#!/usr/bin/env python

import sys

from oslo.config import cfg

from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.rating.storage import get_connection


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('storage_driver', 'billingstack.rating.storage',
                    group='service:rating')

cfg.CONF.import_opt('state_path', 'billingstack.paths')

cfg.CONF.import_opt('database_connection',
                    'billingstack.rating.storage.impl_sqlalchemy',
                    group='rating:sqlalchemy')


if __name__ == '__main__':
    service.prepare_service(sys.argv)
    connection = get_connection()

    LOG.info("Re-Syncing database")
    connection.teardown_schema()
    connection.setup_schema()
