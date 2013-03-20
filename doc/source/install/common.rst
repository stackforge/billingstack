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


.. _system-deps::

System dependencies
===================

.. index::
   double: installing; common_steps

.. note::
   The below operations should take place underneath your <project> folder.

Install module dependencies

Debian, Ubuntu::

   $ apt-get install python-pip python-lxml

Fedora, Centos, RHEL::

   $ yum install pip-python python-lxml


.. _storage-deps::

Storage dependencies
====================

.. index:: installing; storage

Depending on the datastore that is currently supported and your pick of them
you need to install the underlying server and client libraries as well as
python bindings.

See `System dependencies`_ before continuing.

Example for MySQL on Debian, Ubuntu::

   $ apt-get install mysql-server mysql-client libmysqlclient-dev

Using MySQL bindings::

   $ pip install MySQL-python

Using oursql bindings (use 'mysql+oursql://.....' instead of 'mysql://')::

   $ pip install oursql


.. _cloning-git::


Cloning git repo
================
1. Install GIT.

   On ubuntu you do the following::

      $ apt-get install git-core

   On Fedora / Centos / RHEL::

      $ apt-get install git

2. Clone a BS repo off of Github::

   $ git clone https://github.com/billingstack/<project repo>
   $ cd <project repo>

3. Now continue with whatever other thing needs to be setup.