from wsme.types import Base as Base_, text, Unset, DictType, UserType


class Base(Base_):
    id = text

    def as_dict(self):
        """
        Return this model as a DictType
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


class Property(UserType):
    """
    A Property that just passes the value around...
    """
    def tonativetype(self, value):
        return value

    def fromnativetype(self, value):
        return value

metadata_property = Property()


class DescribedBase(Base):
    name = text
    title = text
    description = text


def change_suffixes(data, keys, shorten=True, suffix='_name'):
    """
    Loop thro the keys foreach key setting for example
    'currency_name' > 'currency'
    """
    for key in keys:
        if shorten:
            new, old = key, key + suffix
        else:
            new, old = key + suffix, key
        if old in data:
            if new in data:
                raise RuntimeError("Can't override old key with new key")

            data[new] = data.pop(old)


class Currency(Base):
    id = text
    name = text
    title = text

class Language(Base):
    id = text
    name = text
    title = text


class PaymentMethod(Base):
    name = text
    identifier = text
    expires = text

    properties = DictType(key_type=text, value_type=metadata_property)


class PGMethod(DescribedBase):
    type = text


class PGProvider(DescribedBase):
    def __init__(self, **kw):
        kw['methods'] = [PGMethod(**m) for m in kw.get('methods', {})]
        super(PGProvider, self).__init__(**kw)

    methods = [PGMethod]
    properties = DictType(key_type=text, value_type=metadata_property)


class ContactInfo(Base):
    id = text
    first_name = text
    last_name = text
    company = text
    address1 = text
    address2 = text
    address3 = text
    locality = text
    region = text
    country_name = text
    postal_code = text

    phone = text
    email = text
    website = text


class User(Base):
    def __init__(self, **kw):
        kw['contact_info'] = ContactInfo(**kw.get('contact_info', {}))
        super(User, self).__init__(**kw)

    username = text
    password = text
    merchant_id = text
    contact_info = ContactInfo


class Product(DescribedBase):
    measure = text
    type = text

    properties = DictType(key_type=text, value_type=metadata_property)


class Plan(DescribedBase):
    properties = DictType(key_type=text, value_type=metadata_property)


class Account(Base):
    currency = text
    language = text

    name = text

    def to_db(self):
        values = self.as_dict()
        change_suffixes(values, ['currency', 'language'], shorten=False)
        return values

    @classmethod
    def from_db(cls, values):
        change_suffixes(values, ['currency', 'language'])
        return cls(**values)


class Merchant(Account):
    pass


class Customer(Account):
    def __init__(self, **kw):
        kw['contact_info'] = [ContactInfo(**i) for i in kw.get('contact_info', {})]
        super(Customer, self).__init__(**kw)

    merchant_id = text
    contact_info = [ContactInfo]