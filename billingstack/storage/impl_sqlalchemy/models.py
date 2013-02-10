# Copyright 2012 Bouvet ASA
#
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
from billingstack.storage.impl_sqlalchemy.types import UUID
from billingstack.storage.impl_sqlalchemy.model_base import ModelBase
from sqlalchemy.ext.declarative import declarative_base, declared_attr

LOG = logging.getLogger(__name__)


class ModelBase(ModelBase):
    @declared_attr
    def __tablename__(cls):
        return utils.capital_to_underscore(cls.__name__)

    id = Column(UUID, default=generate_uuid, primary_key=True)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, onupdate=timeutils.utcnow)


ModelBase = declarative_base(cls=ModelBase)


class Currency(ModelBase):
    __table_args__ = (UniqueConstraint('letter', name='currency'),)
    letter = Column(Unicode(10), nullable=False)
    name = Column(Unicode(100), nullable=False)


class Language(ModelBase):
    __table_args__ = (UniqueConstraint('letter', name='language'),)
    letter = Column(Unicode(10), nullable=False)
    name = Column(Unicode(100), nullable=False)


class ContactInfo(ModelBase):
    address1 = Column(Unicode(60))
    address2 = Column(Unicode(60))
    city = Column(Unicode(60))
    company = Column(Unicode(60))
    country = Column(Unicode(40))
    state = Column(Unicode(40))
    zip = Column(Unicode(20))



user_customer = Table('user_customer', ModelBase.metadata,
    Column('user_id', UUID, ForeignKey('user.id')),
    Column('customer_id', UUID, ForeignKey('customer.id')))


user_customer_role = Table('user_customer_roles', ModelBase.metadata,
    Column('user_id', UUID, ForeignKey('user.id', ondelete='CASCADE')),
    Column('customer_id', UUID, ForeignKey('customer.id', ondelete='CASCADE')),
    Column('role', Unicode(40)))


user_merchant_role = Table('user_merchant_roles', ModelBase.metadata,
    Column('user_id', UUID, ForeignKey('user.id', ondelete='CASCADE')),
    Column('merchant_id', UUID, ForeignKey('merchant.id', ondelete='CASCADE')),
    Column('role', Unicode(40)))


class User(ModelBase):
    username = Column(Unicode(20), nullable=False)
    password = Column(Unicode(255), nullable=False)
    # NOTE: Should be uuid?
    api_key = Column(Unicode(255))
    api_secret = Column(Unicode(255))

    customers = relationship('Customer', backref='users', secondary=user_customer)

    contact_info = relationship('ContactInfo', backref='user', uselist=False)
    contact_info_id = Column(UUID, ForeignKey('contact_info.id'), nullable=False)

    merchant = relationship('Merchant', backref='users')
    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'))


class Account(ModelBase):
    """
    An Account is kind of like a Group, it holds the base info for all accounts
    """
    _account_type = Column("account_type", Unicode(20), nullable=False)
    name = Column(Unicode(60), nullable=False)

    currency = relationship('Currency', uselist=False, backref='accounts')
    currency_id = Column(UUID, ForeignKey('currency.id'), nullable=False)

    language = relationship('Language', uselist=False, backref='accounts')
    language_id = Column(UUID, ForeignKey('language.id'), nullable=False)

    @declared_attr
    def __mapper_args__(cls):
        # FIXME: Make this return TestAccount > test_account based on cls name
        name = unicode(cls.__name__)
        return {"polymorphic_on": "_account_type", "polymorphic_identity": name}

    @hybrid_property
    def account_type(self):
        return self._account_type


class Merchant(Account):
    """
    A Merchant is like a Account in Recurly
    """
    id = Column(UUID, ForeignKey("account.id",
                onupdate='CASCADE', ondelete='CASCADE'),
                primary_key=True)

    payment_gateway = relationship('PaymentGateway', backref='merchant', uselist=False)
    customers = relationship('Customer', backref='merchant', foreign_keys="Customer.id")
    plans = relationship('Plan', backref='merchant')
    products = relationship('Product', backref='merchant')


class Customer(Account):
    """
    A Customer is linked to a Merchant and can have Users related to it
    """
    id = Column(UUID, ForeignKey("account.id",
                onupdate='CASCADE', ondelete='CASCADE'),
                primary_key=True)

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)

    invoices = relationship('Invoice', backref='customer')


class PaymentGateway(ModelBase):
    """
    A Payment Gateway
    """
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    is_default = Column(Boolean, nullable=False)

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)


class InvoiceState(ModelBase):
    name = Column(Unicode(40), nullable=False)


class Invoice(ModelBase):
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


class InvoiceLine(ModelBase):
    description = Column(Unicode(255))
    price = Column(Float)
    quantity = Column(Float)
    sub_total = Column(Float)

    invoice_id = Column(UUID, ForeignKey('invoice.id', ondelete='CASCADE'), nullable=False)


class Plan(ModelBase):
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))
    provider = Column(Unicode(255), nullable=False)

    plan_items = relationship('PlanItem', backref='plan')

    merchant_id = Column(UUID, ForeignKey('merchant.id',
                         ondelete='CASCADE'), nullable=False)


class PlanItem(ModelBase):
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    price = Column(Float, nullable=False)
    value_from = Column(Float)
    value_to = Column(Float)

    plan_id = Column(UUID, ForeignKey('plan.id', ondelete='CASCADE'),
                     nullable=False)

    merchant = relationship('Merchant', backref='plan_items')
    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)

    product = relationship('Product', backref='plan_items')
    product_id = Column(UUID, ForeignKey('product.id', ondelete='CASCADE'),
                        nullable=False)


class Product(ModelBase):
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))
    description = Column(Unicode(255))

    measure = Column(Unicode(255))
    source = Column(Unicode(255))
    type = Column(Unicode(255))
    price = Column(Float)

    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)


class Subscription(ModelBase):
    billing_day = Column(Integer)
    payment_method = Column(Unicode(255))
    resource = Column(Unicode(255))

    usages = relationship('Usage', backref='subscription')

    plan = relationship('Plan', backref='subscriptions')
    plan_id = Column(UUID, ForeignKey('plan.id', ondelete='CASCADE'),
                     nullable=False)

    merchant = relationship('Merchant', backref='subscriptions')
    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                         nullable=False)

    customer = relationship('Customer', backref='subscriptions')
    customer_id = Column(UUID, ForeignKey('customer.id', ondelete='CASCADE'),
                         nullable=False)


class Usage(ModelBase):
    measure = Column(Unicode(255))
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)

    price = Column(Float)
    total = Column(Float)
    value = Column(Float)

    subscription_id = Column(UUID, ForeignKey('subscription.id',
                             ondelete='CASCADE'), nullable=False)

    merchant = relationship('Merchant', backref='usages')
    merchant_id = Column(UUID, ForeignKey('merchant.id', ondelete='CASCADE'),
                        nullable=False)

    customer = relationship('Customer', backref='usages')
    customer_id = Column(UUID, ForeignKey('customer.id', ondelete='CASCADE'),
                         nullable=False)
