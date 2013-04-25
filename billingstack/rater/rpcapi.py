from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('rater_topic', default='rater',
               help='the topic rater nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class RaterAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(RaterAPI, self).__init__(
            topic=cfg.CONF.rater_topic,
            default_version=self.BASE_RPC_VERSION)

    # Subscriptions
    def create_usage(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_usage', values=values))

    def list_usages(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_usages',
                         criterion=criterion))

    def get_usage(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_usage', id_=id_))

    def update_usage(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_usage', id_=id_,
                         values=values))

    def delete_usage(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_usage', id_=id_))


rater_api = RaterAPI()
