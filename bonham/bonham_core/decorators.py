import json
from functools import wraps

__all__ = [
    'db_connection',
    'load_data',
    'query_string',
    ]


def db_connection(handler):
    """(decorator) db_connection
    provides request['db_connection'] to wrapped handler.

    Usage:
        @db_connection
        async def my_handler(request):
            my_model_instance = MyModel(request['connection'], **data)
            # use any db function on instance
            await my_model_instance.create()  # or .update(), .get(), etc.
            ...
    """

    @wraps(handler)
    async def db_engine(request):
        print(f"handler {handler} requires a db connection")
        async with request.app.db.pool.acquire() as request['db_connection']:
            async with request['db_connection'].transaction():
                result = await handler(request)
        return result

    return db_engine


def load_data(handler, key: str = 'data'):
    @wraps(handler)
    async def wrapped(request):
        data = await request.content.read()
        if data is not b'':
            request[key] = json.loads(data.decode('utf-8'))
        return await handler(request)

    return wrapped


def query_string(handler):
    @wraps(handler)
    async def wrapped(request):
        qs = request.rel_url.query_string
        if qs:
            request['query'] = {pair.split('=')[0]: pair.split('=')[1] for pair
                                in qs.split('&')}
            print(f"request query: {request['query']}", flush=True)
        else:
            request['query'] = {
                'offset': 0,
                'order_by': 'id',
                'limit': 100
                }
        return await handler(request)

    return wrapped
