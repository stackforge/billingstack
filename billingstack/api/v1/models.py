from wsme.types import Base, text, Unset


class Base(Base):
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


class Currency(Base):
    id = text
    name = text
    title = text


class Language(Base):
    name = text
    title = text


class PGMethod(Base):
    id = text
    name = text
    title = text
    desription = text
    type = text
  

class PGProvider(Base):
    def __init__(self, **kw):
        kw['methods'] = [PGMethod(**m) for m in kw.get('methods', {})]
        kw['properties'] = Property
        import ipdb
        #ipdb.set_trace()

        super(PGProvider, self).__init__(**kw)

    id = text
    name = text
    title = text
    description = text

    methods = [PGMethod]
    properties = text


class ContactInfo(Base):
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
