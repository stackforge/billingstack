import functools
from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack import storage


cfg.CONF.import_opt('central_topic', 'billingstack.central.rpcapi')
cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('state_path', 'billingstack.paths')

LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.central_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

    def start(self):
        self.storage_conn = storage.get_connection()
        super(Service, self).start()

    def __getattr__(self, name):
        """
        Proxy onto the storage api if there is no local method present..

        For now to avoid to have to write up every method once more here...
        """
        if hasattr(self, name):
            return getattr(self, name)

        f = getattr(self.storage_conn, name)
        if not f:
            raise AttributeError

        @functools.wraps(f)
        def _wrapper(*args, **kw):
            return f(*args, **kw)
        setattr(self, name, _wrapper)
        return _wrapper

    def create_currency(self, ctxt, values):
        return self.storage_conn.create_currency(ctxt, values)

    def list_currencies(self, ctxt, **kw):
        return self.storage_conn.list_currencies(ctxt, **kw)

    def get_currency(self, ctxt, id_):
        return self.storage_conn.get_currency(ctxt, id_)

    def update_currency(self, ctxt, id_, values):
        return self.storage_conn.update_currency(ctxt, id_, values)

    def delete_currency(self, ctxt, id_):
        return self.storage_conn.delete_currency(ctxt, id_)

    def create_language(self, ctxt, values):
        return self.storage_conn.create_language(ctxt, values)

    def list_languages(self, ctxt, **kw):
        return self.storage_conn.list_languages(ctxt, **kw)

    def get_language(self, ctxt, id_):
        return self.storage_conn.get_language(ctxt, id_)

    def update_language(self, ctxt, id_, values):
        return self.storage_conn.update_language(ctxt, id_, values)

    def delete_language(self, ctxt, id_):
        return self.storage_conn.delete_language(ctxt, id_)

    def create_invoice_state(self, ctxt, values):
        return self.storage_conn.create_invoice_state(ctxt, values)

    def list_invoice_states(self, ctxt, **kw):
        return self.storage_conn.list_invoice_states(ctxt, **kw)

    def get_invoice_state(self, ctxt, id_):
        return self.storage_conn.get_invoice_state(ctxt, id_)

    def update_invoice_state(self, ctxt, id_, values):
        return self.storage_conn.update_invoice_state(ctxt, id_, values)

    def delete_invoice_state(self, ctxt, id_):
        return self.storage_conn.delete_invoice_state(ctxt, id_)

    # TODO Fix
    def create_contact_info(self, ctxt, obj, values, cls=None,
                            rel_attr='contact_info'):
        return self.storage_conn.create_contact_info(ctxt, values)

    def get_contact_info(self, ctxt, id_):
        return self.storage_conn.get_contact_info(ctxt, id_)

    def update_contact_info(self, ctxt, id_, values):
        return self.storage_conn.update_contact_info(ctxt, values)

    def delete_contact_info(self, ctxt, id_):
        return self.storage_conn.delete_contact_info(ctxt, id_)

    def list_pg_providers(self, ctxt, **kw):
        return self.storage_conn.list_pg_providers(ctxt, **kw)

    def get_pg_provider(self, ctxt, pgp_id):
        return self.storage_conn.get_pg_provider(ctxt, pgp_id)

    def create_pg_method(self, ctxt, values):
        return self.storage_conn.create_pg_method(ctxt, values)

    def list_pg_methods(self, ctxt, **kw):
        return self.storage_conn.list_pg_methods(ctxt, **kw)

    def get_pg_method(self, ctxt, id_):
        return self.storage_conn.get_pg_method(ctxt, id_)

    def update_pg_method(self, ctxt, id_, values):
        return self.storage_conn.update_pg_method(ctxt, id_, values)

    def delete_pg_method(self, ctxt, id_):
        return self.storage_conn.delete_pg_method(ctxt, id_)

    def create_pg_config(self, ctxt, merchant_id, values):
        return self.storage_conn.create_pg_config(ctxt, merchant_id, values)

    def list_pg_configs(self, ctxt, **kw):
        return self.storage_conn.list_pg_configs(ctxt, **kw)

    def get_pg_config(self, ctxt, id_):
        return self.storage_conn.get_pg_config(ctxt, id_)

    def update_pg_config(self, ctxt, id_, values):
        return self.storage_conn.update_pg_config(ctxt, id_, values)

    def delete_pg_config(self, ctxt, id_):
        return self.storage_conn.delete_pg_config(ctxt, id_)

    def create_payment_method(self, ctxt, customer_id, values):
        return self.storage_conn.create_payment_method(
            ctxt, customer_id, values)

    def list_payment_methods(self, ctxt, **kw):
        return self.storage_conn.list_payment_methods(ctxt, **kw)

    def get_payment_method(self, ctxt, id_, **kw):
        return self.storage_conn.get_payment_method(ctxt, id_)

    def update_payment_method(self, ctxt, id_, values):
        return self.storage_conn.update_payment_method(ctxt, id_, values)

    def delete_payment_method(self, ctxt, id_):
        return self.storage_conn.delete_payment_method(ctxt, id_)

    def create_merchant(self, ctxt, values):
        return self.storage_conn.create_merchant(ctxt, values)

    def list_merchants(self, ctxt, **kw):
        return self.storage_conn.list_merchants(ctxt, **kw)

    def get_merchant(self, ctxt, id_):
        return self.storage_conn.get_merchant(ctxt, id_)

    def update_merchant(self, ctxt, id_, values):
        return self.storage_conn.update_merchant(ctxt, id_, values)

    def delete_merchant(self, ctxt, id_):
        return self.storage_conn.delete_merchant(ctxt, id_)

    def create_customer(self, ctxt, merchant_id, values):
        return self.storage_conn.create_customer(ctxt, merchant_id, values)

    def list_customers(self, ctxt, **kw):
        return self.storage_conn.list_customers(ctxt, **kw)

    def get_customer(self, ctxt, id_):
        return self.storage_conn.get_customer(ctxt, id_)

    def update_customer(self, ctxt, id_, values):
        return self.storage_conn.update_customer(ctxt, id_, values)

    def delete_customer(self, ctxt, id_):
        return self.storage_conn.delete_customer(ctxt, id_)

    def create_plan(self, ctxt, merchant_id, values):
        return self.storage_conn.create_plan(ctxt, merchant_id, values)

    def list_plans(self, ctxt, **kw):
        return self.storage_conn.list_plans(ctxt, **kw)

    def get_plan(self, ctxt, id_):
        return self.storage_conn.get_plan(ctxt, id_)

    def update_plan(self, ctxt, id_, values):
        return self.storage_conn.update_plan(ctxt, id_, values)

    def delete_plan(self, ctxt, id_):
        return self.storage_conn.delete_plan(ctxt, id_)

    def create_plan_item(self, ctxt, values):
        return self.storage_conn.create_plan(ctxt, values)

    def update_plan_item(self, ctxt, id_, values):
        return self.storage_conn.update_plan_item(ctxt, id_, values)

    def list_plan_items(self, ctxt, **kw):
        return self.storage_conn.list_plan_items(ctxt, **kw)

    def get_plan_item(self, ctxt, id_):
        return self.storage_conn.get_plan_item(ctxt, id_)

    def delete_plan_item(self, ctxt, id_):
        return self.storage_conn.delete_plan_item(ctxt, id_)

    def create_product(self, ctxt, merchant_id, values):
        return self.storage_conn.create_product(ctxt, merchant_id, values)

    def list_products(self, ctxt, **kw):
        return self.storage_conn.list_products(ctxt, **kw)

    def get_product(self, ctxt, id_):
        return self.storage_conn.get_product(ctxt, id_)

    def update_product(self, ctxt, id_, values):
        return self.storage_conn.update_product(ctxt, id_, values)

    def delete_product(self, ctxt, id_):
        return self.storage_conn.delete_product(ctxt, id_)

    def create_invoice(self, ctxt, merchant_id, values):
        return self.storage_conn.create_invoice_state(
            ctxt, merchant_id, values)

    def list_invoices(self, ctxt, **kw):
        return self.storage_conn.list_invoices(ctxt, **kw)

    def get_invoice(self, ctxt, id_):
        return self.storage_conn.get_invoice(ctxt, id_)

    def update_invoice(self, ctxt, id_, values):
        return self.storage_conn.update_invoice(ctxt, id_, values)

    def delete_invoice(self, ctxt, id_):
        return self.storage_conn.delete_invoice(ctxt, id_)

    def create_invoice_line(self, ctxt, invoice_id, values):
        return self.storage_conn.create_invoice_line_state(
            ctxt, invoice_id, values)

    def list_invoice_lines(self, ctxt, **kw):
        return self.storage_conn.list_invoice_lines(ctxt, **kw)

    def get_invoice_line(self, ctxt, id_):
        return self.storage_conn.get_invoice_line(ctxt, id_)

    def update_invoice_line(self, ctxt, id_, values):
        return self.storage_conn.update_invoice_line(ctxt, id_, values)

    def delete_invoice_line(self, ctxt, id_):
        return self.storage_conn.delete_invoice_line(ctxt, id_)

    def create_subscription(self, ctxt, values):
        return self.storage_conn.create_subscription(ctxt, values)

    def list_subscriptions(self, ctxt, **kw):
        return self.storage_conn.list_subscriptions(ctxt, **kw)

    def get_subscription(self, ctxt, id_):
        return self.storage_conn.get_subscription(ctxt, id_)

    def update_subscription(self, ctxt, id_, values):
        return self.storage_conn.update_subscription(ctxt, id_, values)

    def delete_subscription(self, ctxt, id_):
        return self.storage_conn.delete_subscription(ctxt, id_)

    def create_usage(self, ctxt, values):
        return self.storage_conn.create_usage(ctxt, values)

    def list_usages(self, ctxt, **kw):
        return self.storage_conn.list_usages(ctxt, **kw)

    def get_usage(self, ctxt, id_):
        return self.storage_conn.get_usage(ctxt, id_)

    def update_usage(self, ctxt, id_, values):
        return self.storage_conn.update_usage(ctxt, id_, values)

    def delete_usage(self, ctxt, id_):
        return self.storage_conn.delete_usage(ctxt, id_)
