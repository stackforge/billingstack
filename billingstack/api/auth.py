from oslo.config import cfg

from pecan import hooks

from billingstack.openstack.common.context import RequestContext


class AutherHook(hooks.PecanHook):
    def before(self, state):
        state.request.ctxt = RequestContext(is_admin=True)
