import asyncpg
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy_utils import ChoiceType, JSONType, LocaleType, PasswordType

from bonham.bonham_core.choicetypes import ClientStatusType
from bonham.bonham_core.db import Base, ForeignKey
from bonham.bonham_core.models import Model

__all__ = ('Account', 'Role', 'AccountRole', 'Permission', 'Client')


class Account(Model, Base):
    email = sa.Column(sa.String(255), index=True, primary_key=True, unique=True)
    password = sa.Column(PasswordType(
        schemes=['pbkdf2_sha512']
            ), nullable=False)
    locale = sa.Column(LocaleType, server_default="de_DE")
    logged_in = sa.Column(sa.Boolean, server_default="0")
    is_superuser = sa.Column(sa.Boolean, server_default="0")
    activation_key = sa.Column(sa.String)

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)

    async def create(self, *, data=None, **kwargs):
        if data is None:
            data = {
                key: val for key, val in vars(self).items()
                if key in self.columns and val is not None
                }
        _stmt = self.table.insert().values(data).returning(
            *(self.table.c[key] for key in ['id', 'email', 'created'])
            )
        stmt = _stmt.compile(compile_kwargs={'literal_binds': True})
        print(stmt)
        result = await self.connection.fetchrow(str(stmt))
        vars(self).update(**dict(result))
        return self


class Role(Model, Base):
    name = sa.Column(sa.String(60), primary_key=True)

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)


class Permission(Model, Base):
    role_id = ForeignKey('role')
    table_name = sa.Column(sa.String, nullable=False, primary_key=True)
    can_add = sa.Column(sa.Boolean, server_default='0')
    can_update = sa.Column(sa.Boolean, server_default='0')
    can_delete = sa.Column(sa.Boolean, server_default='0')

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)


class AccountRole(Model, Base):
    r"""AccountRole Model"""
    role_id = ForeignKey('role')
    account_id = ForeignKey('account')
    table_name = sa.Column(sa.String(60))
    object_id = sa.Column(sa.Integer)

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)


class Client(Model, Base):
    """
    Holds bearer tokens for each account and its connected user-agents/devices.
    additional fields:
        owner = ForeignKey('account')  # account id
        user_agent = sa.Column(sa.String, nullable=False)  # user-agent string
        token = sa.Column(sa.String, primary_key=True)  # bearer token
    """
    owner = ForeignKey('account')
    host = sa.Column(sa.String, nullable=False)
    user_agent = sa.Column(sa.String, nullable=False)
    token = sa.Column(sa.String, primary_key=True)
    status = sa.Column(ChoiceType(ClientStatusType, impl=sa.Integer()),
                       server_default="1")  # default is 'undefined'
    settings = sa.Column(JSONType())

    UniqueConstraint(owner, host, user_agent)

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)
