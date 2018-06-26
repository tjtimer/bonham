!  # /usr/bin/python3
"""
security
"""
import os
import secrets
from getpass import getpass
from pathlib import Path

import aiofiles
import arrow
from passlib.context import CryptContext

from bonham.core.utils import opj

pwd_context = CryptContext(
    # Replace this list with the hash(es) you wish to support.
    # this example sets pbkdf2_sha256 as the default,
    # with additional support for reading legacy des_crypt hashes.
    schemes=["pbkdf2_sha512", "pbkdf2_sha256"],

    # Automatically mark all but first hasher in list as deprecated.
    # (this will be the default in Passlib 2.0)
    deprecated="auto",

    # Optionally, set the number of rounds that should be used.
    # Appropriate values may vary for different schemes,
    # and the amount of time you wish it to take.
    # Leaving this alone is usually safe, and will use passlib's defaults.
    ## pbkdf2_sha256__rounds = 29000,
    pbkdf2_sha512__rounds=426642
)


def app_sec_file(config): return opj(config.SECRETS_DIR, f'.{config.NAME}.sec')


def create_app_secret(config):
    fn = app_sec_file(config)
    pw = getpass('application password please:')
    hash = pwd_context.hash(pw)
    with open(fn, 'w') as cf:
        cf.write(hash)
    os.chmod(fn, 300)


def read_app_secret(config):
    with open(app_sec_file(config), 'r') as file:
        secret = file.read()
        return secret


async def get_secret(name, path):
    async with aiofiles.open(opj(path, name), 'rb') as file:
        secret = await file.read()
        return secret


async def create_secret(name, path):
    secret = secrets.token_bytes(48)
    f = opj(path, name)
    async with aiofiles.open(f, 'wb') as file:
        await file.write(secret)
    os.chmod(f, 300)


def verify_start_permissions(config, retry):
    pw_hash = read_app_secret(config)
    to_file = opj(config.SECRETS_DIR, '.to')
    if not pwd_context.verify(
            getpass('application password please:'), pw_hash):
        retry += 1
        if retry > 3:
            with open(to_file, 'wb') as f:
                f.write(b' ')
            os.chmod(to_file, 300)
        return False


def check_retries_to(config):
    to_file = opj(config.SECRETS_DIR, '.to')
    if os.path.exists(to_file):
        five_m_before = arrow.now().replace(minutes=-5)
        created = Path(to_file).stat().st_ctime
        if created > five_m_before:
            raise OSError("You are currently not allowed to start this app!")
        else:
            os.remove(to_file)
