from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('biller_topic', default='biller',
               help='the topic biller nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class BillerAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(BillerAPI, self).__init__(
            topic=cfg.CONF.biller_topic,
            default_version=self.BASE_RPC_VERSION)


biller_api = BillerAPI()
