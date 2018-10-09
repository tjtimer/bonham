import asyncio
import os
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from passlib.context import CryptContext

from bonham.storage import file


pwd_ctx = CryptContext.from_path('ctx.ini')


def encrypt(key, plaintext, associated_data):
    # Generate a random 96-bit IV.
    iv = os.urandom(12)

    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    enc = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    enc.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    enc_msg = enc.update(plaintext) + enc.finalize()

    return iv, enc_msg, enc.tag


def decrypt(key, associated_data, iv, enc_msg, tag):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    dec = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    dec.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return dec.update(enc_msg) + dec.finalize()


async def create_keys(password: bytes, path: [str, Path]=None, prefix: str=None):
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
