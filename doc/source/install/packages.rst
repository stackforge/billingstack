..
      Copyright 2013 Endre Karlson <endre.karlson@gmail.com>

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.



=====================
 Installing Packages
=====================

Common Steps
============

.. index::
   double: installing; common_steps


1. apt-get install python-software-properties
2. apt-add-repository ppa:openstack-ubuntu-testing/grizzly-trunk-testing
3. echo "deb http://cloudistic.me/packages precise main" > /etc/apt/sources.list.d/billingstack.list
4. wget -q http://cloudistic.me/packages/pubkey.gpg -O- | apt-key add -
5. apt-get update
6. apt-get install billingstack-central billingstack-api