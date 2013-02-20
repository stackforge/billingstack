from stevedore.extension import ExtensionManager

from billingstack import exceptions
from billingstack.openstack.common import log
from billingstack.payment_gateway.base import Provider
from billingstack.storage import get_connection


LOG = log.getLogger(__name__)


def _register(ep, conn):
    provider = ep.plugin

    values = provider.values()

    LOG.debug("Attempting registration of PGP %s" % ep.plugin.get_plugin_name())
    try:
        methods = provider.methods()
    except NotImplementedError:
        msg = "PaymentGatewayProvider %s doesn't provide any methods - Skipped"
        LOG.warn(msg, provider.get_plugin_name())
        return

    try:
        conn.pg_provider_register(values, methods=methods)
    except exceptions.ConfigurationError, e:
        return

    LOG.debug("Registered PGP %s with methods %s", values, methods)


def register_providers():
    conn = get_connection()
    em = ExtensionManager(Provider.__plugin_ns__)
    em.map(_register, conn)
