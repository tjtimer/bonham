"""
ssl
"""
import logging
import ssl
from _ssl import PROTOCOL_TLSv1_2

import aiofiles

from bonham.core.crypto import get_secret


logger = logging.getLogger(__name__)

import os
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


async def create_priv_pub_keys(config, name):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=openssl.backend
    )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(
            await get_secret(os.path.join(config.SECRETS_PATH, f".{name}"))
        )
    )
    public_key = key.public_key()
    pub_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1,
    )
    async with aiofiles.open(
            os.path.join(config.CERTIFICATES_DIR, f"{name}_pr.pem"), "w+b") as f:
        f.write(private_key)
    async with aiofiles.open(
            os.path.join(config.CERTIFICATES_DIR, f"{name}_pu.pem"), "w+b") as f:
        f.write(pub_key)


def get_ssl_context(ciphers: str = None, *,
                    protocol=PROTOCOL_TLSv1_2,
                    purpose=ssl.Purpose.SERVER_AUTH) -> ssl.SSLContext:
    ssl_context = ssl.SSLContext(protocol=protocol)
    ssl_context.load_default_certs(purpose=purpose)
    if ciphers is None:
        ciphers = ':'.join([cip['name'] for cip in ssl_context.get_ciphers()
                            if 'ECDSA' in cip['description']])
    ssl_context.set_ciphers(ciphers)
    return ssl_context
