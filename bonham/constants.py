from enum import Enum


# from gettext import translation

# from .settings import LOCALEDIR

# language = translation('messages', localedir=LOCALEDIR, languages=['deDE', 'enEN'])
# language.install()


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
UserStatus.regular.label = (u'Regular bonham_user')
UserStatus.blocked.label = (u'Blocked bonham_user')


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


class Salutations(Enum):
    mr = 1
    mrs = 2
