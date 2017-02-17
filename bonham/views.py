import aiohttp_jinja2


async def index(request):
    response = aiohttp_jinja2.render_template('index.html',
                                              request,
                                              {
                                                  'title': 'Bonham',
                                                  'lang': 'de_DE'
                                              })
    return response
