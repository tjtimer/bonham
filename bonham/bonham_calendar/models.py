from asyncio import gather

from asyncpg.connection import Connection
from sqlalchemy import UniqueConstraint
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.db import Base, BaseModel, Connect, ForeignKey
from bonham.validators import *
from .constants import EntryStatus, ReminderType

__all__ = ['CalendarType', 'Calendar', 'Entry', 'CalendarEntry', 'CalendarEntryReminder',
           'CalendarAdmin', 'CalendarEditor', 'EntryAdmin', 'EntryEditor']


class CalendarType(Base, BaseModel):
    __tablename__ = 'calendar_type'
    title = sa.Column(sa.String(64))

    @staticmethod
    async def valid_type(value: str) -> bool:
        valid = await gather(
                is_longer_than(value, 4),
                is_shorter_than(value, 64),
                has_no_specialchars(value)
                )
        return all(valid)

    async def get_or_create(self, connection: Connection, *, data: dict = None) -> dict:
        stmt = f"SELECT id, title FROM {self.__table__} WHERE title='{data['title']}'"
        cal_type = await connection.fetchrow(stmt)
        if not cal_type:
            columns = "(title, created)"
            values = f"('{data['title']}', CURRENT_TIMESTAMP)"
            stmt = f"INSERT INTO {self.__table__} {columns} VALUES {values} RETURNING *"
            cal_type = await connection.fetchrow(stmt)
        return dict(cal_type)


class Calendar(Base, BaseModel):
    owner = ForeignKey('account')
    type = ForeignKey('calendar_type')
    title = sa.Column(sa.String(64), primary_key=True)
    color = sa.Column(sa.String(20))
    show = sa.Column(sa.Boolean, server_default='1')
    __table_args__ = (UniqueConstraint('owner', 'type', 'title', name='_creator_type_title_uc'),)

    @staticmethod
    async def valid_title(value: str) -> bool:
        valid = await gather(
                is_longer_than(value, 4),
                is_shorter_than(value, 64),
                has_no_specialchars(value)
                )
        return all(valid)

    async def create(self, connection, data: dict = None):
        columns = "(type, owner, title, color, created)"
        values = f"({data['type']}, {data['owner']}, '{data['title']}', '{data['color']}', CURRENT_TIMESTAMP)"
        statement = f"INSERT INTO {self.table__} {columns} VALUES {values} RETURNING *"
        calendar = await connection.fetchrow(statement)
        return dict(calendar)

    async def update(self, connection, id: int = None, data: dict = None):
        columns = f"({' '.join(data.keys())}, last_updated)"
        values = f"({', '.join(data.values())}, CURRENT_TIMESTAMP)"
        statement = f"UPDATE {self.table__} SET {columns} VALUES {values} WHERE id={id} RETURNING *"
        calendar = await connection.fetchrow(statement)
        return dict(calendar)


class Entry(Base, BaseModel):
    owner = ForeignKey('account')
    title = sa.Column(sa.String(120))
    start_date = sa.Column(sa.Date)
    start_time = sa.Column(sa.Time, nullable=True)
    end_date = sa.Column(sa.Date, nullable=True)
    end_time = sa.Column(sa.Time, nullable=True)
    whole_day = sa.Column(sa.Boolean, server_default='0')
    blocked = sa.Column(sa.Boolean, server_default='0')
    status = sa.Column(ChoiceType(EntryStatus, impl=sa.Integer()), server_default='1')
    publish_on = sa.Column(ArrowType(timezone=True))
    info = sa.Column(sa.Text)

    @staticmethod
    async def create(connection, data: dict = None):
        columns = "(type, owner, title, color, created)"
        values = f"({data['type']}, {data['owner']}, '{data['title']}', '{data['color']}', CURRENT_TIMESTAMP)"
        statement = f"INSERT INTO calendar {columns} VALUES {values} RETURNING *"
        calendar = await connection.fetchrow(statement)
        return dict(calendar)

    @staticmethod
    async def update(connection, data: dict = None):
        columns = f"({' '.join(data.keys()) }, last_updated)"
        values = f"({''', '''.join(data.values())}, CURRENT_TIMESTAMP)"
        statement = f"INSERT INTO calendar {columns} VALUES {values} RETURNING *"
        calendar = await connection.fetchrow(statement)
        return dict(calendar)


class CalendarEntry(Base, Connect):
    __tablename__ = 'calendar_entry'
    calendar_id = ForeignKey('calendar')
    entry_id = ForeignKey('entry')


class CalendarEntryReminder(Base, BaseModel):
    __tablename__ = 'calendar_entry_reminder'
    calendar_entry_id = ForeignKey('entry')
    date_time = sa.Column(ArrowType(timezone=True))
    type = sa.Column(ChoiceType(ReminderType, impl=sa.Integer()))


class CalendarAdmin(Base, Connect):
    __tablename__ = 'calendar_admin'
    account_id = ForeignKey('account')
    calendar_id = sa.Column(sa.Integer, nullable=False)


class CalendarEditor(Base, Connect):
    __tablename__ = 'calendar_editor'
    account_id = ForeignKey('account')
    calendar_id = sa.Column(sa.Integer, nullable=False)


class EntryAdmin(Base, Connect):
    __tablename__ = 'entry_admin'
    account_id = ForeignKey('account')
    entry_id = sa.Column(sa.Integer, nullable=False)


class EntryEditor(Base, Connect):
    __tablename__ = 'entry_editor'
    account_id = ForeignKey('account')
    entry_id = sa.Column(sa.Integer, nullable=False)
