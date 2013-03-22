from flask import request


from billingstack.api.base import Rest, render, request_data
from billingstack.api.v1 import models
from billingstack.central.rpcapi import central_api


bp = Rest('v1', __name__)


@bp.get('/')
def index():
    return render()


# Currencies
@bp.post('/currencies')
def create_currency():
    data = request_data(models.Currency)

    row = central_api.create_currency(request.environ['context'], data)

    return render(models.Currency.from_db(row))


@bp.get('/currencies')
def list_currencies():
    rows = central_api.list_currencies(request.environ['context'])

    return render([models.Currency.from_db(r) for r in rows])


@bp.get('/currencies/<currency_id>')
def get_currency(currency_id):
    row = central_api.get_currency(request.environ['context'],
                                   currency_id)

    return render(models.Currency.from_db(row))


@bp.put('/currencies/<currency_id>')
def update_currency(currency_id):
    data = request_data(models.Currency)

    row = central_api.update_currency(
        request.environ['context'],
        currency_id,
        data)

    return render(models.Currency.from_db(row))


@bp.delete('/currencies/<currency_id>')
def delete_currency(currency_id):
    central_api.delete_currency(request.environ['context'], currency_id)
    return render()


# Language
@bp.post('/languages')
def create_language():
    data = request_data(models.Language)

    row = central_api.create_language(request.environ['context'], data)

    return render(models.Language.from_db(row))


@bp.get('/languages')
def list_languages():
    rows = central_api.list_languages(request.environ['context'])

    return render([models.Language.from_db(r) for r in rows])


@bp.get('/languages/<language_id>')
def get_language(language_id):
    row = central_api.get_language(request.environ['context'],
                                   language_id)

    return render(models.Language.from_db(row))


@bp.put('/languages/<language_id>')
def update_language(language_id):
    data = request_data(models.Language)

    row = central_api.update_language(
        request.environ['context'],
        language_id,
        data)

    return render(models.Language.from_db(row))


@bp.delete('/languages/<language_id>')
def delete_language(language_id):
    central_api.delete_language(request.environ['context'], language_id)
    return render()


# PGP / PGM
@bp.get('/payment-gateway-providers')
def list_pg_providers():
    rows = central_api.list_pg_provider(request.environ['context'])

    return render([models.PGProvider.from_db(r) for r in rows])


@bp.get('/payment-gateway-methods')
def list_pg_methods():
    rows = central_api.list_pg_methods(request.environ['context'])

    return render([models.PGMethod.from_db(r) for r in rows])


# invoice_states
@bp.post('/invoice-states')
def create_invoice_state():
    data = request_data(models.InvoiceState)

    row = central_api.create_invoice_state(request.environ['context'], data)

    return render(models.InvoiceState.from_db(row))


@bp.get('/invoice-states')
def list_invoice_states():
    rows = central_api.list_invoice_states(request.environ['context'])

    return render([models.InvoiceState.from_db(r) for r in rows])


@bp.get('/invoice-states/<state_id>')
def get_invoice_state(state_id):
    row = central_api.get_invoice_state(request.environ['context'],
                                        state_id)

    return render(models.InvoiceState.from_db(row))


@bp.put('/invoice-states/<state_id>')
def update_invoice_state(state_id):
    data = request_data(models.InvoiceState)

    row = central_api.update_invoice_state(
        request.environ['context'],
        state_id,
        data)

    return render(models.InvoiceState.from_db(row))


@bp.delete('/invoice-states/<state_id>')
def delete_invoice_state(state_id):
    central_api.delete_invoice_state(
        request.environ['context'],
        state_id)
    return render()


# merchants
@bp.post('/merchants')
def create_merchant():
    data = request_data(models.Merchant)

    row = central_api.create_merchant(request.environ['context'], data)

    return render(models.Merchant.from_db(row))


@bp.get('/merchants')
def list_merchants():
    rows = central_api.list_merchants(request.environ['context'])

    return render([models.Merchant.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>')
def get_merchant(merchant_id):
    row = central_api.get_merchant(request.environ['context'],
                                   merchant_id)

    return render(models.Merchant.from_db(row))


@bp.put('/merchants/<merchant_id>')
def update_merchant(merchant_id):
    data = request_data(models.Merchant)

    row = central_api.update_merchant(
        request.environ['context'],
        merchant_id,
        data)

    return render(models.Merchant.from_db(row))


@bp.delete('/merchants/<merchant_id>')
def delete_merchant(merchant_id):
    central_api.delete_merchant(request.environ['context'], merchant_id)
    return render()


# Invoices
@bp.post('/merchants/<merchant_id>/invoices')
def create_payment_gateway(merchant_id):
    data = request_data(models.Invoice)

    row = central_api.create_pg_config(
        request.environ['context'],
        merchant_id,
        data)

    return render(models.Invoice.from_db(row))


@bp.get('/merchants/<merchant_id>/payment-gateways')
def list_payment_gateways(merchant_id):
    rows = central_api.list_pg_config(request.environ['context'])

    return render([models.Invoice.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/payment-gateways/<pg_config_id>')
def get_payment_gateway(merchant_id, pg_config_id):
    row = central_api.get_pg_config(request.environ['context'], pg_config_id)

    return render(models.Invoice.from_db(row))


@bp.put('/merchants/<merchant_id>/payment-gateways/<pg_config_id>')
def update_payment_gateway(merchant_id, pg_config_id):
    data = request_data(models.Invoice)

    row = central_api.update_pg_config(
        request.environ['context'],
        pg_config_id,
        data)

    return render(models.Invoice.from_db(row))


@bp.delete('/merchants/<merchant_id>/payment-gateways/<pg_config_id>')
def delete_pg_config(merchant_id, pg_config_id):
    central_api.delete_pg_config(
        request.environ['context'],
        pg_config_id)
    return render()


# customers
@bp.post('/merchants/<merchant_id>/customers')
def create_customer(merchant_id):
    data = request_data(models.Customer)

    row = central_api.create_customer(
        request.environ['context'],
        merchant_id,
        data)

    return render(models.Customer.from_db(row))


@bp.get('/merchants/<merchant_id>/customers')
def list_customers(merchant_id):
    rows = central_api.list_customers(request.environ['context'])

    return render([models.Customer.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/customers/<customer_id>')
def get_customer(merchant_id, customer_id):
    row = central_api.get_customer(request.environ['context'],
                                   customer_id)

    return render(models.Customer.from_db(row))


@bp.put('/merchants/<merchant_id>/customers/<customer_id>')
def update_customer(merchant_id, customer_id):
    data = request_data(models.Customer)

    row = central_api.update_customer(
        request.environ['context'],
        customer_id,
        data)

    return render(models.Customer.from_db(row))


@bp.delete('/merchants/<merchant_id>/customers/<customer_id>')
def delete_customer(merchant_id, customer_id):
    central_api.delete_customer(request.environ['context'], customer_id)
    return render()


# PaymentMethods
@bp.post('/merchants/<merchant_id>/customers/<customer_id>/payment-methods')
def create_payment_method(merchant_id, customer_id):
    data = request_data(models.PaymentMethod)

    row = central_api.create_payment_method(
        request.environ['context'],
        customer_id,
        data)

    return render(models.PaymentMethod.from_db(row))


@bp.get('/merchants/<merchant_id>/customers/<customer_id>/payment-methods')
def list_payment_methods(merchant_id, customer_id):
    rows = central_api.list_payment_methods(request.environ['context'])

    return render([models.PaymentMethod.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/'
        '<pm_id>')
def get_payment_method(merchant_id, customer_id, pm_id):
    row = central_api.get_payment_method(request.environ['context'], pm_id)

    return render(models.PaymentMethod.from_db(row))


@bp.put('/merchants/<merchant_id>/customers/<customer_id>')
def update_payment_method(merchant_id, customer_id, pm_id):
    data = request_data(models.PaymentMethod)

    row = central_api.update_payment_method(request.environ['context'], pm_id,
                                            data)

    return render(models.PaymentMethod.from_db(row))


@bp.delete('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/'
           '<pm_id>')
def delete_payment_method(merchant_id, customer_id, pm_id):
    central_api.delete_payment_method(request.environ['context'], pm_id)
    return render()


# Plans
@bp.post('/merchants/<merchant_id>/plans')
def create_plan(merchant_id):
    data = request_data(models.Plan)

    row = central_api.create_plan(
        request.environ['context'],
        merchant_id,
        data)

    return render(models.Plan.from_db(row))


@bp.get('/merchants/<merchant_id>/plans')
def list_plans(merchant_id):
    rows = central_api.list_plans(request.environ['context'])

    return render([models.Plan.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/plans/<plan_id>')
def get_plan(merchant_id, plan_id):
    row = central_api.get_plan(request.environ['context'],
                               plan_id)

    return render(models.Plan.from_db(row))


@bp.put('/merchants/<merchant_id>/plans/<plan_id>')
def update_plan(merchant_id, plan_id):
    data = request_data(models.Plan)

    row = central_api.update_plan(
        request.environ['context'],
        plan_id,
        data)

    return render(models.Plan.from_db(row))


@bp.delete('/merchants/<merchant_id>/plans/<plan_id>')
def delete_plan(merchant_id, plan_id):
    central_api.delete_plan(request.environ['context'], plan_id)
    return render()


# Products
@bp.post('/merchants/<merchant_id>/products')
def create_product(merchant_id):
    data = request_data(models.Product)

    row = central_api.create_product(
        request.environ['context'],
        merchant_id,
        data)

    return render(models.Product.from_db(row))


@bp.get('/merchants/<merchant_id>/products')
def list_products(merchant_id):
    rows = central_api.list_products(request.environ['context'])

    return render([models.Product.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/products/<product_id>')
def get_product(merchant_id, product_id):
    row = central_api.get_product(request.environ['context'],
                                  product_id)

    return render(models.Product.from_db(row))


@bp.put('/merchants/<merchant_id>/products/<product_id>')
def update_product(merchant_id, product_id):
    data = request_data(models.Product)

    row = central_api.update_product(
        request.environ['context'],
        product_id,
        data)

    return render(models.Product.from_db(row))


@bp.delete('/merchants/<merchant_id>/products/<product_id>')
def delete_product(merchant_id, product_id):
    central_api.delete_product(request.environ['context'], product_id)
    return render()


# Invoices
@bp.post('/merchants/<merchant_id>/invoices')
def create_invoice(merchant_id):
    data = request_data(models.Invoice)

    row = central_api.create_invoice(
        request.environ['context'],
        merchant_id,
        data)

    return render(models.Invoice.from_db(row))


@bp.get('/merchants/<merchant_id>/invoices')
def list_invoices(merchant_id):
    rows = central_api.list_invoices(request.environ['context'])

    return render([models.Invoice.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/invoices/<invoice_id>')
def get_invoice(merchant_id, invoice_id):
    row = central_api.get_invoice(request.environ['context'],
                                  invoice_id)

    return render(models.Invoice.from_db(row))


@bp.put('/merchants/<merchant_id>/invoices/<invoice_id>')
def update_invoice(merchant_id, invoice_id):
    data = request_data(models.Invoice)

    row = central_api.update_invoice(
        request.environ['context'],
        invoice_id,
        data)

    return render(models.Invoice.from_db(row))


# Products
@bp.post('/merchants/<merchant_id>/invoices/<invoice_id>/lines')
def create_invoice_line(merchant_id, invoice_id):
    data = request_data(models.Product)

    row = central_api.create_invoice_line(
        request.environ['context'],
        invoice_id,
        data)

    return render(models.Product.from_db(row))


@bp.get('/merchants/<merchant_id>/invoices/<invoice_id>/lines')
def list_invoice_lines(merchant_id, invoice_id):
    rows = central_api.list_invoice_lines(request.environ['context'])

    return render([models.Product.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/invoices/<invoice_id>/lines/<line_id>')
def get_invoice_line(merchant_id, invoice_id, line_id):
    row = central_api.get_invoice_line(request.environ['context'],
                                       line_id)

    return render(models.Product.from_db(row))


@bp.put('/merchants/<merchant_id>/invoices/<invoice_id>/lines/<line_id>')
def update_invoice_line(merchant_id, invoice_id, line_id):
    data = request_data(models.Product)

    row = central_api.update_invoice_line(
        request.environ['context'],
        line_id,
        data)

    return render(models.Product.from_db(row))


@bp.delete('/merchants/<merchant_id>/invoices/<invoice_id>/lines/<line_id>')
def delete_invoice_line(merchant_id, invoice_id, line_id):
    central_api.delete_invoice_line(request.environ['context'], line_id)
    return render()


@bp.delete('/merchants/<merchant_id>/invoices/<invoice_id>')
def delete_invoice(merchant_id, invoice_id):
    central_api.delete_invoice(request.environ['context'], invoice_id)
    return render()


# Subscription
@bp.post('/merchants/<merchant_id>/subscriptions')
def create_subscription(merchant_id):
    data = request_data(models.Subscription)

    row = central_api.create_subscription(
        request.environ['context'],
        data)

    return render(models.Subscription.from_db(row))


@bp.get('/merchants/<merchant_id>/subscriptions')
def list_subscriptions(merchant_id):
    rows = central_api.list_subscriptions(request.environ['context'])

    return render([models.Subscription.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/subscriptions/<subscription_id>')
def get_subscription(merchant_id, subscription_id):
    row = central_api.get_subscription(request.environ['context'],
                                       subscription_id)

    return render(models.Subscription.from_db(row))


@bp.put('/merchants/<merchant_id>/subscriptions/<subscription_id>')
def update_subscription(merchant_id, subscription_id):
    data = request_data(models.Subscription)

    row = central_api.update_subscription(
        request.environ['context'],
        subscription_id,
        data)

    return render(models.Subscription.from_db(row))


@bp.delete('/merchants/<merchant_id>/subscriptions/<subscription_id>')
def delete_subscription(merchant_id, subscription_id):
    central_api.delete_subscription(
        request.environ['context'],
        subscription_id)
    return render()


# Usage
@bp.post('/merchants/<merchant_id>/subscriptions/<subscription_id>/usage')
def create_usage(merchant_id, subscription_id):
    data = request_data(models.Usage)

    row = central_api.create_usage(
        request.environ['context'],
        subscription_id,
        data)

    return render(models.Usage.from_db(row))


@bp.get('/merchants/<merchant_id>/subscriptions/<subscription_id>/usage')
def list_usages(merchant_id, subscription_id):
    rows = central_api.list_usages(request.environ['context'])

    return render([models.Usage.from_db(r) for r in rows])


@bp.get('/merchants/<merchant_id>/subscriptions/subscription_id>/usage/'
        '<usage_id>')
def get_usage(merchant_id, subscription_id, usage_id):
    row = central_api.get_usage(request.environ['context'],
                                usage_id)

    return render(models.Invoice.from_db(row))


@bp.put('/merchants/<merchant_id>/subscriptions/<subscription_id>/usage/'
        '<usage_id>')
def update_usage(merchant_id, subscription_id, usage_id):
    data = request_data(models.Usage)

    row = central_api.update_usage(
        request.environ['context'],
        usage_id,
        data)

    return render(models.Usage.from_db(row))


@bp.delete('/merchants/<merchant_id>/subscriptions/<subscription_id>/usage/'
           '<usage_id>')
def delete_usage(merchant_id, subscription_id, usage_id):
    central_api.delete_usage(
        request.environ['context'],
        usage_id)
    return render()
