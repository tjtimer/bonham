from asyncpg.connection import Connection
import sqlalchemy as sa

from bonham.db import Base, BaseModel, ForeignKey

__all__ = ['Tag', 'TaggedItem']


class Tag(Base, BaseModel):
    name = sa.Column(sa.String(60), primary_key=True)

    @staticmethod
    async def get_or_create(connection: Connection, *, data: dict = None) -> dict:
        if 'tag' not in data.keys():
            print(f"no tag name specified")
            raise ValueError(f"no tag name specified")
        stmt = f"SELECT id, tag FROM tag WHERE title='{data['tag']}'"
        tag = await connection.fetchrow(stmt)
        if not tag:
            columns = "(tag, created)"
            values = f"('{data['tag']}', CURRENT_TIMESTAMP)"
            stmt = f"INSERT INTO tag {columns} VALUES {values} RETURNING *"
            tag = await connection.fetchrow(stmt)
        return dict(tag)

class TaggedItem(Base, BaseModel):
    tag_id = ForeignKey('tag')
    table = sa.Column(sa.String, nullable=False)
    object_id = sa.Column(sa.Integer, nullable=False)
