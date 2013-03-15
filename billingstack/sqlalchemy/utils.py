from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from billingstack.openstack.common import uuidutils


def get_prop_dict(obj):
    return dict([(p.key, p) for p in obj.__mapper__.iterate_properties])


def get_prop_names(obj, exclude=[]):
    props = get_prop_dict(obj)

    local, remote = [], []
    for k, p in props.items():
        if k not in exclude:
            if isinstance(p, ColumnProperty):
                local.append(k)
            if isinstance(p, RelationshipProperty):
                remote.append(k)
    return local, remote


def is_valid_id(id_):
    """
    Return true if this is a valid ID for the cls.id
    """
    if uuidutils.is_uuid_like(id_) or isinstance(id_, int):
        return True
    else:
        return False
