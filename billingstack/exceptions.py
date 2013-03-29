# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import re


class Base(Exception):
    error_code = 500
    message_tmpl = None

    def __init__(self, message='', *args, **kw):
        self.message = message % kw if self.message_tmpl else message

        self.errors = kw.pop('errors', None)
        super(Base, self).__init__(self.message)

    @property
    def error_type(self):
        name = "_".join(l.lower() for l in re.findall('[A-Z][^A-Z]*',
                        self.__class__.__name__))
        name = re.sub('_+remote$', '', name)
        return name

    def __str__(self):
        return self.message

    def get_message(self):
        """
        Return the exception message or None
        """
        if unicode(self):
            return unicode(self)
        else:
            return None


class NotImplemented(Base, NotImplementedError):
    pass


class ConfigurationError(Base):
    pass


class BadRequest(Base):
    error_code = 400


class InvalidObject(BadRequest):
    pass


class InvalidSortKey(BadRequest):
    pass


class InvalidQueryField(BadRequest):
    pass


class InvalidOperator(BadRequest):
    pass


class Forbidden(Base):
    pass


class Duplicate(Base):
    error_code = 409


class NotFound(Base):
    error_code = 404
