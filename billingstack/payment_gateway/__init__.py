from stevedore.extension import ExtensionManager

from billingstack import exceptions
from billingstack.openstack.common import log
from billingstack.payment_gateway.base import Provider
from billingstack.storage import get_connection


LOG = log.getLogger(__name__)


from oslo.config import cfg

cfg.CONF.register_group(cfg.OptGroup(
    name='service:payments', title="Configuration for Payments Service"
))

cfg.CONF.register_opts([
    cfg.IntOpt('workers', default=None,
               help='Number of worker processes to spawn')
], group='service:payments')


def _register(ep, context, conn):
    provider = ep.plugin

    values = provider.values()

    LOG.debug("Attempting registration of PGP %s" %
              ep.plugin.get_plugin_name())
    try:
        methods = provider.methods()
    except NotImplementedError:
        msg = "PaymentGatewayProvider %s doesn't provide any methods - Skipped"
        LOG.warn(msg, provider.get_plugin_name())
        return

    try:
        conn.pg_provider_register(context, values, methods=methods)
    except exceptions.ConfigurationError:
        return

    LOG.debug("Registered PGP %s with methods %s", values, methods)


def register_providers(context):
    conn = get_connection()
    em = ExtensionManager(Provider.__plugin_ns__)
    em.map(_register, context, conn)


def get_provider(name):
    return Provider.get_plugin(name)
