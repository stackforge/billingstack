import re


def capital_to_underscored(string):
    table_name = "_".join(l.lower() for l in re.findall('[A-Z][^A-Z]*',
                                                        string)
    return table_name


def underscored_to_capital(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))
