import sqlalchemy as sa
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.bonham_calendar.constants import ReminderType
from bonham.db import Base, BaseModel, ForeignKey, create_tables


class Calendar(Base, BaseModel):
    title = sa.Column(sa.String(50))
    color = sa.Column(sa.String(20))
    show = sa.Column(sa.Boolean, server_default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Entry(Base, BaseModel):
    title = sa.Column(sa.String(120))
    start_date = sa.Column(sa.Date)
    start_time = sa.Column(sa.Time, nullable=True)
    end_date = sa.Column(sa.Date, nullable=True)
    end_time = sa.Column(sa.Time, nullable=True)
    whole_day = sa.Column(sa.Boolean, server_default=False)
    blocked = sa.Column(sa.Boolean, server_default=False)
    publish_on = sa.Column(sa.DateTime)
    description = sa.Column(sa.Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CalendarEntry(Base, BaseModel):
    calendar_id = ForeignKey(Calendar)
    entry_id = ForeignKey(Entry)


class CalendarEntryReminder(Base, BaseModel):
    calendar_entry_id = ForeignKey(Entry)
    date_time = sa.Column(ArrowType)
    type = sa.Column(ChoiceType(ReminderType, impl=sa.Integer()))


create_tables(models=[Calendar, Entry, CalendarEntry, CalendarEntryReminder])
