import logging

import pytest

from bonham.root import init_app


@pytest.mark.asyncio
async def test_init_app():
    app = await init_app()
    print(app.__dict__)
    assert app.logger == logging.getLogger('bonham.root')
    assert all(key in ['db', 'aiohttp_jinja2_environment'] for key in app.keys())
