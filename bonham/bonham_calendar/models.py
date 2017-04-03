from asyncio import gather

from asyncpg.connection import Connection
from sqlalchemy import UniqueConstraint
import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.db import Association, Base, BaseModel, ForeignKey
from bonham.validators import *
from .constants import EntryStatus, ReminderType

__all__ = ['CalendarType', 'Calendar', 'Entry', 'CalendarEntry', 'CalendarEntryReminder',
           'CalendarAdmin', 'CalendarEditor', 'EntryAdmin', 'EntryEditor']


class CalendarType(Base, BaseModel):
    title = sa.Column(sa.String(64))

    @staticmethod
    async def valid_type(value: str) -> bool:
        valid = await gather(
                is_longer_than(value, 4),
                is_shorter_than(value, 64),
                has_no_specialchars(value)
                )
        return all(valid)

    @staticmethod
    async def get_or_create(connection: Connection, *, data: dict = None) -> dict:
        stmt = f"SELECT id, title FROM calendartype WHERE title='{data['title']}'"
        cal_type = await connection.fetchrow(stmt)
        if not cal_type:
            columns = "(title, created)"
            values = f"('{data['title']}', CURRENT_TIMESTAMP)"
            stmt = f"INSERT INTO calendartype {columns} VALUES {values} RETURNING *"
            cal_type = await connection.fetchrow(stmt)
        return dict(cal_type)


class Calendar(Base, BaseModel):
    owner = ForeignKey('account')
    type = ForeignKey('calendartype')
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

    @staticmethod
    async def create(connection, data: dict = None):
        columns = "(type, owner, title, color, created)"
        values = f"({data['type']}, {data['owner']}, '{data['title']}', '{data['color']}', CURRENT_TIMESTAMP)"
        statement = f"INSERT INTO calendar {columns} VALUES {values} RETURNING *"
        calendar = await connection.fetchrow(statement)
        return dict(calendar)

    @staticmethod
    async def update(connection, id: int = None, data: dict = None):
        columns = f"({' '.join(data.keys())}, last_updated)"
        values = f"({', '.join(data.values())}, CURRENT_TIMESTAMP)"
        statement = f"UPDATE calendar SET {columns} VALUES {values} WHERE id={id} RETURNING *"
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


class CalendarEntry(Base, Association):
    calendar_id = ForeignKey('calendar')
    entry_id = ForeignKey('entry')


class CalendarEntryReminder(Base, BaseModel):
    calendar_entry_id = ForeignKey('entry')
    date_time = sa.Column(ArrowType(timezone=True))
    type = sa.Column(ChoiceType(ReminderType, impl=sa.Integer()))


class CalendarAdmin(Base, Association):
    account_id = ForeignKey('account')
    calendar_id = sa.Column(sa.Integer, nullable=False)


class CalendarEditor(Base, Association):
    account_id = ForeignKey('account')
    calendar_id = sa.Column(sa.Integer, nullable=False)


class EntryAdmin(Base, Association):
    account_id = ForeignKey('account')
    entry_id = sa.Column(sa.Integer, nullable=False)


class EntryEditor(Base, Association):
    account_id = ForeignKey('account')
    entry_id = sa.Column(sa.Integer, nullable=False)
