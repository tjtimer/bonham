from aiohttp_jinja2 import render_template

__all__ = ['index']
async def get_context(request):
    return dict(
            title='NEUME',
            lang='de_DE'
            )

async def index(request):
    context = await get_context(request)
    resp = render_template('index.html', request, context)
    print(resp)
    return resp
