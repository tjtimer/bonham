from asyncio import gather

from asyncpg.connection import Connection
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, LocaleType, PasswordType

from bonham.db import Base, BaseModel, ForeignKey
from bonham.validators import (
    has_digits, has_lowercase, has_no_whitespaces, has_specialchars, has_uppercase,
    is_longer_than, is_valid_email
    )

__all__ = ['validate_data', 'Account', 'AccessToken']


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
    email = sa.Column(sa.String(255), index=True, unique=True)
    password = sa.Column(PasswordType(
            schemes=['pbkdf2_sha512', 'md5_crypt'],
            deprecated=['md5_crypt']
            ), nullable=False)
    locale = sa.Column(LocaleType, server_default="de_DE")
    logged_in = sa.Column(sa.Boolean, server_default="1")
    is_superuser = sa.Column(sa.Boolean, server_default="0")
    is_verified = sa.Column(sa.Boolean, server_default="0")
    activation_key = sa.Column(sa.String)
    disabled = sa.Column(ArrowType)

    async def create(self, connection: Connection, data=None) -> dict or None:
        table = self.__table__
        stmt = table.insert().values(data).returning(table)
        statement = str(stmt.compile(compile_kwargs=dict(literal_binds=True)))
        result = await connection.fetchrow(statement)
        if result:
            return dict(result)
        else:
            return None

class AccessToken(Base, BaseModel):
    __tablename__ = 'access_token'
    account_id = ForeignKey('account')
    acc_token = sa.Column(sa.String)
