"""
    Author: Tim Jedro (a.k.a. tjtimer)
"""
import os
from asyncio import gather
import aiofiles as af
from bonham.utils import prepared_uvloop

async def write_init(config):
    template = os.path.join(os.path.dirname(__file__), 'templates', '__init__.tmpl')
    content = f"# {config['app_name']} / __init__.py\n\n"
    async with af.open(template, 'r') as tpl:
        async with af.open('__init__.py', 'w') as init:
            await init.write(content)
            async for line in tpl:
                print(line)
                await init.write(f"{line}\n")

async def write_root(config):
    async with af.open('root.py', 'w') as root:
        await root.write(f"# {config['app_name']} / root.py\n"
                         f"\n__all__ = []\n"
                         f"\n\n"
                         f"async def setup(app):\n"
                         f"    # setup routes, add db tables, e.t.c."
                         f"    return app\n"
                         f"\n"
                         f"async def shutdown(app):\n"
                         f"    return\n")

async def write_handler(config):
    async with af.open('handler.py', 'w') as handler:
        await handler.write(f"# {config['app_name']} / handler.py\n"
                            f"\n__all__ = []\n")

async def write_models(config):
    async with af.open('models.py', 'w') as models:
        await models.write(f"# {config['app_name']} / models.py\n"
                           f"\nfrom bonham.models import Base, BaseModel\n"
                           f"\n__all__ = []\n")

async def write_middlewares(config):
    async with af.open('middlewares.py', 'w') as middlewares:
        await middlewares.write(f"# {config['app_name']} / middlewares.py\n"
                                f"\n__all__ = []\n")

async def write_tests(config):
    pass


def scaffold(config):
    cwd = os.getcwd()
    print(f"starting scaffolding changing to app directory {config['app_dir']}")
    os.chdir(config['app_dir'])
    print(f"creating tests folder")
    os.mkdir('tests')
    loop = prepared_uvloop()
    print(f"starting now to create files")
    loop.run_until_complete(
            gather(
                    write_init(config),
                    write_root(config),
                    write_handler(config),
                    write_models(config),
                    write_middlewares(config),
                    write_tests(config)
                    )
            )
    print(f"done scaffolding changing back to original directory {cwd}")
    os.chdir(cwd)
    return
