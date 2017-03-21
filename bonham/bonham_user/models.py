from uuid import uuid4

import arrow
import sqlalchemy as sa
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import ArrowType, ChoiceType, LocaleType

from bonham.bonham_user.constants import Friendship
from bonham.constants import PrivacyStatus
from bonham.db import Base, BaseModel, ForeignKey, create_tables


class Friend(Base, BaseModel):
    user_id = ForeignKey('user')
    friend_id = ForeignKey('user')
    friendship = sa.Column(ChoiceType(Friendship, impl=sa.Integer()))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class User(Base, BaseModel):
    account_id = ForeignKey('account')
    name = sa.Column(sa.String(60), unique=True)
    slogan = sa.Column(sa.String(120))
    birthday = sa.Column(ArrowType)
    avatar = sa.Column(sa.String)
    locale = sa.Column(LocaleType)
    logged_in = sa.Column(sa.Boolean, default=False)
    is_active = sa.Column(sa.Boolean, default=False)
    is_admin = sa.Column(sa.Boolean, default=False)
    is_superuser = sa.Column(sa.Boolean, default=False)
    is_verified = sa.Column(sa.Boolean, default=False)
    activation_key = sa.Column(sa.String)
    deactivated = sa.Column(ArrowType)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def create(self, connection):
        user_data = {
            'avatar': 'uploads/default/avatar/me.jpeg',
            'locale': 'de_DE',
            'privacy': PrivacyStatus.pub,
            'logged_in': True,
            'is_active': False,
            'is_admin': False,
            'is_superuser': False,
            'is_verified': False,
            'activation_key': str(uuid4().int),
            'created': arrow.utcnow()
        }
        data = { key: value for key, value in self.__dict__.items() if key in self.__table__.c.keys() }
        user_data.update(data)
        stmt = self.__table__.insert().values(**user_data).returning(self.__table__)
        try:
            proxy = await connection.execute(stmt)
            user = await proxy.first()
            self.__dict__.update(**user)
        except IntegrityError:
            raise IntegrityError(f"username: {user_data['name']} or email: {user_data['email']} already exists")

    async def add_friend(self, connection, *, friend_id=None):
        friendship = Friendship.requested
        new_friend = await Friend(
                user_id=self.id,
                friend_id=friend_id,
                friendship=Friendship.requested).create(connection)
        return new_friend

    async def update_friendship(self, connection, *, friend_id=None, friendship=None):
        _friendship = await Friend(user_id=self.id, friend_id=friend_id, friend_ship=friendship).update(connection)
        return _friendship

    async def get_friends(self, connection):
        """
        
        :param connection: database connection 
        :type connection: aiopg connection
        :return: list of serialized user objects 
        :rtype: generator
        """
        join = sa.join(
                self.__table__, Friend.__table__,
                and_(
                        or_(self.__table__.c.id == Friend.__table__.c.user_id,
                            self.__table__.c.id == Friend.__table__.c.friend_id),
                        Friend.__table__.c.friendship == Friendship.accepted
                )
        )
        query = sa.select([self.__table__, Friend.__table__]) \
            .select_from(join).where(self.__table__.c.id == self.id) \
            .distinct().order_by('name')
        result_proxy = await connection.execute(query)
        friends_serialized = ((await User(**dict(friend)).serialized()) for friend in (await result_proxy.fetchall()))
        return friends_serialized

    async def serialized(self):
        """
        coroutine serialized(self)
        :return: json serializable key-value pairs of instance
        :rtype: object
        """
        if self.birthday:
            self.birthday = arrow.get(self.birthday).format('YYYY-MM-DD')
        if self.created:
            self.created = arrow.get(self.created).humanize()
        if self.privacy:
            self.privacy = PrivacyStatus(self.privacy).label

        return { key: value for key, value in self.__dict__.items() if key in self.__table__.c.keys() }


create_tables(models=[User, Friend])
