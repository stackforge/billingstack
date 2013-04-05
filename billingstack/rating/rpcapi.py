from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('rating_topic', default='rating',
               help='the topic rating nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class RatingAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(RatingAPI, self).__init__(
            topic=cfg.CONF.rating_topic,
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


rating_api = RatingAPI()
