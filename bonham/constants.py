from enum import Enum


class UserAgentStatus(Enum):
    undefined = 1
    blocked = 2
    marked = 3


class UserStatus(Enum):
    admin = 1
    editor = 2
    regular = 3
    blocked = 4


UserStatus.admin.label = (u'Admin')
UserStatus.editor.label = (u'Editor')
UserStatus.regular.label = (u'Regular bonham_profile')
UserStatus.blocked.label = (u'Blocked bonham_profile')


class PrivacyStatus(Enum):
    public = 1
    registered = 2
    follower = 3
    friends = 4
    editors = 5
    admins = 6
    private = 7


PrivacyStatus.public.label = (u'Public')
PrivacyStatus.registered.label = (u'Registered')
PrivacyStatus.follower.label = (u'Follower')
PrivacyStatus.friends.label = (u'Friends')
PrivacyStatus.editors.label = (u'Editors')
PrivacyStatus.admins.label = (u'Admins')
PrivacyStatus.private.label = (u'Private')
