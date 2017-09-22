"""
Name: bonham models 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 

27.08.17 13:43
"""
import asyncpg
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType

from bonham.bonham_core.db import ForeignKey
from bonham.bonham_core.models import Content

__all__ = ()

import logging

logger = logging.getLogger(__name__)


class Gallery(Content):
    r"""Gallery Model
    additional fields:
        profile: int (references a profile)
        title: str (max. length is 60, may not be empty),
        title_image: str,
        description: str,
        pub_date: datetime
    """
    profile = ForeignKey('profile')
    title = sa.Column(sa.String(60), nullable=False, primary_key=True)
    title_image = ForeignKey('picture')
    description = sa.Column(sa.Text)
    pub_date = sa.Column(
        ArrowType(timezone=True),
        server_default=sa.func.current_timestamp())

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)
        self.required_fields.update('profile', 'title')


class Picture(Content):
    r"""Picture Model
    additional fields:
        gallery: int (references a gallery)
        title: str (defaults to filename)
        url: str (url or path to image file)
    """
    gallery = ForeignKey('gallery', ondelete="RESTRICT")
    title = sa.Column(sa.String(60), nullable=False, primary_key=True)
    url = sa.Column(sa.String(120), primary_key=True,
                    server_default='/media/galleries/default.jpeg')

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)
        self.required_fields.update('title', 'url')
