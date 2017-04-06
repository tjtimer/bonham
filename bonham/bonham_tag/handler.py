from aiohttp import web

from bonham import db
from bonham.serializer import serialize, serialize_iter
from .models import Tag, TaggedItem


async def valid_tag(data):
    if 'name' not in data.keys():
        return False
    too_long = len(data['name']) >= 60
    too_short = len(data['name']) <= 3
    invalid = all([too_long, too_short])
    return not invalid


async def create_tag(request):
    try:
        valid = await valid_tag(request['data'])
        if valid:
            tag = await Tag.get_or_create(request['connection'], data=request['data'])
            tag_serialized = await serialize('tag', tag)
            return web.json_response(tag_serialized)
        else:
            message = f"this is not valid tag data"
            #  print(message)
            return web.json_response(dict(error=message), status=400)
    except Exception as e:
        message = f"Exception at create_tag handler: {type(e).__name__}: {e}"
        #  print(message)
        return web.json_response(dict(error=message), status=400)


async def get_tags(request):
    try:
        tags = await db.get(request['connection'], table=Tag.__table__, **request['query'])
        tags_serialized = await serialize_iter('tags', tags)
        return web.json_response(tags_serialized)
    except Exception as e:
        message = f"Exception at get_tags {type(e).__name__}: {e}"
        #  print(message)
        return web.json_response(dict(error=message), status=400)


async def create_tagged_item(request):
    tag_table = Tag.__table__
    tag_data = dict(name=request.match_info['tag_name'])
    ti_table = TaggedItem.__table__
    # print(tag_data, await valid(tag_data))
    try:
        object_exists = await db.get_by_id(request['connection'],
                                           table=request['data']['table'],
                                           object_id=request['data']['object_id'])
        if object_exists:
            tag = await Tag.get_or_create(request['connection'], data=tag_data)
            data = dict(tag_id=tag['id'], table=request['data']['table'], object_id=request['data']['object_id'])
            tagged_item = await db.create(request['connection'], table=ti_table, data=data)
            ti_serialized = await serialize(tagged_item)
            return web.json_response(dict(tagged_item=ti_serialized))
        return web.json_response(dict(error=f"the object you want to tag does not exist."), status=400)
    except Exception as e:
        message = f"Exception at create_tagged_item: {type(e).__name__}: {e}"
        print(message)
        return web.json_response(dict(error=message), status=400)


async def get_tagged_items(request):
    try:
        tagged_items = await db.get(request['connection'],
                                    table=TaggedItem.__table__,
                                    **dict(where=f"tag_id={request['data']['tag']['id']}"))
        tagged_items_serialized = [await serialize(item_data) for item_data in tagged_items]
        return web.json_response(dict(tagged_items=tagged_items_serialized))
    except Exception as e:
        message = f"Exception at get_tagged_items {type(e).__name__}: {e}"
        return web.json_response(dict(error=message))
