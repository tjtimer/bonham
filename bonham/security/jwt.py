from datetime import datetime

import arrow as arrow
import jwt
import aiofiles
from arrow import Arrow
from cryptography.hazmat.backends import openssl
from cryptography.hazmat.primitives import serialization


async def get_private_key():
    async with aiofiles.open(PRIVATE_KEY_FILE, 'rb') as private_key_file:
        _private_key = await private_key_file.read()
        private_key = serialization.load_pem_private_key(
                _private_key,
                password=bytes(RSA_SECRET, encoding='utf-8'),
                backend=openssl.backend)
        return private_key


async def create_token(payload: dict, *, exp: [int, datetime, Arrow]=None) -> str:
    if exp is None:
        exp = arrow.utcnow().replace(minutes=5)
    payload['exp'] = exp
    private_key = await get_private_key()
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token.decode('utf-8')


async def decode_token(token: str) -> dict:
    async with aiofiles.open(PUBLIC_KEY_FILE, 'rb') as pub_file:
        pub_key = await pub_file.read()
        payload = jwt.decode(token, pub_key, algorithms=['RS256'])
    return payload


async def verify_token(token: str) -> dict:
    data = await decode_token(token)
    if expired:
        raise jwt.ExpiredSignatureError
    return data
