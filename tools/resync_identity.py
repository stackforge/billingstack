#!/usr/bin/env python

import sys

from oslo.config import cfg

from billingstack.openstack.common import log as logging

from billingstack import service
from billingstack.identity.base import IdentityPlugin


LOG = logging.getLogger(__name__)


cfg.CONF.import_opt('storage_driver', 'billingstack.identity.api',
                    group='service:identity_api')

cfg.CONF.import_opt('state_path', 'billingstack.paths')

cfg.CONF.import_opt('database_connection',
                    'billingstack.identity.impl_sqlalchemy',
                    group='identity:sqlalchemy')


if __name__ == '__main__':
    service.prepare_service(sys.argv)
    plugin = IdentityPlugin.get_plugin()()

    LOG.info("Re-Syncing database")
    plugin.teardown_schema()
    plugin.setup_schema()
