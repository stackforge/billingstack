from billingstack.payment_gateway import register_providers
from billingstack.manage.base import ListCommand
from billingstack.manage.database import DatabaseCommand


class ProvidersRegister(DatabaseCommand):
    """
    Register Payment Gateway Providers
    """
    def execute(self, parsed_args):
        register_providers()


class ProvidersList(DatabaseCommand, ListCommand):
    def execute(self, parsed_args):
        data = self.conn.pg_provider_list()

        for p in data:
            p['methods'] = ", ".join(
                [":".join([m[k] for k in ['type', 'name']])\
                    for m in p['methods']])
        return data
