import functools
from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack import storage


cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('central_topic', 'billingstack.central.rpcapi')

LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.central_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

        # Get a storage connection
        self.storage_conn = storage.get_connection()

    def __getattr__(self, name):
        """
        Proxy onto the storage api if there is no local method present..

        For now to avoid to have to write up every method once more here...
        """
        if hasattr(self, name):
            return getattr(self, name)

        f = getattr(self.storage_conn, name)
        if not f:
            raise AttributeError

        @functools.wraps(f)
        def _wrapper(*args, **kw):
            return f(*args, **kw)
        setattr(self, name, _wrapper)
        return _wrapper
