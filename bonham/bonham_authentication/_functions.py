import os
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization

from bonham.settings import RSA_DIR, RSA_PEM, RSA_PUB


def create_self_signed_ca():
    print('called')
    from cryptography.hazmat.primitives.asymmetric import rsa
    key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=openssl.backend
    )
    private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = key.public_key()
    pub_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
    )
    with open(os.path.join(RSA_DIR, RSA_PEM), "w+b") as f:
        f.write(private_key)
    with open(os.path.join(RSA_DIR, RSA_PUB), "w+b") as f:
        f.write(pub_key)
    print('keys ready')
