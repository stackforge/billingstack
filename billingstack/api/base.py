import inspect
import pecan
from pecan import request
from pecan.rest import RestController
from wsme.types import Base, Enum, UserType, text, Unset, wsproperty

from billingstack.openstack.common import log


LOG = log.getLogger(__name__)


class Property(UserType):
    """
    A Property that just passes the value around...
    """
    def tonativetype(self, value):
        return value

    def fromnativetype(self, value):
        return value


property_type = Property()


operation_kind = Enum(str, 'lt', 'le', 'eq', 'ne', 'ge', 'gt')


class Query(Base):
    """
    Query filter.
    """

    _op = None  # provide a default

    def get_op(self):
        return self._op or 'eq'

    def set_op(self, value):
        self._op = value

    field = text
    "The name of the field to test"

    #op = wsme.wsattr(operation_kind, default='eq')
    # this ^ doesn't seem to work.
    op = wsproperty(operation_kind, get_op, set_op)
    "The comparison operator. Defaults to 'eq'."

    value = text
    "The value to compare against the stored data"

    def __repr__(self):
        # for logging calls
        return '<Query %r %s %r>' % (self.field, self.op, self.value)

    @classmethod
    def sample(cls):
        return cls(field='resource_id',
                   op='eq',
                   value='bd9431c1-8d69-4ad3-803a-8d4a6b89fd36',
                   )

    def as_dict(self):
        return {
            'op': self.op,
            'field': self.field,
            'value': self.value
        }


def _query_to_kwargs(query, db_func):
    # TODO(dhellmann): This function needs tests of its own.
    valid_keys = inspect.getargspec(db_func)[0]
    if 'self' in valid_keys:
        valid_keys.remove('self')
    translation = {'user_id': 'user',
                   'project_id': 'project',
                   'resource_id': 'resource'}
    stamp = {}
    trans = {}
    metaquery = {}
    for i in query:
        if i.field == 'timestamp':
            # FIXME(dhellmann): This logic is not consistent with the
            # way the timestamps are treated inside the mongo driver
            # (the end timestamp is always tested using $lt). We
            # should just pass a single timestamp through to the
            # storage layer with the operator and let the storage
            # layer use that operator.
            if i.op in ('lt', 'le'):
                stamp['end_timestamp'] = i.value
            elif i.op in ('gt', 'ge'):
                stamp['start_timestamp'] = i.value
            else:
                LOG.warn('_query_to_kwargs ignoring %r unexpected op %r"' %
                         (i.field, i.op))
        else:
            if i.op != 'eq':
                LOG.warn('_query_to_kwargs ignoring %r unimplemented op %r' %
                         (i.field, i.op))
            elif i.field == 'search_offset':
                stamp['search_offset'] = i.value
            elif i.field.startswith('metadata.'):
                metaquery[i.field] = i.value
            else:
                trans[translation.get(i.field, i.field)] = i.value

    kwargs = {}
    if metaquery and 'metaquery' in valid_keys:
        kwargs['metaquery'] = metaquery


class RestBase(RestController):
    __resource__ = None
    __id__ = None

    def __init__(self, parent=None, id_=None):
        self.parent = parent
        if self.__id__:
            request.context[self.__id__ + '_id'] = id_
        self.id_ = id_

    @pecan.expose()
    def _lookup(self, *url_data):
        """
        A fun approach to _lookup - checks self.__resource__ for the "id"
        """
        id_ = None
        if len(url_data) >= 1:
            id_ = url_data[0]
        parts = url_data[1:] if len(url_data) > 1 else ()
        LOG.debug("Lookup: id '%s' parts '%s'", id_, parts)

        resource = self.__resource__
        if inspect.isclass(resource) and issubclass(resource, RestBase):
            return resource(parent=self, id_=id_), parts

    def __getattr__(self, name):
        """
        Overload this to look in self.__resource__ if name is defined as a
        Controller
        """
        if name in self.__dict__:
            return self.__dict__[name]
        elif isinstance(self.__resource__, dict) and name in self.__resource__:
            return self.__resource__[name](parent=self)
        else:
            raise AttributeError


class ModelBase(Base):
    def as_dict(self):
        """
        Return this model as a dict
        """
        data = {}

        for attr in self._wsme_attributes:
            value = attr.__get__(self, self.__class__)
            if value is not Unset:
                if isinstance(value, Base) and hasattr(value, "as_dict"):
                    value = value.as_dict()
                data[attr.name] = value
        return data

    def to_db(self):
        """
        Returns this Model object as it's DB form

        Example
            'currency' vs 'currency_name'
        """
        return self.as_dict()

    @classmethod
    def from_db(cls, values):
        """
        Return a class of this object from values in the from_db
        """
        return cls(**values)
