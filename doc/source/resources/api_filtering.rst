..
    Copyright 2013 Endre Karlson <endre.karlson@gmail.com>
    Copyright 2013 Luis Gervaso <luis@woorea.es>

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.

.. _filtering:


==========================================
Filtering in the API (Internally and REST)
==========================================

.. index::
    double: api_filtering; brief


Filtering Operators
+++++++++++++++++++

.. note:: Some storage plugins may not support all operatirs.


=================  ===========
Name               Operators
=================  ===========
Equals             eq, ==, ==
Not Equals         ne, !=
Greater or equal   le, >=
Less or equal      le, <=
Greater than       >, gt
Less than          <, lt
Like               like
Not Like           nlike
=================  ===========


Filtering in REST API
+++++++++++++++++++++

You can filter using "query" parameters in the URL which works very much like
doing it in other places.

For example querying for Merchants with a name that starts with 'Cloud' you can do it like the below.

.. code::

  http://localhost:9091/v1/merchants?q.field=name&q.op=like&q.value=Cloud%


Results in a internal criteria of:

.. code::

  {'name': {'field': 'name', 'op': 'like', 'value': 'Cloud%'}}


You can also pass multi field / value queries (Same as above but also language)

.. code::

  http://localhost:9091/v1/merchants?q.field=lang&q.field=name&q.op=eq&q.op=like&q.value=nor&q.value=Cloud%


Results in a internal critera of:

.. code::

  {
    'name': {
      'field': 'name', 'op': 'like', 'value': 'Cloud%'
    },
    'language': {
      'field': 'language', 'op': 'eq', 'value': 'nor'
    }
  }

The Params in the URL are parsed to something usable by each service that it's
sent to.


Filtering internally
++++++++++++++++++++

Filtering internally when for example doing a call directly on a api method
or towards a API method that is available over RPC you can pass Criterion dicts
like mentioned above in the "Results in internal criteria of....".

Basically it boils down to something like:

.. code::

  {'fieldname': 'value'}
  {'fieldname': {'op': 'eq', 'value': 'value'}}