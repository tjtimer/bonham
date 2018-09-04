from vibora import Request, Response, blueprints as bp
from vibora.hooks import Events

security = bp.Blueprint()


@security.route('/')
async def index(request: Request):
    print('request')
    return Response(b'security index response')
