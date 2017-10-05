import logging
import os
import socket
from os.path import join as opj

import bonham.local_settings as ls

os.environ['VIRTUAL_ENV'] = '/var/www/tjtimer.com/server/venv/tjtimer-com'
DEBUG = socket.gethostname() in ls.DEV_MACHINE
MAX_PROCESSES = len(os.sched_getaffinity(0)) * 2 + 1

SERVICE_NAME = "tjtimer.com"

if DEBUG:
    HOST = 'tjtimer.dev'
    PORT = 9090

    SUPERUSERS = [ls.LOCAL_SUPERUSER, ]

    DSN = ls.LOCAL_DSN
    DB_USER = ls.LOCAL_DB_USER
    DB_PW = ls.LOCAL_DB_PW

    MONITOR_HOST = ls.MONITOR_HOST
    MONITOR_PORT = ls.MONITOR_PORT

    LOG_LEVEL = logging.DEBUG
else:
    # service host and port
    HOST = 'example.com'
    PORT = 8000

    # superusers/admins
    SUPERUSERS = ['PRODUCTION_ADMIN_1', 'PRODUCTION_ADMIN_2', ...]

    # database
    DSN = 'postgresql://<username>:<password>@<host>:<port>/<dbname>'
    DB_USER = 'PRODUCTION_DB_USER'
    DB_PW = 'PRODUCTION_DB_PASSWORD'

    # service monitor
    MONITOR_HOST = 'localhost'  # could also be a public domain
    MONITOR_PORT = 12345  # a 'secure' port

    # log level
    LOG_LEVEL = logging.INFO


HTTPS = True
BASE_DIR = opj('/var/www', SERVICE_NAME)

PUBLIC_DIR = opj(BASE_DIR, 'public')
SERVER_DIR = opj(BASE_DIR, 'server')
CONF_DIR = opj(SERVER_DIR, 'conf')
TEMPLATES_DIR = opj(SERVER_DIR, 'templates')
LOG_DIR = opj(SERVER_DIR, 'logs')
TMP_DIR = opj(SERVER_DIR, 'tmp')
SOCK_DIR = opj(SERVER_DIR, 'socks')

ASSETS_URL = '/assets'
MEDIA_URL = '/media'

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

