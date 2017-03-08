from aiohttp_jinja2 import template


@template('index.html')
async def index(request):
    return {
        'title': 'Bonham',
        'lang': 'de_DE'
    }
