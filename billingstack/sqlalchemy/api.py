from sqlalchemy import or_
from sqlalchemy.orm import exc

from billingstack import exceptions
from billingstack.openstack.common import log
from billingstack.sqlalchemy import model_base, session


LOG = log.getLogger(__name__)


class HelpersMixin(object):
    def setup(self, config_group):
        self.session = session.get_session(config_group)
        self.engine = session.get_engine(config_group)

    def setup_schema(self):
        """ Semi-Private Method to create the database schema """
        self.base.metadata.create_all(self.session.bind)

    def teardown_schema(self):
        """ Semi-Private Method to reset the database schema """
        self.base.metadata.drop_all(self.session.bind)

    def _save(self, obj, save=True):
        if not save:
            return obj
        try:
            obj.save(self.session)
        except exceptions.Duplicate:
            raise

    def _list(self, cls=None, query=None, criterion=None):
        """
        A generic list method

        :param cls: The model to try to delete
        :param criterion: Criterion to match objects with
        """
        if not cls and not query:
            raise ValueError("Need either cls or query")

        query = query or self.session.query(cls)

        if criterion:
            query = query.filter_by(**criterion)

        try:
            result = query.all()
        except exc.NoResultFound:
            LOG.debug('No results found querying for %s: %s' %
                      (cls, criterion))
            return []
        else:
            return result

    def _get(self, cls, identifier, by_name=False):
        """
        Get an instance of a Model matching ID

        :param cls: The model to try to get
        :param identifier: The ID to get
        :param by_name: Search by name as well as ID
        """
        filters = [cls.id == identifier]
        if by_name:
            filters.append(cls.name == identifier)

        query = self.session.query(cls)\
            .filter(or_(*filters))

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

    def _update(self, cls, id_, values):
        """
        Update an instance of a Model matching an ID with values

        :param cls: The model to try to update
        :param id_: The ID to update
        :param values: The values to update the model instance with
        """
        obj = self._get(cls, id_)
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

    def _delete(self, cls, id_):
        """
        Delete an instance of a Model matching an ID

        :param cls: The model to try to delete
        :param id_: The ID to delete
        """
        obj = self._get(cls, id_)
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
        Return a Key, Value dict where the "key" will be the key and the row as value
        """
        data = {}
        for row in rows:
            if callable(key):
                data_key = key(row)
            else:
                data_key = row[key]
            data[data_key] = func(row)
        return data

