# Author: Endre Karlson <endre.karlson@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import re

from sqlalchemy import Column, Table, ForeignKey, UniqueConstraint
from sqlalchemy import Integer, Float, Enum, Boolean
from sqlalchemy import DateTime, Unicode, UnicodeText
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from billingstack import utils
from billingstack.openstack.common import log as logging
from billingstack.openstack.common import timeutils
from billingstack.openstack.common.uuidutils import generate_uuid
from billingstack.storage.impl_sqlalchemy.types import JSON, UUID
from billingstack.storage.impl_sqlalchemy.model_base import ModelBase
from sqlalchemy.ext.declarative import declarative_base, declared_attr

LOG = logging.getLogger(__name__)


class BaseModel(ModelBase):
    @declared_attr
    def __tablename__(cls):
        return utils.capital_to_underscore(cls.__name__)

    id = Column(UUID, default=generate_uuid, primary_key=True)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, onupdate=timeutils.utcnow)


BASE = declarative_base(cls=BaseModel)


class Currency(BASE):
    """
    Allowed currency
    """
    __table_args__ = (UniqueConstraint('name', name='currency'),)
    name = Column(Unicode(10), nullable=False)
    title = Column(Unicode(100), nullable=False)


class Language(BASE):
    """
    A Language
    """
    __table_args__ = (UniqueConstraint('name', name='language'),)
    name = Column(Unicode(10), nullable=False)
    title = Column(Unicode(100), nullable=False)


pg_provider_methods = Table('pg_provider_methods', BASE.metadata,
    Column('provider_id', UUID, ForeignKey('pg_provider.id')),
    Column('method_id', UUID, ForeignKey('pg_method.id')))


class PGProvider(BASE):
    """
    A Payment Gateway - The thing that processes a Payment Method

    This is registered either by the Admin or by the PaymentGateway plugin
    """
    __tablename__ = 'pg_provider'

    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    properties = Column(JSON)

    methods = relationship(
        'PGMethod',
        backref='providers',
        secondary=pg_provider_methods,
        primaryjoin="PGProvider.id==pg_provider_methods.c.provider_id",
        secondaryjoin="PGMethod.id==pg_provider_methods.c.method_id",
        lazy='joined')

    provider_methods = relationship(
        'PGMethod',
        backref='owner',
        primaryjoin='PGProvider.id == PGMethod.owner_id',
        foreign_keys='[PGMethod.owner_id]',
        post_update=True,
        lazy='joined')

    def method_map(self):
        return self.attrs_map(['provider_methods'])


class PGMethod(BASE):
    """
    This represents a PaymentGatewayProviders method with some information
    like name, type etc to describe what is in other settings known as a
    "CreditCard"

    Example:
        A Visa card: {"type": "creditcard", "visa"}
    """
    __tablename__ = 'pg_method'

    name = Column(Unicode(100), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    type = Column(Unicode(100), nullable=False)
    properties = Column(JSON)

    # NOTE: This is so a PGMethod can be "owned" by a Provider, meaning that
    # other Providers should not be able to use it.
    owner_id = Column(UUID, ForeignKey(
        'pg_provider_methods.provider_id',
        ondelete='CASCADE',
        onupdate='CASCADE',
        use_alter=True,
        name='owner_fk'))

    @staticmethod
    def make_key(data):
        return '%(type)s:%(name)s' % data

    def key(self):
        return self.make_key(self)


class ContactInfo(BASE):
    """
    Contact Information about an entity like a User, Customer etc...
    """

    @declared_attr
    def __mapper_args__(cls):
        name = unicode(utils.capital_to_underscore(cls.__name__))
        return {"polymorphic_on": "info_type", "polymorphic_identity": name}

    info_type = Column(Unicode(20), nullable=False)

    first_name = Column(Unicode(100))
    last_name = Column(Unicode(100))
    company = Column(Unicode(100))
    street_address = Column(Unicode(255))
    extended_address = Column(Unicode(255))
    locality = Column(Unicode(60))
    region = Column(Unicode(60))
    country_name = Column(Unicode(100))
    postal_code = Column(Unicode(40))

    phone = Column(Unicode(100))
    email = Column(Unicode(100))
    website = Column(Unicode(100))


class CustomerInfo(ContactInfo):
    id = Column(UUID, ForeignKey("contact_info.id",
                                 onupdate='CASCADE', ondelete='CASCADE'),
                primary_key=True)

    customer_id = Column(UUID, ForeignKey('customer.id'), nullable=False)


user_customer = Table('user_customer', BASE.metadata,
    Column('user_id', UUID, ForeignKey('user.id')),
    Column('customer_id', UUID, ForeignKey('customer.id')))


user_customer_role = Table('user_customer_roles', BASE.metadata,
    Column('user_id', UUID, ForeignKey('user.id', ondelete='CASCADE')),
    Column('customer_id', UUID, ForeignKey('customer.id', ondelete='CASCADE')),
    Column('role', Unicode(40)))


user_merchant_role = Table('user_merchant_roles', BASE.metadata,
    Column('user_id', UUID, ForeignKey('user.id', ondelete='CASCADE')),
    Column('merchant_id', UUID, ForeignKey('merchant.id', ondelete='CASCADE')),
    Column('role', Unicode(40)))


class User(BASE):
    """
    A User that can login.
    """
    username = Column(Unicode(20), nullable=False)
    password = Column(Unicode(255), nullable=False)

    # NOTE: Should be uuid?
    api_key = Column(Unicode(255))
    api_secret = Column(Unicode(255))

    customers = relationship('Customer', backref='users', secondary=user_customer)

    contact_info = relationship('ContactInfo', backref='user', uselist=False,
                                lazy='joined')
    contact_info_id = Column(UUID, ForeignKey('contact_info.id'))

    merchant = relationship('Merchant', backref='users')
    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'))


class Merchant(BASE):
    """
    A Merchant is like a Account in Recurly
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(60))

    customers = relationship('Customer', backref='merchant')
    payment_gateways = relationship('PGAccountConfig', backref='merchant')

    plans = relationship('Plan', backref='merchant')
    products = relationship('Product', backref='merchant')

    currency = relationship('Currency', uselist=False, backref='merchants')
    currency_id = Column(UUID, ForeignKey('currency.id'), nullable=False)

    language = relationship('Language', uselist=False, backref='merchants')
    language_id = Column(UUID, ForeignKey('language.id'), nullable=False)


class PGAccountConfig(BASE):
    """
    A Merchant's configuration of a PaymentGateway like api keys, url and more
    """
    __tablename__ = 'pg_account_config'
    name = Column(Unicode(100), nullable=False)
    title = Column(Unicode(100))
    configuration = Column(JSON)

    # Link to the Merchant
    merchant_id = Column(UUID, ForeignKey('merchant.id'), nullable=False)

    provider = relationship('PGProvider',
                            backref='merchant_configurations')
    provider_id = Column(UUID, ForeignKey('pg_provider.id',
                                          onupdate='CASCADE'),
                         nullable=False)


class Customer(BASE):
    """
    A Customer is linked to a Merchant and can have Users related to it
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(60))

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)

    invoices = relationship('Invoice', backref='customer')
    payment_methods = relationship('PaymentMethod', backref='customer')

    contact_info = relationship(
        'CustomerInfo',
        backref='customer',
        primaryjoin='Customer.id == CustomerInfo.customer_id',
        lazy='joined')

    default_info = relationship(
        'CustomerInfo',
        primaryjoin='Customer.default_info_id == CustomerInfo.id',
        uselist=False,
        post_update=True)
    default_info_id = Column(
        UUID,
        ForeignKey('customer_info.id', use_alter=True,
                   onupdate='CASCADE', name='default_info'))

    currency = relationship('Currency', uselist=False, backref='customers')
    currency_id = Column(UUID, ForeignKey('currency.id'))

    language = relationship('Language', uselist=False, backref='customers')
    language_id = Column(UUID, ForeignKey('language.id'))


class PaymentMethod(BASE):
    name = Column(Unicode(255), nullable=False)

    identifier = Column(Unicode(255), nullable=False)
    expires = Column(Unicode(255))

    properties = Column(JSON)

    customer_id = Column(UUID, ForeignKey('customer.id', onupdate='CASCADE'),
                         nullable=False)

    provider_method = relationship('PGMethod',
                                   backref='payment_methods')
    provider_method_id = Column(UUID, ForeignKey('pg_method.id',
                                                 onupdate='CASCADE'))


class InvoiceState(BASE):
    """
    A State representing the currented state a Invoice is in

    Example:
        Completed, Failed
    """
    name = Column(Unicode(60), nullable=False)


class Invoice(BASE):
    """
    An invoice
    """
    identifier = Column(Unicode(255), nullable=False)
    due = Column(DateTime, )

    sub_total = Column(Float)
    tax_percentage = Column(Float)
    tax_total = Column(Float)
    total = Column(Float)

    customer_id = Column(UUID, ForeignKey('customer.id', ondelete='CASCADE'),
                         nullable=False)

    line_items = relationship('InvoiceLine', backref='invoice_lines')

    state = relationship('InvoiceState', backref='invoices')
    state_id = Column(UUID, ForeignKey('invoice_state.id'), nullable=False)

    currency = relationship('Currency', backref='invoices')
    currency_id = Column(UUID, ForeignKey('currency.id'), nullable=False)

    merchant = relationship('Merchant', backref='invoices')
    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)


class InvoiceLine(BASE):
    """
    A Line item in which makes up the Invoice
    """
    description = Column(Unicode(255))
    price = Column(Float)
    quantity = Column(Float)
    sub_total = Column(Float)

    invoice_id = Column(UUID, ForeignKey('invoice.id', ondelete='CASCADE',
                                         onupdate='CASCADE'), nullable=False)


class Pricing(BASE):
    """
    Resembles a Price information in some way
    """
    __tablename__ = 'product_pricing'
    value_from = Column(Float)
    value_to = Column(Float)
    price = Column(Float, nullable=False)

    plan_item_id = Column(UUID, ForeignKey('plan_item.id', ondelete='CASCADE',
                                           onupdate='CASCADE'))
    product_id = Column(UUID, ForeignKey('product.id', ondelete='CASCADE',
                                           onupdate='CASCADE'))


class Plan(BASE):
    """
    A Product collection like a "Virtual Web Cluster" with 10 servers
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))
    #provider = Column(Unicode(255), nullable=False)

    plan_items = relationship('PlanItem', backref='plan')

    merchant_id = Column(UUID, ForeignKey('merchant.id',
                         ondelete='CASCADE'), nullable=False)


class PlanProperties(BASE):
    __table_args__ = (UniqueConstraint('plan_id', 'name'), {})

    plan = relationship('Plan', backref='properties', lazy='joined')
    plan_id = Column(
        UUID,
        ForeignKey('plan.id',
                   ondelete='CASCADE',
                   onupdate='CASCADE'))
    name = Column(Unicode(60), index=True, nullable=False)
    value = Column(UnicodeText)


class PlanItem(BASE):
    description = Column(Unicode(255))

    price_rules = relationship(
        'Pricing',
        backref=backref('plan_items', uselist=False),
        lazy='dynamic', cascade='delete, delete-orphan',
        passive_deletes=True)

    plan_id = Column(UUID, ForeignKey('plan.id', ondelete='CASCADE'),
                     nullable=False)

    product = relationship('Product', backref='plan_items', uselist=False)
    product_id = Column(UUID, ForeignKey('product.id', ondelete='CASCADE'),
                        nullable=False)


class Product(BASE):
    """
    A sellable Product, like vCPU hours, bandwidth units
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    measure = Column(Unicode(255))
    source = Column(Unicode(255))
    type = Column(Unicode(255))

    price = relationship('Pricing', backref='product', uselist=False)

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)


class ProductProperties(BASE):
    """
    A Metadata row for something like Product or PlanItem
    """
    __table_args__ = (UniqueConstraint('product_id', 'name'), {})

    product = relationship('Product', backref='properties', lazy='joined')
    product_id = Column(
        UUID,
        ForeignKey('product.id',
                   ondelete='CASCADE',
                   onupdate='CASCADE'))
    name = Column(Unicode(60), index=True, nullable=False)
    value = Column(UnicodeText)


class Subscription(BASE):
    """
    The thing that ties together stuff that is to be billed

    In other words a Plan which is a collection of Products or a Product.
    """
    billing_day = Column(Integer)

    resource_id = Column(Unicode(255))
    resource_type = Column(Unicode(255))

    usages = relationship(
        'Usage',
        backref='subscription',
        lazy='dynamic',
        cascade='delete, delete-orphan',
        passive_deletes=True)

    plan = relationship('Plan', backref='subscriptions', uselist=False)
    plan_id = Column(UUID, ForeignKey('plan.id', ondelete='CASCADE'),
                     nullable=False)

    customer = relationship('Customer', backref='subscriptions')
    customer_id = Column(UUID, ForeignKey('customer.id', ondelete='CASCADE'),
                         nullable=False)

    payment_method = relationship('PaymentMethod', backref='subscriptions')
    payment_method_id = Column(UUID, ForeignKey('payment_method.id',
                                             ondelete='CASCADE',
                                             onupdate='CASCADE'),
                           nullable=False)


class Usage(BASE):
    """
    A record of something that's used from for example a Metering system like
    Ceilometer
    """
    measure = Column(Unicode(255))
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)

    price = Column(Float)
    total = Column(Float)
    value = Column(Float)

    product = relationship('Product', backref='usages')
    prodoct_id = Column(UUID, ForeignKey('product.id', onupdate='CASCADE'),
                        nullable=False)

    subscription_id = Column(UUID, ForeignKey('subscription.id',
                                              onupdate='CASCADE'),
                             nullable=False)
