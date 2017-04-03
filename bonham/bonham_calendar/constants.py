from enum import Enum


class EntryStatus(Enum):
    fix = 1
    cancelled = 2
    negotiation = 3


class ReminderType(Enum):
    notification = 1
    email = 2
    song = 3


ReminderType.notification.label = 'Notification'
ReminderType.email.label = 'Email'
ReminderType.song.label = 'Song'
