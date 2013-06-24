# -*- encoding: utf-8 -*-
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
"""
A Usage plugin using sqlalchemy...
"""

from oslo.config import cfg
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import DateTime, Float, Unicode
from sqlalchemy.orm import relationship

from billingstack.openstack.common import log as logging
from billingstack.sqlalchemy.types import UUID
from billingstack.sqlalchemy import api, model_base, session

from billingstack.biller.storage import Connection, StorageEngine
from billingstack.central import rpcapi as central_api

# DB SCHEMA
BASE = declarative_base(cls=model_base.ModelBase)

LOG = logging.getLogger(__name__)


cfg.CONF.register_group(cfg.OptGroup(
    name='biller:sqlalchemy', title='Config for biller sqlalchemy plugin'))


cfg.CONF.register_opts(session.SQLOPTS, group='biller:sqlalchemy')


class InvoiceState(BASE):
    """
    A State representing the currented state a Invoice is in

    Example:
        Completed, Failed
    """
    name = Column(Unicode(60), nullable=False, primary_key=True)
    title = Column(Unicode(100), nullable=False)
    description = Column(Unicode(255))


class Invoice(BASE, model_base.BaseMixin):
    """
    An invoice
    """
    identifier = Column(Unicode(255), nullable=False)
    due = Column(DateTime, )

    sub_total = Column(Float)
    tax_percentage = Column(Float)
    tax_total = Column(Float)
    total = Column(Float)

    customer_id = Column(UUID, nullable=False)

    line_items = relationship('InvoiceLine', backref='invoice_lines')

    state = relationship('InvoiceState', backref='invoices')
    state_id = Column(Unicode(60), ForeignKey('invoice_state.name'),
                      nullable=False)

    # Keep track of the currency and merchant
    currency_name = Column(Unicode(10), nullable=False)
    merchant_id = Column(UUID, nullable=False)


class InvoiceLine(BASE, model_base.BaseMixin):
    """
    A Line item in which makes up the Invoice
    """
    description = Column(Unicode(255))
    price = Column(Float)
    quantity = Column(Float)
    sub_total = Column(Float)

    invoice_id = Column(UUID, ForeignKey('invoice.id', ondelete='CASCADE',
                                         onupdate='CASCADE'), nullable=False)


class SQLAlchemyEngine(StorageEngine):
    __plugin_name__ = 'sqlalchemy'

    def get_connection(self):
        return Connection()


class Connection(Connection, api.HelpersMixin):
    def __init__(self):
        self.setup('biller:sqlalchemy')

    def base(self):
        return BASE

        # Invoice States
    def create_invoice_state(self, ctxt, values):
        """
        Add a supported invoice_state to the database
        """
        row = InvoiceState(**values)
        self._save(row)
        return dict(row)

    def list_invoice_states(self, ctxt, **kw):
        rows = self._list(InvoiceState, **kw)
        return map(dict, rows)

    def get_invoice_state(self, ctxt, id_):
        row = self._get_id_or_name(InvoiceState, id_)
        return dict(row)

    def update_invoice_state(self, ctxt, id_, values):
        row = self._update(InvoiceState, id_, values, by_name=True)
        return dict(row)

    def delete_invoice_state(self, ctxt, id_):
        self._delete(InvoiceState, id_, by_name=True)

        # Invoices
    def _invoice(self, row):
        invoice = dict(row)
        return invoice

    def create_invoice(self, ctxt, merchant_id, values):
        """
        Add a new Invoice

        :param merchant_id: The Merchant
        :param values: Values describing the new Invoice
        """
        merchant = central_api.get_merchant(merchant_id)

        invoice = Invoice(**values)
        invoice.merchant = merchant

        self._save(invoice)
        return self._invoice(invoice)

    def list_invoices(self, ctxt, **kw):
        """
        List Invoices
        """
        rows = self._list(Invoice, **kw)
        return map(self._invoice, rows)

    def get_invoice(self, ctxt, id_):
        """
        Get a Invoice

        :param id_: The Invoice ID
        """
        row = self._get(Invoice, id_)
        return self.invoice(row)

    def update_invoice(self, ctxt, id_, values):
        """
        Update a Invoice

        :param id_: The Invoice ID
        :param values: Values to update with
        """
        row = self._get(Invoice, id_)
        row.update(values)

        self._save(row)
        return self._invoice(row)

    def delete_invoice(self, ctxt, id_):
        """
        Delete a Invoice

        :param id_: Invoice ID
        """
        self._delete(Invoice, id_)

    # Invoices Items
    def _invoice_line(self, row):
        line = dict(row)
        return line

    def create_invoice_items(self, ctxt, invoice_id, values):
        """
        Add a new Invoice

        :param invoice_id: The Invoice
        :param values: Values describing the new Invoice Line
        """
        invoice = self._get(Invoice, invoice_id)

        line = InvoiceLine(**values)
        line.invoice = invoice

        self._save(line)
        return self._invoice_line(line)

    def list_invoice_lines(self, ctxt, **kw):
        """
        List Invoice Lines
        """
        rows = self._list(InvoiceLine, **kw)
        return map(self._invoice_line, rows)

    def get_invoice_line(self, ctxt, id_):
        """
        Get a Invoice Line

        :param id_: The Invoice Line ID
        """
        row = self._get(InvoiceLine, id_)
        return self._invoice_line(row)

    def update_invoice_line(self, ctxt, id_, values):
        """
        Update a Invoice Line

        :param id_: The Invoice ID
        :param values: Values to update with
        """
        row = self._get(InvoiceLine, id_)
        row.update(values)

        self._save(row)
        return self._invoice_line(row)

    def delete_invoice_line(self, ctxt, id_):
        """
        Delete a Invoice Line

        :param id_: Invoice Line ID
        """
        self._delete(InvoiceLine, id_)
