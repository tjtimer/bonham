# bonham_profile / models.py
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType

from bonham.db import ForeignKey
from bonham.models import Base, BaseModel

__all__ = []


class Profile(Base, BaseModel):
    owner = ForeignKey('account')
    name = sa.Column(sa.String(64), primary_key=True)
    avatar = sa.Column(sa.String, server_default='/defaults/images/avatar.png')
    birthday = sa.Column(ArrowType, nullable=True)




