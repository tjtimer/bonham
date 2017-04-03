import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.db import Base, BaseModel, ForeignKey
from .constants import Connection, ConnectionType

__all__ = ['Group', 'User', 'GGConnection', 'GUConnection', 'UUConnection', 'GroupAdmin', 'GroupEditor']


class Group(Base, BaseModel):
    owner = ForeignKey('account')
    name = sa.Column(sa.String(60), unique=True)
    avatar = sa.Column(sa.String)
    slogan = sa.Column(sa.String(120))


class User(Base, BaseModel):
    owner = ForeignKey('account')
    name = sa.Column(sa.String(60), unique=True)
    avatar = sa.Column(sa.String)
    slogan = sa.Column(sa.String(120))
    birthday = sa.Column(ArrowType)


class GGConnection(Base, BaseModel):
    group1_id = ForeignKey('group')
    group2_id = ForeignKey('group')
    connection = sa.Column(ChoiceType(Connection, impl=sa.Integer()))
    connection_type = sa.Column(ChoiceType(ConnectionType, impl=sa.Integer()))


class GUConnection(Base, BaseModel):
    group_id = ForeignKey('group')
    user_id = ForeignKey('user')
    connection = sa.Column(ChoiceType(Connection, impl=sa.Integer()))
    connection_type = sa.Column(ChoiceType(ConnectionType, impl=sa.Integer()))


class UUConnection(Base, BaseModel):
    user1_id = ForeignKey('user')
    user2_id = ForeignKey('user')
    connection = sa.Column(ChoiceType(Connection, impl=sa.Integer()))
    connection_type = sa.Column(ChoiceType(ConnectionType, impl=sa.Integer()))


class GroupAdmin(Base, BaseModel):
    account_id = ForeignKey('account')
    object_id = sa.Column(sa.Integer, nullable=False)


class GroupEditor(Base, BaseModel):
    account_id = ForeignKey('account')
    object_id = sa.Column(sa.Integer, nullable=False)
