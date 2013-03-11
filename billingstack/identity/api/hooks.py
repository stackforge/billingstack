from pecan import hooks
from oslo.config import cfg

from billingstack.identity.base import IdentityPlugin


class DBHook(hooks.PecanHook):
    def before(self, state):
        plugin = IdentityPlugin.get_plugin(
            cfg.CONF['service:identity_api'].storage_driver)
        state.request.storage_conn = plugin()
