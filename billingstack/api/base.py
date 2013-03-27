import functools
import mimetypes
import traceback

from flask import abort, request, Blueprint, Response
from wsme.types import Base, Enum, UserType, text, Unset, wsproperty
from werkzeug.datastructures import MIMEAccept

from oslo.config import cfg

from billingstack.api import utils
from billingstack.openstack.common import log
from billingstack.openstack.common.wsgi import JSONDictSerializer, \
    XMLDictSerializer, JSONDeserializer


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

                if status:
                    request.status_code = status

                return func(**kw)

            #_rule = "/<tenant_id>" + rule
            # NOTE: Add 2 set of rules, 1 with response content type and one wo
            self.add_url_rule(rule, endpoint, handler, **options)
            rtype_rule = rule + '.<response_type>'
            self.add_url_rule(rtype_rule, endpoint, handler, **options)

            return func
        return decorator


RT_JSON = MIMEAccept([("application/json", 1)])
RT_XML = MIMEAccept([("application/xml", 1)])


def render(res=None, resp_type=None, status=None, **kwargs):
    if not res:
        res = {}
    elif isinstance(res, ModelBase):
        res = res.as_dict()
    elif isinstance(res, list):
        new_res = []
        for r in res:
            new_res.append(r.as_dict())
        res = new_res

    if isinstance(res, dict):
        res.update(kwargs)
    elif kwargs:
        # can't merge kwargs into the non-dict res
        abort_and_log(500, "Non-dict and non-empty kwargs passed to render")

    status_code = getattr(request, 'status_code', None)
    if status:
        status_code = status
    if not status_code:
        status_code = 200

    if not resp_type:
        req_resp_type = getattr(request, 'resp_type', None)
        resp_type = req_resp_type if req_resp_type else RT_JSON

    serializer = None
    if "application/json" in resp_type:
        resp_type = RT_JSON
        serializer = JSONDictSerializer()
    elif "application/xml" in resp_type:
        resp_type = RT_XML
        serializer = XMLDictSerializer()
    else:
        abort_and_log(400, "Content type '%s' isn't supported" % resp_type)

    body = serializer.serialize(res)
    resp_type = str(resp_type)
    return Response(response=body, status=status_code, mimetype=resp_type)


def request_data(model):
    if not request.content_length > 0:
        LOG.debug("Empty body provided in request")
        return dict()

    deserializer = None
    content_type = request.mimetype

    if not content_type or content_type in RT_JSON:
        deserializer = JSONDeserializer()
    elif content_type in RT_XML:
        abort_and_log(400, "XML requests are not supported yet")
        # deserializer = XMLDeserializer()
    else:
        abort_and_log(400, "Content type '%s' isn't supported" % content_type)

    data = deserializer.deserialize(request.data)['body']
    return model(**data).to_db()


def abort_and_log(status_code, descr, exc=None):
    LOG.error("Request aborted with status code %s and message '%s'",
              status_code, descr)

    if exc is not None:
        LOG.error(traceback.format_exc())

    abort(status_code, description=descr)
