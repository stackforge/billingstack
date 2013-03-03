from pecan import hooks

from oslo.config import cfg
from billingstack import storage
from billingstack.central.rpcapi import CentralAPI
from billingstack.openstack.common import log


class ConfigHook(hooks.PecanHook):
    """Attach the configuration object to the request
    so controllers can get to it.
    """

    def before(self, state):
        state.request.cfg = cfg.CONF


class DBHook(hooks.PecanHook):

    def before(self, state):
        storage_engine = storage.get_engine(
            state.request.cfg['service:api'].storage_driver)
        state.request.storage_engine = storage_engine
        state.request.storage_conn = storage_engine.get_connection()

    # def after(self, state):
    #     print 'method:', state.request.method
    #     print 'response:', state.response.status


class RPCHook(hooks.PecanHook):
    def before(self, state):
        state.request.central_api = CentralAPI()
