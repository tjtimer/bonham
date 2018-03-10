import arrow
from aiohttp import web
from passlib.hash import pbkdf2_sha512

from bonham.core.exceptions import RequestDenied


__all__ = [
    'check_password',
    'check_retries',
    'update_failed'
    ]

async def check_password(request: web.Request, db_pass: str):
    req_pass = request['data']['password']
    if not pbkdf2_sha512.verify(req_pass, db_pass):
        await update_failed(request)
        raise RequestDenied('wrong password')


async def check_retries(email: str, failed_logins: dict) -> None:
    now = arrow.now()
    three_or_more = len(failed_logins[email]) >= 3
    less_than_90s = failed_logins[email][-1].replace(seconds=90) <= now
    if three_or_more and less_than_90s:
        wait_until = now.replace(minutes=5).format('HH:mm:ss')
        error_message = f"To many retries. wait 5 minutes, until {wait_until}."
        raise RequestDenied(error_message)


async def update_failed(request: web.Request) -> None:
    email = request['data']['email']
    failed_logins = request.app['failed_logins']
    now = arrow.now()
    if email in failed_logins.keys():
        await check_retries(email, failed_logins)
        failed_logins[email].append(now)
    else:
        failed_logins[email] = [now]
