"""
cert.py
Tim "tjtimer" Jedro
01.10.2018
"""
import asyncio

from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path

from bonham.storage import file


async def create_key_s(password: bytes, path: [str, Path]=None, prefix: str=None):
    key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=openssl.backend
        )
    private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
    public_key = key.public_key()
    pub_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
        )
    if path is None:
        path = Path.cwd() / ".ssl"
    await asyncio.gather(
        file.write(f"{path / f'.{prefix}_priv.pem'}", "b", private_key),
        file.write(f"{path / f'.{prefix}_pub.pem'}", "b", pub_key)
    )
