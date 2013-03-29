import functools
import mimetypes

from flask import request, Blueprint
from wsme.types import Base, Enum, UserType, text, Unset, wsproperty

from oslo.config import cfg

from billingstack.api import utils
from billingstack.openstack.common import log


LOG = log.getLogger(__name__)


cfg.CONF.register_opts([
    cfg.StrOpt('cors_allowed_origin', default='*', help='Allowed CORS Origin'),
    cfg.IntOpt('cors_max_age', default=3600)])


CORS_ALLOW_HEADERS = [
    'origin',
    'authorization',
    'accept',
    'content-type',
    'x-requested-with'
]


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
        # for LOG calls
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


class Rest(Blueprint):
    """
    Helper to do stuff
    """
    def get(self, rule, status_code=200, **kw):
        return self._mroute('GET', rule, status_code, **kw)

    def post(self, rule, status_code=202, **kw):
        return self._mroute('POST', rule, status_code, **kw)

    def patch(self, rule, status_code=202, **kw):
        return self._mroute('PATCH', rule, status_code, **kw)

    def put(self, rule, status_code=202, **kw):
        return self._mroute('PUT', rule, status_code, **kw)

    def delete(self, rule, status_code=204, **kw):
        return self._mroute('DELETE', rule, status_code, **kw)

    def _mroute(self, methods, rule, status_code=None, **kw):
        if type(methods) is str:
            methods = [methods]

        return self.route(rule, methods=methods, status_code=status_code,
                          **kw)

    def guess_response_type(self, type_suffix=None):
        """
        Get the MIME type based on keywords / request
        """
        if type_suffix:
            response_type = mimetypes.guess_type("res." + type_suffix)[0]
            request.response_type = response_type

    def route(self, rule, sig_args=[], sig_kw={}, **options):
        """
        Helper function that sets up the route as well as adding CORS..
        """
        status = options.pop('status_code', None)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)

            if 'body' in options and 'body' not in sig_kw:
                sig_kw['body'] = options['body']

            # NOTE: Wrap the function with CORS support.
            @utils.crossdomain(origin=cfg.CONF.cors_allowed_origin,
                               max_age=cfg.CONF.cors_max_age,
                               headers=",".join(CORS_ALLOW_HEADERS))
            @functools.wraps(func)
            def handler(**kw):
                # extract response content type
                self.guess_response_type(kw.pop('response_type', None))

                # NOTE: Extract fields (column selection)
                fields = list(set(request.args.getlist('fields')))
                fields.sort()
                request.fields_selector = fields

                if hasattr(func, '_wsme_definition'):
                    func._wsme_definition.status_code = status

                return func(**kw)

            #_rule = "/<tenant_id>" + rule
            # NOTE: Add 2 set of rules, 1 with response content type and one wo
            self.add_url_rule(rule, endpoint, handler, **options)
            rtype_rule = rule + '.<response_type>'
            self.add_url_rule(rtype_rule, endpoint, handler, **options)

            return func
        return decorator
