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

from flask import request
from flask import Response

from billingstack.api.base import Rest, Query
from billingstack.api.v1 import models
from billingstack.central.rpcapi import central_api
from billingstack.rater.rpcapi import rater_api

from wsmeext.flask import signature


bp = Rest('v1', __name__)


def _query_to_criterion(query, storage_func=None, **kw):
    """
    Iterate over the query checking against the valid signatures (later).

    :param query: A list of queries.
    :param storage_func: The name of the storage function to very against.
    """
    translation = {
        'customer': 'customer_id'
    }

    criterion = {}
    for q in query:
        key = translation.get(q.field, q.field)
        criterion[key] = q.as_dict()

    criterion.update(kw)

    return criterion


# Currencies
@bp.post('/currencies')
@signature(models.Currency, body=models.Currency)
def create_currency(body):
    row = central_api.create_currency(
        request.environ['context'], body.to_db())
    return models.Currency.from_db(row)


@bp.get('/currencies')
@signature([models.Currency], [Query])
def list_currencies(q=[]):
    criterion = _query_to_criterion(q)

    rows = central_api.list_currencies(
        request.environ['context'], criterion=criterion)

    return map(models.Currency.from_db, rows)


@bp.get('/currencies/<currency_id>')
@signature(models.Currency, str)
def get_currency(currency_id):
    row = central_api.get_currency(request.environ['context'],
                                   currency_id)

    return models.Currency.from_db(row)


@bp.put('/currencies/<currency_id>')
@signature(models.Currency, str, body=models.Currency)
def update_currency(currency_id, body):
    row = central_api.update_currency(
        request.environ['context'],
        currency_id,
        body.to_db())

    return models.Currency.from_db(row)


@bp.delete('/currencies/<currency_id>')
def delete_currency(currency_id):
    central_api.delete_currency(request.environ['context'], currency_id)
    return Response(status=204)


# Language
@bp.post('/languages')
@signature(models.Language, body=models.Language)
def create_language(body):
    row = central_api.create_language(request.environ['context'],
                                      body.to_db())

    return models.Language.from_db(row)


@bp.get('/languages')
@signature([models.Language], [Query])
def list_languages(q=[]):
    criterion = _query_to_criterion(q)

    rows = central_api.list_languages(
        request.environ['context'], criterion=criterion)

    return map(models.Language.from_db, rows)


@bp.get('/languages/<language_id>')
@signature(models.Language, str)
def get_language(language_id):
    row = central_api.get_language(request.environ['context'],
                                   language_id)

    return models.Language.from_db(row)


@bp.put('/languages/<language_id>')
@signature(models.Language, str, body=models.Language)
def update_language(language_id, body):
    row = central_api.update_language(
        request.environ['context'],
        language_id,
        body.to_db())

    return models.Language.from_db(row)


@bp.delete('/languages/<language_id>')
def delete_language(language_id):
    central_api.delete_language(request.environ['context'], language_id)
    return Response(status=204)


# PGP / PGM
@bp.get('/payment-gateway-providers')
@signature([models.PGProvider], [Query])
def list_pg_providers(q=[]):
    criterion = _query_to_criterion(q)

    rows = central_api.list_pg_providers(
        request.environ['context'], criterion=criterion)

    return map(models.PGProvider.from_db, rows)


# invoice_states
@bp.post('/invoice-states')
@signature(models.InvoiceState, body=models.InvoiceState)
def create_invoice_state(body):
    row = central_api.create_invoice_state(
        request.environ['context'], body.to_db())

    return models.InvoiceState.from_db(row)


@bp.get('/invoice-states')
@signature([models.InvoiceState], [Query])
def list_invoice_states(q=[]):
    criterion = _query_to_criterion(q)

    rows = central_api.list_invoice_states(
        request.environ['context'], criterion=criterion)

    return map(models.InvoiceState.from_db, rows)


@bp.get('/invoice-states/<state_id>')
@signature(models.InvoiceState, str,)
def get_invoice_state(state_id):
    row = central_api.get_invoice_state(request.environ['context'],
                                        state_id)

    return models.InvoiceState.from_db(row)


@bp.put('/invoice-states/<state_id>')
@signature(models.InvoiceState, str, body=models.InvoiceState)
def update_invoice_state(state_id, body):
    row = central_api.update_invoice_state(
        request.environ['context'],
        state_id,
        body.to_db())

    return models.InvoiceState.from_db(row)


@bp.delete('/invoice-states/<state_id>')
def delete_invoice_state(state_id):
    central_api.delete_invoice_state(
        request.environ['context'],
        state_id)
    return Response(status=204)


# merchants
@bp.post('/merchants')
@signature(models.Merchant, body=models.Merchant)
def create_merchant(body):
    row = central_api.create_merchant(request.environ['context'],
                                      body.to_db())

    return models.Merchant.from_db(row)


@bp.get('/merchants')
@signature([models.Merchant], [Query])
def list_merchants(q=[]):
    criterion = _query_to_criterion(q)

    rows = central_api.list_merchants(
        request.environ['context'], criterion=criterion)

    return map(models.Merchant.from_db, rows)


@bp.get('/merchants/<merchant_id>')
@signature(models.Merchant, str)
def get_merchant(merchant_id):
    row = central_api.get_merchant(request.environ['context'],
                                   merchant_id)

    return models.Merchant.from_db(row)


@bp.put('/merchants/<merchant_id>')
@signature(models.Merchant, str, body=models.Merchant)
def update_merchant(merchant_id, body):
    row = central_api.update_merchant(
        request.environ['context'],
        merchant_id,
        body.to_db())

    return models.Merchant.from_db(row)


@bp.delete('/merchants/<merchant_id>')
def delete_merchant(merchant_id):
    central_api.delete_merchant(request.environ['context'], merchant_id)
    return Response(status=204)


# Invoices
@bp.post('/merchants/<merchant_id>/payment-gateways')
@signature(models.PGConfig, str, body=models.PGConfig)
def create_payment_gateway(merchant_id, body):
    row = central_api.create_pg_config(
        request.environ['context'],
        merchant_id,
        body.to_db())

    return models.PGConfig.from_db(row)


@bp.get('/merchants/<merchant_id>/payment-gateways')
@signature([models.PGConfig], str, [Query])
def list_payment_gateways(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = central_api.list_pg_configs(
        request.environ['context'], criterion=criterion)

    return map(models.PGConfig.from_db, rows)


@bp.get('/merchants/<merchant_id>/payment-gateways/<pg_config_id>')
@signature(models.PGConfig, str, str)
def get_payment_gateway(merchant_id, pg_config_id):
    row = central_api.get_pg_config(request.environ['context'], pg_config_id)

    return models.PGConfig.from_db(row)


@bp.put('/merchants/<merchant_id>/payment-gateways/<pg_config_id>')
@signature(models.PGConfig, str, str, body=models.PGConfig)
def update_payment_gateway(merchant_id, pg_config_id, body):
    row = central_api.update_pg_config(
        request.environ['context'],
        pg_config_id,
        body.to_db())

    return models.PGConfig.from_db(row)


@bp.delete('/merchants/<merchant_id>/payment-gateways/<pg_config_id>')
def delete_pg_config(merchant_id, pg_config_id):
    central_api.delete_pg_config(
        request.environ['context'],
        pg_config_id)
    return Response(status=204)


# customers
@bp.post('/merchants/<merchant_id>/customers')
@signature(models.Customer, str, body=models.Customer)
def create_customer(merchant_id, body):
    row = central_api.create_customer(
        request.environ['context'],
        merchant_id,
        body.to_db())

    return models.Customer.from_db(row)


@bp.get('/merchants/<merchant_id>/customers')
@signature([models.Customer], str, [Query])
def list_customers(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = central_api.list_customers(
        request.environ['context'], criterion=criterion)

    return map(models.Customer.from_db, rows)


@bp.get('/merchants/<merchant_id>/customers/<customer_id>')
@signature(models.Customer, str, str)
def get_customer(merchant_id, customer_id):
    row = central_api.get_customer(request.environ['context'],
                                   customer_id)

    return models.Customer.from_db(row)


@bp.put('/merchants/<merchant_id>/customers/<customer_id>')
@signature(models.Customer, str, str, body=models.Customer)
def update_customer(merchant_id, customer_id, body):
    row = central_api.update_customer(
        request.environ['context'],
        customer_id,
        body.to_db())

    return models.Customer.from_db(row)


@bp.delete('/merchants/<merchant_id>/customers/<customer_id>')
def delete_customer(merchant_id, customer_id):
    central_api.delete_customer(request.environ['context'], customer_id)
    return Response(status=204)


# PaymentMethods
@bp.post('/merchants/<merchant_id>/customers/<customer_id>/payment-methods')
@signature(models.PaymentMethod, str, str, body=models.PaymentMethod)
def create_payment_method(merchant_id, customer_id, body):
    row = central_api.create_payment_method(
        request.environ['context'],
        customer_id,
        body.to_db())

    return models.PaymentMethod.from_db(row)


@bp.get('/merchants/<merchant_id>/customers/<customer_id>/payment-methods')
@signature([models.PaymentMethod], str, str, [Query])
def list_payment_methods(merchant_id, customer_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id,
                                    customer_id=customer_id)

    rows = central_api.list_payment_methods(
        request.environ['context'], criterion=criterion)

    return map(models.PaymentMethod.from_db, rows)


@bp.get('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/'
        '<pm_id>')
@signature(models.PaymentMethod, str, str, str)
def get_payment_method(merchant_id, customer_id, pm_id):
    row = central_api.get_payment_method(request.environ['context'], pm_id)

    return models.PaymentMethod.from_db(row)


@bp.put('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/'
        '<pm_id>')
@signature(models.PaymentMethod, str, str, str, body=models.PaymentMethod)
def update_payment_method(merchant_id, customer_id, pm_id, body):
    row = central_api.update_payment_method(request.environ['context'], pm_id,
                                            body.to_db())

    return models.PaymentMethod.from_db(row)


@bp.delete('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/'
           '<pm_id>')
def delete_payment_method(merchant_id, customer_id, pm_id):
    central_api.delete_payment_method(request.environ['context'], pm_id)
    return Response(status=204)


# Plans
@bp.post('/merchants/<merchant_id>/plans')
@signature(models.Plan, str, body=models.Plan)
def create_plan(merchant_id, body):
    row = central_api.create_plan(
        request.environ['context'],
        merchant_id,
        body.to_db())

    return models.Plan.from_db(row)


@bp.get('/merchants/<merchant_id>/plans')
@signature([models.Plan], str, [Query])
def list_plans(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = central_api.list_plans(
        request.environ['context'], criterion=criterion)

    return map(models.Plan.from_db, rows)


@bp.get('/merchants/<merchant_id>/plans/<plan_id>')
@signature(models.Plan, str, str)
def get_plan(merchant_id, plan_id):
    row = central_api.get_plan(request.environ['context'],
                               plan_id)

    return models.Plan.from_db(row)


@bp.put('/merchants/<merchant_id>/plans/<plan_id>')
@signature(models.Plan, str, str, body=models.Plan)
def update_plan(merchant_id, plan_id, body):
    row = central_api.update_plan(
        request.environ['context'],
        plan_id,
        body.to_db())

    return models.Plan.from_db(row)


@bp.delete('/merchants/<merchant_id>/plans/<plan_id>')
def delete_plan(merchant_id, plan_id):
    central_api.delete_plan(request.environ['context'], plan_id)
    return Response(status=204)


# Plan Item
@bp.put('/merchants/<merchant_id>/plans/<plan_id>/items/<product_id>')
@signature(models.PlanItem, str, str, str)
def add_plan_item(merchant_id, plan_id, product_id):
    values = {
        'plan_id': plan_id,
        'product_id': product_id
    }

    row = central_api.create_plan_item(request.environ['context'], values)

    return models.PlanItem.from_db(row)


@bp.patch('/merchants/<merchant_id>/plans/<plan_id>/items/<product_id>')
@signature(models.PlanItem, str, str, str, body=models.PlanItem)
def update_plan_item(merchant_id, plan_id, product_id, body):
    row = central_api.update_plan_item(
        request.environ['context'], plan_id, product_id, body.to_db())

    return models.PlanItem.from_db(row)


@bp.delete('/merchants/<merchant_id>/plans/<plan_id>/items/<product_id>')
def delete_plan_item(merchant_id, plan_id, product_id):
    central_api.delete_plan_item(request.environ['context'],
                                 plan_id, product_id)
    return Response(status=204)


# Products
@bp.post('/merchants/<merchant_id>/products')
@signature(models.Product, str, body=models.Product)
def create_product(merchant_id, body):
    row = central_api.create_product(
        request.environ['context'],
        merchant_id,
        body.to_db())

    return models.Product.from_db(row)


@bp.get('/merchants/<merchant_id>/products')
@signature([models.Product], str, [Query])
def list_products(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = central_api.list_products(
        request.environ['context'], criterion=criterion)

    return map(models.Product.from_db, rows)


@bp.get('/merchants/<merchant_id>/products/<product_id>')
@signature(models.Product, str, str)
def get_product(merchant_id, product_id):
    row = central_api.get_product(request.environ['context'],
                                  product_id)

    return models.Product.from_db(row)


@bp.put('/merchants/<merchant_id>/products/<product_id>')
@signature(models.Product, str, str, body=models.Product)
def update_product(merchant_id, product_id, body):
    row = central_api.update_product(
        request.environ['context'],
        product_id,
        body.to_db())

    return models.Product.from_db(row)


@bp.delete('/merchants/<merchant_id>/products/<product_id>')
def delete_product(merchant_id, product_id):
    central_api.delete_product(request.environ['context'], product_id)
    return Response(status=204)


# Invoices
@bp.post('/merchants/<merchant_id>/invoices')
@signature(models.Invoice, str, body=models.Invoice)
def create_invoice(merchant_id, body):
    row = central_api.create_invoice(
        request.environ['context'],
        merchant_id,
        body.to_db())

    return models.Invoice.from_db(row)


@bp.get('/merchants/<merchant_id>/invoices')
@signature([models.InvoiceState], str, [Query])
def list_invoices(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = central_api.list_invoices(
        request.environ['context'], criterion=criterion)

    return map(models.Invoice.from_db, rows)


@bp.get('/merchants/<merchant_id>/invoices/<invoice_id>')
@signature(models.Invoice, str, str)
def get_invoice(merchant_id, invoice_id):
    row = central_api.get_invoice(request.environ['context'],
                                  invoice_id)

    return models.Invoice.from_db(row)


@bp.put('/merchants/<merchant_id>/invoices/<invoice_id>')
@signature(models.Invoice, str, str, body=models.Invoice)
def update_invoice(merchant_id, invoice_id, body):
    row = central_api.update_invoice(
        request.environ['context'],
        invoice_id,
        body.to_db())

    return models.Invoice.from_db(row)


@bp.delete('/merchants/<merchant_id>/invoices/<invoice_id>')
def delete_invoice(merchant_id, invoice_id):
    central_api.delete_invoice(request.environ['context'], invoice_id)
    return Response(status=204)


# Products
@bp.post('/merchants/<merchant_id>/invoices/<invoice_id>/lines')
@signature(models.InvoiceLine, str, str, body=models.InvoiceLine)
def create_invoice_line(merchant_id, invoice_id, body):
    row = central_api.create_invoice_line(
        request.environ['context'],
        invoice_id,
        body.to_db())

    return models.Product.from_db(row)


@bp.get('/merchants/<merchant_id>/invoices/<invoice_id>/lines')
@signature([models.InvoiceLine], str, str, [Query])
def list_invoice_lines(merchant_id, invoice_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id,
                                    invoice_id=invoice_id)

    rows = central_api.list_invoice_lines(
        request.environ['context'], criterion=criterion)

    return map(models.Product.from_db, rows)


@bp.get('/merchants/<merchant_id>/invoices/<invoice_id>/lines/<line_id>')
@signature(models.InvoiceLine, str, str, str)
def get_invoice_line(merchant_id, invoice_id, line_id):
    row = central_api.get_invoice_line(request.environ['context'],
                                       line_id)

    return models.Product.from_db(row)


@bp.put('/merchants/<merchant_id>/invoices/<invoice_id>/lines/<line_id>')
@signature(models.InvoiceLine, str, str, str, body=models.InvoiceLine)
def update_invoice_line(merchant_id, invoice_id, line_id, body):
    row = central_api.update_invoice_line(
        request.environ['context'],
        line_id,
        body.as_dict())

    return models.Product.from_db(row)


@bp.delete('/merchants/<merchant_id>/invoices/<invoice_id>/lines/<line_id>')
def delete_invoice_line(merchant_id, invoice_id, line_id):
    central_api.delete_invoice_line(request.environ['context'], line_id)
    return Response(status=204)


# Subscription
@bp.post('/merchants/<merchant_id>/subscriptions')
@signature(models.Subscription, str, body=models.Subscription)
def create_subscription(merchant_id, body):
    row = central_api.create_subscription(
        request.environ['context'],
        body.to_db())

    return models.Subscription.from_db(row)


@bp.get('/merchants/<merchant_id>/subscriptions')
@signature([models.Subscription], str, [Query])
def list_subscriptions(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = central_api.list_subscriptions(
        request.environ['context'], criterion=criterion)

    return map(models.Subscription.from_db, rows)


@bp.get('/merchants/<merchant_id>/subscriptions/<subscription_id>')
@signature(models.Subscription, str, str)
def get_subscription(merchant_id, subscription_id):
    row = central_api.get_subscription(request.environ['context'],
                                       subscription_id)

    return models.Subscription.from_db(row)


@bp.put('/merchants/<merchant_id>/subscriptions/<subscription_id>')
@signature(models.Subscription, str, str, body=models.Subscription)
def update_subscription(merchant_id, subscription_id, body):
    row = central_api.update_subscription(
        request.environ['context'],
        subscription_id,
        body.to_db())

    return models.Subscription.from_db(row)


@bp.delete('/merchants/<merchant_id>/subscriptions/<subscription_id>')
def delete_subscription(merchant_id, subscription_id):
    central_api.delete_subscription(
        request.environ['context'],
        subscription_id)
    return Response(status=204)


# Usage
@bp.post('/merchants/<merchant_id>/usage')
@signature(models.Usage, str, body=models.Usage)
def create_usage(merchant_id, body):
    values = body.to_db()

    values['merchant_id'] = merchant_id
    row = rater_api.create_usage(request.environ['context'], values)

    return models.Usage.from_db(row)


@bp.get('/merchants/<merchant_id>/usage')
@signature([models.Usage], str, [Query])
def list_usages(merchant_id, q=[]):
    criterion = _query_to_criterion(q, merchant_id=merchant_id)

    rows = rater_api.list_usages(
        request.environ['context'], criterion=criterion)

    return map(models.Usage.from_db, rows)


@bp.get('/merchants/<merchant_id>/usage/<usage_id>')
@signature([models.Usage], str, str)
def get_usage(merchant_id, usage_id):
    row = rater_api.get_usage(request.environ['context'],
                              usage_id)

    return models.Usage.from_db(row)


@bp.put('/merchants/<merchant_id>/usage/<usage_id>')
@signature(models.Usage, str, str, body=models.Usage)
def update_usage(merchant_id, usage_id, body):
    row = rater_api.update_usage(
        request.environ['context'],
        usage_id,
        body.to_db())

    return models.Usage.from_db(row)


@bp.delete('/merchants/<merchant_id>/usage/<usage_id>')
def delete_usage(merchant_id, usage_id):
    rater_api.delete_usage(
        request.environ['context'],
        usage_id)
    return Response(status=204)
