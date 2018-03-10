import os

import aiofiles
import arrow
import jwt
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


__all__ = ['create_token', 'create_self_signed_ca', 'decode_token', 'verify_token']


def create_self_signed_ca(config):
    """
    creates self signed certificates for development purposes
    """
    rsa_dir = os.path.join(
        config['server_root'], config['certificate_directory'])
    key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=openssl.backend
            )
    private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(
                bytes(config['rsa_secret'], encoding='utf-8'))
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

DEFAULT_EXPIRATION = arrow.now().replace(minutes=5).format('X')

async def get_private_key(key_file: str, secrets: str):
    async with aiofiles.open(key_file, 'rb') as private_key_file:
        _private_key = await private_key_file.read()
        private_key = serialization.load_pem_private_key(
                _private_key,
                password=bytes(secrets, encoding='utf-8'),
                backend=openssl.backend)
        return private_key


async def create_token(payload: dict, key_file, secrets) -> str:
    payload['exp'] = payload.pop('exp', DEFAULT_EXPIRATION)
    private_key = await get_private_key(key_file, secrets)
    access_token = jwt.encode(payload, private_key, algorithm='RS256')
    return access_token.decode('utf-8')


async def decode_token(token: str, key_file) -> dict:
    async with aiofiles.open(key_file, 'rb') as pub_file:
        pub_key = await pub_file.read()
        payload = jwt.decode(token, pub_key, algorithms=['RS256'])
    return payload


async def verify_token(token: str) -> dict:
    data = await decode_token(token)
    expired = arrow.get(data['exp']) < arrow.now()
    if expired:
        raise jwt.ExpiredSignatureError('Token Expired!')
    return data

