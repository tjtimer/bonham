"""
app.py
"""
from aiohttp import web


# decorate your handlers with this
# routes instance.
# for more information on routes see:
# http://aiohttp.readthedocs.io/en/stable/web_reference.html#routetabledef
routes = web.RouteTableDef()


async def setup(root: web.Application):
    app = web.Application()
    #
    # You should prepare your apps
    # initial state here.
    # Initialize your database connection pool,
    # populate your tables with whatever could
    # be useful or needs to be there on startup
    # or add your middlewares to your app...
    #
    app.router.add_routes(routes)
    app['root'] = root
    root.add_subapp("/{{ name }}", {{app}})
