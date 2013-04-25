from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('collector_topic', default='collector',
               help='the topic collector nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class CollectorAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(CollectorAPI, self).__init__(
            topic=cfg.CONF.collector_topic,
            default_version=self.BASE_RPC_VERSION)


collector_api = CollectorAPI()
