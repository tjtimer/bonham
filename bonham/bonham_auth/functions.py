import arrow
from aiohttp import web
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from passlib.hash import pbkdf2_sha512

from bonham.bonham_core.exceptions import RequestDenied
from bonham.settings import *

__all__ = [
    'create_self_signed_ca',
    'check_password',
    'check_retries',
    'update_failed'
    ]


def create_self_signed_ca():
    """
    creates self signed certificates for development purposes
    """
    key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=openssl.backend
            )
    private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(bytes(RSA_SECRET, encoding='utf-8'))
            )
    public_key = key.public_key()
    pub_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
            )
    with open(os.path.join(SELF_SIGNED_CA_DIR, PRIVATE_KEY_FILE), 'wb') as f:
        f.write(private_key)
    with open(os.path.join(SELF_SIGNED_CA_DIR, PUBLIC_KEY_FILE), 'wb') as f:
        f.write(pub_key)

async def check_password(request: web.Request, db_pass: str):
    req_pass = request['data']['password']
    if not pbkdf2_sha512.verify(req_pass, db_pass):
        await update_failed(request)
        raise RequestDenied('wrong password')


async def check_retries(email: str, failed_logins: dict) -> None:
    if email in failed_logins.keys():
        now = arrow.now()
        if len(failed_logins[email]) >= 3 and failed_logins[email][-1].replace(seconds=90) <= now:
            wait_until = now.replace(minutes=5).format('HH:mm:ss')
            error_message = f"To many failed retries. Please wait 5 minutes, until {wait_until}."
            raise RequestDenied(error_message)


async def update_failed(request: web.Request) -> None:
    print(f"\n\nupdate_failed:\n\trequest: {vars(request)}")
    email = request['data']['email']
    failed_logins = request.app['failed_logins']
    now = arrow.now()
    if email in failed_logins.keys():
        failed_logins[email].append(now)
    else:
        failed_logins[email] = [now]
