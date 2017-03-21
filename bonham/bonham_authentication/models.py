import re
from uuid import uuid4

import sqlalchemy as sa
from asyncpg import ProtocolViolationError, UniqueViolationError
from sqlalchemy_utils import ArrowType, PasswordType

from bonham.db import Base, BaseModel, ForeignKey, create_tables
from constants import PrivacyStatus


async def valid_email(value: str = None) -> bool:
    print(value)
    print(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value))
    return False if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value) is None else True


async def valid_password(value: str = None) -> bool:
    has_minlength = len(value) >= 8
    has_digits = re.search("[0-9]", value) is not None
    has_uppercase = re.search("[A-Z]", value) is not None
    has_lowercase = re.search("[a-z]", value) is not None
    has_specialchars = re.search("[!*+?$%&/()#\\\]", value) is not None
    has_no_whitespaces = re.search("\s", value) is None
    password_props = [
        has_minlength,
        has_digits,
        has_uppercase,
        has_lowercase,
        has_specialchars,
        has_no_whitespaces
        ]
    return all(val for val in password_props)


async def validate_data(data: dict = None) -> dict:
    for key, value in data.items():
        if key == 'password':
            if await valid_password(value=value):
                yield key, value
            else:
                raise ValueError('Password invalid!')
        if key == 'email':
            if await valid_email(value=value):
                yield key, value
            else:
                raise ValueError('Email invalid!')


class AccessToken(Base, BaseModel):
    account_id = ForeignKey('account')
    acc_token = sa.Column(sa.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Account(Base, BaseModel):
    email = sa.Column(sa.String(255), index=True, unique=True)
    password = sa.Column(PasswordType(
            schemes=['pbkdf2_sha512', 'md5_crypt'],
            deprecated=['md5_crypt']
            ), nullable=False)
    logged_in = sa.Column(sa.Boolean, server_default="1")
    is_admin = sa.Column(sa.Boolean, server_default="0")
    is_superuser = sa.Column(sa.Boolean, server_default="0")
    is_verified = sa.Column(sa.Boolean, server_default="0")
    activation_key = sa.Column(sa.String)
    locked = sa.Column(ArrowType)

    def __init__(self, **kwargs):
        self.tbl = self.__table__
        self.columns = self.tbl.c.keys()
        if 'activation_key' not in kwargs.keys():
            kwargs['activation_key'] = uuid4().hex
        if 'privacy' not in kwargs.keys():
            kwargs['privacy'] = PrivacyStatus.private.value
        super().__init__(**kwargs)

    async def create(self, *, connection=None):
        table = self.tbl
        data = {key: value for key, value in vars(self).items() if key in self.columns}
        try:
            stmt = table.insert().values(**data).returning(table)
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            result = await connection.fetchrow(statement)
            return vars(self).update(dict(result))
        except UniqueViolationError:
            raise UniqueViolationError(f"account with email {self.email} already exists.")
        except ProtocolViolationError as e:
            print(f"ProtocolViolationError at Account.create() -> {e}\n"
                  f"connection: {connection}")
        except Exception as e:
            print(f"create {self.tbl} exception: {type(e).__name__} -> {e}")
            raise

    async def serialized(self):
        """
        coroutine serialized(self)
        :return: json serializable key-value pairs of instance
        :rtype: object
        """
        data = await super().serialized()
        return {key: value for key, value in data.items() if key in self.columns and key not in 'password'}


create_tables(models=[Account, AccessToken])
