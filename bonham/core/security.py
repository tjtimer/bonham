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


def read_app_secret(config):
    app_sec_file = opj(config.SECRETS_DIR, config.NAME)
    with open(app_sec_file, 'r') as file:
        secret = file.read()
        return secret


async def get_secret(path):
    async with aiofiles.open(path, 'rb') as file:
        secret = await file.read()
        return secret


async def create_secret(path):
    secret = secrets.token_bytes(48)
    async with aiofiles.open(path, 'wb') as file:
        await file.write(secret)
    os.chmod(path, 300)


def create_app_pw(config):
    app_pwd_path = f'.secrets/.{config["name"]}.{arrow.now().for_json()}.sec'
    app_sec = opj(config['root_dir'], app_pwd_path)
    pw = getpass('application password please:')
    hash = pwd_context.hash(pw)
    with open(app_sec, 'w') as cf:
        cf.write(hash)
    os.chmod(app_sec, 300)


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
