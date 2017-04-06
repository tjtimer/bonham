from aiohttp import web
from asyncpg import UniqueViolationError

from bonham import db
from bonham.bonham_authentication.models import Account
from bonham.bonham_authentication.root import authentication_required_response
from bonham.error_responses import invalid_data_response
from bonham.serializer import serialize
from bonham.utils import random_rgb
from bonham.validators import is_valid_color
from .models import Calendar, CalendarType


async def validate(data):
    invalid = dict()
    if not await CalendarType.valid_type(data['type']):
        has_to_be = "longer than 4 and shorter than 64 characters and must not contain special characters"
        invalid['calendar_type'] = dict(value=data['type'], has_to_be=has_to_be)
    if not await Calendar.valid_title(data['title']):
        has_to_be = "longer than 4 and shorter than 64 characters and must not contain special characters"
        invalid['title'] = dict(value=data['title'], has_to_be=has_to_be)
    if not await is_valid_color(data['color']):
        has_to_be = "a valid rgb value, e.g rgb(255, 255, 255)"
        invalid['color'] = dict(value=data['color'], has_to_be=has_to_be)
    if len(invalid.keys()):
        return invalid
    return None


async def create_calendar(request):
    data = request['data']
    if not request['is_authenticated']:
        response = await authentication_required_response()
        return response
    if 'color' not in data.keys():
        data['color'] = await random_rgb()
    invalid = await validate(data)
    if invalid is not None:
        response = await invalid_data_response(invalid)
        return response
    cal_type = await CalendarType.get_or_create(request['connection'], data=dict(title=data['type']))
    cal_data = {
        'owner': request['account']['id'],
        'type': cal_type           ['id'],
        'title': data              ['title'],
        'color': data              ['color']
        }
    try:
        calendar = await Calendar.create(request['connection'], data=cal_data)
        calendar['type'] = cal_type
        calendar_serialized = await serialize('calendar', calendar)
        return web.json_response(calendar_serialized)
    except UniqueViolationError:
        return web.json_response(dict(error="You already have a calendar with that type and that title."), status=400)


async def get_calendars(request):
    calendars = await db.get(request['connection'], table=Calendar.__table__)
    async with request['connection'].transaction():
        for calendar in calendars:
            calendar['type'] = await db.get_by_id(request['connection'],
                                          table=CalendarType.__table__,
                                          object_id=calendar['type'])
            calendar['owner'] = await db.get_by_id(request['connection'],
                                                   table=Account.__table__,
                                                   object_id=calendar['owner'])
        calendars = await serialize('calendars', calendars)
    return web.json_response(calendars)
