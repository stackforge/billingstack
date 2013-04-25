from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.biller import storage


cfg.CONF.import_opt('biller_topic', 'billingstack.biller.rpcapi')
cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('state_path', 'billingstack.paths')

LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    """
    Biller service
    """
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.biller_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

    def start(self):
        self.storage_conn = storage.get_connection()
        super(Service, self).start()
