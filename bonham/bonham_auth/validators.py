from asyncio import gather

from bonham.bonham_core import validators as v

__all__ = ['is_valid_password', 'is_valid_sign_up_data']

async def is_valid_password(value: str = None) -> bool:
    password_props = await gather(
            v.is_longer_than(value, 8),
            v.has_digits(value),
            v.has_uppercase(value),
            v.has_lowercase(value),
            v.has_special_chars(value),
            v.has_no_whitespaces(value)
            )
    return all(val for val in password_props)


async def is_valid_sign_up_data(data: dict = None) -> bool:
    return all(await gather(v.is_valid_email(data['email']), is_valid_password(data['password'])))
