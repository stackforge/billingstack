from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('payment_topic', default='payment',
               help='the topic payments nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class PaymentAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(PaymentAPI, self).__init__(
            topic=cfg.CONF.payment_topic,
            default_version=self.BASE_RPC_VERSION)

    def _do_call(self, ctxt, msg, async=True):
        """
        Helper for doing RPC calls.
        """
        rpc_func = self.cast if async else self.call
        return rpc_func(ctxt, msg)

    def create_account(self, ctxt, pg_config, values, async=False):
        msg = self.make_msg('create_account', pg_config=pg_config,
                            values=values)
        return self._do_call(ctxt, msg, async=async)

    def create_payment_method(self, ctxt, pg_config, values, async=True):
        msg = self.make_msg('create_payment_method', pg_config=pg_config,
                            values=values)
        return self._do_call(ctxt, msg, async=async)

    def create_tranaction(self, ctxt, pg_config, values, async=True):
        msg = self.make_msg('create_tranaction', pg_config=pg_config,
                            values=values)
        return self._do_call(ctxt, msg, async=async)


payment_api = PaymentAPI()
