from oslo.config import cfg
from billingstack.storage import base


class StorageEngine(base.StorageEngine):
    """Base class for the rater storage"""
    __plugin_ns__ = 'billingstack.rater.storage'


class Connection(base.Connection):
    """Define the base API for rater storage"""
    def create_usage(self, ctxt, values):
        raise NotImplementedError

    def list_usages(self, ctxt, **kw):
        raise NotImplementedError

    def get_usage(self, ctxt, id_):
        raise NotImplementedError

    def update_usage(self, ctxt, id_, values):
        raise NotImplementedError

    def delete_usage(self, ctxt, id_):
        raise NotImplementedError


def get_connection():
    name = cfg.CONF['service:rater'].storage_driver
    plugin = StorageEngine.get_plugin(name, invoke_on_load=True)
    return plugin.get_connection()
