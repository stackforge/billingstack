import pycountry
import re

from billingstack import exceptions


def capital_to_underscore(string):
    return "_".join(l.lower() for l in re.findall('[A-Z][^A-Z]*',
                                                  string))


def underscore_to_capital(string):
    return ''.join(x.capitalize() or '_' for x in string.split('_'))


def get_country(country_obj, **kw):
    try:
        obj = country_obj.get(**kw)
    except KeyError:
        raise exceptions.InvalidObject(errors=kw)
    return dict([(k, v) for k, v in obj.__dict__.items() \
                if not k.startswith('_')])


def get_currency(letter):
    obj = get_country(pycountry.currencies, letter=letter.upper())
    obj['letter'] = obj['letter'].lower()
    del obj['numeric']
    return obj


def get_language(letter):
    obj = get_country(pycountry.languages, terminology=letter)
    return {'letter': obj['terminology'].lower(), 'name': obj['name']}
