"""
crypto
"""
import os

from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def create_priv_pub_keypair(config):
    """
    creates self signed certificates for development purposes
    """
    rsa_dir = os.path.join(config['server_root'], config['rsa_dir'])
    rsa_secret = get_rsa_secret()
    key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=openssl.backend
            )
    private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(
                rsa_secret)
            )
    public_key = key.public_key()
    pub_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1,
            )
    with open(os.path.join(rsa_dir, 'priv.pem'), 'wb') as f:
        f.write(private_key)
    with open(os.path.join(rsa_dir, 'pub.pem'), 'wb') as f:
        f.write(pub_key)
