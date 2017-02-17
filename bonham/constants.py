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
    pub = 1
    reg = 2
    fol = 3
    fri = 4
    edi = 5
    adm = 6
    pri = 7


PrivacyStatus.pub.label = (u'Public')
PrivacyStatus.reg.label = (u'Registered')
PrivacyStatus.fol.label = (u'Follower')
PrivacyStatus.fri.label = (u'Friends')
PrivacyStatus.edi.label = (u'Editors')
PrivacyStatus.adm.label = (u'Admins')
PrivacyStatus.pri.label = (u'Private')


class Salutations(Enum):
    mr = 1
    mrs = 2
