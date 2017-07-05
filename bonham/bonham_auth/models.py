import sqlalchemy as sa
from asyncpg.connection import Connection
from bonham.bonham_core import *
from bonham.bonham_core.models import Base, BaseModel
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy_utils import ArrowType, LocaleType, PasswordType

__all__ = ['Account', 'Role', 'Permission', 'RefreshToken']


class Account(Base, BaseModel):
    email = sa.Column(sa.String(255), index=True, primary_key=True, unique=True)
    password = sa.Column(PasswordType(
            schemes=['pbkdf2_sha512', 'md5_crypt'],
            deprecated=['md5_crypt']
            ), nullable=False)
    locale = sa.Column(LocaleType, server_default="de_DE")
    logged_in = sa.Column(sa.Boolean, server_default="0")
    is_superuser = sa.Column(sa.Boolean, server_default="0")
    is_verified = sa.Column(sa.Boolean, server_default="0")
    activation_key = sa.Column(sa.String)
    disabled = sa.Column(ArrowType)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def create(self, connection: Connection, **kwargs):
        if self.email is None or self.password is None:
            raise TypeError(f"email and password must be given")
        account = await db.create(connection, self.__table__, data=dict(email=self.email, password=self.password), **kwargs)
        return account


class Role(Base, BaseModel):
    name = sa.Column(sa.String(60), primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Permission(Base, BaseModel):
    role_id = ForeignKey('role')
    table = sa.Column(sa.String, nullable=False, primary_key=True)
    can_add = sa.Column(sa.Boolean, server_default='0')
    can_update = sa.Column(sa.Boolean, server_default='0')
    can_delete = sa.Column(sa.Boolean, server_default='0')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RefreshToken(Base, BaseModel):
    owner = ForeignKey('account')
    token = sa.Column(sa.String, primary_key=True)

