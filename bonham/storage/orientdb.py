# _orientdb
from aio_pyorient.pool import ODBPool
from aiohttp import web


async def setup(app: web.Application, user: str, password: str, *, min: int = 5, max: int = -1, db_name: str = None,
                **kwargs):
    pool = ODBPool(user=user, password=password, db_name=db_name, min=min, max=max, **kwargs)
    await pool.setup()
    await check_db_state(pool)


async def shutdown(app: web.Application):
    await app['odb'].shutdown()
    app['odb'] = None


async def check_db_state(pool: ODBPool):
    cl = await pool.acquire()
