from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('central_topic', default='central',
               help='the topic central nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class CentralAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(CentralAPI, self).__init__(
            topic=cfg.CONF.central_topic,
            default_version=self.BASE_RPC_VERSION)

    # Currency
    def create_currency(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_currency', values=values))

    def list_currency(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_currency',
                         criterion=criterion))

    def get_currency(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_currency',
                         id_=id_))

    def update_currency(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_currency',
                         id_=id_, values=values))

    def delete_currency(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_currency',
                         id_=id_))

    # Language
    def create_language(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_language', values=values))

    def list_language(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_language',
                         criterion=criterion))

    def get_language(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_language', id_=id_))

    def update_language(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_language',
                         id_=id_, values=values))

    def delete_language(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_language', id_=id_))

    # Invoice States
    def create_invoice_state(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_invoice_state',
                         values=values))

    def list_invoice_state(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoice_state',
                         criterion=criterion))

    def get_invoice_state(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice_state', id_=id_))

    def update_invoice_state(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoice_state',
                         id_=id_, values=values))

    def delete_invoice_state(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice_state', id_=id_))

    # Contact Info
    def create_contact_info(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('create_contact_info', id_=id_,
                         values=values))

    def get_contact_info(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_contact_info', id_))

    def update_contact_info(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_contact_info', id_=id_,
                         values=values))

    def delete_contact_info(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_contact_info', id_=id_))

    # PGP
    def list_pg_provider(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_provider',
                         criterion=criterion))

    def get_pg_provider(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_provider', id_=id_))

    # PGM
    def list_pg_method(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_method',
                         criterion=criterion))

    def get_pg_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('list_pg_method', id_=id_))

    # PGC
    def create_pg_config(self, ctxt, merchant_id, provider_id, values):
        return self.call(ctxt, self.make_msg('create_pg_config',
                         merchant_id=merchant_id, provider_id=provider_id,
                         values=values))

    def list_pg_config(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_config',
                         criterion=criterion))

    def get_pg_config(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_config', id_=id_))

    def update_pg_config(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_pg_config', id_=id_,
                         values=values))

    def delete_pg_config(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_pg_config', id_=id_))

    # PaymentMethod
    def create_payment_method(self, ctxt, customer_id, pg_method_id, values):
        return self.call(ctxt, self.make_msg('create_payment_method',
                         customer_id=customer_id, pg_method_id=pg_method_id,
                         values=values))

    def list_payment_method(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_payment_method',
                         criterion=criterion))

    def get_payment_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_payment_method', id_=id_))

    def update_payment_method(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_payment_method', id_=id_,
                         values=values))

    def delete_payment_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_payment_method', id_=id_))

    # Merchant
    def create_merchant(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_merchant', values=values))

    def list_merchant(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_merchant',
                         criterion=criterion))

    def get_merchant(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_merchant', id_=id_))

    def update_merchant(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_merchant',
                         id_=id_, values=values))

    def delete_merchant(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_merchant',
                         id_=id_))

    # Customer
    def create_customer(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_customer',
                         merchant_id=merchant_id, values=values))

    def list_customer(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_customer',
                         criterion=criterion))

    def get_customer(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_customer', id_=id_))

    def update_customer(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_customer',
                         id_=id_, values=values))

    def delete_customer(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_customer', id_=id_))

    # Plans
    def create_plan(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_plan',
                         merchant_id=merchant_id, values=values))

    def list_plan(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_plan', criterion=criterion))

    def get_plan(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_plan', id_=id_))

    def update_plan(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_plan', id_=id_,
                         values=values))

    def delete_plan(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_plan', id_=id_))

    # PlanItems
    def create_plan_item(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_plan_item',
                         values=values))

    def list_plan_item(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_plan_item',
                         criterion=criterion))

    def get_plan_item(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_plan_item', id_=id_))

    def update_plan_item(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_plan_item', id_=id_,
                         values=values))

    def delete_plan_item(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_plan_item', id_=id_))

    # Products
    def create_product(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_product',
                         merchant_id=merchant_id, values=values))

    def list_product(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_product',
                         criterion=criterion))

    def get_product(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_product', id_=id_))

    def update_product(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_product', id_=id_,
                         values=values))

    def delete_product(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_product', id_=id_))

    # Invoices
    def create_invoice(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_invoice',
                         merchant_id=merchant_id, values=values))

    def list_invoice(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoice',
                         criterion=criterion))

    def get_invoice(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice', id_=id_))

    def update_invoice(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoicet', id_=id_,
                         values=values))

    def delete_invoice(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice', id_=id_))

    # Subscriptions
    def create_subscription(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_subscription',
                         merchant_id=merchant_id, values=values))

    def list_subscription(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_subscription',
                         criterion=criterion))

    def get_subscription(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_subscription', id_=id_))

    def update_subscription(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_subscriptiont', id_=id_,
                         values=values))

    def delete_subscription(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_subscription', id_=id_))
