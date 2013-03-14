from pecan import request, expose, rest
import wsmeext.pecan as wsme_pecan
from wsme.types import text, wsattr

from billingstack.api.base import ModelBase, RestBase


class LoginCredentials(ModelBase):
    name = wsattr(text, mandatory=True)
    password = text
    merchant = text


class LoginResponse(ModelBase):
    """
    The response of the login
    """
    token = text


class User(ModelBase):
    def __init__(self, **kw):
        #kw['contact_info'] = ContactInfo(**kw.get('contact_info', {}))
        super(User, self).__init__(**kw)

    id = text
    name = text
    password = text

    @classmethod
    def from_db(cls, values):
        """
        Remove the password and anything else that's private.
        """
        del values['password']
        return cls(**values)


class Account(ModelBase):
    id = text
    name = text
    type = text


class Role(ModelBase):
    id = text
    name = text
    type = text


class UserController(RestBase):
    """User controller"""
    __id__ = 'user'

    @wsme_pecan.wsexpose(User)
    def get_all(self):
        row = request.storage_conn.get_user(request.ctxt, self.id_)
        return User.from_db(row)

    @wsme_pecan.wsexpose(User, body=User)
    def put(self, body):
        row = request.storage_conn.update_user(
            request.ctxt,
            self.id_,
            body.to_db())

        return User.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.delete_user(request.ctxt, self.id_)


class UsersController(RestBase):
    """Users controller"""
    __resource__ = UserController

    @wsme_pecan.wsexpose([User])
    def get_all(self):
        criterion = {}
        rows = request.storage_conn.list_users(
            request.ctxt,
            criterion=criterion)

        return [User.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(User, body=User)
    def post(self, body):
        row = request.storage_conn.create_user(
            request.ctxt,
            body.to_db())

        return User.from_db(row)


class AccountRolesController(rest.RestController):
    def __init__(self, account_id, user_id, role_id):
        self.account_id = account_id
        self.user_id = user_id
        self.role_id = role_id

    @wsme_pecan.wsexpose()
    def put(self):
        return request.storage_conn.create_grant(request.ctxt, self.user_id,
                                                 self.account_id, self.role_id)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.revoke_grant(request.ctxt, self.user_id,
                                          self.account_id, self.role_id)


class AccountController(RestBase):
    @expose()
    def _lookup(self, *remainder):
        if remainder[0] == 'users' and remainder[2] == 'roles':
            return AccountRolesController(self.id_, remainder[1],
                                          remainder[3]), ()
        return super(AccountController, self)._lookup(remainder)

    @wsme_pecan.wsexpose(Account)
    def get_all(self):
        row = request.storage_conn.get_account(request.ctxt, self.id_)
        return Account.from_db(row)

    @wsme_pecan.wsexpose(Account, body=Account)
    def put(self, body):
        row = request.storage_conn.update_account(
            request.ctxt,
            self.id_,
            body.to_db())

        return Account.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.delete_account(request.ctxt, self.id_)


class AccountsController(RestBase):
    __resource__ = AccountController

    @wsme_pecan.wsexpose([Account])
    def get_all(self):
        rows = request.storage_conn.list_accounts(request.ctxt)
        return [Account.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(Account, body=Account)
    def post(self, body):
        row = request.storage_conn.create_account(
            request.ctxt,
            body.to_db())
        return Account.from_db(row)


class RoleController(RestBase):
    @wsme_pecan.wsexpose(Role, unicode)
    def get_all(self):
        row = request.storage_conn.get_role(request.ctxt, self.id_)
        return Role.from_db(row)

    @wsme_pecan.wsexpose(Role, body=Role)
    def put(self, body):
        row = request.storage_conn.update_role(
            request.ctxt,
            self.id_,
            body.to_db())

        return Role.from_db(row)

    @wsme_pecan.wsexpose()
    def delete(self):
        request.storage_conn.delete_role(request.ctxt, self.id_)


class RolesController(RestBase):
    __resource__ = RoleController

    @wsme_pecan.wsexpose([Role])
    def get_all(self):
        rows = request.storage_conn.list_roles(request.ctxt,)
        return [Role.from_db(r) for r in rows]

    @wsme_pecan.wsexpose(Role, body=Role)
    def post(self, body):
        row = request.storage_conn.create_role(
            request.ctxt,
            body.to_db())
        return Role.from_db(row)


class TokensController(RestBase):
    """
    controller that authenticates a user...
    """

    @wsme_pecan.wsexpose(LoginResponse, body=LoginCredentials)
    def post(self, body):
        data = {
            'user_id': body.name,
            'password': body.password}

        auth_response = request.storage_conn.authenticate(request.ctxt, **data)
        return LoginResponse(**auth_response)


class V1Controller(RestBase):
    accounts = AccountsController()
    roles = RolesController()
    users = UsersController()

    tokens = TokensController()


class RootController(RestBase):
    v1 = V1Controller()
