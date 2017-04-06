import sqlalchemy as sa
from sqlalchemy_utils import ArrowType

from bonham.db import Base, BaseModel, Connect, ForeignKey

__all___ = ['Gallery', 'Picture', 'GalleryPicture', 'GalleryAdmin', 'GalleryEditor', 'PictureAdmin', 'PictureEditor']


class Gallery(Base, BaseModel):
    owner = ForeignKey('account')
    title = sa.Column(sa.String(120))
    publish_on = sa.Column(ArrowType(timezone=True), server_default=sa.func.current_timestamp())


class Picture(Base, BaseModel):
    owner = ForeignKey('account')
    title = sa.Column(sa.String(120))
    description = sa.Column(sa.String)
    path = sa.Column(sa.String)


class GalleryPicture(Base, Connect):
    __tablename__ = 'gallery_picture'
    gallery_id = ForeignKey('gallery')
    picture_id = ForeignKey('picture')


class GalleryAdmin(Base, Connect):
    __tablename__ = 'gallery_admin'
    account_id = ForeignKey('account')
    object_id = sa.Column(sa.Integer, nullable=False)


class GalleryEditor(Base, Connect):
    __tablename__ = 'gallery_editor'
    account_id = ForeignKey('account')
    object_id = sa.Column(sa.Integer, nullable=False)


class PictureAdmin(Base, Connect):
    __tablename__ = 'picture_admin'
    account_id = ForeignKey('account')
    object_id = sa.Column(sa.Integer, nullable=False)


class PictureEditor(Base, Connect):
    __tablename__ = 'picture_editor'
    account_id = ForeignKey('account')
    object_id = sa.Column(sa.Integer, nullable=False)
