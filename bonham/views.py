from aiohttp_jinja2 import template


@template('index.html')
async def index(request):
    print(f"Index page was requested.\nrequest:\t{request}")
    return {
        'title': 'Bonham',
        'lang': 'de_DE'
    }
