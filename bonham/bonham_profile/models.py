"""
Name: bonham models 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 

27.08.17 16:35
"""
from sqlalchemy.orm import scoped_session, sessionmaker

from bonham.bonham_core.db import ForeignKey
from bonham.bonham_core.models import Base, BaseModel

__all__ = ()

import logging
import sqlalchemy as sa

logger = logging.getLogger(__name__)


class Profile(BaseModel, Base):
    r"""Profile Model

    additional fields:
        owner: int (account id)
        name: str (max length is 60, primary_key is True, nullable is False)
        avatar: str (url or path to an image)
    """
    name = sa.Column(sa.String(60), index=True, primary_key=True)
    avatar = sa.Column(sa.String(120),
                       server_default="/media/galleries/default.jpeg")


class ProfileAccount(BaseModel, Base):
    r"""ProfileAdmin Model"""

    owner = ForeignKey('account')
    profile = ForeignKey('profile')


db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
