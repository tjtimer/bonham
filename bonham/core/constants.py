from enum import Enum


__all__ = [
    'UserAgentStatus',
    'Privacy'
    ]


class UserAgentStatus(Enum):
    undefined = 1
    blocked = 2
    marked = 3


class Privacy(Enum):
    public = 1
    registered = 2
    follower = 3
    friends = 4
    editors = 5
    admins = 6
    private = 7


Privacy.public.label = (u'Public')
Privacy.registered.label = (u'Registered')
Privacy.follower.label = (u'Follower')
Privacy.friends.label = (u'Friends')
Privacy.editors.label = (u'Editors')
Privacy.admins.label = (u'Admins')
Privacy.private.label = (u'Private')
