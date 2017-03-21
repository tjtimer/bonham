import datetime
import os.path as path
from functools import partial

import jwt

from bonham.settings import DEBUG, RSA_PEM, RSA_PUB
from bonham.utils import prepared_uvloop
from ._functions import create_self_signed_ca

if DEBUG and not path.isfile(RSA_PUB):
    create_self_signed_ca()


class Token(object):
    def __init__(self, *, loop=None):
        self.loop = loop or prepared_uvloop()
        self.expire = datetime.datetime.now() + datetime.timedelta(hours=10)

    @staticmethod
    def decode(*, token: str = None) -> dict:
        pub = open(RSA_PUB, 'r').read()
        payload = jwt.decode(token, pub, algorithms=['RS256'])
        return payload

    async def create_token(self, *, payload: dict = None) -> str:
        payload.update(exp=self.expire)
        secret_key = open(RSA_PEM, 'r').read()
        token = jwt.encode(payload, secret_key, algorithm='RS256')
        yield token

    async def create(self, *, payload: dict = None) -> bytes:
        if payload is None:
            raise ValueError(f"payload must not be None")
        payload['exp'] = self.expire
        token = b''
        async for a in self.create_token(payload=payload):
            token += a
        return token.decode('utf-8')

    async def verify_token(self, *, token: bytes = None) -> dict:
        data = await self.loop.run_in_executor(None, partial(self.decode, token=token))
        expired = datetime.datetime.utcfromtimestamp(data['exp']) < datetime.datetime.now()
        if expired:
            raise jwt.ExpiredSignatureError("Token expired! Please try to log in again.")
        return data
