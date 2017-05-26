from asyncio import gather

import sqlalchemy as sa
from asyncpg.connection import Connection
from sqlalchemy import UniqueConstraint
from sqlalchemy_utils import ArrowType, LocaleType, PasswordType

from bonham import db
from bonham.db import ForeignKey, create_tables
from bonham.models import Base, BaseModel
from bonham.validators import *

__all__ = ['validate_data', 'Account', 'Permission', 'RefreshToken']


async def valid_password(value: str = None) -> bool:
    password_props = await gather(
            is_longer_than(value, 8),
            has_digits(value),
            has_uppercase(value),
            has_lowercase(value),
            has_specialchars(value),
            has_no_whitespaces(value)
            )
    return all(val for val in password_props)


async def validate_data(data: dict = None) -> bool:
    return all(await gather(is_valid_email(data['email']), valid_password(data['password'])))


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
        new = await db.create(connection, self.__table__, data=dict(email=self.email, password=self.password), **kwargs)
        return new


class Role(Base, BaseModel):
    name = sa.Column(sa.String(60), primary_key=True)


class Permission(Base, BaseModel):
    role_id = ForeignKey('role')
    table = sa.Column(sa.String, nullable=False, primary_key=True)
    can_add = sa.Column(sa.Boolean, server_default='0')
    can_update = sa.Column(sa.Boolean, server_default='0')
    can_delete = sa.Column(sa.Boolean, server_default='0')
    __table_args__ = (UniqueConstraint('account_id', 'table'),)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RefreshToken(Base, BaseModel):
    owner = ForeignKey('account')
    token = sa.Column(sa.String, primary_key=True)

create_tables((Account, Role, Permission, RefreshToken))
