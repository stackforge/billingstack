import re


def capital_to_underscore(string):
    return "_".join(l.lower() for l in re.findall('[A-Z][^A-Z]*',
                                                  string))


def underscore_to_capital(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))
