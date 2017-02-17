from enum import Enum


class Friendship(Enum):
    requested = 1
    ignored = 2
    blocked = 3
    accepted = 4


Friendship.requested.label = (u'requested')
Friendship.ignored.label = (u'ignored')
Friendship.blocked.label = (u'blocked')
Friendship.accepted.label = (u'accepted')
