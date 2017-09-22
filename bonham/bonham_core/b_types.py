from enum import Enum


class ClientStatusType(Enum):
    undefined = 1
    marked = 2
    blocked = 3


ClientStatusType.undefined.label = (u'undefined')
ClientStatusType.marked.label = (u'marked')
ClientStatusType.blocked.label = (u'blocked')


class PrivacyType(Enum):
    public = 1
    registered = 2
    follower = 3
    friends = 4
    editors = 5
    admins = 6
    private = 7


PrivacyType.public.label = (u'Public')
PrivacyType.registered.label = (u'Registered')
PrivacyType.follower.label = (u'Follower')
PrivacyType.friends.label = (u'Friends')
PrivacyType.editors.label = (u'Editors')
PrivacyType.admins.label = (u'Admins')
PrivacyType.private.label = (u'Private')
