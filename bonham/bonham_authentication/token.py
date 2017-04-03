import datetime
import os.path as path

import aiofiles
from aiohttp.web_request import Request
import jwt

from bonham.settings import DEBUG, RSA_PEM, RSA_PUB
from ._functions import create_self_signed_ca

if DEBUG and not path.isfile(RSA_PUB):
    create_self_signed_ca()


async def create(*, payload: dict = None) -> str:
    if payload is None:
        raise ValueError(f"payload must not be None")
    payload['exp'] = datetime.datetime.now() + datetime.timedelta(seconds=10)
    async with aiofiles.open(RSA_PEM, 'r') as secret_key_file:
        secret_key = await secret_key_file.read()
    token = jwt.encode(payload, secret_key, algorithm='RS256')
    return token.decode('utf-8')


async def decode(*, token: str = None) -> dict:
    async with aiofiles.open(RSA_PUB, 'r') as pub_file:
        pub_key = await pub_file.read()
    payload = jwt.decode(token, pub_key, algorithms=['RS256'])
    return payload


async def verify_token(*, request: Request = None) -> dict:
    try:
        data = await decode(token=request['auth_token'])
        expired = datetime.datetime.utcfromtimestamp(data['exp']) < datetime.datetime.now()
        if expired:
            raise jwt.ExpiredSignatureError(data['id'])
        return data
    except jwt.DecodeError:
        raise jwt.DecodeError
