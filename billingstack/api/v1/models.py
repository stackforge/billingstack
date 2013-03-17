from wsme.types import text, DictType


from billingstack.api.base import ModelBase, property_type
from billingstack.openstack.common import log

LOG = log.getLogger(__name__)


class Base(ModelBase):
    id = text


class DescribedBase(Base):
    name = text
    title = text
    description = text


def change_suffixes(data, keys, shorten=True, suffix='_name'):
    """
    Loop thro the keys foreach key setting for example
    'currency_name' > 'currency'
    """
    for key in keys:
        if shorten:
            new, old = key, key + suffix
        else:
            new, old = key + suffix, key
        if old in data:
            if new in data:
                raise RuntimeError("Can't override old key with new key")

            data[new] = data.pop(old)


class Currency(DescribedBase):
    pass


class Language(DescribedBase):
    pass


class InvoiceState(DescribedBase):
    pass


class PGMethod(DescribedBase):
    type = text


class PGProvider(DescribedBase):
    def __init__(self, **kw):
        kw['methods'] = [PGMethod(**m) for m in kw.get('methods', {})]
        super(PGProvider, self).__init__(**kw)

    methods = [PGMethod]
    properties = DictType(key_type=text, value_type=property_type)


class ContactInfo(Base):
    id = text
    first_name = text
    last_name = text
    company = text
    address1 = text
    address2 = text
    address3 = text
    locality = text
    region = text
    country_name = text
    postal_code = text

    phone = text
    email = text
    website = text


class Plan(DescribedBase):
    properties = DictType(key_type=text, value_type=property_type)


class Product(DescribedBase):
    properties = DictType(key_type=text, value_type=property_type)


class Invoice(Base):
    identifier = text
    sub_total = float
    tax_percentage = float
    tax_total = float
    total = float


class Subscription(Base):
    billing_day = int
    resource_id = text
    resource_type = text

    plan_id = text
    customer_id = text
    payment_method_id = text


class PGConfig(Base):
    name = text
    title = text

    properties = DictType(key_type=text, value_type=property_type)


class PaymentMethod(Base):
    name = text
    identifier = text
    expires = text

    properties = DictType(key_type=text, value_type=property_type)


class Account(Base):
    currency = text
    language = text

    name = text

    def to_db(self):
        values = self.as_dict()
        change_suffixes(values, ['currency', 'language'], shorten=False)
        return values

    @classmethod
    def from_db(cls, values):
        change_suffixes(values, ['currency', 'language'])
        return cls(**values)


class Merchant(Account):
    pass


class Customer(Account):
    def __init__(self, **kw):
        infos = kw.get('contact_info', {})
        kw['contact_info'] = [ContactInfo(**i) for i in infos]
        super(Customer, self).__init__(**kw)

    merchant_id = text
    contact_info = [ContactInfo]
