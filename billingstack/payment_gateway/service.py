"""
A service that does calls towards the PGP web endpoint or so
"""

import functools
from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.central.rpcapi import CentralAPI
from billingstack.payment_gateway import get_provider
from billingstack import exceptions


cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('payment_topic', 'billingstack.payment_gateway.rpcapi')
cfg.CONF.import_opt('state_path', 'billingstack.paths')


LOG = logging.getLogger(__name__)


central_api = CentralAPI()


class Service(rpc_service.Service):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.payment_topic
        )

        super(Service, self).__init__(*args, **kwargs)

    def get_pg_provider(self, ctxt, pg_config):
        """
        Work out a PGP from PGC.

        :param ctxt: Request context.
        :param pg_info: Payment Gateway Config...
        """
        try:
            name = pg_config['name']
        except KeyError:
            msg = 'Missing name in config'
            LOG.error(msg)
            raise exceptions.ConfigurationError(msg)

        provider = get_provider(name)
        return provider(pg_config)

    def create_account(self, ctxt, pg_config, values):
        """
        Create an Account on the underlying Provider. (Typically a Customer)

        :param ctxt: Request context.
        :param values: The account values.
        """
        provider = self.get_pg_provider(pg_config)
        account = provider.create_account(values)

    def create_payment_method(self, ctxt, pg_config, values):
        """
        Create a PaymentMethod.

        :param ctxt: Request context.
        :param values: The account values.
        """
        provider = self.get_pg_provider(pg_config)
        method = provider.create_payment_method(values)

    def create_transaction(self, ctxt, pg_config, values):
        """
        Create a Transaction.

        :param ctxt: Request context.
        :param values: The Transaction values.
        """
        provider = self.get_pg_provider(pg_config)
        transaction = provider.create_transaction(values)