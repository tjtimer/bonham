import os

from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization

from bonham.local_settings import RSA_SECRET
from bonham.settings import PRIVATE_KEY_FILE, PUBLIC_KEY_FILE, SELF_SIGNED_CA_DIR


def create_self_signed_ca():
    print('called')
    from cryptography.hazmat.primitives.asymmetric import rsa
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
    with open(os.path.join(SELF_SIGNED_CA_DIR, PRIVATE_KEY_FILE), "w+b") as f:
        f.write(private_key)
    with open(os.path.join(SELF_SIGNED_CA_DIR, PUBLIC_KEY_FILE), "w+b") as f:
        f.write(pub_key)
    print('keys _ready')
