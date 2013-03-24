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

    def list_currencies(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_currencies',
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

    def list_languages(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_languages',
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

    def list_invoice_states(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoice_states',
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
    def list_pg_providers(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_providers',
                         criterion=criterion))

    def get_pg_provider(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_provider', id_=id_))

    # PGM
    def list_pg_methods(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_methods',
                         criterion=criterion))

    def get_pg_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_method', id_=id_))

    def delete_pg_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_pg_method', id_=id_))

    # PGC
    def create_pg_config(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_pg_config',
                         merchant_id=merchant_id, values=values))

    def list_pg_configs(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_configs',
                         criterion=criterion))

    def get_pg_config(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_config', id_=id_))

    def update_pg_config(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_pg_config', id_=id_,
                         values=values))

    def delete_pg_config(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_pg_config', id_=id_))

    # PaymentMethod
    def create_payment_method(self, ctxt, customer_id, values):
        return self.call(ctxt, self.make_msg('create_payment_method',
                         customer_id=customer_id, values=values))

    def list_payment_methods(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_payment_methods',
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

    def list_merchants(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_merchants',
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

    def list_customers(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_customers',
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

    def list_plans(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_plans',
                         criterion=criterion))

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

    def list_plan_items(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_plan_items',
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

    def list_products(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_products',
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

    def list_invoices(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoices',
                         criterion=criterion))

    def get_invoice(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice', id_=id_))

    def update_invoice(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoice', id_=id_,
                         values=values))

    def delete_invoice(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice', id_=id_))

    # Invoice lines
    def create_invoice_line(self, ctxt, invoice_id, values):
        return self.call(ctxt, self.make_msg('create_invoice_line',
                         invoice_id=invoice_id, values=values))

    def list_invoice_lines(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoice_lines',
                         criterion=criterion))

    def get_invoice_line(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice_line', id_=id_))

    def update_invoice_line(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoice_line', id_=id_,
                         values=values))

    def delete_invoice_line(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice_line', id_=id_))

    # Subscriptions
    def create_subscription(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_subscription',
                         values=values))

    def list_subscriptions(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_subscriptions',
                         criterion=criterion))

    def get_subscription(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_subscription', id_=id_))

    def update_subscription(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_subscription', id_=id_,
                         values=values))

    def delete_subscription(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_subscription', id_=id_))

    # Subscriptions
    def create_usage(self, ctxt, subscription_id, values):
        return self.call(ctxt, self.make_msg('create_usage',
                         subscription_id=subscription_id, values=values))

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


central_api = CentralAPI()
