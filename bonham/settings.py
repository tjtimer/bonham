import logging
import os
import socket

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'public', 'templates')
UPLOAD_DIR = os.path.join(BASE_DIR, 'public', 'media')
STATIC_URL = 'assets/'
MEDIA_URL = 'media/'

LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')
LOG_FORMAT = '\n%(asctime)s\t%(name)s - %(levelname)s\n' \
             '\t-\t%(pathname)s - %(filename)s - %(funcName)s\n' \
             '\t-\t%(''message)s'

DEBUG = socket.gethostname() in 'tjs-roadrunner'  # True if it is my machine, false if it is not

if DEBUG:
    DSN = 'postgresql://tjtimer@127.0.0.1:5432/tjs_dev_db'
    LOG_LEVEL = logging.DEBUG


else:
    DSN = 'postgresql://<username>:<password>@<host>:<port>/<dbname>'
    LOG_LEVEL = logging.WARN

INSTALLED_MIDDLEWARES = []

RSA_DIR = os.path.join(BASE_DIR, 'rsa/self_signed')
RSA_PEM = os.path.join(RSA_DIR, 'rsa.pem')
RSA_PUB = os.path.join(RSA_DIR, 'rsa.pub')

LOCALE_DIR = os.path.join(BASE_DIR, 'application/locales')

IMAGE_VARIANTS = {
    'original': None,  # save image as is
    'xs': 80,  # resize and maybe crop to 80 x 80 pixels
    's': 160,  # resize and maybe crop to 160 x 160 pixels
    'm': 320,  # resize longest side to 320 and keep aspect ratio
    'l': 480,  # resize longest side to 480 and keep aspect ratio
    'xl': 800  # resize longest side to 800 and keep aspect ratio
}

EMAIL_ADDRESSES = {
    'registration': {
        'address': 'registration@domain.com',
        'password': 'MyHolySecret'
    }
}
EMAIL_TEMPLATES_DIR = os.path.join(BASE_DIR, 'email/templates')
MAIL_HOST = 'mail.wservices.ch'
SMTP_PORT = 465
IMAP_PORT = 993
POP3_PORT = 995
