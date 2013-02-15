from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty


def get_prop_names(obj, exclude=[]):
    local, remote = [], []
    for p in obj.__mapper__.iterate_properties:
        if p.key not in exclude:
            if isinstance(p, ColumnProperty):
                local.append(p.key)
            if isinstance(p, RelationshipProperty):
                remote.append(p.key)
    return local, remote


def get_local_values(model, values):
    """
    Make a new dictionary out of values containing only values relevant to
    the Model

    Example usage:
        values, metadata = get_local_values(models.Product, values)

    :param model: SQLAlchemy Model
    :param values: Values to get from
    """
    local, _ = get_prop_names(model)

    new_values = {}
    for key in values.keys():
        if key in local:
            new_values[key] = values.pop(key)
    return new_values, values
