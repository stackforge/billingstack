#!/usr/bin/env python

import sys

from oslo.config import cfg

from billingstack.openstack.common import log as logging
from billingstack import service
from billingstack.storage.utils import get_connection

# NOTE: make this based on entrypoints ?
SERVICES = ['biller', 'central', 'rater']

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('state_path', 'billingstack.paths')

cfg.CONF.register_cli_opt(cfg.StrOpt('services', default=SERVICES))
cfg.CONF.register_cli_opt(cfg.BoolOpt('resync', default=False))


def import_service_opts(service):
    cfg.CONF.import_opt('storage_driver', 'billingstack.%s.storage' % service,
                        group='service:%s' % service)
    cfg.CONF.import_opt('database_connection',
                        'billingstack.%s.storage.impl_sqlalchemy' % service,
                        group='%s:sqlalchemy' % service)


def resync_service_storage(service, resync=False):
    """
    Resync the storage for a service
    """
    connection = get_connection(service)
    if resync:
        connection.teardown_schema()
    connection.setup_schema()


if __name__ == '__main__':
    service.prepare_service(sys.argv)

    try:
        services = cfg.CONF.services
        for svc in services:
            import_service_opts(svc)
    except Exception:
        LOG.error('Error importing service options for %s, will exit' % svc)
        sys.exit(0)

    for svc in services:
        LOG.info("Doing storage for %s" % svc)
        resync_service_storage(svc)
