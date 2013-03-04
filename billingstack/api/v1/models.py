from wsme.types import Base as Base_, text, Unset, DictType, UserType


class Base(Base_):
    def as_dict(self):
        data = {}

        for attr in self._wsme_attributes:
            value = attr.__get__(self, self.__class__)
            if value is not Unset:
                if isinstance(value, Base) and hasattr(value, "as_dict"):
                    value = value.as_dict()
                data[attr.name] = value
        return data

    id = text


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


class Currency(Base):
    id = text
    name = text
    title = text


class Language(Base):
    id = text
    name = text
    title = text


class PGMethod(DescribedBase):
    type = text
 

class PGProvider(DescribedBase):
    def __init__(self, **kw):
        kw['methods'] = [PGMethod(**m) for m in kw.get('methods', {})]
        super(PGProvider, self).__init__(**kw)

    methods = [PGMethod]
    properties = DictType(key_type=text, value_type=metadata_property)


class ContactInfo(Base_):
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
    merchant_id = text
    contact_info = ContactInfo


class Product(DescribedBase):
    measure = text
    type = text

    properties = DictType(key_type=text, value_type=metadata_property)
   

class Plan(DescribedBase):
    properties = DictType(key_type=text, value_type=metadata_property)

    
class Account(Base):
    currency_id = text
    language_id = text

    name = text


class Merchant(Account):
    pass


class Customer(Account):
    def __init__(self, **kw):
        kw['contact_info'] = [ContactInfo(**i) for i in kw.get('contact_info', {})]
        super(Customer, self).__init__(**kw)

    merchant_id = text
    contact_info = [ContactInfo]