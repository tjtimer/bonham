import datetime
from uuid import uuid4

import jwt
import os.path as path

from bonham.settings import DEBUG, RSA_PEM, RSA_PUB
from ._functions import create_self_signed_ca


class Token:
    def __init__(self):
        self.RSA_PEM = RSA_PEM
        self.RSA_PUB = RSA_PUB
        if DEBUG and not path.isfile(self.RSA_PUB):
            create_self_signed_ca()

    async def create(self, user):
        """
        :params payload:
            iss: The issuer of the token

            sub: The subject of the token

            aud: The audience of the token

            qsh: query string hash

            exp: Token expiration time defined in Unix time

            nbf: “Not before” time that identifies the time before which the JWT must not be accepted for processing

            iat: “Issued at” time, in Unix time, at which the token was issued

            jti: JWT ID claim provides a unique identifier for the JWT
            - See more at: http://blog.apcelent.com/json-web-token-tutorial-example-python.html#sthash.leAneZ4u.dpuf
        """
        uid = uuid4()
        expire = datetime.datetime.today() + datetime.timedelta(days=10)
        payload = {
            'exp': expire,
            'uid': uid.int,
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
        secret_key = open(self.RSA_PEM, 'r').read()
        token = jwt.encode(payload, secret_key, algorithm='RS256')
        return token

    async def decode(self, token):
        pub = open(self.RSA_PUB, 'r').read()
        return jwt.decode(token, pub, algorithms=['RS256'])

    async def verify_user(self, token):
        try:
            data = await self.decode(token)
            expired = datetime.datetime.fromtimestamp(data['exp']) < datetime.datetime.now()
            if not expired:
                return { key: value for key, value in data.items() if key in 'id name email' }
        except Exception as error:
            raise ValueError(f"Token verify error: {error}")
        return None
