#!/usr/bin/env python
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
from setuptools import setup, find_packages
import textwrap
from billingstack.openstack.common import setup as common_setup

install_requires = common_setup.parse_requirements(['tools/pip-requires'])
install_options = common_setup.parse_requirements(['tools/pip-options'])
tests_require = common_setup.parse_requirements(['tools/test-requires'])
setup_require = common_setup.parse_requirements(['tools/setup-requires'])
dependency_links = common_setup.parse_dependency_links([
    'tools/pip-requires',
    'tools/pip-options',
    'tools/test-requires',
    'tools/setup-requires'
])

setup(
    name='billingstack',
    version=common_setup.get_version('billingstack'),
    description='Subscription based Billing in Python',
    author='Endre Karlson',
    author_email='endre.karlson@gmail.com',
    url='https://github/billingstack/billingstack',
    packages=find_packages(exclude=['bin']),
    include_package_data=True,
    test_suite='nose.collector',
    setup_requires=setup_require,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'optional': install_options,
    },
    dependency_links=dependency_links,
    scripts=[
        'bin/billingstack-api',
        'bin/billingstack-db-manage',
        'bin/billingstack-manage',
    ],
    cmdclass=common_setup.get_cmdclass(),
    entry_points=textwrap.dedent("""
        [billingstack.storage]
        sqlalchemy = billingstack.storage.impl_sqlalchemy:SQLAlchemyStorage

        [billingstack.payment_gateway]
        dummy = billingstack.payment_gateway.dummy:DummyProvider

        [billingstack.manage]
        pg-register = billingstack.manage.provider:ProvidersRegister
        pg-list = billingstack.manage.provider:ProvidersList
        """),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Finance :: Subscription Billing',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: OpenStack',
    ],
)
