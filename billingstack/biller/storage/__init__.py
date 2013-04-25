from oslo.config import cfg
from billingstack.storage import base


class StorageEngine(base.StorageEngine):
    """Base class for the biller storage"""
    __plugin_ns__ = 'billingstack.biller.storage'


class Connection(base.Connection):
    """Define the base API for biller storage"""


def get_connection():
    name = cfg.CONF['service:biller'].storage_driver
    plugin = StorageEngine.get_plugin(name, invoke_on_load=True)
    return plugin.get_connection()
