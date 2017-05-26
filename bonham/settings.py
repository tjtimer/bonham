import logging
import os
import socket

from .local_settings import LOCAL_ADMIN, LOCAL_DB_PW, LOCAL_DB_USER, LOCAL_DSN

HOST = 'tjtimer.dev'
PORTS = [9090, 9091, 9092]
DEBUG = socket.gethostname() in 'tjs-roadrunner'  # True if it is my machine, false if it is not
if not DEBUG:
    DEVELOPMENT_MODE = False
else:
    DEVELOPMENT_MODE = True

ADMINS = [LOCAL_ADMIN, ]

APPLICATION_NAME = 'bonham'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_DIR = os.path.join(BASE_DIR, APPLICATION_NAME)
TEMPLATE_DIR = os.path.join(SERVER_DIR, 'templates')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
UPLOAD_DIR = os.path.join(PUBLIC_DIR, 'media')
ASSETS_DIR = os.path.join(PUBLIC_DIR, 'assets')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
SOCKET_FILE = os.path.join(TMP_DIR, HOST)

ASSETS_URL = '/assets'
MEDIA_URL = '/media'

DB_USER = LOCAL_DB_USER
DB_PW = LOCAL_DB_PW

CA_DIR = os.path.join(BASE_DIR, 'rsa')
SELF_SIGNED_CA_DIR = os.path.join(CA_DIR, 'self_signed')
PRIVATE_KEY_FILE = os.path.join(SELF_SIGNED_CA_DIR, 'rsa.pem')
PUBLIC_KEY_FILE = os.path.join(SELF_SIGNED_CA_DIR, 'rsa.pub')

LOCALES_DIR = os.path.join(BASE_DIR, 'locales')

IMAGE_VARIANTS = {
    'original': None,  # save image as is
    'xs': 80,  # resize and maybe crop to 80 x 80 pixels
    's': 160,  # resize and maybe crop to 160 x 160 pixels
    'm': 320,  # resize longest side to 320 and keep aspect ratio
    'l': 480,  # resize longest side to 480 and keep aspect ratio
    'xl': 800  # resize longest side to 800 and keep aspect ratio
}

EMAIL_SERVER_HOST = 'localhost'
EMAIL_SERVER_PORT = 3030
SMTP_HOST = 'smtp.googlemail.com'
SMTP_PORT = 465
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
POP3_HOST = 'pop3.gmail.com'
POP3_PORT = 995

if DEBUG:
    DSN = LOCAL_DSN
    LOG_LEVEL = logging.DEBUG


else:
    DSN = 'postgresql://<username>:<password>@<host>:<port>/<dbname>'
    LOG_LEVEL = logging.INFO
