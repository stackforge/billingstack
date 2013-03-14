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
    def currency_add(self, ctxt, values):
        return self.call(ctxt, self.make_msg('currency_add', values=values))

    def currency_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('currency_list',
                         criterion=criterion))

    def currency_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('currency_get',
                         id_=id_))

    def currency_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('currency_update',
                         id_=id_, values=values))

    def currency_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('currency_delete',
                         id_=id_))

    # Language
    def language_add(self, ctxt, values):
        return self.call(ctxt, self.make_msg('language_add', values=values))

    def language_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('language_list',
                         criterion=criterion))

    def language_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('language_get', id_=id_))

    def language_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('language_update',
                         id_, values))

    def language_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('language_delete', id_=id_))

    # Contact Info
    def contact_info_add(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('contact_info_add', id_=id_,
                         values=values))

    def contact_info_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('contact_info_get', id_))

    def contact_info_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('contact_info_update', id_=id_,
                         values=values))

    def contact_info_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('contact_info_delete', id_=id_))

    # PGP
    def pg_provider_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('pg_provider_list',
                         criterion=criterion))

    def pg_provider_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('pg_provider_get', id_=id_))

    # PGM
    def pg_method_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('pg_method_list',
                         criterion=criterion))

    def pg_method_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('pg_method_list', id_=id_))

    # PGC
    def pg_config_add(self, ctxt, merchant_id, provider_id, values):
        return self.call(ctxt, self.make_msg('pg_config_add',
                         merchant_id=merchant_id, provider_id=provider_id,
                         values=values))

    def pg_config_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('pg_config_list',
                         criterion=criterion))

    def pg_config_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('pg_config_get', id_=id_))

    def pg_config_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('pg_config_update', id_=id_,
                         values=values))

    def pg_config_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('pg_config_delete', id_=id_))

    # PaymentMethod
    def payment_method_add(self, ctxt, customer_id, pg_method_id, values):
        return self.call(ctxt, self.make_msg('payment_method_add',
                         customer_id=customer_id, pg_method_id=pg_method_id,
                         values=values))

    def payment_method_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('payment_method_list',
                         criterion=criterion))

    def payment_method_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('payment_method_get', id_=id_))

    def payment_method_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('payment_method_update', id_=id_,
                         values=values))

    def payment_method_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('payment_method_delete', id_=id_))

    # Merchant
    def merchant_add(self, ctxt, values):
        return self.call(ctxt, self.make_msg('merchant_add', values=values))

    def merchant_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('merchant_list',
                         criterion=criterion))

    def merchant_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('merchant_get', id_=id_))

    def merchant_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('merchant_update',
                         id_=id_, values=values))

    def merchant_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('merchant_delete',
                         id_=id_))

    # Customer
    def customer_add(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('customer_add',
                         merchant_id=merchant_id, values=values))

    def customer_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('customer_list',
                         criterion=criterion))

    def customer_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('customer_get', id_=id_))

    def customer_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('customer_update',
                         id_=id_, values=values))

    def customer_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('customer_delete', id_=id_))

    # User
    def user_add(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('user_add',
                         merchant_id=merchant_id, values=values))

    def user_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('user_list', criterion=criterion))

    def user_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('user_get', id_=id_))

    def user_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('user_update', id_=id_,
                         values=values))

    def user_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('user_delete', id_=id_))

    # Products
    def product_add(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('product_add',
                         merchant_id=merchant_id, values=values))

    def product_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('product_list',
                         criterion=criterion))

    def product_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('product_get', id_=id_))

    def product_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('product_update', id_=id_,
                         values=values))

    def product_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('product_delete', id_=id_))

    # PlanItems
    def plan_item_add(self, ctxt, values):
        return self.call(ctxt, self.make_msg('plan_item_add', values=values))

    def plan_item_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('plan_item_list',
                         criterion=criterion))

    def plan_item_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('plan_item_get', id_=id_))

    def plan_item_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('plan_item_update', id_=id_,
                         values=values))

    def plan_item_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('plan_item_delete', id_=id_))

    # Plans
    def plan_add(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('plan_add',
                         merchant_id=merchant_id, values=values))

    def plan_list(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('plan_list', criterion=criterion))

    def plan_get(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('plan_get', id_=id_))

    def plan_update(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('plan_update', id_=id_,
                         values=values))

    def plan_delete(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('plan_delete', id_=id_))
