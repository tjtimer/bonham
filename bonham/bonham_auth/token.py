import os.path as path

import aiofiles
import arrow
import jwt
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization

from bonham.local_settings import RSA_SECRET
from bonham.settings import DEBUG, HOST, PRIVATE_KEY_FILE, PUBLIC_KEY_FILE
from ._functions import create_self_signed_ca

__all__ = ['create_access_token', 'decode_token', 'verify_token']


if DEBUG and not path.isfile(PUBLIC_KEY_FILE):
    create_self_signed_ca()

async def get_private_key():

    async with aiofiles.open(PRIVATE_KEY_FILE, 'rb') as private_key_file:
        _private_key = await private_key_file.read()
        private_key = serialization.load_pem_private_key(
                _private_key,
                password=bytes(RSA_SECRET, encoding='utf-8'),
                backend=openssl.backend)
        return private_key

async def get_payload(request) -> dict:
    payload = dict(
            id=request['account']['id'],
            email=request['account']['email'],
            host=HOST
            )
    return payload

async def create_refresh_token(request) -> str:
    payload = await get_payload(request)
    payload['exp'] = arrow.utcnow().replace(hours=24).format('X')
    private_key = await get_private_key()
    refresh_token = jwt.encode(payload, private_key, algorithm='RS256')
    return refresh_token.decode('utf-8')

async def create_access_token(request) -> str:
    payload = await get_payload(request)
    payload['exp'] = arrow.utcnow().replace(minutes=5).format('X')
    private_key = await get_private_key()
    access_token = jwt.encode(payload, private_key, algorithm='RS256')
    return access_token.decode('utf-8')


async def decode_token(token: str) -> dict:
    async with aiofiles.open(PUBLIC_KEY_FILE, 'rb') as pub_file:
        pub_key = await pub_file.read()
        payload = jwt.decode(token, pub_key, algorithms=['RS256'])
    return payload


async def verify_token(token: str) -> dict:
    data = await decode_token(token)
    expired = arrow.get(data['exp']) < arrow.now()
    if expired:
        raise jwt.ExpiredSignatureError
    return data

