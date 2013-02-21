# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Woorea Solutions, S.L
#
# Author: Luis Gervaso <luis@woorea.es>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import flask

from billingstack.openstack.common import log

LOG = log.getLogger(__name__)


blueprint = flask.Blueprint('v1', __name__,
                            template_folder='templates',
                            static_folder='static')


def request_wants_html():
    best = flask.request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'text/html' and \
        flask.request.accept_mimetypes[best] > \
        flask.request.accept_mimetypes['application/json']
        
## APIs for working with languages.

@blueprint.route('/languages', methods=('GET'))
def language_list():
    """Return a list of languages.
    """
    rq = flask.request
    languages = rq.storage_conn.language_list()
    return flask.jsonify(list(languages))

@blueprint.route('/languages', methods=('POST'))
def language_create():
    """Return a list of languages.
    """
    rq = flask.request
    language = rq.storage_conn.language_add(rq.json)
    return flask.jsonify(language)


@blueprint.route('/languages/<language_id>', methods=('GET'))
def language_show(language_id):
    """Return a language by ID

    :param language_id: The ID of the resource.
    """
    rq = flask.request
    language = rq.storage_conn.languages_get(language_id)
    return flask.jsonify(language)

@blueprint.route('/languages/<language_id>', methods=('PUT'))
def language_update(language_id):
    """Update a a language.
    """
    rq = flask.request
    language = rq.storage_conn.language_update(language_id, rq.json)
    return flask.jsonify(language)


@blueprint.route('/languages/<language_id>', methods=('DELETE'))
def language_delete(language_id):
    """Deletes a language by ID

    :param language_id: The ID of the language.
    """
    rq = flask.request
    rq.storage_conn.language_delete(language_id)
    

## APIs for working with currencys.

@blueprint.route('/currencys', methods=('GET'))
def currency_list():
    """Return a list of currencys.
    """
    rq = flask.request
    currencys = rq.storage_conn.currency_list()
    return flask.jsonify(list(currencys))

@blueprint.route('/currencys', methods=('POST'))
def currency_create():
    """Return a list of currencys.
    """
    rq = flask.request
    currency = rq.storage_conn.currency_add(rq.json)
    return flask.jsonify(currency)


@blueprint.route('/currencys/<currency_id>', methods=('GET'))
def currency_show(currency_id):
    """Return a currency by ID

    :param currency_id: The ID of the resource.
    """
    rq = flask.request
    currency = rq.storage_conn.currencys_get(currency_id)
    return flask.jsonify(currency)

@blueprint.route('/currencys/<currency_id>', methods=('PUT'))
def currency_update(currency_id):
    """Update a a currency.
    """
    rq = flask.request
    currency = rq.storage_conn.currency_update(currency_id, rq.json)
    return flask.jsonify(currency)


@blueprint.route('/currencys/<currency_id>', methods=('DELETE'))
def currency_delete(currency_id):
    """Deletes a currency by ID

    :param currency_id: The ID of the currency.
    """
    rq = flask.request
    rq.storage_conn.currency_delete(currency_id)

        
## APIs for working with payment gateway providers.

@blueprint.route('/payment-gateway-providers', methods=('GET'))
def payment_gateway_provider_list():
    """Return a list of payment_gateway_providers.
    """
    rq = flask.request
    payment_gateway_providers = rq.storage_conn.payment_gateway_provider_list()
    return flask.jsonify(list(payment_gateway_providers))

@blueprint.route('/payment-gateway-providers', methods=('POST'))
def payment_gateway_provider_create():
    """Return a list of payment_gateway_providers.
    """
    rq = flask.request
    payment_gateway_provider = rq.storage_conn.payment_gateway_provider_add(rq.json)
    return flask.jsonify(payment_gateway_provider)


@blueprint.route('/payment-gateway-providers/<payment_gateway_provider_id>', methods=('GET'))
def payment_gateway_provider_show(payment_gateway_provider_id):
    """Return a payment_gateway_provider by ID

    :param payment_gateway_provider_id: The ID of the resource.
    """
    rq = flask.request
    payment_gateway_provider = rq.storage_conn.payment_gateway_providers_get(payment_gateway_provider_id)
    return flask.jsonify(payment_gateway_provider)

@blueprint.route('/payment-gateway-providers/<payment_gateway_provider_id>', methods=('PUT'))
def payment_gateway_provider_update(payment_gateway_provider_id):
    """Update a a payment_gateway_provider.
    """
    rq = flask.request
    payment_gateway_provider = rq.storage_conn.payment_gateway_provider_update(payment_gateway_provider_id, rq.json)
    return flask.jsonify(payment_gateway_provider)


@blueprint.route('/payment-gateway-providers/<payment_gateway_provider_id>', methods=('DELETE'))
def payment_gateway_provider_delete(payment_gateway_provider_id):
    """Deletes a payment_gateway_provider by ID

    :param payment_gateway_provider_id: The ID of the payment_gateway_provider.
    """
    rq = flask.request
    rq.storage_conn.payment_gateway_provider_delete(payment_gateway_provider_id)

## APIs for working with merchants.

@blueprint.route('/merchants', methods=('GET'))
def merchant_list():
    """Return a list of merchants.
    """
    rq = flask.request
    merchants = rq.storage_conn.merchant_list()
    return flask.jsonify(list(merchants))

@blueprint.route('/merchants', methods=('POST'))
def merchant_create():
    """Return a list of merchants.
    """
    rq = flask.request
    merchant = rq.storage_conn.merchant_add(rq.json)
    return flask.jsonify(merchant)


@blueprint.route('/merchants/<merchant_id>', methods=('GET'))
def merchant_show(merchant_id):
    """Return a merchant by ID

    :param merchant_id: The ID of the resource.
    """
    rq = flask.request
    merchant = rq.storage_conn.merchants_get(merchant_id)
    return flask.jsonify(merchant)

@blueprint.route('/merchants/<merchant_id>', methods=('PUT'))
def merchant_update(merchant_id):
    """Update a a merchant.
    """
    rq = flask.request
    merchant = rq.storage_conn.merchant_update(merchant_id, rq.json)
    return flask.jsonify(merchant)


@blueprint.route('/merchants/<merchant_id>', methods=('DELETE'))
def merchant_delete(merchant_id):
    """Deletes a merchant by ID

    :param merchant_id: The ID of the merchant.
    """
    rq = flask.request
    rq.storage_conn.merchant_delete(merchant_id)
    
## APIs for working with merchant users.

@blueprint.route('/merchants/<merchant_id>/users', methods=('GET'))
def user_list(merchant_id):
    """Return a list of a merchant users.
    """
    rq = flask.request
    users = rq.storage_conn.user_list()
    return flask.jsonify(list(users))

@blueprint.route('/merchants/<merchant_id>/users', methods=('POST'))
def user_create(merchant_id):
    """Return a list of merchant users.
    """
    rq = flask.request
    user = rq.storage_conn.user_add(rq.json)
    return flask.jsonify(user)


@blueprint.route('/merchants/<merchant_id>/users/<user_id>', methods=('GET'))
def user_show(merchant_id, user_id):
    """Return a merchant user by ID

    :param user_id: The ID of the resource.
    """
    rq = flask.request
    user = rq.storage_conn.users_get(user_id)
    return flask.jsonify(user)

@blueprint.route('/merchants/<merchant_id>/users/<user_id>', methods=('PUT'))
def user_update(merchant_id, user_id):
    """Update a merchant user.
    """
    rq = flask.request
    user = rq.storage_conn.user_update(user_id, rq.json)
    return flask.jsonify(user)


@blueprint.route('/merchants/<merchant_id>/users/<user_id>', methods=('DELETE'))
def user_delete(merchant_id, user_id):
    """Deletes a merchant user by ID

    :param user_id: The ID of the user.
    """
    rq = flask.request
    rq.storage_conn.user_delete(user_id)
    
## APIs for working with merchant products.

@blueprint.route('/merchants/<merchant_id>/products', methods=('GET'))
def product_list(merchant_id):
    """Return a list of a merchant products.
    """
    rq = flask.request
    products = rq.storage_conn.product_list()
    return flask.jsonify(list(products))

@blueprint.route('/merchants/<merchant_id>/products', methods=('POST'))
def product_create(merchant_id):
    """Return a list of merchant products.
    """
    rq = flask.request
    product = rq.storage_conn.product_add(rq.json)
    return flask.jsonify(product)


@blueprint.route('/merchants/<merchant_id>/products/<product_id>', methods=('GET'))
def product_show(merchant_id, product_id):
    """Return a merchant product by ID

    :param product_id: The ID of the resource.
    """
    rq = flask.request
    product = rq.storage_conn.products_get(product_id)
    return flask.jsonify(product)

@blueprint.route('/merchants/<merchant_id>/products/<product_id>', methods=('PUT'))
def product_update(merchant_id, product_id):
    """Update a merchant product.
    """
    rq = flask.request
    product = rq.storage_conn.product_update(product_id, rq.json)
    return flask.jsonify(product)


@blueprint.route('/merchants/<merchant_id>/products/<product_id>', methods=('DELETE'))
def product_delete(merchant_id, product_id):
    """Deletes a merchant product by ID

    :param product_id: The ID of the product.
    """
    rq = flask.request
    rq.storage_conn.product_delete(product_id)
    
## APIs for working with merchant plans.

@blueprint.route('/merchants/<merchant_id>/plans', methods=('GET'))
def plan_list(merchant_id):
    """Return a list of a merchant plans.
    """
    rq = flask.request
    plans = rq.storage_conn.plan_list()
    return flask.jsonify(list(plans))

@blueprint.route('/merchants/<merchant_id>/plans', methods=('POST'))
def plan_create(merchant_id):
    """Return a list of merchant plans.
    """
    rq = flask.request
    plan = rq.storage_conn.plan_add(rq.json)
    return flask.jsonify(plan)


@blueprint.route('/merchants/<merchant_id>/plans/<plan_id>', methods=('GET'))
def plan_show(merchant_id, plan_id):
    """Return a merchant plan by ID

    :param plan_id: The ID of the resource.
    """
    rq = flask.request
    plan = rq.storage_conn.plans_get(plan_id)
    return flask.jsonify(plan)

@blueprint.route('/merchants/<merchant_id>/plans/<plan_id>', methods=('PUT'))
def plan_update(merchant_id, plan_id):
    """Update a merchant plan.
    """
    rq = flask.request
    plan = rq.storage_conn.plan_update(plan_id, rq.json)
    return flask.jsonify(plan)


@blueprint.route('/merchants/<merchant_id>/plans/<plan_id>', methods=('DELETE'))
def plan_delete(merchant_id, plan_id):
    """Deletes a merchant plan by ID

    :param plan_id: The ID of the plan.
    """
    rq = flask.request
    rq.storage_conn.plan_delete(plan_id)
    

## APIs for working with merchant plan items.

@blueprint.route('/merchants/<merchant_id>/plan/<plan_id>/items', methods=('GET'))
def plan_item_list(merchant_id):
    """Return a list of a merchant plan_items.
    """
    rq = flask.request
    plan_items = rq.storage_conn.plan_item_list()
    return flask.jsonify(list(plan_items))

@blueprint.route('/merchants/<merchant_id>/plan/<plan_id>/items', methods=('POST'))
def plan_item_create(merchant_id):
    """Return a list of merchant plan_items.
    """
    rq = flask.request
    plan_item = rq.storage_conn.plan_item_add(rq.json)
    return flask.jsonify(plan_item)


@blueprint.route('/merchants/<merchant_id>/plan/<plan_id>/items/<plan_item_id>', methods=('GET'))
def plan_item_show(merchant_id, plan_item_id):
    """Return a merchant plan_item by ID

    :param plan_item_id: The ID of the resource.
    """
    rq = flask.request
    plan_item = rq.storage_conn.plan_items_get(plan_item_id)
    return flask.jsonify(plan_item)

@blueprint.route('/merchants/<merchant_id>/plan/<plan_id>/items/<plan_item_id>', methods=('PUT'))
def plan_item_update(merchant_id, plan_item_id):
    """Update a merchant plan_item.
    """
    rq = flask.request
    plan_item = rq.storage_conn.plan_item_update(plan_item_id, rq.json)
    return flask.jsonify(plan_item)


@blueprint.route('/merchants/<merchant_id>/plan/<plan_id>/items/<plan_item_id>', methods=('DELETE'))
def plan_item_delete(merchant_id, plan_item_id):
    """Deletes a merchant plan_item by ID

    :param plan_item_id: The ID of the plan_item.
    """
    rq = flask.request
    rq.storage_conn.plan_item_delete(plan_item_id)
    
## APIs for working with merchant subscriptions.

@blueprint.route('/merchants/<merchant_id>/subscriptions', methods=('GET'))
def subscription_list(merchant_id):
    """Return a list of a merchant subscriptions.
    """
    rq = flask.request
    subscriptions = rq.storage_conn.subscription_list()
    return flask.jsonify(list(subscriptions))

@blueprint.route('/merchants/<merchant_id>/subscriptions', methods=('POST'))
def subscription_create(merchant_id):
    """Return a list of merchant subscriptions.
    """
    rq = flask.request
    subscription = rq.storage_conn.subscription_add(rq.json)
    return flask.jsonify(subscription)


@blueprint.route('/merchants/<merchant_id>/subscriptions/<subscription_id>', methods=('GET'))
def subscription_show(merchant_id, subscription_id):
    """Return a merchant subscription by ID

    :param subscription_id: The ID of the resource.
    """
    rq = flask.request
    subscription = rq.storage_conn.subscriptions_get(subscription_id)
    return flask.jsonify(subscription)

@blueprint.route('/merchants/<merchant_id>/subscriptions/<subscription_id>', methods=('PUT'))
def subscription_update(merchant_id, subscription_id):
    """Update a merchant subscription.
    """
    rq = flask.request
    subscription = rq.storage_conn.subscription_update(subscription_id, rq.json)
    return flask.jsonify(subscription)


@blueprint.route('/merchants/<merchant_id>/subscriptions/<subscription_id>', methods=('DELETE'))
def subscription_delete(merchant_id, subscription_id):
    """Deletes a merchant subscription by ID

    :param subscription_id: The ID of the subscription.
    """
    rq = flask.request
    rq.storage_conn.subscription_delete(subscription_id)
    
## APIs for working with merchant invoices.

@blueprint.route('/merchants/<merchant_id>/invoices', methods=('GET'))
def invoice_list(merchant_id):
    """Return a list of a merchant invoices.
    """
    rq = flask.request
    invoices = rq.storage_conn.invoice_list()
    return flask.jsonify(list(invoices))

@blueprint.route('/merchants/<merchant_id>/invoices', methods=('POST'))
def invoice_create(merchant_id):
    """Return a list of merchant invoices.
    """
    rq = flask.request
    invoice = rq.storage_conn.invoice_add(rq.json)
    return flask.jsonify(invoice)


@blueprint.route('/merchants/<merchant_id>/invoices/<invoice_id>', methods=('GET'))
def invoice_show(merchant_id, invoice_id):
    """Return a merchant invoice by ID

    :param invoice_id: The ID of the resource.
    """
    rq = flask.request
    invoice = rq.storage_conn.invoices_get(invoice_id)
    return flask.jsonify(invoice)

@blueprint.route('/merchants/<merchant_id>/invoices/<invoice_id>', methods=('PUT'))
def invoice_update(merchant_id, invoice_id):
    """Update a merchant invoice.
    """
    rq = flask.request
    invoice = rq.storage_conn.invoice_update(invoice_id, rq.json)
    return flask.jsonify(invoice)


@blueprint.route('/merchants/<merchant_id>/invoices/<invoice_id>', methods=('DELETE'))
def invoice_delete(merchant_id, invoice_id):
    """Deletes a merchant invoice by ID

    :param invoice_id: The ID of the invoice.
    """
    rq = flask.request
    rq.storage_conn.invoice_delete(invoice_id)
    
## APIs for working with merchant payment gateways.

@blueprint.route('/merchants/<merchant_id>/payment-gateways', methods=('GET'))
def payment_gateway_list(merchant_id):
    """Return a list of a merchant payment_gateways.
    """
    rq = flask.request
    payment_gateways = rq.storage_conn.payment_gateway_list()
    return flask.jsonify(list(payment_gateways))

@blueprint.route('/merchants/<merchant_id>/payment-gateways', methods=('POST'))
def payment_gateway_create(merchant_id):
    """Return a list of merchant payment_gateways.
    """
    rq = flask.request
    payment_gateway = rq.storage_conn.payment_gateway_add(rq.json)
    return flask.jsonify(payment_gateway)


@blueprint.route('/merchants/<merchant_id>/payment-gateways/<payment_gateway_id>', methods=('GET'))
def payment_gateway_show(merchant_id, payment_gateway_id):
    """Return a merchant payment_gateway by ID

    :param payment_gateway_id: The ID of the resource.
    """
    rq = flask.request
    payment_gateway = rq.storage_conn.payment_gateways_get(payment_gateway_id)
    return flask.jsonify(payment_gateway)

@blueprint.route('/merchants/<merchant_id>/payment-gateways/<payment_gateway_id>', methods=('PUT'))
def payment_gateway_update(merchant_id, payment_gateway_id):
    """Update a merchant payment_gateway.
    """
    rq = flask.request
    payment_gateway = rq.storage_conn.payment_gateway_update(payment_gateway_id, rq.json)
    return flask.jsonify(payment_gateway)


@blueprint.route('/merchants/<merchant_id>/payment-gateways/<payment_gateway_id>', methods=('DELETE'))
def payment_gateway_delete(merchant_id, payment_gateway_id):
    """Deletes a merchant payment_gateway by ID

    :param payment_gateway_id: The ID of the payment_gateway.
    """
    rq = flask.request
    rq.storage_conn.payment_gateway_delete(payment_gateway_id)


## APIs for working with merchant customers.

@blueprint.route('/merchants/<merchant_id>/customers', methods=('GET'))
def customer_list(merchant_id):
    """Return a list of a merchant customers.
    """
    rq = flask.request
    customers = rq.storage_conn.customer_list()
    return flask.jsonify(list(customers))

@blueprint.route('/merchants/<merchant_id>/customers', methods=('POST'))
def customer_create(merchant_id):
    """Return a list of merchant customers.
    """
    rq = flask.request
    customer = rq.storage_conn.customer_add(rq.json)
    return flask.jsonify(customer)


@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>', methods=('GET'))
def customer_show(merchant_id, customer_id):
    """Return a merchant customer by ID

    :param customer_id: The ID of the resource.
    """
    rq = flask.request
    customer = rq.storage_conn.customers_get(customer_id)
    return flask.jsonify(customer)

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>', methods=('PUT'))
def customer_update(merchant_id, customer_id):
    """Update a merchant customer.
    """
    rq = flask.request
    customer = rq.storage_conn.customer_update(customer_id, rq.json)
    return flask.jsonify(customer)


@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>', methods=('DELETE'))
def customer_delete(merchant_id, customer_id):
    """Deletes a merchant customer by ID

    :param customer_id: The ID of the customer.
    """
    rq = flask.request
    rq.storage_conn.customer_delete(customer_id)
    
## APIs for working with customers users.

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/users', methods=('GET'))
def customer_user_list(merchant_id):
    """Return a list of a merchant users.
    """
    rq = flask.request
    users = rq.storage_conn.user_list()
    return flask.jsonify(list(users))

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/users', methods=('POST'))
def customer_user_create(merchant_id):
    """Return a list of merchant users.
    """
    rq = flask.request
    user = rq.storage_conn.user_add(rq.json)
    return flask.jsonify(user)


@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/users/<user_id>', methods=('GET'))
def customer_user_show(merchant_id, user_id):
    """Return a merchant user by ID

    :param user_id: The ID of the resource.
    """
    rq = flask.request
    user = rq.storage_conn.users_get(user_id)
    return flask.jsonify(user)

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/users/<user_id>', methods=('PUT'))
def customer_user_update(merchant_id, user_id):
    """Update a merchant user.
    """
    rq = flask.request
    user = rq.storage_conn.user_update(user_id, rq.json)
    return flask.jsonify(user)


@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/users/<user_id>', methods=('DELETE'))
def customer_user_delete(merchant_id, user_id):
    """Deletes a merchant user by ID

    :param user_id: The ID of the user.
    """
    rq = flask.request
    rq.storage_conn.user_delete(user_id)
    
## APIs for working with customers payment_methods.

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/payment-methods', methods=('GET'))
def customer_payment_method_list(merchant_id):
    """Return a list of a merchant payment_methods.
    """
    rq = flask.request
    payment_methods = rq.storage_conn.payment_method_list()
    return flask.jsonify(list(payment_methods))

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/payment-methods', methods=('POST'))
def customer_payment_method_create(merchant_id):
    """Return a list of merchant payment_methods.
    """
    rq = flask.request
    payment_method = rq.storage_conn.payment_method_add(rq.json)
    return flask.jsonify(payment_method)


@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/<payment_method_id>', methods=('GET'))
def customer_payment_method_show(merchant_id, payment_method_id):
    """Return a merchant payment_method by ID

    :param payment_method_id: The ID of the resource.
    """
    rq = flask.request
    payment_method = rq.storage_conn.payment_methods_get(payment_method_id)
    return flask.jsonify(payment_method)

@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/<payment_method_id>', methods=('PUT'))
def customer_payment_method_update(merchant_id, payment_method_id):
    """Update a merchant payment_method.
    """
    rq = flask.request
    payment_method = rq.storage_conn.payment_method_update(payment_method_id, rq.json)
    return flask.jsonify(payment_method)


@blueprint.route('/merchants/<merchant_id>/customers/<customer_id>/payment-methods/<payment_method_id>', methods=('DELETE'))
def customer_payment_method_delete(merchant_id, payment_method_id):
    """Deletes a merchant payment_method by ID

    :param payment_method_id: The ID of the payment_method.
    """
    rq = flask.request
    rq.storage_conn.payment_method_delete(payment_method_id)