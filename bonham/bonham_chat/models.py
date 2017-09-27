"""
Name: bonham - models 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 24.09.17 21:07
"""

import logging

import sqlalchemy as sa
from sqlalchemy_utils import ScalarListType, TSVectorType

from bonham.bonham_core.db import ForeignKey
from bonham.bonham_core.models import Base, Model

__all__ = ()

logger = logging.getLogger(__name__)


class Chat(Base, Model):
    name = sa.Column(sa.String(60), primary_key=True)
    profile_ids = sa.Column(ScalarListType(), nullable=False)


class Entry(Base, Model):
    chat_id = ForeignKey('chat')
    profile_id = ForeignKey('profile')
    message = sa.Column(sa.Text, nullable=True)
    message_vector = sa.Column(TSVectorType)
