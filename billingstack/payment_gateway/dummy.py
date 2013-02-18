from billingstack.payment_gateway.base import Provider


class BraintreeProvider(Provider):
    __plugin_name__ = 'dummy'
    __title__ = 'Dummy Provider'
    __description__ = 'Noop Dummy'

    @classmethod
    def methods(cls):
        return [
            {"name": "visa", "type": "creditcard"}]

    @classmethod
    def data(cls):
        return {"enabled": 0}
