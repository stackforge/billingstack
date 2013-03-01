billingstack
============

What is Billingstack?
BillingStack is a convergence of efforts done in the previous started Bufunfa
project and the BillingStack Grails (Java) version by Luis Gervaso. 

The goal is to provide a free alternative to anyone that has a need for a
subscription based billingsystem with features compared to other popular ones.


Features include:
* Plans - Collections of Products like Compute Gold or similar
* Products - A Compute server for example
* Merchants - Multi-Tenancy via Merchants where the Merchant is the Tenant of
              the application and can have multiple Customers, it's own
              settings etc.

* Plugin based Storage API - The Storage API is pluggable and other backends
              can be added.
* REST API - Currently based on Pecan for V1.


Installing
==========

1. git clone https://github.com/billingstack/billingstack
2. virtualenv .venv
3. pip install -r tools/test-requires -r tools/pip-options -r tools/pip-requires
4. python setup.py develop
5. Edit the config to your liking
   vi etc/billingstack/billingstack.conf
6. Run the API
   billingstack-api --config-file etc/billingstack/billingstack.conf
