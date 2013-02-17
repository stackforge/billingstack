from stevedore.extension import ExtensionManager

from billingstack.openstack.common import log
from billingstack.payment_gateway.base import Provider
from billingstack.storage import get_connection


LOG = log.getLogger(__name__)


def _register(ep, conn):
    provider = ep.plugin

    values = provider.values()
    methods = provider.methods()

    conn.pg_provider_register(values, methods=methods)
    LOG.debug("Registered PGP %s with methods %s", values, methods)


def register_providers():
    conn = get_connection()
    em = ExtensionManager(Provider.__plugin_ns__)
    em.map(_register, conn)
