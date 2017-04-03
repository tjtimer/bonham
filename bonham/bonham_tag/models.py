import sqlalchemy as sa

from bonham.db import Base, BaseModel, ForeignKey

__all__ = ['Tag', 'TaggedItem']


class Tag(Base, BaseModel):
    name = sa.Column(sa.String(60), primary_key=True)


class TaggedItem(Base, BaseModel):
    tag_id = ForeignKey('tag')
    table = sa.Column(sa.String, nullable=False)
    object_id = sa.Column(sa.Integer, nullable=False)
