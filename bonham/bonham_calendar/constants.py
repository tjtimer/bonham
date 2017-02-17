from enum import Enum


class ReminderType(Enum):
    notification = 1
    email = 2
    song = 3


ReminderType.notification.label = 'Notification'
ReminderType.email.label = 'Email'
ReminderType.song.label = 'Song'
