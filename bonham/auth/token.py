import aiofiles
import arrow
import jwt
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization


__all__ = ['create_token', 'decode_token', 'verify_token']

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

