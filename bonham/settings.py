import logging
import os
from os.path import join as opj
import socket

from .local_settings import *
os.environ['VIRTUAL_ENV'] = '/var/www/tjtimer.com/server/venv/tjtimer-com'
DEBUG = socket.gethostname() in 'tjs-roadrunner'  # True if it is my machine, false if not

if DEBUG:
    DSN = LOCAL_DSN
    LOG_LEVEL = logging.DEBUG
    ADMINS = [LOCAL_ADMIN, ]
else:
    DSN = 'postgresql://<username>:<password>@<host>:<port>/<dbname>'
    LOG_LEVEL = logging.INFO
    ADMINS = 'PRODUCTION_ADMINS'

APPLICATION_NAME = 'tjtimer.com'
BASE_DIR = opj('/var/www', APPLICATION_NAME)

PUBLIC_DIR = opj(BASE_DIR, 'public')
SERVER_DIR = opj(BASE_DIR, 'server')
CONF_DIR = opj(SERVER_DIR, 'conf')
TEMPLATES_DIR = opj(SERVER_DIR, 'templates')
LOG_DIR = opj(SERVER_DIR, 'logs')
TMP_DIR = opj(SERVER_DIR, 'tmp')
PID_DIR = opj(SERVER_DIR, 'pids')
SOCK_DIR = opj(SERVER_DIR, 'socks')
SOCKET_FILE = opj(SOCK_DIR, f"{APPLICATION_NAME}")

ASSETS_URL = '/assets'
MEDIA_URL = '/media'

DB_USER = LOCAL_DB_USER
DB_PW = LOCAL_DB_PW

RSA_DIR = opj(SERVER_DIR, 'rsa')
SELF_SIGNED_CA_DIR = opj(RSA_DIR, 'self_signed')
PRIVATE_KEY_FILE = opj(SELF_SIGNED_CA_DIR, 'rsa.pem')
PUBLIC_KEY_FILE = opj(SELF_SIGNED_CA_DIR, 'rsa.pub')

LOCALES_DIR = opj(SERVER_DIR, 'locales')

EMAIL_SERVER_HOST = 'localhost'
EMAIL_SERVER_PORT = 3030
SMTP_HOST = 'smtp.googlemail.com'
SMTP_PORT = 465
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
POP3_HOST = 'pop3.gmail.com'
POP3_PORT = 995

