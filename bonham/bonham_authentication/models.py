import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, PasswordType

from bonham.db import Base, BaseModel


class AuthUser(Base, BaseModel):
    email = sa.Column(sa.String(255), index=True, unique=True)
    password = sa.Column(PasswordType(
            schemes=['pbkdf2_sha512', 'md5_crypt'],
            deprecated=['md5_crypt']
    ), nullable=False)
    logged_in = sa.Column(sa.Boolean, default=False)
    is_admin = sa.Column(sa.Boolean, default=False)
    is_superuser = sa.Column(sa.Boolean, default=False)
    is_verified = sa.Column(sa.Boolean, default=False)
    activation_key = sa.Column(sa.String)
    deactivated = sa.Column(ArrowType)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
