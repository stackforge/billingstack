# Author: Endre Karlson <endre.karlson@gmail.com>
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
"""
A Identity plugin...
"""
from oslo.config import cfg
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import Unicode
from sqlalchemy.orm import exc
from sqlalchemy.ext.declarative import declarative_base

from billingstack import exceptions
from billingstack.openstack.common import log as logging
from billingstack.sqlalchemy.types import JSON, UUID
from billingstack.sqlalchemy import api, model_base, session
from billingstack.identity.base import IdentityPlugin
from billingstack.identity import utils as identity_utils


LOG = logging.getLogger(__name__)


# DB SCHEMA
BASE = declarative_base(cls=model_base.ModelBase)


cfg.CONF.register_group(cfg.OptGroup(
    name='identity:sqlalchemy', title='Config for internal identity plugin'))


cfg.CONF.register_opts(session.SQLOPTS, group='identity:sqlalchemy')


class Role(BASE, model_base.BaseMixin):
    name = Column(Unicode(64), unique=True, nullable=False)
    extra = Column(JSON)


class UserAccountGrant(BASE):
    user_id = Column(UUID, ForeignKey('user.id', ondelete='CASCADE',
                     onupdate='CASCADE'), primary_key=True)
    account_id = Column(UUID, ForeignKey('account.id', ondelete='CASCADE',
                     onupdate='CASCADE'), primary_key=True)
    data = Column(JSON)


class Account(BASE, model_base.BaseMixin):
    type = Column(Unicode(10), nullable=False)
    name = Column(Unicode(60), nullable=False)
    title = Column(Unicode(100))


class User(BASE, model_base.BaseMixin):
    """
    A User that can login.
    """
    name = Column(Unicode(20), nullable=False)
    password = Column(Unicode(255), nullable=False)


class SQLAlchemyPlugin(IdentityPlugin, api.HelpersMixin):
    """
    A Internal IdentityPlugin that currently relies on SQLAlchemy as
    the "Backend"
    """
    def __init__(self):
        self.setup('identity:sqlalchemy')

    def base(self):
        return BASE

    def authenticate(self, context, user_id=None, password=None, account_id=None):
        #self._get_by_name(models.
        pass

    def create_user(self, context, values):
        row = User(**values)
        row.password = identity_utils.hash_password(row.password)
        self._save(row)
        return dict(row)

    def list_users(self, context, criterion=None):
        rows = self._list(User, criterion=criterion)
        return map(dict, rows)

    def get_user(self, context, id_):
        row = self._get(User, id_)
        return dict(row)

    def update_user(self, context, id_, values):
        row = self._update(User, id_, values)
        return dict(row)

    def delete_user(self, context, id_):
        self._delete(User, id_)

    def create_account(self, context, values):
        row = Account(**values)
        self._save(row)
        return dict(row)

    def list_accounts(self, context, criterion=None):
        rows = self._list(Account, criterion=criterion)
        return map(dict, rows)

    def get_account(self, context, id_):
        row = self._get(Account, id_)
        return dict(row)

    def update_account(self, context, id_, values):
        row = self._update(Account, id_, values)
        return dict(row)

    def delete_account(self, context, id_):
        self._delete(Account, id_)

    def create_role(self, context, values):
        row = Role(**values)
        self._save(row)
        return dict(row)

    def list_roles(self, context, criterion=None):
        rows = self._list(Role, criterion=criterion)
        return map(dict, rows)

    def get_role(self, context, id_):
        row = self._get(Role, id_)
        return dict(row)

    def update_role(self, context, id_, values):
        row = self._update(Role, id_, values)
        return dict(row)

    def delete_role(self, context, id_):
        self._delete(Role, id_)

    def get_metadata(self, user_id=None, account_id=None):
        q = self.session.query(UserAccountGrant)\
            .filter_by(user_id=user_id, account_id=account_id)
        try:
            return q.one().data
        except exc.NoResultFound:
            raise exceptions.NotFound

    def create_metadata(self, user_id, account_id, metadata):
        ref = UserAccountGrant(
            account_id=account_id,
            user_id=user_id,
            data=metadata)
        ref.save(self.session)
        return metadata

    def update_metadata(self, user_id, account_id, metadata):
        q = self.session.query(UserAccountGrant)\
            .filter_by(user_id=user_id, account_id=account_id)
        ref = q.first()
        data = ref.data.copy()
        data.update(metadata)
        ref.data = data
        ref.save(self.session)
        return ref

    def create_grant(self, context, user_id, account_id, role_id):
        self._get(Role, role_id)

        try:
            ref = self.get_metadata(user_id=user_id, account_id=account_id)
            is_new = False
        except exceptions.NotFound:
            ref = {}
            is_new = True

        roles = set(ref.get('roles', []))
        roles.add(role_id)
        ref['roles'] = list(roles)

        if is_new:
            self.create_metadata(user_id, account_id, ref)
        else:
            self.update_metadata(user_id, account_id, ref)

    def revoke_grant(self, context, user_id, account_id, role_id):
        self._get(Role, role_id)

        try:
            ref = self.get_metadata(user_id=user_id, account_id=account_id)
            is_new = False
        except exceptions.NotFound:
            ref = {}
            is_new = True

        roles = set(ref.get('roles', []))

        try:
            roles.remove(role_id)
        except KeyError:
            raise exceptions.NotFound(role_id=role_id)

        ref['roles'] = list(roles)

        if is_new:
            self.create_metadata(user_id, account_id, ref)
        else:
            self.update_metadata(user_id, account_id, ref)
