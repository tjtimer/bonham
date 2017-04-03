from enum import Enum


class Connection(Enum):
    accepted = 1
    blocked = 2
    ignored = 3
    requested = 4


Connection.accepted.label = (u'accepted')
Connection.blocked.label = (u'blocked')
Connection.ignored.label = (u'ignored')
Connection.requested.label = (u'requested')


class ConnectionType(Enum):
    admin = 1
    editor = 2
    follower = 3


ConnectionType.admin.label = u'admin'
ConnectionType.editor.label = u'editor'
ConnectionType.follower.label = u'follower'
