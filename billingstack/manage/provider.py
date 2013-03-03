from billingstack.openstack.common.context import get_admin_context
from billingstack.payment_gateway import register_providers
from billingstack.manage.base import ListCommand
from billingstack.manage.database import DatabaseCommand


class ProvidersRegister(DatabaseCommand):
    """
    Register Payment Gateway Providers
    """
    def execute(self, parsed_args):
        context = get_admin_context()
        register_providers(context)


class ProvidersList(DatabaseCommand, ListCommand):
    def execute(self, parsed_args):
        context = get_admin_context()
        data = self.conn.pg_provider_list(context)

        for p in data:
            p['methods'] = ", ".join(
                [":".join([m[k] for k in ['type', 'name']])\
                    for m in p['methods']])
        return data
