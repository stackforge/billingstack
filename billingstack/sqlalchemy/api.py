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
# under the License

from sqlalchemy.orm import exc


from billingstack import exceptions
from billingstack.openstack.common import log
from billingstack.sqlalchemy import model_base, session, utils
from billingstack.storage.filterer import BaseFilterer


LOG = log.getLogger(__name__)


class SQLAFilterer(BaseFilterer):
    def apply_criteria(self, query, model):
        """
        Apply the actual criterion in this filterer and return a query with
        filters applied.
        """
        LOG.debug('Applying Critera %s' % self.criterion)

        for field, c in self.criterion.items():
            # NOTE: Try to get the column
            try:
                col_obj = getattr(model, field)
            except AttributeError:
                msg = '%s is not a valid field to query by' % field
                raise exceptions.InvalidQueryField(msg)

            # NOTE: Handle a special operator
            std_op = self.get_op(c.op)
            if hasattr(self, c.op):
                getattr(self, c.op)(c)
            elif std_op:
                query = query.filter(std_op(col_obj, c.value))
            elif c.op in ('%', 'like'):
                query = query.filter(col_obj.like(c.value))
            elif c.op in ('!%', 'nlike'):
                query = query.filter(col_obj.notlike(c.value))
            else:
                msg = 'Invalid operator in criteria \'%s\'' % c
                raise exceptions.InvalidOperator(msg)

            return query


class HelpersMixin(object):
    def setup(self, config_group):
        """
        Setup the Connection

        :param config_group: The config group to get the config from
        """
        self.session = session.get_session(config_group)
        self.engine = session.get_engine(config_group)

    def setup_schema(self):
        """ Semi-Private Method to create the database schema """
        LOG.debug('Setting up schema')
        base = self.base()
        base.metadata.create_all(self.session.bind)

    def teardown_schema(self):
        """ Semi-Private Method to reset the database schema """
        LOG.debug('Tearing down schema')
        base = self.base()
        base.metadata.drop_all(self.session.bind)

    def _save(self, row, save=True):
        """
        Save a row.

        :param row: The row to save.
        :param save: Save or just return a ref.
        """
        if not save:
            return row

        try:
            row.save(self.session)
        except exceptions.Duplicate:
            raise
        return row

    def _list(self, cls=None, query=None, criterion=None):
        """
        A generic list/search helper method.

        Example criterion:
            [{'field': 'id', 'op': 'eq', 'value': 'someid'}]

        :param cls: The model to try to delete
        :param criterion: Criterion to match objects with
        """
        if not cls and not query:
            raise ValueError("Need either cls or query")

        query = query or self.session.query(cls)

        if criterion:
            filterer = SQLAFilterer(criterion)
            query = filterer.apply_criteria(query, cls)

        try:
            result = query.all()
        except exc.NoResultFound:
            LOG.debug('No results found querying for %s: %s' %
                      (cls, criterion))
            return []
        else:
            return result

    def _filter_id(self, cls, identifier, by_name):
        """
        Apply filter for either id or name

        :param cls: The Model class.
        :param identifier: The identifier of it.
        :param by_name: By name.
        """
        if hasattr(cls, 'id') and utils.is_valid_id(identifier):
            return cls.id == identifier
        elif hasattr(cls, 'name') and by_name:
            return cls.name == identifier
        else:
            raise exceptions.NotFound('No criterias matched')

    def _get(self, cls, identifier, by_name=False):
        """
        Get an instance of a Model matching ID

        :param cls: The model to try to get
        :param identifier: The ID to get
        :param by_name: Search by name as well as ID
        """
        id_filter = self._filter_id(cls, identifier, by_name)

        query = self.session.query(cls).filter(id_filter)

        try:
            obj = query.one()
        except exc.NoResultFound:
            raise exceptions.NotFound(identifier)
        return obj

    def _get_id_or_name(self, *args, **kw):
        """
        Same as _get but with by_name on ass default
        """
        kw['by_name'] = True
        return self._get(*args, **kw)

    def _update(self, cls, id_, values, by_name=False):
        """
        Update an instance of a Model matching an ID with values

        :param cls: The model to try to update
        :param id_: The ID to update
        :param values: The values to update the model instance with
        """
        obj = self._get_id_or_name(cls, id_, by_name=by_name)
        if 'id' in values and id_ != values['id']:
            msg = 'Not allowed to change id'
            errors = {'id': id_}
            raise exceptions.InvalidObject(msg, errors=errors)
        obj.update(values)
        try:
            obj.save(self.session)
        except exceptions.Duplicate:
            raise
        return obj

    def _delete(self, cls, id_, by_name=False):
        """
        Delete an instance of a Model matching an ID

        :param cls: The model to try to delete
        :param id_: The ID to delete
        """
        obj = self._get(cls, id_, by_name=by_name)
        obj.delete(self.session)

    def _get_row(self, obj, cls=None, **kw):
        """
        Used to either check that passed 'obj' is a ModelBase inheriting object
        and just return it

        :param obj: ID or instance / ref of the object
        :param cls: The class to run self._get on if obj is not a ref
        """
        if isinstance(obj, model_base.ModelBase):
            return obj
        elif isinstance(obj, basestring) and cls:
            return self._get(cls, obj)
        else:
            msg = 'Missing obj and/or obj and cls...'
            raise exceptions.BadRequest(msg)

    def _make_rel_row(self, row, rel_attr, values):
        """
        Get the class of the relation attribute in 'rel_attr' and make a
        row from values with it.

        :param row: A instance of ModelBase
        :param rel_attr: The relation attribute
        :param values: The values to create the new row from
        """
        cls = row.__mapper__.get_property(rel_attr).mapper.class_
        return cls(**values)

    def _dict(self, row, extra=[]):
        data = dict(row)
        for key in extra:
            if isinstance(row[key], list):
                data[key] = map(dict, row[key])
            else:
                data[key] = dict(row[key])
        return data

    def _kv_rows(self, rows, key='name', func=lambda i: i):
        """
        Return a Key, Value dict where the "key" will be the key and the row
        as value
        """
        data = {}
        for row in rows:
            if callable(key):
                data_key = key(row)
            else:
                data_key = row[key]
            data[data_key] = func(row)
        return data
